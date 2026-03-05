#!/usr/bin/env bash
set -e

echo "Waiting for Postgres..."

until python - << 'EOF'
import psycopg

dsn = "postgresql://db:pass@db:5432/db"

try:
    with psycopg.connect(dsn, connect_timeout=3):
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

echo "Starting app..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8888 --reload