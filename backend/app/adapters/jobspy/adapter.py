"""JobSpy adapter via self-hosted JobSpy FastAPI sidecar.

Requires ``JOBSPY_API_URL`` pointing at a running ``jobspy_api`` instance.
Each worker page maps to one search-term sweep across configured job boards.
"""

from __future__ import annotations

import hashlib
import logging

import httpx

from app.adapters.base import FetchParams, JobSourceAdapter
from app.adapters.utils import (
    normalize_salary_period,
    parse_datetime,
    split_csv_field,
    title_case_snake,
    to_decimal,
)
from app.config import settings
from app.models.schemas import CanonicalJobInput, LocationSchema

logger = logging.getLogger(__name__)


class JobSpyAdapter(JobSourceAdapter):
    """Fetches job listings from a self-hosted JobSpy API service."""

    source_name = "jobspy"

    @staticmethod
    def is_configured() -> bool:
        """Return True when the adapter is enabled and the API base URL is set."""
        return settings.jobspy_enabled and bool(settings.jobspy_api_url.strip())

    async def fetch_jobs(self, params: FetchParams) -> list[dict]:
        if not self.is_configured():
            logger.warning("JobSpy API URL not set; skip sync for source=jobspy")
            return []

        query: dict[str, int] = {"page": params.page}
        base_url = settings.jobspy_api_url.rstrip("/")
        url = f"{base_url}/jobs/search"
        logger.info("JobSpy API request: %s params=%s", url, query)
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.get(url, params=query)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            logger.warning("JobSpy API request failed (page=%s): %s", params.page, exc)
            return []

        if not data.get("success", True):
            logger.warning("JobSpy API returned success=false (page=%s)", params.page)
            return []

        jobs = data.get("jobs", [])
        logger.info(
            "JobSpy API page %s (%s) returned %s jobs",
            params.page,
            data.get("search_term"),
            len(jobs),
        )
        return jobs

    def normalize(self, raw: dict) -> CanonicalJobInput:
        """Map a JobSpy record to ``CanonicalJobInput``."""
        job_url = raw.get("job_url") or raw.get("job_url_direct") or ""
        source_job_id = raw.get("id") or _fallback_job_id(job_url)

        location_text = raw.get("location") or ""
        apply_url = raw.get("job_url_direct") or raw.get("job_url") or job_url

        posted = raw.get("date_posted")
        posted_str = str(posted) if posted is not None else None

        return CanonicalJobInput(
            source=self.source_name,
            source_job_id=str(source_job_id),
            title=raw.get("title", "Untitled role"),
            company_name=raw.get("company") or "Unknown company",
            company_uen=None,
            location=LocationSchema(
                address=location_text or None,
                district=None,
                region=location_text or None,
            ),
            salary_min=to_decimal(raw.get("min_amount")),
            salary_max=to_decimal(raw.get("max_amount")),
            salary_currency=raw.get("currency"),
            salary_period=normalize_salary_period(raw.get("interval")),
            employment_type=title_case_snake(raw.get("job_type")),
            seniority_level=raw.get("job_level"),
            skills=split_csv_field(raw.get("skills")),
            description=raw.get("description"),
            posted_date=parse_datetime(posted_str),
            expiry_date=None,
            apply_url=apply_url or f"jobspy:{source_job_id}",
            raw_payload=raw,
        )


def _fallback_job_id(job_url: str) -> str:
    """Derive a stable ID from the job URL when the scraper omits ``id``."""
    if job_url:
        return hashlib.sha256(job_url.encode()).hexdigest()[:16]
    return hashlib.sha256(b"unknown").hexdigest()[:16]
