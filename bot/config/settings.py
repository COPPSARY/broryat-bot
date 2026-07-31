from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    telegram_bot_token: str
    ai_provider: Literal["gemini", "openai", "anthropic", "huggingface"] = "gemini"
    llm_model: str = "google/gemma-4-31B-it"
    gemini_api_key: str | None = None
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    huggingface_api_key: str | None = None

    max_file_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES

    vt_api_key: str
    vt_rpm_limit: int = 4
    vt_daily_limit: int = 500
    vt_monthly_limit: int = 15500

    database_url: str

    group_scan_enabled: bool = True
    log_level: str = "INFO"
    admin_chat_id: int | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
