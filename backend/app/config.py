from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_ROOT = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Monalex Dictionary"
    app_version: str = "0.3.0"
    site_url: str = ""

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash-lite"

    search_limit: int = 50
    ai_input_limit: int = 1200

    dictionary_sql_path: str = str(_REPO_ROOT / "dictionary.sql")
    sqlite_path: str = "/tmp/monalex.sqlite3"


settings = Settings()
