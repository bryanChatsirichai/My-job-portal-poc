# Documentation

Reference documentation for how the Smart Job Portal POC works today.

## Architecture

| Document | Description |
|----------|-------------|
| [Job ingestion](architecture/job-ingestion.md) | How jobs are gathered from external APIs, normalized, stored in SQLite, and served to the frontend |
| [Worker sync trace & config](architecture/worker-sync-and-config.md) | Step-by-step `python -m app.worker --sync` trace and how `backend/.env` flows through worker vs API |

## Development guides

| Document | Description |
|----------|-------------|
| [SQLite viewer (Mac & Windows)](development/sqlite-viewer.md) | Open and inspect `backend/jobportal.db` during dev and testing |
| [LinkedIn scraper setup](development/linkedin-scraper.md) | Run the self-hosted scraper and sync LinkedIn listings |
| [Local PostgreSQL (optional)](development/postgres-local.md) | Docker Postgres for future scale — not required for the POC |

## Job source adapters

Setup and API reference for each ingestion adapter:

| Source | API key | Doc |
|--------|---------|-----|
| MyCareersFuture | None | [adapters/mycareersfuture.md](adapters/mycareersfuture.md) |
| Jobicy | None | [adapters/jobicy.md](adapters/jobicy.md) |
| Adzuna | Free key | [adapters/adzuna.md](adapters/adzuna.md) |
| LinkedIn | Self-hosted scraper | [adapters/linkedin.md](adapters/linkedin.md) |
| JobSpy | Self-hosted sidecar | [adapters/jobspy.md](adapters/jobspy.md) |

See [adapters/README.md](adapters/README.md) for a quick overview and sync command.

## Implementation plans

Roadmaps for in-progress and completed work live under [`plan/`](../plan/README.md).
