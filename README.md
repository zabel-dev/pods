# pods

FastAPI backend + React (Vite) frontend for working with YouTube video subtitles and an AI chat layer (xAI Grok).

## Prerequisites

- **Python** 3.12+
- **Node.js** 20+ (or current LTS) and npm
- **Docker** (for PostgreSQL and optional nginx deployment)

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

## Run with Docker + Nginx (frontend in Docker, backend local)

This starts:

- `postgres` (DB)
- `nginx` (serves the built frontend + proxies `/api/*` → your locally running FastAPI; exposed as `:80`)

```bash
docker compose up -d postgres nginx
```

Start the backend locally (outside Docker):

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

- Frontend: **http://localhost/**
- API docs: **http://localhost/api/docs** (proxied to local backend)

## One Docker image: frontend + API + nginx

Use this when you want a **single** container (good for **Render** or a simple local full stack).

- `Dockerfile.combined` builds the Vite app, installs Python deps, runs **nginx** (public port) and **uvicorn** on `127.0.0.1:8000` behind `/api`.
- `RUN_UNIFIED=1` is set in that image; **entrypoint** waits for Postgres, runs **Alembic**, then starts both processes.

**Local (with Compose Postgres):** in `.env`, point the app at the `postgres` service (Docker network), not `localhost:5433`, for example:

`DATABASE_URL=postgresql+asyncpg://db:pass@postgres:5432/db`

Then:

```bash
docker compose up -d postgres web
```

- App + UI: **http://localhost:3080/**  
- API docs: **http://localhost:3080/api/docs**

The `web` service overrides `PORT` to `80` inside the container (host maps **3080 → 80**) so it does not clash with a `PORT=8000` you might keep in `.env` for local uvicorn.

**Render:** create a **Web Service** with **Docker**, set **Dockerfile Path** to `Dockerfile.combined`. Do **not** set `PORT` yourself (Render injects it); nginx listens on that port. Set the same env vars as for the API-only image (`DATABASE_URL`, secrets, etc.).

## Monitoring (Prometheus + Grafana + Loki)

Start the stack:

```bash
docker compose up -d prometheus grafana loki promtail
```

Open:

- Prometheus: **http://localhost:9090**
- Grafana: **http://localhost:3000** (login `admin` / `admin`)
- Loki: **http://localhost:3100**

Notes:

- Prometheus scrapes your **local** backend at `http://127.0.0.1:8000/metrics` (exposed as `/metrics`).
- Grafana is pre-provisioned with **Prometheus** and **Loki** datasources.
- Loki receives nginx logs via a shared `nginx-logs` volume (nginx access/error logs are enabled in `nginx/nginx.conf`).

## Branches

- `dev` — main development branch  
- `main` — as configured on the remote
