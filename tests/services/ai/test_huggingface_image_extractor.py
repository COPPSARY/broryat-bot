import base64
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from openai import APIStatusError

from bot.services.ai.image_extractors.huggingface import HuggingFaceImageExtractor
from bot.services.ai.image_extractors.base import ImageExtractionError


def _fake_client(response_text: str):
    client = MagicMock()
    message = MagicMock(content=response_text)
    choice = MagicMock(message=message)
    client.chat.completions.create = AsyncMock(return_value=MagicMock(choices=[choice]))
    return client


def _status_error(status_code: int) -> APIStatusError:
    request = httpx.Request("POST", "https://router.huggingface.co/v1/chat/completions")
    response = httpx.Response(status_code, request=request)
    return APIStatusError("key rejected", response=response, body=None)


async def test_extract_text_returns_the_stripped_model_output():
    client = _fake_client("  Your account is suspended, click http://evil.example  ")
    extractor = HuggingFaceImageExtractor(api_key="test-key", client=client)

    text = await extractor.extract_text(b"\x89PNG fake", "image/png")

    assert text == "Your account is suspended, click http://evil.example"


async def test_extract_text_sends_the_image_as_a_base64_data_uri():
    client = _fake_client("some text")
    extractor = HuggingFaceImageExtractor(api_key="test-key", client=client)
    image_bytes = b"\x89PNG fake bytes"

    await extractor.extract_text(image_bytes, "image/png")

    _, kwargs = client.chat.completions.create.call_args
    content = kwargs["messages"][0]["content"]
    image_parts = [p for p in content if p["type"] == "image_url"]
    assert len(image_parts) == 1
    expected = base64.b64encode(image_bytes).decode("ascii")
    assert image_parts[0]["image_url"]["url"] == f"data:image/png;base64,{expected}"


async def test_extract_text_uses_the_configured_model():
    client = _fake_client("text")
    extractor = HuggingFaceImageExtractor(api_key="test-key", client=client, model="google/gemma-4-31B-it")

    await extractor.extract_text(b"img", "image/jpeg")

    _, kwargs = client.chat.completions.create.call_args
    assert kwargs["model"] == "google/gemma-4-31B-it"


async def test_extract_text_returns_empty_string_when_model_returns_no_content():
    client = MagicMock()
    choice = MagicMock(message=MagicMock(content=None))
    client.chat.completions.create = AsyncMock(return_value=MagicMock(choices=[choice]))
    extractor = HuggingFaceImageExtractor(api_key="test-key", client=client)

    text = await extractor.extract_text(b"img", "image/jpeg")

    assert text == ""


async def test_extract_text_raises_image_extraction_error_on_client_failure():
    client = MagicMock()
    client.chat.completions.create = AsyncMock(side_effect=RuntimeError("router down"))
    extractor = HuggingFaceImageExtractor(api_key="test-key", client=client)

    with pytest.raises(ImageExtractionError, match="router down"):
        await extractor.extract_text(b"img", "image/jpeg")


async def test_extract_text_rotates_to_next_key_when_quota_is_exhausted():
    exhausted = _fake_client("")
    exhausted.chat.completions.create.side_effect = _status_error(429)
    working = _fake_client("visible text")
    extractor = HuggingFaceImageExtractor(api_key="first", client=exhausted)
    extractor._clients = (exhausted, working)

    text = await extractor.extract_text(b"img", "image/jpeg")

    assert text == "visible text"
    exhausted.chat.completions.create.assert_awaited_once()
    working.chat.completions.create.assert_awaited_once()
    assert extractor._client_index == 1
