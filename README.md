# Monalex

![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)
![Frontend](https://img.shields.io/badge/Frontend-Next.js_16-black)
![AI](https://img.shields.io/badge/AI-Gemini_2.5-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![CI](https://github.com/PSchmitz-Valckenberg/monalexdictionary/actions/workflows/ci.yml/badge.svg)

**The open-source French–Monégasque dictionary.** 14,200 entries, AI-powered study cards, daily word of the day, and conjugation tables — built to preserve and promote the Monégasque language spoken in Monaco.

---

## Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI + Python 3.11 |
| Frontend | Next.js 16, TypeScript, Tailwind CSS |
| Database | SQLite (built from `dictionary.sql` at startup) |
| AI | Google Gemini 2.5 Flash Lite via AI Studio |
| Backend Hosting | Render |
| Frontend Hosting | Vercel |

---

## Project Structure

```
monalex/
├── backend/                  # FastAPI API
│   ├── app/
│   │   ├── main.py           # App entry point, middleware, lifespan
│   │   ├── config.py         # Pydantic settings
│   │   ├── routes/           # search, ai, health endpoints
│   │   ├── services/         # search logic, Gemini client, AI cache
│   │   └── database/         # SQLite setup and connection
│   ├── requirements.txt
│   └── .env.example
├── frontend/                 # Next.js app
│   ├── app/                  # App Router pages
│   ├── components/           # Nav, WordCard
│   └── lib/api.ts            # Typed API client
├── dictionary.sql            # 14,200 French–Monégasque entries
├── data/                     # Future: parallel corpora for model training
├── docs/                     # API reference, architecture notes
└── render.yaml               # Render deployment blueprint
```

---

## Local Development

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your GEMINI_API_KEY to .env
uvicorn app.main:app --reload --port 8000
```

API runs at `http://localhost:8000`. Auto-generated docs at `http://localhost:8000/docs`.

The SQLite database is built automatically from `dictionary.sql` on first startup. No database setup needed.

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000 is the default
npm run dev
```

Frontend runs at `http://localhost:3000`.

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | — | Required for AI features. Get one free at [aistudio.google.com](https://aistudio.google.com). |
| `GEMINI_MODEL` | `gemini-2.5-flash-lite` | Gemini model to use. |
| `SEARCH_LIMIT` | `50` | Max results per search query (1–200). |
| `AI_INPUT_LIMIT` | `1200` | Max characters sent per field to the AI. |
| `SQLITE_PATH` | `/tmp/monalex.sqlite3` | SQLite database path. |
| `SITE_URL` | — | Canonical public URL for metadata. |
| `APP_VERSION` | `0.3.0` | Version string returned by `/healthz`. |

### Frontend (`frontend/.env.local`)

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API base URL. |

---

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/api/search?q=<term>` | Search the dictionary. Returns up to 50 results. |
| `POST` | `/api/ai/explain` | Generate an AI explanation for a dictionary entry. Body: `{ word, definition }` |
| `GET` | `/api/ai/word-of-day` | Get today's featured word with AI explanation (cached per day). |
| `GET` | `/healthz` | Service health check. |
| `GET` | `/docs` | Interactive API documentation (Swagger UI). |

See [docs/API.md](docs/API.md) for full request/response examples.

---

## Deployment

### Backend → Render

The `render.yaml` blueprint is included. Connect the repo to Render and it deploys automatically.

Set the following in Render's Environment dashboard:
- `GEMINI_API_KEY` (secret)

### Frontend → Vercel

1. Import the repo in [vercel.com](https://vercel.com)
2. Set **Root Directory** to `frontend/`
3. Add environment variable: `NEXT_PUBLIC_API_URL=https://monalexdictionary.onrender.com`
4. Deploy

---

## Contributing

Contributions are welcome — especially:
- Additional dictionary entries
- Monégasque text corpora (for future translation model training)
- Conjugation table improvements
- Bug fixes and UI improvements

Please open an issue before starting large changes. All PRs go through CI and Copilot review.

---

## License

MIT — see [LICENSE](LICENSE).
