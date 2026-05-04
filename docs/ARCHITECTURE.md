# Architecture

Monalex is intentionally small: Flask renders the public pages, MySQL stores
the dictionary data, and the same search helper powers both the HTML page and
the JSON API.

## Runtime Components

| Component | Responsibility |
|-----------|----------------|
| `app.py` | Flask app, route definitions, MySQL/OpenAI configuration, search helper, AI helper, error handlers. |
| `templates/` | Server-rendered Jinja pages for dictionary search and conjugation views. |
| `static/` | CSS, small browser script, and historical/conjugation image assets. |
| `dictionary.sql` | MySQL dump used to bootstrap the dictionary table locally. |
| `tests/` | Standard-library `unittest` suite with mocked database connections. |

## Request Flow

1. A browser requests `/search?searchInput=...` or a client calls
   `/api/search?q=...`.
2. Flask trims the query and skips the database for empty searches.
3. `search_dictionary_entries()` opens a MySQL connection from environment
   configuration.
4. The query searches both `word` and `definition`, orders by `word`, and caps
   results with `SEARCH_LIMIT`.
5. Flask returns either rendered HTML or structured JSON from the same result
   set.

## AI Helper Flow

1. A user clicks `Assistant IA` on a rendered search result or a client posts to
   `/api/ai/explain`.
2. Flask validates the supplied `word` and `definition` payload and caps each
   field with `AI_INPUT_LIMIT`.
3. If `OPENAI_API_KEY` is missing, the endpoint returns HTTP `503` and the rest
   of the app continues to work normally.
4. If configured, the OpenAI Responses API generates a structured JSON study
   card with explanation, notes, examples, a memory tip, and a practice prompt.
5. The browser renders the returned fields without injecting raw HTML.

## Configuration

The app reads `.env` during local development. Production platforms can provide
the same values as environment variables.

| Variable | Default | Description |
|----------|---------|-------------|
| `JAWSDB_URL` | unset | Optional full MySQL URL, useful on Heroku/JawsDB-style deployments. |
| `MYSQL_HOST` | `localhost` | MySQL host when `JAWSDB_URL` is not set. |
| `MYSQL_PORT` | `3306` | MySQL port. |
| `MYSQL_USER` | `root` | MySQL user. |
| `MYSQL_PASSWORD` | empty | MySQL password. |
| `MYSQL_DATABASE` | `dictionary` | Database name. |
| `MYSQL_TABLE` | `dictionary` | Dictionary table name. Limited to letters, numbers, and underscores. |
| `SEARCH_LIMIT` | `50` | Maximum rendered/API search results. Must be between 1 and 200. |
| `APP_VERSION` | `0.2.0` | Version string returned by `/healthz`. |
| `OPENAI_API_KEY` | empty | Enables the optional AI study helper. |
| `OPENAI_MODEL` | `gpt-5.4-mini` | Model used for AI explanations. |
| `AI_INPUT_LIMIT` | `1200` | Per-field character limit for AI explanation input. |

## Reliability Notes

- Empty searches avoid unnecessary database connections.
- Database failures return user-facing error states instead of raw tracebacks.
- `/healthz` is independent from MySQL so platform health checks do not fail
  during transient database maintenance.
- The AI helper is isolated behind its own endpoint and does not affect normal
  search when OpenAI credentials are absent.
- Structured JSON output keeps the AI feature predictable for the UI.
- Basic security headers are added to every response.
- Tests use mocked database objects, making CI fast and deterministic.
