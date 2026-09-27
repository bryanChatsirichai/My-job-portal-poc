"""Job source adapter protocol.

Each external job API implements ``JobSourceAdapter`` with two responsibilities:

1. ``fetch_jobs`` — retrieve a page of raw records from the upstream API.
2. ``normalize`` — map one raw record into ``CanonicalJobInput`` for DB upsert.

The sync worker (`app.worker.sync`) paginates through adapters using
``FetchParams`` and persists normalized rows via ``upsert_job``.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.models.schemas import CanonicalJobInput


@dataclass
class FetchParams:
    """Pagination and batching controls passed to every adapter fetch call."""

    page: int = 0
    limit: int = 100
    max_pages: int | None = None  # from source *_MAX_PAGES in settings; passed to Jobicy for count


class JobSourceAdapter(ABC):
    """Abstract base for third-party job listing integrations."""

    source_name: str

    @abstractmethod
    async def fetch_jobs(self, params: FetchParams) -> list[dict]:
        """Return one page of raw job dicts from the upstream API.

        An empty list signals end-of-results or a skipped fetch (e.g. missing
        credentials). Page indices are **0-based**; adapters translate to
        provider-specific pagination as needed.
        """
        raise NotImplementedError

    @abstractmethod
    def normalize(self, raw: dict) -> CanonicalJobInput:
        """Map a single upstream record into the canonical job schema."""
        raise NotImplementedError
