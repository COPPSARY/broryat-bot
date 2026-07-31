import base64
import logging
from collections.abc import Sequence
from typing import Any

from openai import APIStatusError, AsyncOpenAI

from bot.services.ai.image_extractors.base import INSTRUCTION, ImageExtractionError, ImageExtractor

_BASE_URL = "https://router.huggingface.co/v1"
_MODEL = "google/gemma-4-31B-it"
_ROTATABLE_STATUS_CODES = {401, 402, 403, 429}

logger = logging.getLogger(__name__)


class HuggingFaceImageExtractor(ImageExtractor):
    """Reads text out of an image using a HuggingFace-hosted vision model."""

    def __init__(
        self,
        api_key: str | None = None,
        client: Any | None = None,
        model: str = _MODEL,
        base_url: str = _BASE_URL,
        api_keys: Sequence[str] | None = None,
    ):
        keys = list(dict.fromkeys(key for key in (api_keys or [api_key]) if key))
        if client is None and not keys:
            raise ValueError("At least one Hugging Face API key is required")

        self._clients = (
            (client,)
            if client is not None
            else tuple(AsyncOpenAI(api_key=key, base_url=base_url) for key in keys)
        )
        self._client = self._clients[0]
        self._client_index = 0
        self._model = model

    async def extract_text(self, image_bytes: bytes, mime_type: str) -> str:
        encoded = base64.b64encode(image_bytes).decode("ascii")
        data_uri = f"data:{mime_type};base64,{encoded}"

        last_error = None
        for _ in self._clients:
            index = self._client_index
            try:
                response = await self._clients[index].chat.completions.create(
                    model=self._model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": INSTRUCTION},
                                {"type": "image_url", "image_url": {"url": data_uri}},
                            ],
                        }
                    ],
                )
                break
            except APIStatusError as exc:
                if exc.status_code not in _ROTATABLE_STATUS_CODES:
                    raise ImageExtractionError(str(exc)) from exc
                last_error = exc
                self._client_index = (index + 1) % len(self._clients)
                logger.warning(
                    "Hugging Face OCR key %d rejected with HTTP %d; trying next key",
                    index + 1,
                    exc.status_code,
                )
            except Exception as exc:
                raise ImageExtractionError(str(exc)) from exc
        else:
            raise ImageExtractionError(str(last_error)) from last_error

        content = response.choices[0].message.content
        return content.strip() if content else ""
