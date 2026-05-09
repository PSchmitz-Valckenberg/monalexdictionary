import hashlib
import json
import sqlite3
import time
from datetime import date

from google import genai
from google.genai import types

from app.config import settings
from app.database.sqlite import get_connection
from app.services.search import get_entry_at_offset, get_total_count, search_entries

_client: genai.Client | None = None

# Explanation schema: no generated Monégasque sentences — Gemini only explains
# in French using the provided entry. Fabricated Monégasque is the main
# hallucination risk for a low-resource language.
_EXPLANATION_SCHEMA = {
    "type": "object",
    "properties": {
        "summary_fr": {"type": "string"},
        "usage_notes": {"type": "array", "items": {"type": "string"}},
        "memory_tip": {"type": "string"},
        "practice_question": {"type": "string"},
    },
    "required": ["summary_fr", "usage_notes", "memory_tip", "practice_question"],
}

_EXPLANATION_PROMPT = (
    "Tu es un assistant pédagogique pour Monalex, un dictionnaire français-monégasque. "
    "Explique l'entrée fournie en français clair pour un apprenant débutant. "
    "Règles strictes : "
    "1. N'invente aucun mot, phrase ou texte en monégasque — utilise UNIQUEMENT les termes présents dans l'entrée. "
    "2. Tes explications sont en français uniquement. "
    "3. Ne déduis pas de règles grammaticales qui ne sont pas visibles dans l'entrée. "
    "4. Sois concis et pédagogique."
)

_RELATED_SCHEMA = {
    "type": "object",
    "properties": {
        "suggestions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Liste de mots français susceptibles d'être sémantiquement proches",
        }
    },
    "required": ["suggestions"],
}

_RELATED_PROMPT = (
    "Tu es un assistant lexicographique pour un dictionnaire français-monégasque. "
    "Donne une liste de 10 mots français sémantiquement proches du mot fourni "
    "(synonymes, mots de la même famille, même champ lexical, antonymes utiles). "
    "Réponds uniquement avec des mots français simples, sans explication."
)


def get_gemini_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def _cache_key(word: str, definition: str) -> str:
    payload = f"{settings.gemini_model}:{word}:{definition}"
    return hashlib.sha256(payload.encode()).hexdigest()


def _get_cache(key: str) -> dict | None:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT response_json FROM ai_response_cache WHERE cache_key = ?", (key,)
        ).fetchone()
        return json.loads(row[0]) if row else None
    except sqlite3.Error:
        return None
    finally:
        conn.close()


def _set_cache(key: str, data: dict) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO ai_response_cache (cache_key, response_json, created_at) VALUES (?, ?, ?)",
            (key, json.dumps(data, ensure_ascii=False), int(time.time())),
        )
        conn.commit()
    except sqlite3.Error:
        pass
    finally:
        conn.close()


async def generate_explanation(word: str, definition: str) -> dict:
    key = _cache_key(word, definition)
    cached = _get_cache(key)
    if cached:
        return cached

    prompt = (
        f"{_EXPLANATION_PROMPT}\n\n"
        f"Mot français : {word[:settings.ai_input_limit]}\n"
        f"Traduction / définition monégasque : {definition[:settings.ai_input_limit]}"
    )

    response = await get_gemini_client().aio.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=_EXPLANATION_SCHEMA,
            max_output_tokens=600,
        ),
    )
    result = json.loads(response.text)
    _set_cache(key, result)
    return result


async def generate_related(word: str, definition: str) -> list[dict]:
    key = _cache_key(f"related:{word}", definition)
    cached = _get_cache(key)
    if cached:
        return cached.get("entries", [])

    prompt = (
        f"{_RELATED_PROMPT}\n\n"
        f"Mot : {word[:settings.ai_input_limit]}\n"
        f"Définition monégasque : {definition[:settings.ai_input_limit]}"
    )

    response = await get_gemini_client().aio.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=_RELATED_SCHEMA,
            max_output_tokens=200,
        ),
    )
    try:
        suggestions: list[str] = json.loads(response.text).get("suggestions", [])
    except (json.JSONDecodeError, AttributeError):
        suggestions = []

    # Validate every suggestion against the real dictionary — never return
    # words that don't exist in the 14,200 entries.
    entries: list[dict] = []
    seen: set[str] = {word.lower()}
    for suggestion in suggestions:
        if len(entries) >= 5:
            break
        term = suggestion.strip()
        if len(term) < 2:  # skip empty / single-char suggestions
            continue
        hits = search_entries(term)
        for hit in hits:
            if hit["word"].lower() not in seen:
                entries.append(hit)
                seen.add(hit["word"].lower())
                break

    _set_cache(key, {"entries": entries})
    return entries


async def get_word_of_day() -> dict:
    today = date.today().isoformat()
    key = f"wotd:{today}"
    cached = _get_cache(key)
    if cached:
        return cached

    total = get_total_count()
    offset = date.today().toordinal() % total
    entry = get_entry_at_offset(offset) or {"word": "bonjour", "definition": "bon giurnu"}

    explanation = await generate_explanation(entry["word"], entry["definition"])
    result = {
        "date": today,
        "word": entry["word"],
        "definition": entry["definition"],
        "explanation": explanation,
    }
    _set_cache(key, result)
    return result
