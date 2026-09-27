# Smart Job Portal POC

All-in-one Singapore job aggregator with:
- Python FastAPI backend
- React + TypeScript frontend (`module.scss`)
- SQLite job storage (no Docker required for local POC)
- MyCareersFuture ingestion adapter (no API key)
- Jobicy ingestion adapter (remote jobs, no API key — [Jobicy API](https://jobicy.com/jobs-rss-feed))
- Adzuna ingestion adapter (free API key — see [docs/adapters/adzuna.md](docs/adapters/adzuna.md))
- LinkedIn ingestion adapter (self-hosted [LinkedIn Jobs API](https://github.com/atharv01h/Linkedin-Jobs-Api) scraper — sync only, not runtime)
- JobSpy ingestion adapter (self-hosted [JobSpy](https://github.com/speedyapply/JobSpy) sidecar — [docs/adapters/jobspy.md](docs/adapters/jobspy.md))
- Browser `localStorage` application tracking (POC)

## Quick start

### First-time setup

**1. Backend** — requires [uv](https://docs.astral.sh/uv/) (`pip install uv` or see uv install docs).

```bash
cd backend
uv sync                       # install Python deps into .venv
uv run python -m app.worker --init-db
uv run python -m app.worker --sync
```

Create `backend/.env` from [`backend/.env.example`](backend/.env.example). For a fast POC sync, uncomment `*_MAX_PAGES=2` in `.env` (see [Refreshing job data](#refreshing-job-data)).

| Command | Purpose |
|---------|---------|
| `uv sync` | Creates `.venv` and installs dependencies from `pyproject.toml` |
| `--init-db` | Creates SQLite tables in `jobportal.db` (run once, or after a DB/schema change) |
| `--sync` | Fetches from each source into SQLite (page limits from `*_MAX_PAGES` in `.env`) |

**Job sources:** see [docs/adapters/](docs/adapters/) — MyCareersFuture and Jobicy need no API keys; Adzuna needs `ADZUNA_APP_ID` and `ADZUNA_APP_KEY`; LinkedIn needs a self-hosted scraper on `localhost:3000`; JobSpy needs a self-hosted sidecar on `localhost:8001` (both enabled by default). Quick links: [MCF](docs/adapters/mycareersfuture.md) · [Jobicy](docs/adapters/jobicy.md) · [Adzuna](docs/adapters/adzuna.md) · [LinkedIn](docs/adapters/linkedin.md) · [JobSpy](docs/adapters/jobspy.md).

**2. Frontend**

```bash
cd frontend
npm install
```

### Local dev (every day)

Run **two terminals** — one for the API, one for the UI:

```bash
# Terminal 1 — backend API (serves jobs from SQLite)
cd backend
uv run uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend dev server
cd frontend
npm run dev
```

Open **http://localhost:5173**.

You do **not** need to re-run `--init-db` or `--sync` on every start. The API reads whatever is already in `jobportal.db`.

**How the frontend talks to the API:** Vite proxies `/api` to `http://localhost:8000` (see `frontend/vite.config.ts`), so the browser calls the same origin and CORS is not an issue. API docs: http://localhost:8000/docs

### How job data flows

The running API **does not** call external job sources on each search. It only reads from **SQLite**:

```
External APIs  →  sync worker (--sync)  →  jobportal.db  →  FastAPI  →  React
                 (manual or scheduled)      (cache)
```

When you search or open a job card, FastAPI queries the local database. External APIs are contacted only when you run the sync worker.

See [job ingestion architecture](docs/architecture/job-ingestion.md) for the full pipeline, sync behaviour, and `*_MAX_PAGES` expiry rules.

### Refreshing job data

Re-run sync when you want fresher listings. No need to restart `uvicorn` — reload the browser after sync completes.

```bash
cd backend
uv run python -m app.worker --sync
```

| Setting | Meaning |
|---------|---------|
| `--sync` | Fetch from each registered source and upsert into SQLite |
| `MCF_MAX_PAGES`, `ADZUNA_MAX_PAGES`, … in `.env` | Cap pages **per source** (omit = unlimited full sync) |

For fast local testing, set e.g. `MCF_MAX_PAGES=2` in `backend/.env`. Remove or comment out `*_MAX_PAGES` for a full refresh (can be thousands of jobs). Per-source page sizes and expiry behaviour are documented in [job ingestion architecture](docs/architecture/job-ingestion.md).

**JobSpy:** start the sidecar on port 8001 before syncing — see [JobSpy (optional)](#jobspy-optional).

**Jobicy:** optional filters in `backend/.env`: `JOBICY_GEO`, `JOBICY_INDUSTRY`, `JOBICY_TAG` — see [Jobicy API docs](https://jobicy.com/jobs-rss-feed).

### LinkedIn (optional)

LinkedIn requires a separate scraper service before sync. See [LinkedIn scraper setup](docs/development/linkedin-scraper.md).

### JobSpy (optional)

JobSpy aggregates listings from configured boards (Indeed, LinkedIn, Glassdoor, Google, Bayt, etc. — set in the JobSpy repo `.env`). It runs as a **separate FastAPI sidecar** in your local JobSpy clone — the portal worker calls it over HTTP during sync only. Full reference: [docs/adapters/jobspy.md](docs/adapters/jobspy.md).

**One-time sidecar setup** (in your JobSpy repo, e.g. `D:\Projects\JobSpy`):

```bash
cd D:\Projects\JobSpy
uv pip install -e .
```

**Sync with JobSpy** — run the sidecar first, then sync in a second terminal:

```bash
# Terminal 1 — JobSpy sidecar
cd D:\Projects\JobSpy
uv run uvicorn jobspy_api.main:app --port 8001

# Terminal 2 — sync
cd backend
uv run python -m app.worker --sync
```

| Setting | Default | Purpose |
|---------|---------|---------|
| `JOBSPY_ENABLED` | `true` | Set `false` to skip JobSpy during sync |
| `JOBSPY_API_URL` | `http://localhost:8001/v1` | Sidecar base URL |
| `JOBSPY_PAGE_SIZE` | `1` | Term-based pagination (one worker page = one search term) |
| `JOBSPY_MAX_PAGES` | unset | Max search terms per sync (omit = all terms; can take 1–2+ hours) |

For JobSpy, `JOBSPY_MAX_PAGES` means **N search terms** (not N API pages like other sources). Sidecar health check: `http://localhost:8001/health`.

Configure scrape behaviour in the JobSpy repo — copy `D:\Projects\JobSpy\.env.example` to `.env` and edit `JOBSPY_SITE_NAMES`, `JOBSPY_SEARCH_TERMS`, `JOBSPY_RESULTS_WANTED`, `JOBSPY_HOURS_OLD`, etc. (loaded by `jobspy_api/config.py` and `scrape_sg.py`). When using both JobSpy and the LinkedIn adapter, set `JOBSPY_SITE_NAMES=indeed,glassdoor,google,bayt` to avoid duplicate LinkedIn listings.

### Database

**Current POC — SQLite (default):** `sqlite:///./jobportal.db` in `backend/.env`. No Docker required.

- Browse job rows: [SQLite viewer setup](docs/development/sqlite-viewer.md)
- Optional Postgres: [Local PostgreSQL](docs/development/postgres-local.md)

## Documentation

| Area | Entry |
|------|-------|
| All reference docs | [`docs/README.md`](docs/README.md) |
| Job ingestion pipeline | [docs/architecture/job-ingestion.md](docs/architecture/job-ingestion.md) |
| Dev guides (SQLite, LinkedIn, Postgres) | [docs/development/](docs/development/) |
| Job source adapters | [docs/adapters/](docs/adapters/) |
| Implementation plans | [`plan/README.md`](plan/README.md) |

## Environment

- **Backend:** create `backend/.env` from [`backend/.env.example`](backend/.env.example). Toggle sources with `*_ENABLED`; tune batch size with `*_PAGE_SIZE` and sync depth with `*_MAX_PAGES` (unset = full sync per source).
- **Jobicy (optional):** no API key. Uncomment filters in `backend/.env.example` to narrow remote listings, e.g. `JOBICY_GEO=singapore`, `JOBICY_INDUSTRY=engineering`, `JOBICY_TAG=python`.
- **Job sources:** [docs/adapters/](docs/adapters/) — setup and API reference per adapter.
- **Frontend:** optional `frontend/.env` — leave `VITE_API_BASE_URL` empty so requests use the Vite `/api` proxy in dev.

## Notes

- Application tracking is stored in browser `localStorage` for this POC.
- Future production should move tracking to Postgres with portal auth — see [database setup plan](plan/database-setup/README.md).
- `backend/docker/postgres/docker-compose.yml` is kept for **future database use** (Postgres); SQLite remains the default until you choose to switch.
