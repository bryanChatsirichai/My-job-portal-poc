"""Shared normalization helpers used across job source adapters."""

from datetime import datetime, timezone
from decimal import Decimal


def parse_datetime(value: str | None, *, default_now: bool = True) -> datetime:
    """Parse ISO-8601 datetime or date-only strings into timezone-aware datetimes.

    Handles full timestamps (``2024-01-15T08:30:00Z``) and date-only values
    (``2024-01-15``) returned by some government APIs. Falls back to UTC now
    when parsing fails and ``default_now`` is True.
    """
    if not value:
        if default_now:
            return datetime.now(timezone.utc)
        raise ValueError("empty datetime value")

    try:
        if "T" in value:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return datetime.fromisoformat(f"{value}T00:00:00+00:00")
    except ValueError:
        if default_now:
            return datetime.now(timezone.utc)
        raise


def to_decimal(value: object | None) -> Decimal | None:
    """Coerce API numeric values (int, float, str) to ``Decimal`` for storage."""
    if value is None:
        return None
    return Decimal(str(value))


def normalize_salary_period(value: str | None) -> str | None:
    """Map source-specific salary period labels to canonical values.

    Returns ``annual`` for yearly variants and ``None`` for missing/unknown
    values so downstream storage stays consistent across adapters.
    """
    if not value or value == "unknown":
        return None
    normalized = value.lower()
    if normalized == "yearly":
        return "annual"
    return normalized


def title_case_snake(value: str | None) -> str | None:
    """Convert snake_case API enums (e.g. ``full_time``) to display labels."""
    if not value:
        return None
    return value.replace("_", " ").title()


def split_csv_field(value: str | list | None) -> list[str]:
    """Split comma-separated scraper fields into a trimmed string list."""
    if not value:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [part.strip() for part in str(value).split(",") if part.strip()]
