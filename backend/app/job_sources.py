"""Job source ids and labels for API filters (aligned with frontend badges)."""

from __future__ import annotations

from app.adapters.adzuna.adapter import AdzunaAdapter
from app.adapters.jobspy.sites import jobspy_board_source_ids
from app.adapters.linkedin.adapter import LinkedInAdapter
from app.config import settings

SOURCE_LABELS: dict[str, str] = {
    "mycareersfuture": "MyCareersFuture",
    "adzuna": "Adzuna",
    "jobicy": "Jobicy",
    "linkedin": "LinkedIn",
    "jobstreet": "JobStreet",
    "indeed": "Indeed",
    # "glassdoor": "Glassdoor",
    # "google": "Google Jobs",
    # "bayt": "Bayt",
    # "ziprecruiter": "ZipRecruiter",
    # "naukri": "Naukri",
    # "bdjobs": "BDJobs",
    "jobspy": "JobSpy",
}


def label_for_source(source_id: str) -> str:
    return SOURCE_LABELS.get(source_id, source_id.replace("_", " ").title())


def list_job_source_options() -> list[dict[str, str]]:
    """Sources shown in portal job-source filters (enabled adapters + JobSpy boards)."""
    seen: set[str] = set()
    options: list[dict[str, str]] = []

    def add(source_id: str) -> None:
        if source_id in seen:
            return
        seen.add(source_id)
        options.append({"id": source_id, "label": label_for_source(source_id)})

    if settings.mcf_enabled:
        add("mycareersfuture")
    if settings.jobicy_enabled:
        add("jobicy")
    if settings.adzuna_enabled and AdzunaAdapter.is_configured():
        add("adzuna")
    if settings.linkedin_enabled and LinkedInAdapter.is_configured():
        add("linkedin")
    if settings.jobspy_enabled and settings.jobspy_api_url.strip():
        for source_id in jobspy_board_source_ids():
            add(source_id)

    options.sort(key=lambda item: item["label"].lower())
    return options
