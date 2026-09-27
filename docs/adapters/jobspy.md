# JobSpy

Job listings from a **self-hosted** [JobSpy](https://github.com/speedyapply/JobSpy) FastAPI sidecar (`jobspy_api` on the `custom-api-upgrade` branch). Optional — the portal calls the sidecar during sync only, never at browse time.

Each scraped row is stored under the **board** name (`indeed`, `linkedin`, …), not a single `jobspy` source id. The portal **Source** filter lists JobSpy board ids from `SITE_TO_SOURCE` in `sites.py` (not from portal env).

| Item | Value |
|------|--------|
| Adapter | `backend/app/adapters/jobspy/adapter.py` |
| HTTP client | `backend/app/adapters/jobspy/client.py` |
| Site → source map | `backend/app/adapters/jobspy/sites.py` |
| Worker registration | `source_name = jobspy` (one adapter); DB `source` per board |
| Sidecar repo | [speedyapply/JobSpy](https://github.com/speedyapply/JobSpy) — use branch with `jobspy_api` (see portal `backend/.env.example`) |

## Setup

### 1. Run the JobSpy sidecar

Install the JobSpy package in your local clone, then start the API on port **8001**:

```bash
cd /path/to/JobSpy
uv pip install -e .
uv run uvicorn jobspy_api.main:app --port 8001
```

Health: `http://localhost:8001/health` · Search: `GET http://localhost:8001/v1/jobs/search?page=0`

Configure scrape behaviour in the **JobSpy repo** `.env` (copy from `.env.example` there): `JOBSPY_SEARCH_TERMS`, `JOBSPY_SITE_NAMES`, `JOBSPY_RESULTS_WANTED`, `JOBSPY_HOURS_OLD`, etc.

### 2. Configure the portal backend

Defaults in `backend/.env.example`:

```env
JOBSPY_ENABLED=true
JOBSPY_API_URL=http://localhost:8001/v1
JOBSPY_PAGE_SIZE=1
# JOBSPY_MAX_PAGES=2
```

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JOBSPY_ENABLED` | No | `true` | Set `false` to skip JobSpy during `--sync` |
| `JOBSPY_API_URL` | No | `http://localhost:8001/v1` | Sidecar base URL including `/v1`. Empty = adapter not registered |
| `JOBSPY_PAGE_SIZE` | No | `1` | Worker batch size; keep `1` — one worker page = one search term |
| `JOBSPY_MAX_PAGES` | No | unset | **Last 0-based search-term index (inclusive)**. `2` → pages `0`, `1`, `2`. Unset = all terms (can take 1–2+ hours) |

**Boards scraped** come only from the JobSpy repo `.env` (`JOBSPY_SITE_NAMES` on the sidecar).

When using **both** JobSpy and the [LinkedIn adapter](./linkedin.md), omit `linkedin` from the JobSpy repo `JOBSPY_SITE_NAMES` (e.g. `indeed,glassdoor,google,bayt`) to avoid duplicate LinkedIn rows.

Set `JOBSPY_API_URL=` (empty) or `JOBSPY_ENABLED=false` to disable.

### 3. Sync

```bash
cd backend
uv run python -m app.worker --sync
```

The sidecar must be reachable. Sync uses a **300 second** HTTP timeout per request.

## API (sidecar)

```http
GET http://localhost:8001/v1/jobs/search?page=0
```

| Parameter | Description |
|-----------|-------------|
| `page` | **0-based index** into `JOBSPY_SEARCH_TERMS` in the JobSpy repo — one term per request, not a traditional results page |

### Response

JSON with at least:

| Field | Description |
|-------|-------------|
| `success` | When `false`, the adapter skips the page |
| `page` | Term index served |
| `search_term` | Term for this page (logging) |
| `has_more` | Whether more terms exist (informational; worker stops on empty `jobs`) |
| `jobs` | Array of JobSpy row objects |

## Pagination (portal worker)

Unlike other adapters, JobSpy pagination is **search-term based**:

- Worker loops `page = 0, 1, …` until the sidecar returns no jobs or `page > JOBSPY_MAX_PAGES`.
- A non-empty page does **not** stop the loop (job count can be any size for that term).

| `JOBSPY_MAX_PAGES` | Terms fetched (0-based pages) |
|--------------------|-------------------------------|
| `2` | 3 terms: pages `0`, `1`, `2` |
| unset | All terms configured in JobSpy |

## Board → `source` mapping

Defined in `backend/app/adapters/jobspy/sites.py`:

| JobSpy `site` | Stored `source` |
|---------------|-----------------|
| `indeed` | `indeed` |
| `linkedin` | `linkedin` |
| `zip_recruiter` | `ziprecruiter` |
| `naukri` | `naukri` |
| `bdjobs` | `bdjobs` |
| (other / missing) | normalized site name, or `jobspy` if empty |

Glassdoor, Google, and Bayt mappings exist in code but are commented out until enabled in `sites.py` and labels.

## Data mapping

| JobSpy field | Stored as |
|--------------|-----------|
| `site` | `source` (via mapping above) |
| `id` or hash of URL | `source_job_id` |
| `title` | `title` |
| `company` | `company_name` |
| `location` | `location.address` / `region` |
| `min_amount`, `max_amount`, `currency`, `interval` | salary fields |
| `job_type` | `employment_type` |
| `job_level` | `seniority_level` |
| `skills` | `skills` (comma-separated) |
| `description` | `description` |
| `date_posted` | `posted_date` |
| `job_url_direct` / `job_url` | `apply_url` |

## Verify in the UI

1. `uv run uvicorn app.main:app --reload --port 8000` (from `backend/`)
2. `npm run dev` (from `frontend/`)
3. Open http://localhost:5173 → **Source** filter → JobSpy boards (e.g. **Indeed**, **LinkedIn**) when the sidecar is enabled

`GET /api/v1/job-sources` returns enabled adapters plus JobSpy board ids.

## Notes

- **Sync-time only** — UI reads from SQLite after sync.
- **Enabled by default** — expects sidecar at `http://localhost:8001/v1`; disable with empty URL or `JOBSPY_ENABLED=false`.
- **Unofficial scraping** — board sites may block scrapers; reliability not guaranteed.
- Use in line with each board's terms and applicable law.

See also: [job-ingestion.md](../architecture/job-ingestion.md)
