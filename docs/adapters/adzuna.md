# Adzuna

Adzuna aggregates job listings from many sites in Singapore via their **official REST API**. Optional — requires a free developer account.

| Item | Value |
|------|--------|
| Adapter | `backend/app/adapters/adzuna/adapter.py` |
| Source ID in DB | `adzuna` |
| Developer portal | [developer.adzuna.com](https://developer.adzuna.com) |

## Setup

1. Register at [developer.adzuna.com](https://developer.adzuna.com) and create an application.
2. Add credentials to `backend/.env`:

```env
ADZUNA_APP_ID=your_app_id_here
ADZUNA_APP_KEY=your_app_key_here
```

3. Restart the API server or re-run sync.

The adapter is **only registered** when both variables are set. Without keys, Adzuna is skipped and other sources still sync.

```bash
cd backend
uv run python -m app.worker --sync
```

## API

```http
GET https://api.adzuna.com/v1/api/jobs/sg/search/{page}
```

| Part | Description |
|------|-------------|
| `sg` | Singapore country code |
| `{page}` | **1-based** page number (`1` = first page) |

### Query parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `app_id` | Yes | Application ID |
| `app_key` | Yes | Application key |
| `results_per_page` | No | Jobs per page (default: **50**) |

### Example request

```http
GET https://api.adzuna.com/v1/api/jobs/sg/search/1?app_id=YOUR_ID&app_key=YOUR_KEY&results_per_page=50
```

### Response

JSON with a `results` array.

## Configuration

| Setting | Location | Default |
|---------|----------|---------|
| App ID | `adzuna_app_id` / `ADZUNA_APP_ID` | `""` (disabled) |
| App key | `adzuna_app_key` / `ADZUNA_APP_KEY` | `""` (disabled) |
| Page size | `adzuna_page_size` / `ADZUNA_PAGE_SIZE` | `50` |
| Max pages | `ADZUNA_MAX_PAGES` | unset = unlimited |

Run commands from `backend/` so `.env` is loaded correctly.

## Pagination

The worker uses 0-based pages internally; the adapter converts to Adzuna's 1-based URL (`page + 1`).

| Mode | Pages | Approx. jobs |
|------|-------|--------------|
| `ADZUNA_MAX_PAGES=2` | 2 | up to **~100** (2 × 50) |
| `ADZUNA_MAX_PAGES` unset | all | until API exhausted |

**Expiry warning:** limited sync may mark unfetched Adzuna jobs as expired in SQLite.

## Data mapping

| API field | Stored as |
|-----------|-----------|
| `id` | `source_job_id` |
| `title` | `title` |
| `company.display_name` | `company_name` |
| `location.display_name` | `location.address` / `location.district` |
| `location.area[0]` | `location.region` |
| `latitude` / `longitude` | `location.lat` / `location.lng` |
| `salary_min` / `salary_max` | `salary_min` / `salary_max` |
| `contract_time` or `contract_type` | `employment_type` |
| `category.label` | `skills` |
| `description` | `description` |
| `created` | `posted_date` |
| `redirect_url` | `apply_url` |
| — | `source = adzuna`, `salary_currency = SGD`, `salary_period = annual` |

Apply URL fallback: `https://www.adzuna.sg/details/{id}`

## Verify in the UI

1. `uv run uvicorn app.main:app --reload --port 8000` (from `backend/`)
2. `npm run dev` (from `frontend/`)
3. Open http://localhost:5173 → **Source** filter → **Adzuna**

## Notes

- Salaries stored as **annual SGD** when provided.
- Rate limits apply per developer account — use `ADZUNA_MAX_PAGES` for testing.
- No search filters yet — paginated Singapore listings only.

See also: [mycareersfuture.md](./mycareersfuture.md) · [job-ingestion.md](../architecture/job-ingestion.md)
