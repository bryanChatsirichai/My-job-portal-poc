#!/usr/bin/env bash
# Verify local Postgres from backend/docker/postgres compose stack.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
COMPOSE_DIR="$ROOT/backend/docker/postgres"
ENV_FILE="$COMPOSE_DIR/.env"

if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  set -a && source "$ENV_FILE" && set +a
fi

USER="${POSTGRES_USER:-jobportal}"
PASS="${POSTGRES_PASSWORD:-jobportal}"
DB="${POSTGRES_DB:-jobportal}"
PORT="${POSTGRES_HOST_PORT:-5432}"

RUNTIME=""
COMPOSE_CMD=()
if command -v podman >/dev/null 2>&1 && podman compose version >/dev/null 2>&1; then
  RUNTIME=podman
  COMPOSE_CMD=(podman compose)
elif command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  RUNTIME=docker
  COMPOSE_CMD=(docker compose)
else
  echo "FAIL: neither podman compose nor docker compose found"
  exit 1
fi

cd "$COMPOSE_DIR"

pass=0
fail=0

check() {
  local name="$1"
  shift
  if "$@"; then
    echo "PASS: $name"
    pass=$((pass + 1))
  else
    echo "FAIL: $name"
    fail=$((fail + 1))
  fi
}

check "compose ps shows healthy" bash -c \
  "${COMPOSE_CMD[*]} ps 2>/dev/null | grep -q healthy"

check "port $PORT reachable" nc -z localhost "$PORT"

CID="$("$RUNTIME" ps --filter "name=postgres" --format '{{.ID}}' 2>/dev/null | head -1 || true)"
if [[ -n "$CID" ]]; then
  psql_out="$("$RUNTIME" exec "$CID" psql -U "$USER" -d "$DB" -tAc "SELECT 1;" 2>/dev/null || true)"
  if [[ "$psql_out" == "1" ]]; then
    echo "PASS: psql SELECT 1"
    pass=$((pass + 1))
  else
    echo "FAIL: psql SELECT 1"
    fail=$((fail + 1))
  fi
else
  echo "FAIL: psql SELECT 1 (no container id)"
  fail=$((fail + 1))
fi

echo "---"
echo "Results: $pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
