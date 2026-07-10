from unittest.mock import MagicMock

import pytest

from bot.schemas.enums import RiskLevel
from bot.services.ai.base import AIProviderError
from bot.services.ai.gemini_provider import GeminiProvider
from bot.services.ai.prompt import DISCLAIMER


def _fake_client(response_text: str):
    client = MagicMock()
    client.models.generate_content.return_value = MagicMock(text=response_text)
    return client


async def test_classify_parses_plain_text_response():
    text = "Impersonates a bank asking for OTP.\n\nExplanation:\n- x\n\nRecommendation:\ny\n\nRISK:HIGH"
    client = _fake_client(text)
    provider = GeminiProvider(api_key="test-key", client=client)

    result = await provider.classify("your account is suspended", "en")

    assert result.risk_level == RiskLevel.HIGH
    assert result.language == "en"
    assert result.raw_response == text


async def test_classify_appends_disclaimer_that_the_prompt_no_longer_asks_for():
    text = "Nothing suspicious.\n\nExplanation:\n- x\n\nRecommendation:\ny\n\nRISK:SAFE"
    client = _fake_client(text)
    provider = GeminiProvider(api_key="test-key", client=client)

    result = await provider.classify("hello", "en")

    visible = "Nothing suspicious.\n\nExplanation:\n- x\n\nRecommendation:\ny"
    assert result.message == f"{visible}\n\n{DISCLAIMER['en']}"


async def test_classify_uses_khmer_disclaimer_when_language_is_khmer():
    text = "សារនេះមិនមានបញ្ហា។\n\nRISK:SAFE"
    client = _fake_client(text)
    provider = GeminiProvider(api_key="test-key", client=client)

    result = await provider.classify("hello", "km")

    assert result.message == f"សារនេះមិនមានបញ្ហា។\n\n{DISCLAIMER['km']}"


async def test_classify_raises_when_no_risk_level_found():
    client = _fake_client("This response forgot to include a risk level.")
    provider = GeminiProvider(api_key="test-key", client=client)

    with pytest.raises(AIProviderError):
        await provider.classify("some text", "en")


async def test_classify_does_not_request_json_response_format():
    client = _fake_client("Nothing suspicious.\n\nRISK:SAFE")
    provider = GeminiProvider(api_key="test-key", client=client)

    await provider.classify("hello friend", "en")

    _, kwargs = client.models.generate_content.call_args
    config = kwargs.get("config")
    assert config is None or getattr(config, "response_mime_type", None) != "application/json"


async def test_classify_passes_built_prompt_to_model():
    client = _fake_client("Nothing suspicious.\n\nRISK:SAFE")
    provider = GeminiProvider(api_key="test-key", client=client)

    await provider.classify("hello friend", "en")

    _, kwargs = client.models.generate_content.call_args
    assert "hello friend" in kwargs["contents"]


async def test_classify_includes_vt_context_in_prompt_when_provided():
    client = _fake_client("Malicious file.\n\nRISK:HIGH")
    provider = GeminiProvider(api_key="test-key", client=client)

    await provider.classify("check this link", "en", vt_context="malicious (10/70 engines)")

    _, kwargs = client.models.generate_content.call_args
    assert "malicious (10/70 engines)" in kwargs["contents"]


async def test_error_includes_the_raw_response_for_debugging():
    client = _fake_client("no risk level here at all")
    provider = GeminiProvider(api_key="test-key", client=client)

    with pytest.raises(AIProviderError, match="no risk level here at all"):
        await provider.classify("some text", "en")
