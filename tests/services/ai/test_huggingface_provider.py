from unittest.mock import AsyncMock, MagicMock

import pytest

from bot.schemas.enums import RiskLevel
from bot.services.ai.base import AIProviderError
from bot.services.ai.huggingface_provider import HuggingFaceProvider
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
    provider = HuggingFaceProvider(api_key="test-key", client=client)

    result = await provider.classify("your account is suspended", "en")

    assert result.risk_level == RiskLevel.HIGH
    assert result.language == "en"
    assert result.raw_response == text


async def test_classify_appends_disclaimer_that_the_prompt_no_longer_asks_for():
    text = "Nothing suspicious.\n\nExplanation:\n- x\n\nRecommendation:\ny\n\nRISK:SAFE"
    client = _fake_client(text)
    provider = HuggingFaceProvider(api_key="test-key", client=client)

    result = await provider.classify("hello", "en")

    visible = "Nothing suspicious.\n\nExplanation:\n- x\n\nRecommendation:\ny"
    assert result.message == f"{visible}\n\n{DISCLAIMER['en']}"


async def test_classify_uses_khmer_disclaimer_when_language_is_khmer():
    text = "សារនេះមិនមានបញ្ហា។\n\nRISK:SAFE"
    client = _fake_client(text)
    provider = HuggingFaceProvider(api_key="test-key", client=client)

    result = await provider.classify("hello", "km")

    assert result.message == f"សារនេះមិនមានបញ្ហា។\n\n{DISCLAIMER['km']}"


async def test_classify_raises_when_no_risk_level_found():
    client = _fake_client("This response forgot to include a risk level.")
    provider = HuggingFaceProvider(api_key="test-key", client=client)

    with pytest.raises(AIProviderError):
        await provider.classify("some text", "en")


async def test_classify_does_not_request_json_response_format():
    client = _fake_client("Nothing suspicious.\n\nRISK:SAFE")
    provider = HuggingFaceProvider(api_key="test-key", client=client)

    await provider.classify("hello friend", "en")

    _, kwargs = client.chat.completions.create.call_args
    assert "response_format" not in kwargs


async def test_classify_passes_built_prompt_to_model():
    client = _fake_client("Nothing suspicious.\n\nRISK:SAFE")
    provider = HuggingFaceProvider(api_key="test-key", client=client, model="test-model")

    await provider.classify("hello friend", "en")

    _, kwargs = client.chat.completions.create.call_args
    assert kwargs["model"] == "test-model"
    assert "hello friend" in kwargs["messages"][0]["content"]


async def test_classify_includes_vt_context_in_prompt_when_provided():
    client = _fake_client("Malicious file.\n\nRISK:HIGH")
    provider = HuggingFaceProvider(api_key="test-key", client=client)

    await provider.classify("check this link", "en", vt_context="malicious (10/70 engines)")

    _, kwargs = client.chat.completions.create.call_args
    assert "malicious (10/70 engines)" in kwargs["messages"][0]["content"]


async def test_error_includes_the_raw_response_for_debugging():
    client = _fake_client("no risk level here at all")
    provider = HuggingFaceProvider(api_key="test-key", client=client)

    with pytest.raises(AIProviderError, match="no risk level here at all"):
        await provider.classify("some text", "en")
