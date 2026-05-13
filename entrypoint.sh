#!/bin/sh
set -e

echo "Waiting for Postgres..."

until python - << 'EOF'
import os
from urllib.parse import urlparse

import psycopg

raw = os.getenv("POSTGRES_DSN") or os.getenv("DATABASE_URL_SYNC") or os.getenv("DATABASE_URL")
if not raw:
    raw = "postgresql://db:pass@postgres:5432/db"
# async SQLAlchemy URL → psycopg DSN (local Docker / Render)
if raw.startswith("postgresql+asyncpg://"):
    raw = "postgresql://" + raw.removeprefix("postgresql+asyncpg://")
elif raw.startswith("postgresql+psycopg://"):
    raw = "postgresql://" + raw.removeprefix("postgresql+psycopg://")
elif raw.startswith("postgres://"):
    raw = "postgresql://" + raw.removeprefix("postgres://")

host = (urlparse(raw).hostname or "").lower()
if host.endswith(".render.com") and "sslmode" not in raw.lower():
    sep = "&" if "?" in raw else "?"
    raw = f"{raw}{sep}sslmode=require"

try:
    with psycopg.connect(raw, connect_timeout=3):
        pass
except Exception:
    raise SystemExit(1)
EOF
do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "Running Alembic migrations..."
alembic upgrade head

PORT="${PORT:-8000}"
echo "Starting app on 0.0.0.0:${PORT}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
