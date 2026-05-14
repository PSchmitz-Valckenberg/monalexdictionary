# Architecture

Monalex is a two-part application:

- `backend/` is the active FastAPI service deployed by `render.yaml`.
- `frontend/` is the active Next.js application intended for Vercel.

The older Flask app in the repository root is kept for compatibility and tests,
but it is not the service described by the current Render blueprint.

## Runtime Components

| Component | Responsibility |
|-----------|----------------|
| `backend/app/main.py` | FastAPI entry point, CORS middleware, lifespan startup. |
| `backend/app/config.py` | Pydantic settings loaded from environment variables. |
| `backend/app/database/sqlite.py` | Builds and opens the SQLite cache generated from `dictionary.sql`. |
| `backend/app/services/search.py` | Dictionary lookup helpers. |
| `backend/app/services/ai.py` | Gemini client, explanation generation, related-word validation, AI cache. |
| `backend/app/routes/` | Search, AI, and health API routes. |
| `frontend/app/` | Next.js App Router pages. |
| `frontend/components/` | Navigation, search result cards, PWA helpers, theme provider. |
| `frontend/lib/api.ts` | Typed API client shared by frontend pages and components. |
| `dictionary.sql` | Source dump for the public French-Monégasque dictionary. |
| `render.yaml` | Render backend blueprint. |

## Backend Startup

1. FastAPI starts through Gunicorn with Uvicorn workers.
2. The lifespan handler calls `ensure_db()`.
3. `ensure_db()` checks whether the SQLite cache matches the current
   `dictionary.sql` signature.
4. If the cache is missing or stale, it rebuilds the `dictionary` table and
   cache metadata.
5. If the dictionary cache is current but the AI cache table is missing, it adds
   that table without rebuilding the dictionary.
6. If `GEMINI_API_KEY` is set, the Gemini client is initialized during startup.

## Search Flow

1. The frontend calls `GET /api/search?q=...`.
2. FastAPI trims the query and returns an empty result for blank input.
3. `search_entries()` searches both `word` and `definition` in SQLite.
4. Results are ordered by `word` and capped by `SEARCH_LIMIT`.
5. The frontend renders results through `WordCard`.

## AI Flow

1. The user requests an explanation, related words, or the word of the day.
2. The API rejects AI routes with HTTP `503` when `GEMINI_API_KEY` is absent.
3. AI prompts are deliberately constrained for a low-resource language: Gemini
   explains in French and must not invent Monégasque sentences.
4. Explanation and word-of-day payloads are cached in SQLite by stable keys.
5. Related-word suggestions are treated as candidates only. Each candidate must
   match a real dictionary entry before it is returned.

## Frontend Flow

1. The homepage renders editorial content and a cached word-of-day section.
2. The search page supports both typed searches and shareable
   `/search?q=<term>` links.
3. Search responses are guarded so slower, older requests cannot overwrite a
   newer result set.
4. Search history is kept in `localStorage` and never sent to the backend.
5. The theme provider stores dark-mode preference in `localStorage`.

## Configuration

The backend reads environment variables through Pydantic settings.

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_VERSION` | `0.3.0` | Version returned by `/healthz`. |
| `SITE_URL` | empty | Canonical public URL for metadata and future absolute links. |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins for browser API calls. |
| `GEMINI_API_KEY` | empty | Enables AI endpoints when set. |
| `GEMINI_MODEL` | `gemini-2.5-flash-lite` | Gemini model used for AI calls. |
| `SEARCH_LIMIT` | `50` | Search result cap. Must be between 1 and 200. |
| `AI_INPUT_LIMIT` | `1200` | Per-field character limit sent to Gemini. |
| `DICTIONARY_SQL_PATH` | repo `dictionary.sql` | SQL dump used to build SQLite. |
| `SQLITE_PATH` | `/tmp/monalex.sqlite3` | Runtime SQLite cache path. |

The frontend reads:

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Base URL for the FastAPI backend. |

## Reliability Notes

- SQLite cache rebuilds are protected with a file lock so parallel workers do
  not rebuild the cache at the same time.
- The health endpoint reports AI configuration and dictionary cache readiness.
- AI cache creation is idempotent, which protects existing deployed SQLite
  files from older schema versions.
- Search history and theme state are client-only.
- Frontend lint and TypeScript checks are available in `frontend/package.json`.
