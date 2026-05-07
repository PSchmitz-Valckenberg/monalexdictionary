import hashlib
import json
import sqlite3
import time
from datetime import date

from google import genai
from google.genai import types

from app.config import settings
from app.database.sqlite import get_connection
from app.services.search import get_entry_at_offset, get_total_count

_client: genai.Client | None = None

_EXPLANATION_SCHEMA = {
    "type": "object",
    "properties": {
        "summary_fr": {"type": "string"},
        "usage_notes": {"type": "array", "items": {"type": "string"}},
        "examples": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "fr": {"type": "string"},
                    "monegasque": {"type": "string"},
                },
                "required": ["fr", "monegasque"],
            },
        },
        "memory_tip": {"type": "string"},
        "practice_question": {"type": "string"},
    },
    "required": ["summary_fr", "usage_notes", "examples", "memory_tip", "practice_question"],
}

_SYSTEM_PROMPT = (
    "Tu es un assistant pédagogique pour Monalex, un dictionnaire français-"
    "monégasque. Utilise uniquement l'entrée fournie. N'invente pas "
    "d'étymologie ou de règle grammaticale non visible dans l'entrée. "
    "Réponds en français clair, avec des exemples courts et prudents."
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
        f"{_SYSTEM_PROMPT}\n\n"
        "Explique cette entrée du dictionnaire pour un apprenant.\n\n"
        f"Mot français: {word[:settings.ai_input_limit]}\n"
        f"Traduction / définition monégasque: {definition[:settings.ai_input_limit]}"
    )

    response = await get_gemini_client().aio.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=_EXPLANATION_SCHEMA,
            max_output_tokens=900,
        ),
    )
    result = json.loads(response.text)
    _set_cache(key, result)
    return result


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
