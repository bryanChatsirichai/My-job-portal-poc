"""Job sync orchestration.

Pulls listings from enabled ``JobSourceAdapter`` instances, normalizes each
record into ``CanonicalJobInput``, and upserts into the database. After a
full source sync, jobs that were not seen during the run are marked expired.

CLI trace (continues from ``app.worker.__main__``):

  Step 6  — ``sync_all()`` (entry from ``run_sync``).
  Step 7  — ``get_adapters()`` — which sources run (``*_ENABLED`` + credentials).
  Step 8  — ``sync_source(adapter)`` — once per adapter in the list.
  Step 9  — inside ``sync_source``: ``fetch_jobs`` loop (see ``app.adapters.*``).
  Step 10 — ``_upsert_batch`` → ``app.db.upsert.upsert_job``.
  Step 11 — ``expire_stale_jobs`` after all pages for that adapter.
  Step 12 — ``sync_all`` merges stats and returns to ``run_sync``.
"""

import logging
from typing import TypedDict

from app.adapters.adzuna.adapter import AdzunaAdapter
from app.adapters.base import FetchParams, JobSourceAdapter
from app.adapters.jobicy.adapter import JobicyAdapter
from app.adapters.jobspy.adapter import JobSpyAdapter
from app.adapters.linkedin.adapter import LinkedInAdapter
from app.adapters.mycareersfuture.adapter import MyCareersFutureAdapter
from app.config import settings
from app.db.session import SessionLocal
from app.db.upsert import expire_stale_jobs, upsert_job

logger = logging.getLogger(__name__)

# Per-source batch size; must align with each adapter's pagination semantics.
_PAGE_SIZE_BY_SOURCE: dict[str, int] = {
    "adzuna": settings.adzuna_page_size,
    "jobicy": settings.jobicy_page_size,
    "linkedin": settings.linkedin_page_size,
    "jobspy": settings.jobspy_page_size,
    "mycareersfuture": settings.mcf_page_size,
}

_MAX_PAGES_BY_SOURCE: dict[str, int | None] = {
    "adzuna": settings.adzuna_max_pages,
    "jobicy": settings.jobicy_max_pages,
    "linkedin": settings.linkedin_max_pages,
    "jobspy": settings.jobspy_max_pages,
    "mycareersfuture": settings.mcf_max_pages,
}


class SyncResult(TypedDict, total=False):
    """Summary returned by ``sync_source`` / ``sync_all``."""

    source: str
    fetched: int
    upserted: int
    expired: int
    skipped: str
    error: str


def get_adapters() -> list[JobSourceAdapter]:
    """Build the list of adapters to run based on feature flags and credentials.

    Toggle-only sources (MCF, Jobicy) register when ``*_ENABLED`` is true.
    Credential-gated sources (Adzuna, LinkedIn) also require API settings.
    """
    # Step 7 — register adapters in fixed order (MCF → Jobicy → Adzuna → LinkedIn → JobSpy)
    adapters: list[JobSourceAdapter] = []

    _register_toggle(
        adapters,
        enabled=settings.mcf_enabled,
        adapter_cls=MyCareersFutureAdapter,
        label="MyCareersFuture",
        env_flag="MCF_ENABLED",
    )
    _register_toggle(
        adapters,
        enabled=settings.jobicy_enabled,
        adapter_cls=JobicyAdapter,
        label="Jobicy",
        env_flag="JOBICY_ENABLED",
    )
    _register_credential_gated(
        adapters,
        enabled=settings.adzuna_enabled,
        adapter_cls=AdzunaAdapter,
        label="Adzuna",
        env_flag="ADZUNA_ENABLED",
        missing_config_hint="set ADZUNA_APP_ID and ADZUNA_APP_KEY",
    )
    _register_credential_gated(
        adapters,
        enabled=settings.linkedin_enabled,
        adapter_cls=LinkedInAdapter,
        label="LinkedIn",
        env_flag="LINKEDIN_ENABLED",
        missing_config_hint="set LINKEDIN_JOBS_API_URL",
    )
    _register_credential_gated(
        adapters,
        enabled=settings.jobspy_enabled,
        adapter_cls=JobSpyAdapter,
        label="JobSpy",
        env_flag="JOBSPY_ENABLED",
        missing_config_hint="set JOBSPY_API_URL",
    )
    return adapters


def _register_toggle(
    adapters: list[JobSourceAdapter],
    *,
    enabled: bool,
    adapter_cls: type[JobSourceAdapter],
    label: str,
    env_flag: str,
) -> None:
    if enabled:
        adapters.append(adapter_cls())
    else:
        logger.info("%s adapter disabled (%s=false)", label, env_flag)


def _register_credential_gated(
    adapters: list[JobSourceAdapter],
    *,
    enabled: bool,
    adapter_cls: type[JobSourceAdapter],
    label: str,
    env_flag: str,
    missing_config_hint: str,
) -> None:
    if adapter_cls.is_configured():
        adapters.append(adapter_cls())
    elif enabled:
        logger.info("%s adapter not registered (%s)", label, missing_config_hint)
    else:
        logger.info("%s adapter disabled (%s=false)", label, env_flag)


