# Deployment

The current production shape is:

- Backend: FastAPI on Render, configured by `render.yaml`.
- Frontend: Next.js on Vercel, rooted at `frontend/`.

## Render Backend

The included `render.yaml` defines the backend service:

| Setting | Value |
|---------|-------|
| Root Directory | `backend` |
| Runtime | Python |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --workers 2` |
| Health Check Path | `/healthz` |

Render should provide `GEMINI_API_KEY` as a secret environment variable when AI
features are enabled.

Recommended backend environment:

```env
PYTHON_VERSION=3.11.5
APP_VERSION=0.3.0
SITE_URL=https://monalexdictionary.onrender.com
CORS_ORIGINS=*
SEARCH_LIMIT=50
GEMINI_MODEL=gemini-2.5-flash-lite
AI_INPUT_LIMIT=1200
SQLITE_PATH=/tmp/monalex.sqlite3
GEMINI_API_KEY=...
```

`dictionary.sql` is the source of truth for the SQLite cache. The backend builds
or refreshes the cache on startup when the SQL file changes.

## Vercel Frontend

1. Import the GitHub repository in Vercel.
2. Set the root directory to `frontend/`.
3. Set `NEXT_PUBLIC_API_URL` to the Render backend URL.
4. Deploy with Node.js `20.9.0` or newer. Next.js 16 will not build on Node 18.

Recommended frontend environment:

```env
NEXT_PUBLIC_API_URL=https://monalexdictionary.onrender.com
```

## Local Development

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open `http://localhost:3000` for the app and `http://localhost:8000/docs` for
the FastAPI docs.

## Smoke Checks

Backend health:

```bash
curl http://127.0.0.1:8000/healthz
```

Frontend static checks:

```bash
cd frontend
npm run lint
npm exec -- tsc --noEmit
npm run build
```

`npm run build` requires Node.js `20.9.0` or newer because this project uses
Next.js 16.
