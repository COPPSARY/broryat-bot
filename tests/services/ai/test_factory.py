import pytest

from bot.config.settings import Settings
from bot.services.ai.factory import get_ai_provider
from bot.services.ai.gemini_provider import GeminiProvider
from bot.services.ai.huggingface_provider import HuggingFaceProvider


def _settings(**overrides) -> Settings:
    defaults = dict(
        telegram_bot_token="t",
        vt_api_key="v",
        database_url="postgresql://user:pass@localhost:5432/postgres",
        gemini_api_key="g",
        huggingface_api_key="hf",
    )
    defaults.update(overrides)
    return Settings(_env_file=None, **defaults)


def test_returns_gemini_provider_by_default():
    provider = get_ai_provider(_settings())
    assert isinstance(provider, GeminiProvider)


def test_gemini_provider_uses_model_from_settings():
    provider = get_ai_provider(_settings(llm_model="gemini-1.5-pro"))
    assert provider._model == "gemini-1.5-pro"


def test_returns_huggingface_provider():
    provider = get_ai_provider(_settings(ai_provider="huggingface"))
    assert isinstance(provider, HuggingFaceProvider)


def test_huggingface_provider_uses_model_and_base_url_from_settings():
    provider = get_ai_provider(
        _settings(
            ai_provider="huggingface",
            llm_model="test-model",
            huggingface_base_url="https://example.com/v1",
        )
    )
    assert provider._model == "test-model"


def test_raises_for_unsupported_provider():
    settings = _settings(ai_provider="openai")
    with pytest.raises(ValueError):
        get_ai_provider(settings)
