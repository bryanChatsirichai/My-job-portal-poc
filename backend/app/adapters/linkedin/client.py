"""HTTP client for the self-hosted LinkedIn Jobs API."""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 120.0


async def fetch_jobs_page(
    *,
    base_url: str,
    page: int,
    location: str,
    keywords: str | None,
    date_since_posted: str | None,
    use_analyze: bool,
    user_skills: list[str],
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """Call ``/jobs/search`` or ``/jobs/analyze`` and return the parsed JSON body."""
    root = base_url.rstrip("/")
    path = "/jobs/analyze" if use_analyze else "/jobs/search"
    url = f"{root}{path}"

    query: dict[str, str | int] = {
        "page": page,
        "location": location,
    }
    if keywords:
        query["keywords"] = keywords
    if date_since_posted:
        query["dateSincePosted"] = date_since_posted
    if use_analyze and user_skills:
        query["userSkills"] = ",".join(user_skills)

    logger.info("LinkedIn Jobs API request: %s params=%s", url, query)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url, params=query)
        response.raise_for_status()
        return response.json()
