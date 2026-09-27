# LinkedIn

LinkedIn jobs via a **self-hosted** [LinkedIn Jobs API](https://github.com/bryanChatsirichai/Linkedin-Jobs-Api) scraper (v2.1+). Optional — the portal calls the scraper during sync only, never at browse time.

| Item | Value |
|------|--------|
| Adapter | `backend/app/adapters/linkedin/adapter.py` |
| HTTP client | `backend/app/adapters/linkedin/client.py` |
| Source ID in DB | `linkedin` |
| Scraper repo | [bryanChatsirichai/Linkedin-Jobs-Api](https://github.com/bryanChatsirichai/Linkedin-Jobs-Api) |

## Setup

### 1. Run the scraper service

Requires [Node.js 18+](https://nodejs.org/). Keep running while syncing LinkedIn jobs:

```bash
git clone https://github.com/bryanChatsirichai/Linkedin-Jobs-Api.git
cd Linkedin-Jobs-Api
npm install
npm run dev --workspace=backend
```

API: **http://localhost:3000** · Docs: http://localhost:3000/api/v1/docs

### 2. Configure the portal backend

Optional overrides in `backend/.env`:

```env
# LINKEDIN_JOBS_API_URL=http://localhost:3000/api/v1
# LINKEDIN_KEYWORDS=software engineer,data engineer
# LINKEDIN_LOCATION=Singapore
# LINKEDIN_USE_ANALYZE=true
# LINKEDIN_USER_SKILLS=Python,React
# LINKEDIN_DATE_SINCE_POSTED=past_week
```

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LINKEDIN_JOBS_API_URL` | No | `http://localhost:3000/api/v1` | Scraper base URL including `/api/v1` |
| `LINKEDIN_KEYWORDS` | No | `""` | Search keywords; comma-separated runs one sync pass per term |
| `LINKEDIN_KEYWORDS_REQUIRED` | No | `false` | When `true`, skip LinkedIn sync if keywords are empty |
| `LINKEDIN_USE_ANALYZE` | No | `true` | Use `/jobs/analyze` for `insights` (salary, skills, seniority) |
| `LINKEDIN_USER_SKILLS` | No | `""` | Comma-separated skills for analyze match scoring (upstream) |
| `LINKEDIN_LOCATION` | No | `Singapore` | Location filter |
| `LINKEDIN_DATE_SINCE_POSTED` | No | `past_week` | `past_24h`, `past_week`, or `past_month` |

Set `LINKEDIN_JOBS_API_URL=` (empty) to disable the adapter.

### 3. Sync

```bash
cd backend
uv run python -m app.worker --sync
```

The scraper must be reachable. Sync uses a **120 second** HTTP timeout per page.

## API

With `LINKEDIN_USE_ANALYZE=true` (default):

```http
GET http://localhost:3000/api/v1/jobs/analyze?location=Singapore&keywords=developer&page=1
```

With `LINKEDIN_USE_ANALYZE=false`:

```http
GET http://localhost:3000/api/v1/jobs/search?location=Singapore&page=1
```

| Parameter | Description |
|-----------|-------------|
| `page` | **1-based** page number per keyword (`LINKEDIN_MAX_PAGES=2` → pages 1 and 2 **per keyword**) |
| `location` | From `LINKEDIN_LOCATION` (default `Singapore`) |
| `keywords` | Optional per pass; from each term in `LINKEDIN_KEYWORDS` |
| `dateSincePosted` | Optional, from `LINKEDIN_DATE_SINCE_POSTED` |
| `userSkills` | Optional, from `LINKEDIN_USER_SKILLS` (analyze only) |

### Response

JSON with `jobs` array (and `success` flag). Analyze responses include `insights` on each job.

## Configuration

| Setting | Location | Default |
|---------|----------|---------|
| API URL | `linkedin_jobs_api_url` / `LINKEDIN_JOBS_API_URL` | `http://localhost:3000/api/v1` |
| Analyze mode | `linkedin_use_analyze` / `LINKEDIN_USE_ANALYZE` | `true` |
| Page size | `linkedin_page_size` / `LINKEDIN_PAGE_SIZE` | `70` |

## Pagination

| Mode | Pages | Approx. jobs |
|------|-------|--------------|
| `LINKEDIN_MAX_PAGES=2`, one keyword | 2 | up to **~140** (2 × 70) |
| `LINKEDIN_MAX_PAGES=2`, two keywords | 2 per keyword | up to **~280** |
| Full `--sync` | all | until scraper returns no more (per keyword) |

## Data mapping

| Scraper field | Stored as |
|---------------|-----------|
| `title` | `title` |
| `company` | `company_name` |
| `location` | `location.address` / `region` |
| `link` | `apply_url` |
| `listDate` | `posted_date` |
| `id` (from URL) | `source_job_id` |
| `insights.salaryRange` | `salary_min` / `salary_max` / `salary_currency` / `salary_period` |
| `insights.seniorityLevel` | `seniority_level` |
| `insights.jobType` | `employment_type` |
| `insights.requiredSkills` | `skills` |
| — | `source = linkedin` |

Job descriptions are **not** stored. **Salary and skills require analyze mode** (`LINKEDIN_USE_ANALYZE=true`); basic search often omits `insights`.

## Verify in the UI

1. `uv run uvicorn app.main:app --reload --port 8000` (from `backend/`)
2. `npm run dev` (from `frontend/`)
3. Open http://localhost:5173 → **Source** filter → **LinkedIn**

## Notes

- **Unofficial** — LinkedIn may block scraping; reliability not guaranteed.
- **Sync-time only** — UI reads from SQLite after sync.
- **Enabled by default** — points at `http://localhost:3000/api/v1`; set `LINKEDIN_JOBS_API_URL=` to disable.
- Use in line with LinkedIn's terms and applicable law.

See also: [job-ingestion.md](../architecture/job-ingestion.md)
