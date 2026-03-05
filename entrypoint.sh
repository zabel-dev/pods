#!/usr/bin/env bash
set -e

echo "Waiting for Postgres..."

until python - << 'EOF'
import os
import psycopg

dsn = os.getenv("DATABASE_URL")
if not dsn:
    raise SystemExit("DATABASE_URL is not set")

# если используешь asyncpg в URL, превращаем в sync-URL для psycopg/Alembic
dsn = dsn.replace("postgresql+asyncpg", "postgresql")

try:
    with psycopg.connect(dsn, connect_timeout=3):
        pass
except Exception as e:
    raise SystemExit(1)
EOF
do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting app..."
PORT=${PORT:-8000}
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
