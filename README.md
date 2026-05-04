# Monalex Dictionary

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-2.3-black)
![Database](https://img.shields.io/badge/MySQL-ready-orange)
![Tests](https://img.shields.io/badge/tests-unittest-green)

Monalex is a small but production-minded Flask dictionary for French to
Monégasque vocabulary. It combines a server-rendered learning interface,
conjugation pages, a MySQL-backed dictionary search, a JSON API, and a test
suite that runs without a local database.

## Highlights

- French -> Monégasque dictionary search backed by MySQL.
- Browser UI built with Flask/Jinja templates and responsive CSS.
- JSON search API at `/api/search` for future frontend, mobile, or data tools.
- Optional AI study helper that explains dictionary entries, suggests examples,
  creates memory tips, and produces practice prompts.
- Lightweight `/healthz` endpoint for deployment health checks.
- Environment-based configuration with `.env.example` and `JAWSDB_URL` support.
- Security headers added on every response.
- Deterministic `unittest` suite with mocked database connections.
- CI workflow ready for GitHub Actions.
- Makefile shortcuts for install, run, test, and cleanup.
- Repo hygiene for virtualenvs, caches, local credentials, and generated files.

## Project Structure

```text
.
├── app.py                    # Flask app, routes, config, API, search helper
├── dictionary.sql            # MySQL bootstrap data
├── templates/                # Jinja pages
├── static/                   # CSS, JS, and image assets
├── tests/                    # Unit and smoke tests
├── docs/
│   ├── API.md                # Endpoint reference
│   └── ARCHITECTURE.md       # Runtime and configuration notes
├── .github/workflows/ci.yml  # GitHub Actions test workflow
├── Makefile                  # Common developer commands
└── requirements.txt          # Runtime dependencies
```

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
make install
cp .env.example .env
```

Import the database dump into MySQL:

```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS dictionary CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p dictionary < dictionary.sql
```

Run the app:

```bash
make run
```

Open `http://127.0.0.1:5000`.

## Configuration

Local development reads values from `.env`; production can provide the same
values as environment variables.

| Variable | Default | Purpose |
|----------|---------|---------|
| `JAWSDB_URL` | unset | Optional full MySQL URL. Overrides individual MySQL settings. |
| `MYSQL_HOST` | `localhost` | MySQL host. |
| `MYSQL_PORT` | `3306` | MySQL port. |
| `MYSQL_USER` | `root` | MySQL username. |
| `MYSQL_PASSWORD` | empty | MySQL password. |
| `MYSQL_DATABASE` | `dictionary` | Database name. |
| `MYSQL_TABLE` | `dictionary` | Dictionary table name. |
| `SEARCH_LIMIT` | `50` | Maximum results returned by search. |
| `APP_VERSION` | `0.2.0` | Version returned by `/healthz`. |
| `OPENAI_API_KEY` | empty | Enables the optional AI study helper. |
| `OPENAI_MODEL` | `gpt-5.4-mini` | Model used by the AI helper. |
| `AI_INPUT_LIMIT` | `1200` | Per-field character limit before sending dictionary text to the AI model. |

## Commands

```bash
make install  # install runtime dependencies
make run      # start Flask on PORT=5000 by default
make test     # run the unittest suite
make check    # compile Python files and run tests
make clean    # remove local Python cache files
```

## HTTP Surface

| Route | Format | Description |
|-------|--------|-------------|
| `/` | HTML | Landing/history page. |
| `/search` | HTML | Browser-facing dictionary search. |
| `/api/search?q=...` | JSON | Programmatic dictionary search. |
| `/api/ai/explain` | JSON | Optional AI explanation for one dictionary entry. |
| `/conjugaison` | HTML | Verb group navigation. |
| `/conjugaison/premier` | HTML | Clean URL for first-group verb endings. |
| `/conjugaison/deuxieme` | HTML | Clean URL for second-group verb endings. |
| `/conjugaison/troisieme` | HTML | Clean URL for third-group verb endings. |
| `/healthz` | JSON | Service metadata and health response. |

See [docs/API.md](docs/API.md) for response examples.

## Tests

```bash
make check
```

The tests mock MySQL, so CI and local development do not require a running
database just to validate routes, errors, headers, and API responses.

## Architecture

The app keeps the runtime deliberately compact:

- `search_dictionary_entries()` is the single database-backed search path.
- `/search` and `/api/search` reuse that path and only differ in response
  format.
- `/api/ai/explain` turns one dictionary result into a learner-friendly study
  card when `OPENAI_API_KEY` is configured.
- `/healthz` does not query MySQL, so health checks stay fast and stable.
- Error handlers render friendly pages instead of exposing tracebacks.

Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

## Data Notes

`dictionary.sql` contains the bootstrap table used by the app. By default,
Monalex queries:

```sql
SELECT word, definition FROM dictionary
WHERE word LIKE ? OR definition LIKE ?
ORDER BY word
LIMIT 50;
```

Set `MYSQL_TABLE` only if you intentionally import the data under another table
name.
