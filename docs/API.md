# API Reference

Monalex serves the public dictionary through HTML pages and a small JSON API.
The JSON endpoints are intentionally simple so they can be used by a future
frontend, mobile app, or data cleanup script without scraping rendered HTML.

## `GET /api/search`

Searches the configured dictionary table.

Query parameters:

| Name | Required | Description |
|------|----------|-------------|
| `q` | No | Search term for dictionary lookups. |
| `searchInput` | No | Backward-compatible alias used by the HTML form. |

Example:

```bash
curl "http://127.0.0.1:5000/api/search?q=bonjour"
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

Empty searches do not touch the database:

```json
{
  "query": "",
  "count": 0,
  "results": []
}
```

Database connection errors return HTTP `503`:

```json
{
  "query": "bonjour",
  "error": "Connexion à la base de données impossible.",
  "results": []
}
```

## `GET /search`

Renders the browser-facing search page. It accepts the same `searchInput`
parameter used by the form.

Example:

```bash
curl "http://127.0.0.1:5000/search?searchInput=bonjour"
```

## `POST /api/ai/explain`

Generates a learner-friendly study card for one dictionary result. This endpoint
is optional and requires `OPENAI_API_KEY`.

Request:

```bash
curl -X POST "http://127.0.0.1:5000/api/ai/explain" \
  -H "Content-Type: application/json" \
  -d '{"word":"bonjour","definition":"bun giurnu"}'
```

Successful response:

```json
{
  "word": "bonjour",
  "definition": "bun giurnu",
  "model": "gpt-5.4-mini",
  "explanation": {
    "summary_fr": "Une salutation simple et quotidienne.",
    "usage_notes": [
      "À utiliser pour saluer quelqu'un.",
      "Convient dans un contexte poli ou neutre."
    ],
    "examples": [
      {
        "fr": "Bonjour.",
        "monegasque": "Bun giurnu."
      }
    ],
    "memory_tip": "Rapproche bun de bon et giurnu de jour.",
    "practice_question": "Comment saluerais-tu une personne le matin ?"
  }
}
```

If the key is missing, the endpoint returns HTTP `503` with a configuration
message. The browser UI surfaces this message inside the result card.

## Conjugation Pages

The app keeps the original `.html` routes for compatibility and also exposes
cleaner URLs for navigation and sharing:

| Clean URL | Legacy URL |
|-----------|------------|
| `/conjugaison/premier` | `/premier.html` |
| `/conjugaison/deuxieme` | `/deuxieme.html` |
| `/conjugaison/troisieme` | `/troisieme.html` |
| `/conjugaison/etre` | `/etre_conjugation` |
| `/conjugaison/avoir` | `/avoir_conjugation` |
| `/exceptions/premier` | `/exceptions_premier.html` |
| `/exceptions/deuxieme` | `/exception_deuxieme.html` |

## `GET /healthz`

Returns lightweight service metadata. It does not query MySQL, which keeps it
safe for load balancer and platform health checks.

Example response:

```json
{
  "service": "Monalex Dictionary",
  "status": "ok",
  "version": "0.2.0",
  "ai": {
    "configured": false,
    "model": "gpt-5.4-mini"
  }
}
```
