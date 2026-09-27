# Local PostgreSQL (optional)

The POC uses **SQLite** by default (`sqlite:///./jobportal.db` in `backend/.env`). No Docker or separate database server is required for local development.

[`backend/docker/postgres/docker-compose.yml`](../../backend/docker/postgres/docker-compose.yml) is included for when you later move job storage to Postgres (e.g. production scale, full sync volume, or hosted deployment). You do **not** need to run it for the current POC.

## When ready

```bash
cd backend/docker/postgres
cp .env.example .env   # adjust credentials if needed
podman compose up -d   # or: docker compose up -d
podman compose ps      # should show healthy after ~10s
```

Then set in `backend/.env`:

```env
DATABASE_URL=postgresql+psycopg2://jobportal:jobportal@localhost:5432/jobportal
```

Re-run `uv run python -m app.worker --init-db` and sync after switching.

## Related

- [SQLite viewer setup](./sqlite-viewer.md) — browse the default POC database
- [Database setup plan](../../plan/database-setup/README.md) — full Postgres migration roadmap
- [Docker Compose step](../../plan/database-setup/jobdb/01-docker-compose.md) — detailed Phase 1.1 checklist
