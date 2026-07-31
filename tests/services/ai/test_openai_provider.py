from unittest.mock import AsyncMock, MagicMock

import pytest

from bot.schemas.enums import RiskLevel
from bot.services.ai.providers.base import AIProviderError
from bot.services.ai.providers.openai import OpenAIProvider
from bot.services.ai.prompt import DISCLAIMER


def _fake_client(response_text: str):
    client = MagicMock()
    message = MagicMock(content=response_text)
    choice = MagicMock(message=message)
    client.chat.completions.create = AsyncMock(return_value=MagicMock(choices=[choice]))
    return client


async def test_classify_parses_plain_text_response():
    text = "Impersonates a bank asking for OTP.\n\nExplanation:\n- x\n\nRecommendation:\ny\n\nRISK:HIGH"
    client = _fake_client(text)
    provider = OpenAIProvider(api_key="test-key", client=client)

    result = await provider.classify("your account is suspended", "en")

    assert result.risk_level == RiskLevel.HIGH
    assert result.language == "en"
    assert result.raw_response == text


async def test_classify_appends_disclaimer():
    text = "Nothing suspicious.\n\nExplanation:\n- x\n\nRecommendation:\ny\n\nRISK:SAFE"
    client = _fake_client(text)
    provider = OpenAIProvider(api_key="test-key", client=client)

    result = await provider.classify("hello", "en")

    visible = "Nothing suspicious.\n\nExplanation:\n- x\n\nRecommendation:\ny"
    assert result.message == f"{visible}\n\n{DISCLAIMER['en']}"


async def test_classify_raises_when_no_risk_level_found():
    client = _fake_client("This response forgot to include a risk level.")
    provider = OpenAIProvider(api_key="test-key", client=client)

    with pytest.raises(AIProviderError):
        await provider.classify("some text", "en")


async def test_classify_passes_built_prompt_to_model():
    client = _fake_client("Nothing suspicious.\n\nRISK:SAFE")
    provider = OpenAIProvider(api_key="test-key", client=client, model="test-model")

    await provider.classify("hello friend", "en")

    _, kwargs = client.chat.completions.create.call_args
    assert kwargs["model"] == "test-model"
    assert "hello friend" in kwargs["messages"][0]["content"]


async def test_classify_includes_vt_context_in_prompt_when_provided():
    client = _fake_client("Malicious file.\n\nRISK:HIGH")
    provider = OpenAIProvider(api_key="test-key", client=client)

    await provider.classify("check this link", "en", vt_context="malicious (10/70 engines)")

    _, kwargs = client.chat.completions.create.call_args
    assert "malicious (10/70 engines)" in kwargs["messages"][0]["content"]
