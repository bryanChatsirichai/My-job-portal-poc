# MyCareersFuture

Singapore government job board listings via the **public REST API**. No API key or account is required.

| Item | Value |
|------|--------|
| Adapter | `backend/app/adapters/mycareersfuture/adapter.py` |
| Source ID in DB | `mycareersfuture` |
| Official site | [mycareersfuture.gov.sg](https://www.mycareersfuture.gov.sg) |

## Setup

No configuration needed. MyCareersFuture is **always registered** and syncs on every `--sync` run.

```bash
cd backend
uv run python -m app.worker --init-db   # first time only
uv run python -m app.worker --sync
```

## API

```http
GET https://api.mycareersfuture.gov.sg/v2/jobs?page={page}&limit={limit}
```

| Parameter | Description |
|-----------|-------------|
| `page` | **0-based** page index (`0` = first page) |
| `limit` | Jobs per page (default in this project: **100**) |

### Example requests

```http
GET https://api.mycareersfuture.gov.sg/v2/jobs?page=0&limit=100
GET https://api.mycareersfuture.gov.sg/v2/jobs?page=1&limit=100
```

### Response

JSON with a `results` array. The adapter reads `results` only.

### Authentication

None.

## Configuration

| Setting | Location | Default |
|---------|----------|---------|
| Page size | `mcf_page_size` in `backend/app/config.py` | `100` |
| Env override | `MCF_PAGE_SIZE` in `backend/.env` | — |
| Max pages | `MCF_MAX_PAGES` in `backend/.env` | unset = unlimited |

## Pagination

Stops when:

1. `MCF_MAX_PAGES` reached (if set in `.env`)
2. API returns empty `results`
3. Fewer jobs than `limit` on a page

| Mode | Pages | Approx. jobs |
|------|-------|--------------|
| `MCF_MAX_PAGES=2` | 2 | up to **~200** (2 × 100) |
| `MCF_MAX_PAGES` unset | all | until API exhausted (tens of thousands possible) |

**Expiry warning:** with `MCF_MAX_PAGES=2`, jobs not in those pages may be marked expired in SQLite even though they still exist on MCF. Leave `MCF_MAX_PAGES` unset for an accurate catalog.

## Data mapping

| API field | Stored as |
|-----------|-----------|
| `uuid` | `source_job_id` |
| `title` | `title` |
| `postedCompany.name` or `hiringCompany.name` | `company_name` |
| `postedCompany.uen` | `company_uen` |
| `address` (block, street, building, postal) | `location.address` |
| `address.districts[0].location` | `location.district` |
| `address.districts[0].region` | `location.region` |
| `salary.minimum` / `salary.maximum` | `salary_min` / `salary_max` |
| `salary.type.salaryType` | `salary_period` |
| `employmentTypes[0].employmentType` | `employment_type` |
| `positionLevels[0].position` | `seniority_level` |
| `skills[].skill` | `skills` |
| `description` | `description` |
| `metadata.newPostingDate` or `originalPostingDate` | `posted_date` |
| `metadata.expiryDate` | `expiry_date` |
| `metadata.jobDetailsUrl` | `apply_url` |
| — | `source = mycareersfuture`, `salary_currency = SGD` |

Apply URL fallback: `https://www.mycareersfuture.gov.sg/job/{uuid}`

## Verify in the UI

1. `uv run uvicorn app.main:app --reload --port 8000` (from `backend/`)
2. `npm run dev` (from `frontend/`)
3. Open http://localhost:5173 → **Source** filter → **MyCareersFuture**

## Notes

- Works out of the box — no `.env` keys.
- Full job descriptions are stored.
- Public API — no retries/backoff in this POC.

See also: [adzuna.md](./adzuna.md) · [job-ingestion.md](../architecture/job-ingestion.md)
