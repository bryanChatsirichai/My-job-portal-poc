"""JobSpy board names and portal ``source`` ids (shared by adapter and API)."""

from __future__ import annotations

# JobSpy ``site`` column → portal ``source`` (filter / badge category).
SITE_TO_SOURCE: dict[str, str] = {
    "indeed": "indeed",
    "linkedin": "linkedin",
    # "glassdoor": "glassdoor",
    # "google": "google",
    # "bayt": "bayt",
    "zip_recruiter": "ziprecruiter",
    "naukri": "naukri",
    "bdjobs": "bdjobs",
}


def normalize_site_key(site: object) -> str:
    if not site or not isinstance(site, str):
        return ""
    return site.strip().lower().replace(" ", "_")


def source_from_site(site: object) -> str:
    """Map JobSpy board name to portal source; unknown sites use the raw name."""
    key = normalize_site_key(site)
    if not key:
        return "jobspy"
    return SITE_TO_SOURCE.get(key, key)


def source_from_site_name(site_name: str) -> str:
    """Map a ``JOBSPY_SITE_NAMES`` entry to portal source."""
    return source_from_site(site_name)


def parse_site_names_csv(raw: str) -> list[str]:
    return [site.strip() for site in raw.split(",") if site.strip()]
