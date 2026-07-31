import base64
from typing import Any

from anthropic import AsyncAnthropic

from bot.services.ai.image_extractors.base import INSTRUCTION, ImageExtractionError, ImageExtractor

_MODEL = "claude-haiku-4-5"
_MAX_TOKENS = 1024


class AnthropicImageExtractor(ImageExtractor):
    """Reads text out of an image using an Anthropic vision model."""

    def __init__(self, api_key: str, client: Any | None = None, model: str = _MODEL):
        self._client = client or AsyncAnthropic(api_key=api_key)
        self._model = model

    async def extract_text(self, image_bytes: bytes, mime_type: str) -> str:
        encoded = base64.b64encode(image_bytes).decode("ascii")

        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=_MAX_TOKENS,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": INSTRUCTION},
                            {
                                "type": "image",
                                "source": {"type": "base64", "media_type": mime_type, "data": encoded},
                            },
                        ],
                    }
                ],
            )
        except Exception as exc:
            raise ImageExtractionError(str(exc)) from exc

        content = response.content[0].text if response.content else ""
        return content.strip() if content else ""
