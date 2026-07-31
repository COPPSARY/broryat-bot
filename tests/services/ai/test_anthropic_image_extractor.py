import base64
from unittest.mock import AsyncMock, MagicMock

import pytest

from bot.services.ai.image_extractors.anthropic import AnthropicImageExtractor
from bot.services.ai.image_extractors.base import ImageExtractionError


def _fake_client(response_text: str | None):
    client = MagicMock()
    block = MagicMock(text=response_text) if response_text is not None else None
    client.messages.create = AsyncMock(return_value=MagicMock(content=[block] if block else []))
    return client


async def test_extract_text_returns_the_stripped_model_output():
    client = _fake_client("  Your account is suspended, click http://evil.example  ")
    extractor = AnthropicImageExtractor(api_key="test-key", client=client)

    text = await extractor.extract_text(b"\x89PNG fake", "image/png")

    assert text == "Your account is suspended, click http://evil.example"


async def test_extract_text_sends_the_image_as_base64_with_media_type():
    client = _fake_client("some text")
    extractor = AnthropicImageExtractor(api_key="test-key", client=client)
    image_bytes = b"\x89PNG fake bytes"

    await extractor.extract_text(image_bytes, "image/png")

    _, kwargs = client.messages.create.call_args
    content = kwargs["messages"][0]["content"]
    image_parts = [p for p in content if p["type"] == "image"]
    assert len(image_parts) == 1
    expected = base64.b64encode(image_bytes).decode("ascii")
    assert image_parts[0]["source"]["data"] == expected
    assert image_parts[0]["source"]["media_type"] == "image/png"


async def test_extract_text_uses_the_configured_model():
    client = _fake_client("text")
    extractor = AnthropicImageExtractor(api_key="test-key", client=client, model="claude-3-opus")

    await extractor.extract_text(b"img", "image/jpeg")

    _, kwargs = client.messages.create.call_args
    assert kwargs["model"] == "claude-3-opus"


async def test_extract_text_returns_empty_string_when_model_returns_no_content():
    client = _fake_client(None)
    extractor = AnthropicImageExtractor(api_key="test-key", client=client)

    text = await extractor.extract_text(b"img", "image/jpeg")

    assert text == ""


async def test_extract_text_raises_image_extraction_error_on_client_failure():
    client = MagicMock()
    client.messages.create = AsyncMock(side_effect=RuntimeError("anthropic down"))
    extractor = AnthropicImageExtractor(api_key="test-key", client=client)

    with pytest.raises(ImageExtractionError, match="anthropic down"):
        await extractor.extract_text(b"img", "image/jpeg")
