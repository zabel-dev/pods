#!/usr/bin/env bash
set -e

echo "Waiting for Postgres..."

until python - << 'EOF'
import psycopg

dsn = "postgresql://db:pass@localhost:5433/db"

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
<<<<<<< HEAD
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
=======
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
>>>>>>> 9263fc6 (fixed gub with yt-dlp errors for ru\end subtitles donsloading)
