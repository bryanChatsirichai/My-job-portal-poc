# Database Setup — Overview

**Goal:** Understand why Docker + Postgres fits this project, how the backend switches databases, and what each phase delivers.

**Status:** Planning  
**Blocks:** All implementation steps in [jobdb/](./jobdb/), [authentication/](./authentication/), [applied-jobs/](./applied-jobs/)

---

## Current state

| Layer | Today |
|-------|-------|
| Job storage | SQLite file `backend/jobportal.db` |
| Schema creation | `Base.metadata.create_all()` in worker `--init-db` |
| Migrations | None (Alembic listed in `pyproject.toml` but not configured) |
| API | FastAPI reads jobs from DB via `get_db()` → `settings.database_url` |
| Worker | Sync adapters upsert into same DB |
| Applied jobs | Browser `localStorage` (`jobPortal_trackedApplications`) |
| Auth | None |

Key files:

- `backend/app/config.py` — `database_url` default `sqlite:///./jobportal.db`
- `backend/app/db/session.py` — SQLAlchemy engine + `SessionLocal`
- `backend/app/db/search.py` — `USE_SQLITE` branch for JSON location filters
- `backend/docker/postgres/docker-compose.yml` — Postgres 16 Alpine (optional, not required for POC today)

---

## Is Docker appropriate?

**Yes**, for your stated goals:

1. **Deploy on a server** — Postgres in Docker runs the same on your PC and a VPS.
2. **Test locally as a server** — `docker compose up -d` + `uvicorn --host 0.0.0.0` simulates production.
3. **Future auth + per-user data** — Postgres handles concurrent access and foreign keys.

You do **not** need to containerize the FastAPI app or React frontend in Phase 1. Database-only Docker keeps complexity low.

### Database options compared

| Option | Good for | Limitation |
|--------|----------|------------|
| **SQLite** (current default) | Solo dev, zero infra | Single writer; poor fit for multi-user auth at scale |
| **Postgres in Docker** (recommended) | Local server test, VPS deploy | Requires Docker + migrations |
| **Managed Postgres** (future) | Railway, Supabase, RDS | Cost; same `DATABASE_URL` pattern |

### Recommended image

```yaml
image: postgres:16-alpine
```

Already in `backend/docker/postgres/docker-compose.yml`. Reasons:

- `psycopg2-binary` already in `backend/pyproject.toml`
- `search.py` already has Postgres-specific JSON path queries
- JSON columns for `location`, `skills`, `job_snapshot`
- Industry standard for production Python/FastAPI stacks

Do **not** introduce MySQL or a second engine — one Postgres target simplifies ops.

---

## How the backend chooses a database

There is **no separate `DATABASE_MODE` flag**. Both the API and worker read `DATABASE_URL` from `backend/.env` (or OS env).

```mermaid
flowchart LR
  subgraph env [Environment]
    DotEnv["backend/.env"]
    DATABASE_URL
  end
  subgraph backend [Backend processes]
    API["uvicorn app.main"]
    Worker["python -m app.worker"]
  end
  subgraph stores [Storage]
    SQLite["jobportal.db"]
    Postgres["Docker Postgres :5432"]
  end
  DotEnv --> DATABASE_URL
  DATABASE_URL --> API
  DATABASE_URL --> Worker
  DATABASE_URL -->|sqlite:///...| SQLite
  DATABASE_URL -->|postgresql+psycopg2://...| Postgres
```

| Profile | `DATABASE_URL` | When to use |
|---------|----------------|-------------|
| **Local POC** | `sqlite:///./jobportal.db` | Default; no Docker |
| **Docker DB** | `postgresql+psycopg2://jobportal:jobportal@localhost:5432/jobportal` | Local server test, deploy prep |

Switching `.env` switches **both** worker and API. They always share one database — there is no mixed mode (worker on SQLite, API on Postgres).

SQLite and Postgres hold **separate datasets**. Syncing into one does not populate the other.

---

## Data flow (unchanged for jobs)

```
External APIs (MCF, Jobicy, Adzuna, LinkedIn)
        ↓  fetch + normalize
  app.worker.sync (--sync)
        ↓  upsert_job / expire_stale_jobs
   jobs table (SQLite or Postgres)
        ↓  search_jobs / get_job_by_id
  FastAPI /api/v1/jobs
        ↓
     React frontend
```

Phase 2–3 add `users` and `applications` tables in the **same** database selected by `DATABASE_URL`.

---

## Phase roadmap

### Phase 1 — jobdb

- Harden `backend/docker/postgres/docker-compose.yml`
- Set up Alembic migrations for `jobs` table
- Verify worker + API on SQLite **and** Postgres
- Document env profiles (`.env.sqlite` / `.env.postgres` templates)

### Phase 2 — authentication

- `users` table + password hashing
- `POST /auth/register`, `POST /auth/login`, `GET /auth/me`
- Frontend login/register + protected `/dashboard`

### Phase 3 — applied-jobs

- `applications` table scoped to `user_id`
- CRUD API replacing `localStorage`
- Optional one-time import of existing browser data

```mermaid
flowchart TD
  jobdb["1. jobdb"]
  auth["2. authentication"]
  apps["3. applied-jobs"]
  jobdb --> auth
  auth --> apps
```

**Why auth before applied jobs:** Applications must belong to a user (`user_id` FK). `localStorage` is per-browser, not per-account.

---

## Local “server” test workflow (after Phase 1)

```bash
# Terminal A — database
docker compose up -d

# backend/.env
DATABASE_URL=postgresql+psycopg2://jobportal:jobportal@localhost:5432/jobportal

# Terminal B — schema + data
cd backend
uv run alembic upgrade head
uv run python -m app.worker --sync --max-pages 2

# Terminal C — API (LAN-accessible)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal D — frontend (optional LAN)
cd frontend && npm run dev -- --host
```

---

## Risks and mitigations

| Risk | Mitigation |
|------|------------|
| SQLite vs Postgres SQL differences | `search.py` already branches; add verification matrix in Phase 1.3 |
| Schema drift without migrations | Block Phases 2–3 until Alembic works |
| Weak default Postgres password | Phase 1.4 + security checklist in Phase 2.4 |
| Lost `localStorage` data | Phase 3.3 import on first login |
| Accidental `docker compose down -v` | Document in Phase 1.1 |

---

## What stays the same

- Job ingestion adapters and sync pipeline
- Public job search and detail pages (no login required)
- Vite `/api` proxy in dev
- Frontend analytics shape (`TrackedApplication`) — mapped from API in Phase 3
