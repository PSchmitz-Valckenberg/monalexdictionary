# API Reference

Monalex exposes a small FastAPI JSON API for dictionary search, AI-assisted
study cards, related entries, and service health.

Local examples assume the backend is running at `http://127.0.0.1:8000`.

## `GET /api/search`

Searches the generated SQLite dictionary cache. Empty searches do not touch the
database.

Query parameters:

| Name | Required | Description |
|------|----------|-------------|
| `q` | No | Search term matched against French words and Monégasque definitions. |

Example:

```bash
curl "http://127.0.0.1:8000/api/search?q=bonjour"
```

Successful response:

```json
{
  "query": "bonjour",
  "count": 1,
  "results": [
    {
      "word": "bonjour",
      "definition": "bun giurnu"
    }
  ]
}
```

Empty response:

```json
{
  "query": "",
  "count": 0,
  "results": []
}
```

## `POST /api/ai/explain`

Generates a learner-friendly French explanation for one dictionary entry.
Requires `GEMINI_API_KEY`.

Request:

```bash
curl -X POST "http://127.0.0.1:8000/api/ai/explain" \
  -H "Content-Type: application/json" \
  -d '{"word":"bonjour","definition":"bun giurnu"}'
```

Successful response:

```json
{
  "word": "bonjour",
  "definition": "bun giurnu",
  "model": "gemini-2.5-flash-lite",
  "explanation": {
    "summary_fr": "Une salutation simple et quotidienne.",
    "usage_notes": [
      "À utiliser pour saluer quelqu'un.",
      "Convient dans un contexte poli ou neutre."
    ],
    "memory_tip": "Rapproche bun de bon et giurnu de jour.",
    "practice_question": "Comment saluerais-tu une personne le matin ?"
  }
}
```

If AI is not configured, FastAPI returns HTTP `503`:

```json
{
  "detail": "Assistant IA non configuré."
}
```

## `POST /api/ai/related`

Asks Gemini for candidate French related words, then validates every suggestion
against the real dictionary before returning it. This endpoint never returns
AI-only entries that are absent from `dictionary.sql`.

Request:

```bash
curl -X POST "http://127.0.0.1:8000/api/ai/related" \
  -H "Content-Type: application/json" \
  -d '{"word":"bonjour","definition":"bun giurnu"}'
```

Successful response:

```json
{
  "word": "bonjour",
  "related": [
    {
      "word": "salut",
      "definition": "..."
    }
  ]
}
```

## `GET /api/ai/word-of-day`

Returns a deterministic daily dictionary entry with a cached AI explanation.
Requires `GEMINI_API_KEY`.

Example:

```bash
curl "http://127.0.0.1:8000/api/ai/word-of-day"
```

Successful response:

```json
{
  "date": "2026-05-14",
  "word": "bonjour",
  "definition": "bun giurnu",
  "explanation": {
    "summary_fr": "Une salutation simple et quotidienne.",
    "usage_notes": [],
    "memory_tip": "Rapproche bun de bon.",
    "practice_question": "Comment saluerais-tu quelqu'un ?"
  }
}
```

## `GET /healthz`

Returns lightweight service metadata for Render or another load balancer.

Example response:

```json
{
  "service": "Monalex Dictionary",
  "status": "ok",
  "version": "0.3.0",
  "ai": {
    "configured": false,
    "model": "gemini-2.5-flash-lite"
  },
  "dictionary_cache": {
    "path": "/tmp/monalex.sqlite3",
    "ready": true,
    "rows": 14200,
    "source_current": true
  }
}
```

## Discovery

FastAPI also exposes generated OpenAPI documentation:

| Route | Description |
|-------|-------------|
| `/docs` | Swagger UI for manual endpoint exploration. |
| `/openapi.json` | Machine-readable OpenAPI schema. |
