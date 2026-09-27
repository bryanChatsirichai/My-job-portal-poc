# Step 1.2 — Alembic Migrations

**Goal:** Replace ad-hoc `create_all()` with versioned Alembic migrations so schema changes deploy reliably to SQLite and Postgres.

**Status:** ⬜ Not started  
**Depends on:** [01-docker-compose.md](./01-docker-compose.md) (Postgres available for testing)  
**Blocks:** [03-dual-backend-verify.md](./03-dual-backend-verify.md), Phase 2 (`users` table)

**Estimated effort:** 1–2 sessions

---

## Context

Today schema is created in `backend/app/worker/__main__.py`:

```python
def init_db() -> None:
    Base.metadata.create_all(bind=engine)
```

`alembic>=1.14.0` is in `pyproject.toml` but no `alembic/` directory exists. Auth and applications tables **require** migrations before production use.

Existing ORM model: `backend/app/models/orm.py` — `Job` table with indexes on `(source, source_job_id)`, `status`, etc.

---

## Tasks

### 1.2.1 Initialize Alembic

From `backend/`:

```bash
uv run alembic init alembic
```

Produces:

```
backend/
├── alembic.ini
└── alembic/
    ├── env.py
    ├── script.py.mako
    └── versions/
```

### 1.2.2 Wire `env.py` to app settings

**File:** `backend/alembic/env.py`

- Import `settings` from `app.config`
- Set `config.set_main_option("sqlalchemy.url", settings.database_url)`
- Import `Base` from `app.models.orm` (or a shared `app.models` module)
- Set `target_metadata = Base.metadata`

Ensure `sys.path` includes the backend root so `app` imports work when running from `backend/`.

### 1.2.3 Configure `alembic.ini`

- Set `script_location = alembic`
- Remove or comment hardcoded `sqlalchemy.url` in `alembic.ini` (env.py overrides from settings)

### 1.2.4 Generate initial revision

With `DATABASE_URL` pointing at a **fresh** database (or empty schema):

```bash
uv run alembic revision --autogenerate -m "create jobs table"
uv run alembic upgrade head
```

Review the generated migration:

- `jobs` table columns match `Job` model
- Unique index `uq_jobs_source_source_job_id`
- Indexes on `status`, `posted_date`, etc.

Fix any autogenerate quirks (SQLite vs Postgres JSON types).

### 1.2.5 Update worker `--init-db`

**File:** `backend/app/worker/__main__.py`

Change `init_db()` to run migrations:

```python
from alembic.config import Config
from alembic import command

def init_db() -> None:
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    print("Database migrations applied.")
```

**Decision:** Remove `create_all()` for deploy paths, or keep as dev-only fallback behind an env flag. Recommended: **migrations only** to avoid drift.

### 1.2.6 Document migration workflow

Add to `README.md` or `docs/development/database-migrations.md`:

| Task | Command |
|------|---------|
| Apply all migrations | `uv run alembic upgrade head` |
| New migration after model change | `uv run alembic revision --autogenerate -m "description"` |
| Roll back one revision | `uv run alembic downgrade -1` |
| Show current revision | `uv run alembic current` |

### 1.2.7 Handle existing SQLite databases

For developers who already have `jobportal.db` from `create_all`:

**Option A (simple):** Delete `jobportal.db` and run `alembic upgrade head` + re-sync.

**Option B (preserve data):** Stamp existing DB:

```bash
uv run alembic stamp head
```

Only if the live schema matches the migration exactly.

---

## Postgres-specific notes

- JSON columns: SQLAlchemy `JSON` maps to `JSON`/`JSONB` on Postgres and `JSON` on SQLite
- `UUID` primary keys: ensure migration uses compatible type for both backends (SQLAlchemy handles this)
- Test autogenerate on **both** engines before committing the initial revision

---

## Verification checklist

- [ ] `uv run alembic upgrade head` succeeds on **SQLite** (`DATABASE_URL=sqlite:///./jobportal.db`)
- [ ] `uv run alembic upgrade head` succeeds on **Postgres** (Docker running)
- [ ] `uv run python -m app.worker --init-db` applies migrations (no `create_all`)
- [ ] `\dt` / DB browser shows `jobs` table and `alembic_version`
- [ ] `uv run alembic downgrade base` then `upgrade head` round-trips cleanly (on empty DB)

---

## Files touched (implementation)

| File | Change |
|------|--------|
| `backend/alembic.ini` | New |
| `backend/alembic/env.py` | Wire settings + metadata |
| `backend/alembic/versions/001_*.py` | Initial `jobs` migration |
| `backend/app/worker/__main__.py` | `--init-db` → Alembic |
| `README.md` | Migration commands |
