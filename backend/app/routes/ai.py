from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.services.ai import generate_explanation, generate_related, get_word_of_day

router = APIRouter(prefix="/api/ai")


class ExplainRequest(BaseModel):
    word: str
    definition: str


def _require_ai() -> None:
    if not settings.gemini_api_key:
        raise HTTPException(status_code=503, detail="Assistant IA non configuré.")


@router.post("/explain")
async def explain(body: ExplainRequest):
    _require_ai()
    if not body.word.strip() or not body.definition.strip():
        raise HTTPException(status_code=400, detail="word and definition are required.")
    explanation = await generate_explanation(body.word.strip(), body.definition.strip())
    return {
        "word": body.word,
        "definition": body.definition,
        "model": settings.gemini_model,
        "explanation": explanation,
    }


@router.get("/related")
async def related(word: str, definition: str):
    _require_ai()
    if not word.strip() or not definition.strip():
        raise HTTPException(status_code=400, detail="word and definition are required.")
    entries = await generate_related(word.strip(), definition.strip())
    return {
        "word": word,
        "related": entries,
    }


@router.get("/word-of-day")
async def word_of_day():
    _require_ai()
    return await get_word_of_day()
