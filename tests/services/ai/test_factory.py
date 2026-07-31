from types import SimpleNamespace

import pytest

from bot.config.settings import Settings
from bot.services.ai.providers.anthropic import AnthropicProvider
from bot.services.ai.providers.broryat import BroryatProvider
from bot.services.ai.providers.factory import get_ai_provider
from bot.services.ai.providers.gemini import GeminiProvider
from bot.services.ai.providers.huggingface import HuggingFaceProvider
from bot.services.ai.providers.openai import OpenAIProvider


def _settings(**overrides) -> Settings:
    defaults = dict(
        telegram_bot_token="t",
        vt_api_key="v",
        database_url="postgresql://user:pass@localhost:5432/postgres",
        gemini_api_key="g",
        openai_api_key="oa",
        anthropic_api_key="an",
        huggingface_api_key="hf",
        broryat_api_key="br",
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


def test_huggingface_provider_uses_model_from_settings():
    provider = get_ai_provider(
        _settings(
            ai_provider="huggingface",
            llm_model="test-model",
        )
    )
    assert provider._model == "test-model"


def test_huggingface_provider_receives_all_numbered_keys():
    provider = get_ai_provider(
        _settings(
            ai_provider="huggingface",
            huggingface_api_key2="hf-2",
            huggingface_api_key3="hf-3",
        )
    )

    assert len(provider._clients) == 3


def test_returns_openai_provider():
    provider = get_ai_provider(_settings(ai_provider="openai"))
    assert isinstance(provider, OpenAIProvider)


def test_openai_provider_uses_model_from_settings():
    provider = get_ai_provider(_settings(ai_provider="openai", llm_model="gpt-4o"))
    assert provider._model == "gpt-4o"


def test_returns_anthropic_provider():
    provider = get_ai_provider(_settings(ai_provider="anthropic"))
    assert isinstance(provider, AnthropicProvider)


def test_anthropic_provider_uses_model_from_settings():
    provider = get_ai_provider(_settings(ai_provider="anthropic", llm_model="claude-3-opus"))
    assert provider._model == "claude-3-opus"


def test_returns_broryat_provider_with_configured_model():
    provider = get_ai_provider(_settings(ai_provider="broryat", llm_model="gemma4"))

    assert isinstance(provider, BroryatProvider)
    assert provider._model == "gemma4"


def test_raises_for_unsupported_provider():
    settings = SimpleNamespace(ai_provider="carrier-pigeon")
    with pytest.raises(ValueError):
        get_ai_provider(settings)
