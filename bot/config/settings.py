import os
import re
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

    telegram_bot_token: str
    ai_provider: Literal["gemini", "openai", "anthropic", "huggingface", "broryat"] = "gemini"
    llm_model: str = "google/gemma-4-31B-it"
    gemini_api_key: str | None = None
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    huggingface_api_key: str | None = None
    broryat_api_key: str | None = None

    max_file_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES

    vt_api_key: str | None = None
    vt_rpm_limit: int = 4
    vt_daily_limit: int = 500
    vt_monthly_limit: int = 15500

    database_url: str

    group_scan_enabled: bool = True
    log_level: str = "INFO"
    admin_chat_id: int | None = None

    def _api_keys(self, prefix: str, primary: str | None) -> list[str]:
        values = {
            str(key).upper(): value
            for key, value in (self.model_extra or {}).items()
        }
        values.update(os.environ)

        numbered = []
        for name, value in values.items():
            match = re.fullmatch(rf"{prefix}(\d+)", name)
            if match and value:
                numbered.append((int(match.group(1)), str(value)))

        keys = ([primary] if primary else []) + [
            value for _, value in sorted(numbered)
        ]
        return list(dict.fromkeys(keys))

    @property
    def huggingface_api_keys(self) -> list[str]:
        return self._api_keys("HUGGINGFACE_API_KEY", self.huggingface_api_key)

    @property
    def vt_api_keys(self) -> list[str]:
        return self._api_keys("VT_API_KEY", self.vt_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
