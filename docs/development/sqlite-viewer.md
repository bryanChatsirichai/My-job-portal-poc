# Viewing the SQLite database (Mac & Windows)

The POC stores ingested jobs in a **SQLite file**, not a Postgres server. For local dev and testing, you open that file directly in a GUI or query it from the terminal.

## Database location

| Item | Path |
|------|------|
| File | `backend/jobportal.db` |
| Default connection | `sqlite:///./jobportal.db` in `backend/.env` |
| Table | `jobs` |

The file is created when you run:

```bash
cd backend
uv run python -m app.worker --init-db
uv run python -m app.worker --sync --max-pages 2
```

If `jobportal.db` is missing or empty, run `--init-db` and `--sync` first.

## Recommended tool: DB Browser for SQLite

Free, cross-platform, and works the same on Mac and Windows.

- Download: [https://sqlitebrowser.org](https://sqlitebrowser.org)
- Choose the macOS or Windows installer from the homepage.

SQLite has **no host, port, username, or password**. You only open the file.

### macOS

1. Install and open **DB Browser for SQLite**.
2. Click **Open Database** (or **File → Open Database…**).
3. Navigate to your project clone and select:

   ```
   My-smart-job-portal-poc/backend/jobportal.db
   ```

   Full path example:

   ```
   /Users/you/Desktop/personal/My-smart-job-portal-poc/backend/jobportal.db
   ```

4. Open the **Browse Data** tab.
5. In the **Table** dropdown, choose **`jobs`**.

### Windows

1. Install and open **DB Browser for SQLite**.
2. Click **Open Database** (or **File → Open Database…**).
3. Navigate to your project clone and select:

   ```
   My-smart-job-portal-poc\backend\jobportal.db
   ```

   Full path example:

   ```
   C:\Users\you\Desktop\My-smart-job-portal-poc\backend\jobportal.db
   ```

4. Open the **Browse Data** tab.
5. In the **Table** dropdown, choose **`jobs`**.

### Run a quick check (both platforms)

1. Open the **Execute SQL** tab.
2. Run:

```sql
SELECT source, status, COUNT(*) AS count
FROM jobs
GROUP BY source, status
ORDER BY source;
```

3. Click the play / execute button.

You should see rows for sources such as `mycareersfuture` and `jobicy` after a sync.

### Useful queries for dev testing

```sql
-- Latest 10 jobs
SELECT title, company_name, source, posted_date
FROM jobs
ORDER BY posted_date DESC
LIMIT 10;

-- Jobs from one source
SELECT title, company_name, apply_url
FROM jobs
WHERE source = 'jobicy'
LIMIT 20;

-- Active vs expired
SELECT status, COUNT(*) FROM jobs GROUP BY status;
```

## Alternative: terminal (Mac & Windows)

`sqlite3` is built into macOS. On Windows, install [SQLite tools](https://www.sqlite.org/download.html) or use DB Browser’s SQL tab instead.

```bash
cd backend
sqlite3 jobportal.db
```

Inside the shell:

```sql
.tables
.schema jobs
SELECT source, COUNT(*) FROM jobs GROUP BY source;
.quit
```

On Windows PowerShell, use the same commands after `cd backend` and ensuring `sqlite3` is on your `PATH`.

## Other GUI options

| Tool | Notes |
|------|--------|
| [TablePlus](https://tableplus.com) | New connection → **SQLite** → select `jobportal.db` |
| [DBeaver](https://dbeaver.io) | New connection → **SQLite** → select `jobportal.db` |
| VS Code / Cursor extension | Install **SQLite Viewer** or **SQLite** and open `jobportal.db` in the editor |

## Tips while developing

- **Reading** the DB while FastAPI is running is fine.
- **Avoid editing** rows while `--sync` is running — SQLite may lock the file during writes.
- If sync fails with a database lock, close DB Browser (or any other tool holding the file open) and retry.
- The API does **not** call external job APIs on each search; it reads from this file. If the UI looks stale, re-run sync — you do not need to restart `uvicorn`.
- Application tracking (dashboard “applied” status) is stored in the browser’s **localStorage**, not in `jobportal.db`.

## Postgres vs SQLite

This POC uses **SQLite** by default. Tools like pgAdmin or `psql` connect to a **Postgres server**, not a `.db` file.

Postgres is optional for a future setup via [`backend/docker/postgres/docker-compose.yml`](../../backend/docker/postgres/docker-compose.yml). Until you change `DATABASE_URL` to Postgres and re-run `--init-db`, use a SQLite viewer and `backend/jobportal.db`.

See [Local PostgreSQL (optional)](./postgres-local.md) or the root [README](../../README.md#database) for switching to Postgres later.
