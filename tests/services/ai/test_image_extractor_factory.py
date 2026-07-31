from types import SimpleNamespace

import pytest

from bot.config.settings import Settings
from bot.services.ai.image_extractors.anthropic import AnthropicImageExtractor
from bot.services.ai.image_extractors.factory import get_image_extractor
from bot.services.ai.image_extractors.gemini import GeminiImageExtractor
from bot.services.ai.image_extractors.huggingface import HuggingFaceImageExtractor
from bot.services.ai.image_extractors.openai import OpenAIImageExtractor


def _settings(**overrides) -> Settings:
    defaults = dict(
        telegram_bot_token="t",
        vt_api_key="v",
        database_url="postgresql://user:pass@localhost:5432/postgres",
        gemini_api_key="g",
        openai_api_key="oa",
        anthropic_api_key="an",
        huggingface_api_key="hf",
    )
    defaults.update(overrides)
    return Settings(_env_file=None, **defaults)


def test_returns_gemini_image_extractor_by_default():
    extractor = get_image_extractor(_settings())
    assert isinstance(extractor, GeminiImageExtractor)


def test_gemini_image_extractor_uses_model_from_settings():
    extractor = get_image_extractor(_settings(llm_model="gemini-1.5-pro"))
    assert extractor._model == "gemini-1.5-pro"


def test_returns_openai_image_extractor():
    extractor = get_image_extractor(_settings(ai_provider="openai"))
    assert isinstance(extractor, OpenAIImageExtractor)


def test_openai_image_extractor_uses_model_from_settings():
    extractor = get_image_extractor(_settings(ai_provider="openai", llm_model="gpt-4o"))
    assert extractor._model == "gpt-4o"


def test_returns_anthropic_image_extractor():
    extractor = get_image_extractor(_settings(ai_provider="anthropic"))
    assert isinstance(extractor, AnthropicImageExtractor)


def test_anthropic_image_extractor_uses_model_from_settings():
    extractor = get_image_extractor(_settings(ai_provider="anthropic", llm_model="claude-3-opus"))
    assert extractor._model == "claude-3-opus"


def test_returns_huggingface_image_extractor():
    extractor = get_image_extractor(_settings(ai_provider="huggingface"))
    assert isinstance(extractor, HuggingFaceImageExtractor)


def test_huggingface_image_extractor_uses_model_from_settings():
    extractor = get_image_extractor(_settings(ai_provider="huggingface", llm_model="test-model"))
    assert extractor._model == "test-model"


def test_raises_for_unsupported_provider():
    settings = SimpleNamespace(ai_provider="carrier-pigeon")
    with pytest.raises(ValueError):
        get_image_extractor(settings)
