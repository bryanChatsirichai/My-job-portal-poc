import argparse
import asyncio

from app.models.orm import Base
from app.db.session import engine
from app.worker.sync import sync_all


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")


async def run_sync() -> None:
    init_db()
    results = await sync_all()
    for result in results:
        print(result)


def main() -> None:
    parser = argparse.ArgumentParser(description="Job portal worker")
    parser.add_argument("--init-db", action="store_true", help="Create database tables")
    parser.add_argument("--sync", action="store_true", help="Run ingestion sync")
    args = parser.parse_args()

    if args.init_db:
        init_db()
    if args.sync:
        asyncio.run(run_sync())
    if not args.init_db and not args.sync:
        parser.print_help()


if __name__ == "__main__":
    main()
