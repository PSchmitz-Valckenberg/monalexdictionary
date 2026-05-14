from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Monalex Dictionary"
    app_version: str = "0.3.0"
    site_url: str = ""
    cors_origins: str = "*"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash-lite"

    search_limit: int = Field(default=50, ge=1, le=200)
    ai_input_limit: int = Field(default=1200, ge=1, le=4000)

    dictionary_sql_path: str = str(_REPO_ROOT / "dictionary.sql")
    sqlite_path: str = "/tmp/monalex.sqlite3"

    @property
    def allowed_cors_origins(self) -> list[str]:
        origins = [origin.strip() for origin in self.cors_origins.split(",")]
        return [origin for origin in origins if origin] or ["*"]


settings = Settings()
