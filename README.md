# pods

FastAPI backend + React (Vite) frontend for working with YouTube video subtitles and an AI chat layer (xAI Grok).

## Prerequisites

- **Python** 3.12+
- **Node.js** 20+ (or current LTS) and npm
- **Docker** (for PostgreSQL)

## Quick start

### 1. Clone and Python environment

```bash
cd pods
python -m venv .venv
```

**Windows (PowerShell)**

```powershell
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt
```

**macOS / Linux**

```bash
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

`uvloop` is skipped on Windows via a platform marker in `requirements.txt`.

### 2. Environment variables

Create a `.env` file in the project root (not committed to git). Required keys match `app/core/config.py`, for example:

- `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
- `DATABASE_URL` — for local Docker Postgres, e.g.  
  `postgresql+asyncpg://db:pass@localhost:5433/db`
- `XAI_API_KEY`, `XAI_MODEL`

### 3. Database

```bash
docker compose up -d postgres
```

Wait until the `db` container is healthy. Postgres is exposed on **host port 5433**.

> **Note:** In the default `docker-compose.yml`, Postgres data uses **tmpfs**. Data is lost when the container is recreated; run migrations again after a fresh DB.

### 4. Migrations

```bash
python -m alembic upgrade head
```

The URL used by Alembic is set in `alembic.ini` (`sqlalchemy.url`) and should match your Postgres credentials.

### 5. Run the API

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000/docs** for the interactive API.

### 6. Run the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` to `http://127.0.0.1:8000`, so keep the backend on port **8000** while developing.

## Branches

- `dev` — main development branch  
- `main` — as configured on the remote
