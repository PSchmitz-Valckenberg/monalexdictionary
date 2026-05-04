# Architecture

Monalex is intentionally small: Flask renders the public pages, MySQL stores
the dictionary data, and the same search helper powers both the HTML page and
the JSON API.

## Runtime Components

| Component | Responsibility |
|-----------|----------------|
| `app.py` | Flask app, route definitions, MySQL configuration, search helper, error handlers. |
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

## Reliability Notes

- Empty searches avoid unnecessary database connections.
- Database failures return user-facing error states instead of raw tracebacks.
- `/healthz` is independent from MySQL so platform health checks do not fail
  during transient database maintenance.
- Basic security headers are added to every response.
- Tests use mocked database objects, making CI fast and deterministic.
