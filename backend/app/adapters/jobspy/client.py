"""HTTP client for the self-hosted JobSpy API sidecar."""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 300.0


async def fetch_search_page(
    *,
    base_url: str,
    page: int,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """Call ``GET /jobs/search`` (0-based search-term index) and return JSON."""
    root = base_url.rstrip("/")
    url = f"{root}/jobs/search"
    query = {"page": page}

    logger.info("JobSpy API request: %s params=%s", url, query)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url, params=query)
        response.raise_for_status()
        return response.json()
