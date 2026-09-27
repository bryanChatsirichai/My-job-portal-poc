# Step 1.1 — Docker Compose (PostgreSQL)

**Goal:** Run PostgreSQL 16 locally via Docker so the backend can use Postgres instead of SQLite, with a repeatable setup on your PC or a VPS.

**Status:** ✅ Done (2026-09-18)  
**Depends on:** —  
**Blocks:** [02-alembic-migrations.md](./02-alembic-migrations.md), [03-dual-backend-verify.md](./03-dual-backend-verify.md)

**Estimated effort:** 1 session

---

## Context

Implemented and verified locally with **Podman**:

- `[backend/docker/postgres/docker-compose.yml](../../../backend/docker/postgres/docker-compose.yml)` — Postgres 16, healthcheck, restart policy, named volume
- `[backend/docker/postgres/.env.example](../../../backend/docker/postgres/.env.example)` — compose credentials template
- `[backend/docker/postgres/.env](../../../backend/docker/postgres/.env)` — local compose env (gitignored)
- `[backend/docker/postgres/check-postgres.sh](../../../backend/docker/postgres/check-postgres.sh)` — connectivity checker
- `[backend/.env](../../../backend/.env)` — SQLite/Postgres `DATABASE_URL` switch via comment/uncomment (covers 1.1.5)

**Verified:** `podman compose up -d` → healthy container; port 5432 reachable; DBeaver connected with `jobportal`/`jobportal`.

---



## Tasks



### 1.1.1 Add healthcheck ✅

**File:** `backend/docker/postgres/docker-compose.yml`

Add a `healthcheck` so dependent services (future) and humans know when Postgres is ready:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U jobportal -d jobportal"]
  interval: 5s
  timeout: 5s
  retries: 5
  start_period: 10s
```



### 1.1.2 Add restart policy ✅

```yaml
restart: unless-stopped
```

Keeps the DB running after reboot on a server.

### 1.1.3 Externalize credentials (optional but recommended) ✅

Create `backend/docker/postgres/.env` (or `docker-compose.env`) for compose only:

```env
POSTGRES_USER=jobportal
POSTGRES_PASSWORD=jobportal
POSTGRES_DB=jobportal
```

Reference in `backend/docker/postgres/docker-compose.yml`:

```yaml
environment:
  POSTGRES_USER: ${POSTGRES_USER:-jobportal}
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-jobportal}
  POSTGRES_DB: ${POSTGRES_DB:-jobportal}
```

Add `backend/docker/postgres/.env` to `.gitignore` if it contains production secrets. Commit a `backend/docker/postgres/.env.example` for compose vars.

### 1.1.4 Keep named volume ✅

Retain `postgres_data` volume — data survives `docker compose down`. Only `docker compose down -v` wipes data.

### 1.1.5 Create backend env template for Postgres ✅ (alternate)

Implemented as comment/uncomment `DATABASE_URL` lines in `backend/.env` (both SQLite and Postgres URLs present; only one active at a time). Separate `.env.postgres.example` / `.env.sqlite.example` files deferred — not required for local switching.

### 1.1.6 Update README ✅ (partial)

`README.md` documents Postgres compose setup and `DATABASE_URL` switch. Full “Switching databases” subsection can expand in step 1.3.

---



## Commands reference

Run from `backend/docker/postgres/` (Docker or Podman — see Podman section below):


| Command                                                                         | Effect                                |
| ------------------------------------------------------------------------------- | ------------------------------------- |
| `docker compose up -d` / `podman compose up -d`                                 | Start Postgres in background          |
| `docker compose ps` / `podman compose ps`                                       | Check status (should show `healthy`)  |
| `docker compose logs postgres` / `podman compose logs postgres`                 | View logs                             |
| `docker compose down` / `podman compose down`                                   | Stop container; **keeps** data volume |
| `docker compose down -v` / `podman compose down -v`                             | Stop and **delete** all data          |
| `docker exec -it <container> psql ...` / `podman exec -it <container> psql ...` | Interactive SQL shell                 |




### Podman (instead of Docker)

On macOS, Podman runs containers inside a Linux VM. One-time setup:

```bash
brew install podman podman-compose   # or Podman Desktop
podman machine init
podman machine start
```

Then use the same compose file from `backend/docker/postgres/`:

```bash
cd backend/docker/postgres
podman compose up -d
podman compose ps
```

Podman reads the same `docker-compose.yml` format. Named volumes (`postgres_data`) work the same way. If `podman compose` is unavailable, use `podman-compose up -d` (hyphenated CLI from the `podman-compose` package).

Optional alias so muscle memory from Docker still works:

```bash
alias docker=podman
alias docker-compose='podman compose'
```

---



## Verification checklist

- [x] `podman compose up -d` succeeds (from `backend/docker/postgres/`)
- [x] `podman compose ps` shows `healthy` after ~10s
- [x] Port `5432` reachable; DBeaver connects with `jobportal`/`jobportal`
- [x] `backend/docker/postgres/.env` + `backend/.env` configured for SQLite ↔ Postgres switch
- [x] `check-postgres.sh` passes (container healthy, port open, psql `SELECT 1`)
- [x] Data persists across `compose down` + `up -d` (not re-tested this session)
- [x] Worker `--sync` into Postgres (requires uncommenting Postgres `DATABASE_URL` in `backend/.env`)

---



## Troubleshooting


| Problem                     | Fix                                                                                      |
| --------------------------- | ---------------------------------------------------------------------------------------- |
| Port 5432 already in use    | Stop local Postgres service or change host port to `5433:5432` and update `DATABASE_URL` |
| `connection refused`        | Wait for healthcheck; check `docker compose logs`                                        |
| Wrong password after change | `docker compose down -v` (wipes data) or update volume credentials manually              |


---



## Security note (local vs server)

Default `jobportal`/`jobportal` is fine for **local dev only**. Before exposing to the internet, follow [04-production-hardening.md](./04-production-hardening.md).