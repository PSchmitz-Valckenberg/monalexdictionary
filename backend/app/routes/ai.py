from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.services.ai import generate_explanation, generate_related, get_word_of_day

router = APIRouter(prefix="/api/ai")


class ExplainRequest(BaseModel):
    word: str
    definition: str


def _clean_entry(body: ExplainRequest) -> tuple[str, str]:
    word = body.word.strip()
    definition = body.definition.strip()
    if not word or not definition:
        raise HTTPException(status_code=400, detail="word and definition are required.")
    return word, definition


def _require_ai() -> None:
    if not settings.gemini_api_key:
        raise HTTPException(status_code=503, detail="Assistant IA non configuré.")


@router.post("/explain")
async def explain(body: ExplainRequest):
    word, definition = _clean_entry(body)
    _require_ai()
    explanation = await generate_explanation(word, definition)
    return {
        "word": word,
        "definition": definition,
        "model": settings.gemini_model,
        "explanation": explanation,
    }


@router.post("/related")
async def related(body: ExplainRequest):
    word, definition = _clean_entry(body)
    _require_ai()
    entries = await generate_related(word, definition)
    return {
        "word": word,
        "related": entries,
    }


@router.get("/word-of-day")
async def word_of_day():
    _require_ai()
    return await get_word_of_day()
