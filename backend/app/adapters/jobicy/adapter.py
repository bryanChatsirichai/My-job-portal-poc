"""Jobicy remote jobs adapter.

API docs: https://jobicy.com/jobs-rss-feed
Endpoint: ``GET /api/v2/remote-jobs``

No API key required. The upstream API returns up to 200 jobs in a single
response with no real pagination — ``fetch_jobs`` only runs on page 0 and
uses ``FetchParams.max_pages`` (from ``JOBICY_MAX_PAGES``) to cap the requested ``count``.
"""

import httpx

from app.adapters.base import FetchParams, JobSourceAdapter
from app.adapters.utils import normalize_salary_period, parse_datetime, to_decimal
from app.config import settings
from app.models.schemas import CanonicalJobInput, LocationSchema

JOBICY_BASE_URL = "https://jobicy.com/api/v2/remote-jobs"
API_MAX_COUNT = 200  # Hard cap enforced by the Jobicy API.
COUNT_PER_PAGE = 100  # One ``JOBICY_MAX_PAGES`` unit maps to 100 jobs.


def _resolve_count(max_pages: int | None) -> int:
    """Translate ``JOBICY_MAX_PAGES`` into the Jobicy ``count`` query parameter."""
    if max_pages is None:
        return API_MAX_COUNT
    return min(max_pages * COUNT_PER_PAGE, API_MAX_COUNT)


class JobicyAdapter(JobSourceAdapter):
    """Fetches remote job listings from the Jobicy public API."""

    source_name = "jobicy"

    async def fetch_jobs(self, params: FetchParams) -> list[dict]:
        # Jobicy has no pagination; only the first page request is meaningful.
        if params.page > 0:
            return []

        count = _resolve_count(params.max_pages)
        query: dict[str, str | int] = {"count": count}
        if settings.jobicy_geo:
            query["geo"] = settings.jobicy_geo
        if settings.jobicy_tag:
            query["tag"] = settings.jobicy_tag
        if settings.jobicy_industry:
            query["industry"] = settings.jobicy_industry

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(JOBICY_BASE_URL, params=query)
            response.raise_for_status()
            data = response.json()
            return data.get("jobs", [])

    def normalize(self, raw: dict) -> CanonicalJobInput:
        """Map a Jobicy job object to ``CanonicalJobInput``."""
        job_types = raw.get("jobType") or []
        industries = raw.get("jobIndustry") or []
        geo = raw.get("jobGeo")

        return CanonicalJobInput(
            source=self.source_name,
            source_job_id=str(raw["id"]),
            title=raw.get("jobTitle", "Untitled role"),
            company_name=raw.get("companyName") or "Unknown company",
            company_uen=None,
            location=LocationSchema(
                address=geo,
                district=None,
                region=geo,
            ),
            salary_min=to_decimal(raw.get("salaryMin")),
            salary_max=to_decimal(raw.get("salaryMax")),
            salary_currency=raw.get("salaryCurrency"),
            salary_period=normalize_salary_period(raw.get("salaryPeriod")),
            employment_type=job_types[0] if job_types else None,
            seniority_level=raw.get("jobLevel"),
            # Jobicy exposes industries, not discrete skills — stored in skills for search.
            skills=industries,
            description=raw.get("jobDescription"),
            posted_date=parse_datetime(raw.get("pubDate")),
            expiry_date=None,
            apply_url=raw.get("url") or f"https://jobicy.com/jobs/{raw['id']}",
            raw_payload=raw,
        )
