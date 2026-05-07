from fastapi import APIRouter

from app.config import settings

router = APIRouter()


@router.get("/healthz")
def health():
    return {
        "service": settings.app_name,
        "status": "ok",
        "version": settings.app_version,
        "ai": {
            "configured": bool(settings.gemini_api_key),
            "model": settings.gemini_model,
        },
    }
