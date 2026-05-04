# Deployment

Monalex is ready to run as a Python web service with Gunicorn. The simplest
deployment target is Render, using the included `render.yaml` blueprint.

## Render

1. Push the repository to GitHub.
2. In Render, create a new Blueprint or Web Service from the repository.
3. Render can read `render.yaml`; otherwise use these settings manually:

| Setting | Value |
|---------|-------|
| Runtime | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |
| Health Check Path | `/healthz` |

## Required Environment Variables

For a demo deployment with the generated SQLite fallback:

```env
APP_VERSION=0.2.0
SEARCH_LIMIT=50
ENABLE_SQLITE_FALLBACK=1
SQLITE_FALLBACK_PATH=/tmp/monalex_dictionary.sqlite3
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5.4-mini
AI_INPUT_LIMIT=1200
```

`OPENAI_API_KEY` must be set as a secret environment variable in the hosting
dashboard. Do not commit it.

## Optional MySQL Production Mode

For a dedicated MySQL database, set:

```env
ENABLE_SQLITE_FALLBACK=0
MYSQL_HOST=...
MYSQL_PORT=3306
MYSQL_USER=...
MYSQL_PASSWORD=...
MYSQL_DATABASE=dictionary
MYSQL_TABLE=dictionary
```

Import `dictionary.sql` into that database before disabling the fallback.

## Local Production Smoke Test

```bash
pip install -r requirements.txt
gunicorn app:app
```

Open `http://127.0.0.1:8000`.

## Health Check

`GET /healthz` returns service metadata and whether the AI helper is configured.
Hosting platforms should use this path for health checks.
