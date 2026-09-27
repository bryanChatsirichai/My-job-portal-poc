"""JobSpy adapter via self-hosted JobSpy FastAPI sidecar.

Requires ``JOBSPY_API_URL`` pointing at a running ``jobspy_api`` instance
(see https://github.com/bryanChatsirichai/JobSpy/tree/feature/custom-api-upgrade/jobspy_api).

Each sync page is one 0-based search-term index: ``GET /v1/jobs/search?page=N``.
Configure terms and boards in the JobSpy repo ``.env`` (``JOBSPY_SEARCH_TERMS``,
``JOBSPY_SITE_NAMES``). Portal reads the same board list via ``JOBSPY_ENV_FILE`` or
``JOBSPY_SITE_NAMES`` for ingest filtering and UI source filters.

Each job's ``site`` field (indeed, glassdoor, …) is mapped to canonical ``source``
for filtering and badges in the portal UI.
"""

from __future__ import annotations

import hashlib
import logging

import httpx

from app.adapters.base import FetchParams, JobSourceAdapter
from app.adapters.jobspy.client import fetch_search_page
from app.adapters.jobspy.sites import source_from_site
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

        try:
            data = await fetch_search_page(
                base_url=settings.jobspy_api_url,
                page=params.page,
            )
        except httpx.HTTPError as exc:
            logger.warning("JobSpy API request failed (page=%s): %s", params.page, exc)
            return []

        if not data.get("success", True):
            logger.warning(
                "JobSpy API returned success=false (page=%s term=%s)",
                params.page,
                data.get("search_term"),
            )
            return []

        jobs = data.get("jobs") or []
        # Portal site filter disabled — boards are controlled by JobSpy ``JOBSPY_SITE_NAMES`` only.
        # allowed = allowed_jobspy_sources()
        # if allowed:
        #     jobs = [job for job in jobs if source_from_site(job.get("site")) in allowed]

        logger.info(
            "JobSpy API page %s (%s) returned %s jobs has_more=%s",
            data.get("page", params.page),
            data.get("search_term"),
            len(jobs),
            data.get("has_more"),
        )
        return jobs

    def normalize(self, raw: dict) -> CanonicalJobInput:
        """Map a JobSpy record to ``CanonicalJobInput``."""
        source = source_from_site(raw.get("site"))
        job_url = raw.get("job_url") or raw.get("job_url_direct") or ""
        source_job_id = raw.get("id") or _fallback_job_id(job_url)

        location_text = raw.get("location") or ""
        apply_url = raw.get("job_url_direct") or raw.get("job_url") or job_url

        posted = raw.get("date_posted")
        posted_str = str(posted) if posted is not None else None

        return CanonicalJobInput(
            source=source,
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
            apply_url=apply_url or f"{source}:{source_job_id}",
            raw_payload=raw,
        )


def _fallback_job_id(job_url: str) -> str:
    """Derive a stable ID from the job URL when the scraper omits ``id``."""
    if job_url:
        return hashlib.sha256(job_url.encode()).hexdigest()[:16]
    return hashlib.sha256(b"unknown").hexdigest()[:16]
