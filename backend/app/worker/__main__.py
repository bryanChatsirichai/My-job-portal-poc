"""Worker CLI entry point.

Trace map for ``uv run python -m app.worker --sync`` (read steps in order):

  Step 0  — Import time: ``app.config`` loads ``settings`` from ``backend/.env``;
            ``app.db.session`` creates the SQLAlchemy ``engine`` (see those modules).
  Step 1  — ``main()`` runs when this file is executed as ``__main__``.
  Step 2  — ``argparse`` parses ``--sync``.
  Step 3  — ``asyncio.run(run_sync())`` starts the async sync coroutine.
  Step 4  — ``run_sync()`` calls ``init_db()``.
  Step 5  — ``init_db()`` creates DB tables if missing (``jobs``, etc.).
  Step 6  — ``run_sync()`` awaits ``sync_all()`` in ``app.worker.sync``.
  Step 7  — ``sync_all()`` → ``get_adapters()`` (enabled sources from settings).
  Step 8  — ``sync_all()`` loops each adapter → ``sync_source(adapter)``.
  Step 9  — ``sync_source()`` paginates: ``adapter.fetch_jobs()`` (HTTP/API).
  Step 10 — ``sync_source()`` → ``_upsert_batch()`` → ``upsert_job()`` per row.
  Step 11 — ``sync_source()`` → ``expire_stale_jobs()`` for IDs not seen this run.
  Step 12 — ``sync_all()`` collects per-source stats (or ``error``).
  Step 13 — ``run_sync()`` prints each result dict to stdout.
"""

import argparse
import asyncio

from app.models.orm import Base
from app.db.session import engine
from app.worker.sync import sync_all


def init_db() -> None:
    # Step 5 — ensure ORM tables exist before ingestion
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")


async def run_sync() -> None:
    # Step 4 — prepare database, then run full ingestion
    init_db()
    # Step 6 — orchestration lives in app.worker.sync
    results = await sync_all()
    # Step 13 — CLI summary (one line per source)
    for result in results:
        print(result)


def main() -> None:
    # Step 1 — worker CLI entry
    parser = argparse.ArgumentParser(description="Job portal worker")
    parser.add_argument("--init-db", action="store_true", help="Create database tables")
    parser.add_argument("--sync", action="store_true", help="Run ingestion sync")
    # Step 2 — flags from argv (e.g. ``--sync``)
    args = parser.parse_args()

    if args.init_db:
        init_db()
    if args.sync:
        # Step 3 — single event loop for the whole sync
        asyncio.run(run_sync())
    if not args.init_db and not args.sync:
        parser.print_help()


if __name__ == "__main__":
    main()
