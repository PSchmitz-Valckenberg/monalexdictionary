from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.sqlite import ensure_db
from app.routes.ai import router as ai_router
from app.routes.health import router as health_router
from app.routes.search import router as search_router
from app.services.ai import get_gemini_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_db()
    if settings.gemini_api_key:
        get_gemini_client()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(search_router)
app.include_router(ai_router)
app.include_router(health_router)