def _page_size(adapter: JobSourceAdapter) -> int:
    """Return the configured fetch batch size for a source."""
    return _PAGE_SIZE_BY_SOURCE.get(adapter.source_name, settings.mcf_page_size)


def _max_pages(adapter: JobSourceAdapter) -> int | None:
    """Return the configured page cap for a source (``None`` = unlimited)."""
    return _MAX_PAGES_BY_SOURCE.get(adapter.source_name)


def _upsert_batch(
    adapter: JobSourceAdapter,
    raw_jobs: list[dict],
    seen_by_source: dict[str, set[str]],
) -> int:
    """Normalize and persist one page of raw jobs; track IDs seen this run per source."""
    # Step 10 — one DB session per API page batch
    db = SessionLocal()
    upserted = 0
    try:
        for raw in raw_jobs:
            normalized = adapter.normalize(raw)
            # Step 10 (continued) — insert or update ``jobs`` row; see app.db.upsert
            upsert_job(db, normalized)
            seen_by_source.setdefault(normalized.source, set()).add(normalized.source_job_id)
            upserted += 1
    finally:
        db.close()
    return upserted


def _page_limit_reached(adapter: JobSourceAdapter, page: int, max_pages: int | None) -> bool:
    """Return True when pagination should stop before fetching ``page``."""
    if max_pages is None:
        return False
    # JobSpy: max_pages is the last 0-based search-term index (inclusive).
    if adapter.source_name == "jobspy":
        return page > max_pages
    return page >= max_pages


async def sync_source(adapter: JobSourceAdapter) -> SyncResult:
    """Fetch, normalize, and upsert all pages for one job source.

    Step 8 — one adapter per call from ``sync_all``.

    Paginates until the adapter returns an empty page, a short page (fewer
    results than ``limit``), or the source ``*_MAX_PAGES`` env cap is reached.
    Jobs active in the DB but absent from this run are marked expired afterward.

    Returns a ``skipped`` result when called directly with an unconfigured
    credential-gated adapter (defensive guard; ``get_adapters`` normally
    omits those).
    """
    if adapter.source_name == "adzuna" and not AdzunaAdapter.is_configured():
        return {"source": adapter.source_name, "skipped": "not_configured"}
    if adapter.source_name == "linkedin" and not LinkedInAdapter.is_configured():
        return {"source": adapter.source_name, "skipped": "not_configured"}
    if adapter.source_name == "jobspy" and not JobSpyAdapter.is_configured():
        return {"source": adapter.source_name, "skipped": "not_configured"}

    page_size = _page_size(adapter)
    max_pages = _max_pages(adapter)
    seen_by_source: dict[str, set[str]] = {}
    fetched = 0
    upserted = 0

    contexts = adapter.fetch_contexts()
    if not contexts:
        logger.info("sync skipped for source=%s (no fetch contexts)", adapter.source_name)
        return {"source": adapter.source_name, "skipped": "no_fetch_contexts"}

    for keywords in contexts:
        page = 0
        while True:
            if _page_limit_reached(adapter, page, max_pages):
                break

            # Step 9 — adapter calls upstream API (implementation in app.adapters.<source>)
            raw_jobs = await adapter.fetch_jobs(
                FetchParams(
                    page=page,
                    limit=page_size,
                    max_pages=max_pages,
                    keywords=keywords,
                )
            )
            if not raw_jobs:
                break

            fetched += len(raw_jobs)
            upserted += _upsert_batch(adapter, raw_jobs, seen_by_source)

            # JobSpy: one API page = one search term (any job count); stop on empty only.
            if adapter.source_name == "jobspy":
                page += 1
                continue

            # A partial page means the upstream API has no more results.
            if len(raw_jobs) < page_size:
                break
            page += 1

    # Step 11 — mark active jobs missing from this run as expired (per canonical source)
    db = SessionLocal()
    expired = 0
    try:
        for source, seen_ids in seen_by_source.items():
            expired += expire_stale_jobs(db, source, seen_ids)
    finally:
        db.close()

    stats: SyncResult = {"fetched": fetched, "upserted": upserted, "expired": expired}
    logger.info("sync complete", extra={"source": adapter.source_name, **stats})
    return stats


async def sync_all() -> list[SyncResult]:
    """Run ``sync_source`` for every registered adapter.

    Failures are isolated per source — one adapter error does not block the
    rest. Each result includes ``source`` plus stats or an ``error`` key.
    """
    # Step 6 — top-level ingestion entry (CLI and scheduler both call this)
    results: list[SyncResult] = []
    for adapter in get_adapters():
        try:
            stats = await sync_source(adapter)
            # Step 12 — per-source outcome (stats or skipped keys inside stats)
            results.append({"source": adapter.source_name, **stats})
        except Exception:
            logger.exception("sync failed for source %s", adapter.source_name)
            results.append({"source": adapter.source_name, "error": "sync_failed"})
    return results
