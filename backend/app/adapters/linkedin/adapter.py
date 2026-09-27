"""LinkedIn jobs adapter via self-hosted LinkedIn Jobs API.

Wraps: https://github.com/bryanChatsirichai/Linkedin-Jobs-Api (v2.1+ analyze)

Requires ``LINKEDIN_JOBS_API_URL`` pointing at a running instance. Search
filters (location, keywords, recency) come from application settings. The
upstream API uses 1-based pages; this adapter accepts 0-based ``FetchParams``.

Use ``LINKEDIN_USE_ANALYZE=true`` (default) so listings include ``insights``
(salary, skills, seniority). Comma-separated ``LINKEDIN_KEYWORDS`` runs one
sync pass per term via ``fetch_contexts``.
"""

from __future__ import annotations

import logging
import re
from typing import Any
from urllib.parse import urlparse

import httpx

from app.adapters.base import FetchParams, JobSourceAdapter
from app.adapters.linkedin.client import fetch_jobs_page
from app.adapters.utils import (
    normalize_salary_period,
    parse_datetime,
    split_csv_field,
    to_decimal,
)
from app.config import settings
from app.models.schemas import CanonicalJobInput, LocationSchema

logger = logging.getLogger(__name__)

_JOB_ID_PATTERN = re.compile(r"(?:view/|-)(\d+)")


class LinkedInAdapter(JobSourceAdapter):
    """Fetches job listings from a self-hosted LinkedIn Jobs API service."""

    source_name = "linkedin"

    @staticmethod
    def is_configured() -> bool:
        """Return True when the adapter is enabled and the API base URL is set."""
        if not settings.linkedin_enabled or not settings.linkedin_jobs_api_url.strip():
            return False
        if settings.linkedin_keywords_required and not split_csv_field(settings.linkedin_keywords):
            return False
        return True

    def fetch_contexts(self) -> list[str | None]:
        """One upstream search per keyword; ``None`` means location-only (no keywords param)."""
        terms = split_csv_field(settings.linkedin_keywords)
        if settings.linkedin_keywords_required and not terms:
            return []
        if not terms:
            return [None]
        return terms

    async def fetch_jobs(self, params: FetchParams) -> list[dict]:
        if not self.is_configured():
            logger.warning("LinkedIn Jobs API URL not set; skip sync for source=linkedin")
            return []

        api_page = params.page + 1
        user_skills = split_csv_field(settings.linkedin_user_skills)
        try:
            data = await fetch_jobs_page(
                base_url=settings.linkedin_jobs_api_url,
                page=api_page,
                location=settings.linkedin_location,
                keywords=params.keywords,
                date_since_posted=settings.linkedin_date_since_posted or None,
                use_analyze=settings.linkedin_use_analyze,
                user_skills=user_skills,
            )
        except httpx.HTTPError as exc:
            logger.warning(
                "LinkedIn Jobs API request failed (keywords=%r page=%s): %s",
                params.keywords,
                api_page,
                exc,
            )
            return []

        if not data.get("success", True):
            logger.warning(
                "LinkedIn Jobs API returned success=false (keywords=%r page=%s)",
                params.keywords,
                api_page,
            )
            return []

        jobs = data.get("jobs", [])
        logger.info(
            "LinkedIn Jobs API keywords=%r page %s returned %s jobs",
            params.keywords,
            api_page,
            len(jobs),
        )
        return jobs

    def normalize(self, raw: dict) -> CanonicalJobInput:
        """Map a LinkedIn Jobs API record to ``CanonicalJobInput``."""
        link = raw.get("link") or ""
        source_job_id = raw.get("id") or _extract_job_id(link) or link

        insights = raw.get("insights") or {}
        salary = _extract_salary(raw, insights)

        seniority = insights.get("seniorityLevel")
        if seniority == "unknown":
            seniority = None

        employment_type = insights.get("jobType")
        if employment_type == "unknown":
            employment_type = None
        elif employment_type:
            employment_type = employment_type.replace("-", " ").title()

        skills = insights.get("requiredSkills") or []
        location_text = raw.get("location") or ""

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
            salary_min=to_decimal(salary.get("min")),
            salary_max=to_decimal(salary.get("max")),
            salary_currency=salary.get("currency"),
            salary_period=normalize_salary_period(salary.get("period")),
            employment_type=employment_type,
            seniority_level=seniority,
            skills=skills,
            description=None,
            posted_date=parse_datetime(raw.get("listDate")),
            expiry_date=None,
            apply_url=link or f"https://www.linkedin.com/jobs/view/{source_job_id}",
            raw_payload=raw,
        )


def _extract_salary(raw: dict[str, Any], insights: dict[str, Any]) -> dict[str, Any]:
    """Resolve salary from analyze ``insights`` or legacy/top-level shapes."""
    for candidate in (
        insights.get("salaryRange"),
        raw.get("salaryRange"),
        raw.get("salary"),
    ):
        if isinstance(candidate, dict) and any(
            candidate.get(k) is not None for k in ("min", "max", "currency", "period")
        ):
            return candidate
    return {}


def _extract_job_id(link: str) -> str | None:
    """Derive a stable job ID from a LinkedIn job URL when ``id`` is absent."""
    if not link:
        return None
    match = _JOB_ID_PATTERN.search(link)
    if match:
        return match.group(1)
    path = urlparse(link).path.rstrip("/")
    if path:
        return path.split("/")[-1]
    return None
