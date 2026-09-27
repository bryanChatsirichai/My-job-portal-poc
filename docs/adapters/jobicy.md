# Jobicy

Remote job listings via the **public Jobicy API**. No API key or account required.

| Item | Value |
|------|--------|
| Adapter | `backend/app/adapters/jobicy/adapter.py` |
| Source ID in DB | `jobicy` |
| API docs | [jobicy.com/jobs-rss-feed](https://jobicy.com/jobs-rss-feed) |

## Setup

No credentials needed. Jobicy is **always registered**.

Optional filters in `backend/.env` (see [`backend/.env.example`](../../backend/.env.example)):

```env
# JOBICY_GEO=singapore
# JOBICY_INDUSTRY=engineering
# JOBICY_TAG=python
```

```bash
cd backend
uv run python -m app.worker --sync
```

## API

```http
GET https://jobicy.com/api/v2/remote-jobs?count={count}&geo={geo}&tag={tag}&industry={industry}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `count` | No | Max jobs to return; adapter sets `100 × JOBICY_MAX_PAGES` (1→100, 2→200), default **200** when unset |
| `geo` | No | Location eligibility slug (from `JOBICY_GEO`) |
| `tag` | No | Keyword search (from `JOBICY_TAG`) |
| `industry` | No | Category slug (from `JOBICY_INDUSTRY`) |

### Response

JSON with a `jobs` array.

### Authentication

None.

## Configuration

| Setting | Location | Default |
|---------|----------|---------|
| Page size | `jobicy_page_size` / `JOBICY_PAGE_SIZE` | `200` |
| Max pages | `JOBICY_MAX_PAGES` | unset = 200 jobs (API max) |
| Geo filter | `jobicy_geo` / `JOBICY_GEO` | `""` |
| Industry filter | `jobicy_industry` / `JOBICY_INDUSTRY` | `""` |
| Tag filter | `jobicy_tag` / `JOBICY_TAG` | `""` |

## Pagination

Single API request on page 0. The `count` parameter is driven by `JOBICY_MAX_PAGES`:

| `JOBICY_MAX_PAGES` | API `count` |
|---------------|-------------|
| `1` | **100** |
| `2` | **200** |
| omitted | **200** (default) |

Page > 0 returns no jobs (Jobicy has no server-side pagination).

## Data mapping

| API field | Stored as |
|-----------|-----------|
| `id` | `source_job_id` |
| `jobTitle` | `title` |
| `companyName` | `company_name` |
| `jobGeo` | `location.address` / `location.region` |
| `salaryMin` / `salaryMax` | `salary_min` / `salary_max` |
| `salaryCurrency` | `salary_currency` |
| `salaryPeriod` | `salary_period` |
| `jobType[0]` | `employment_type` |
| `jobLevel` | `seniority_level` |
| `jobIndustry` | `skills` |
| `jobDescription` | `description` |
| `pubDate` | `posted_date` |
| `url` | `apply_url` |
| — | `source = jobicy` |

Apply URL fallback: `https://jobicy.com/jobs/{id}`

## Verify in the UI

1. `uv run uvicorn app.main:app --reload --port 8000` (from `backend/`)
2. `npm run dev` (from `frontend/`)
3. Open http://localhost:5173 → **Source** filter → **Jobicy**

## Notes

- Remote jobs only — not Singapore-government listings like MyCareersFuture.
- Single fetch per sync; `JOBICY_MAX_PAGES` controls how many jobs are requested (up to 200).

See also: [job-ingestion.md](../architecture/job-ingestion.md)
