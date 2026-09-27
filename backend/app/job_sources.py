"""Job source ids and labels for API filters (aligned with frontend badges)."""

from __future__ import annotations

from pathlib import Path

from dotenv import dotenv_values

from app.adapters.adzuna.adapter import AdzunaAdapter
from app.adapters.jobspy.sites import parse_site_names_csv, source_from_site_name
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


def resolve_jobspy_site_names() -> list[str]:
    """Site list from portal ``JOBSPY_SITE_NAMES`` or ``JOBSPY_ENV_FILE`` (JobSpy repo ``.env``)."""
    if settings.jobspy_site_names.strip():
        return parse_site_names_csv(settings.jobspy_site_names)

    env_file = settings.jobspy_env_file.strip()
    if env_file:
        path = Path(env_file)
        if path.is_file():
            values = dotenv_values(path)
            raw = values.get("JOBSPY_SITE_NAMES") or ""
            if raw.strip():
                return parse_site_names_csv(raw)

    return parse_site_names_csv("indeed,linkedin")


def allowed_jobspy_sources() -> set[str]:
    return {source_from_site_name(site) for site in resolve_jobspy_site_names()}


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
        for site in resolve_jobspy_site_names():
            add(source_from_site_name(site))

    options.sort(key=lambda item: item["label"].lower())
    return options
