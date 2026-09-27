# LinkedIn scraper setup (optional)

LinkedIn listings are **not** fetched when users search the portal. They are ingested during `--sync`, same as every other source. You must run the unofficial [LinkedIn Jobs API](https://github.com/bryanChatsirichai/Linkedin-Jobs-Api) scraper as a **separate Node service** before syncing.

## 1. Start the scraper

One-time clone; keep this terminal running during sync:

```bash
git clone https://github.com/bryanChatsirichai/Linkedin-Jobs-Api.git
cd Linkedin-Jobs-Api
npm install
npm run dev --workspace=backend   # listens on http://localhost:3000
```

Swagger docs: http://localhost:3000/api/v1/docs

## 2. Configure the portal backend (optional)

Defaults work for local dev:

| Variable | Default | Description |
|----------|---------|-------------|
| `LINKEDIN_JOBS_API_URL` | `http://localhost:3000/api/v1` | Scraper API base URL |
| `LINKEDIN_LOCATION` | `Singapore` | Location filter |
| `LINKEDIN_KEYWORDS` | `""` | Optional; comma-separated = one search per term |
| `LINKEDIN_USE_ANALYZE` | `true` | Use `/jobs/analyze` for salary and skills in `insights` |
| `LINKEDIN_DATE_SINCE_POSTED` | `past_week` | `past_24h`, `past_week`, or `past_month` |

Set `LINKEDIN_JOBS_API_URL=` in `backend/.env` to disable LinkedIn sync.

## 3. Sync

The scraper must be running:

```bash
cd backend
uv run python -m app.worker --sync --max-pages 2
```

Expected output includes a `linkedin` entry (e.g. `fetched: 140` with `--max-pages 2`). The adapter calls `GET /jobs/search?location=Singapore&page=1` then `page=2`.

## 4. Browse

Filter by **LinkedIn** in the UI, or set `?source=linkedin` in the URL. Apply links open LinkedIn in a new tab.

> **Note:** This uses an unofficial LinkedIn scraper (Puppeteer). It may break if LinkedIn changes their site, and job descriptions are not stored in the POC. Use responsibly.

See also: [LinkedIn adapter reference](../adapters/linkedin.md) · [Job ingestion architecture](../architecture/job-ingestion.md)
