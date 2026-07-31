from unittest.mock import MagicMock

import pytest

from bot.services.ai.image_extractors.base import ImageExtractionError
from bot.services.ai.image_extractors.gemini import GeminiImageExtractor


def _fake_client(response_text: str | None):
    client = MagicMock()
    client.models.generate_content.return_value = MagicMock(text=response_text)
    return client


async def test_extract_text_returns_the_stripped_model_output():
    client = _fake_client("  Your account is suspended, click http://evil.example  ")
    extractor = GeminiImageExtractor(api_key="test-key", client=client)

    text = await extractor.extract_text(b"\x89PNG fake", "image/png")

    assert text == "Your account is suspended, click http://evil.example"


async def test_extract_text_sends_the_image_bytes_and_mime_type():
    client = _fake_client("some text")
    extractor = GeminiImageExtractor(api_key="test-key", client=client)
    image_bytes = b"\x89PNG fake bytes"

    await extractor.extract_text(image_bytes, "image/png")

    _, kwargs = client.models.generate_content.call_args
    image_part = kwargs["contents"][1]
    assert image_part.inline_data.data == image_bytes
    assert image_part.inline_data.mime_type == "image/png"


async def test_extract_text_uses_the_configured_model():
    client = _fake_client("text")
    extractor = GeminiImageExtractor(api_key="test-key", client=client, model="gemini-1.5-flash")

    await extractor.extract_text(b"img", "image/jpeg")

    _, kwargs = client.models.generate_content.call_args
    assert kwargs["model"] == "gemini-1.5-flash"


async def test_extract_text_returns_empty_string_when_model_returns_no_content():
    client = _fake_client(None)
    extractor = GeminiImageExtractor(api_key="test-key", client=client)

    text = await extractor.extract_text(b"img", "image/jpeg")

    assert text == ""


async def test_extract_text_raises_image_extraction_error_on_client_failure():
    client = MagicMock()
    client.models.generate_content.side_effect = RuntimeError("gemini down")
    extractor = GeminiImageExtractor(api_key="test-key", client=client)

    with pytest.raises(ImageExtractionError, match="gemini down"):
        await extractor.extract_text(b"img", "image/jpeg")
