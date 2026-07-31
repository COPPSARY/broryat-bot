import base64
from typing import Any

from openai import AsyncOpenAI

from bot.services.ai.image_extractors.base import INSTRUCTION, ImageExtractionError, ImageExtractor

_BASE_URL = "https://router.huggingface.co/v1"
_MODEL = "google/gemma-4-31B-it"


class HuggingFaceImageExtractor(ImageExtractor):
    """Reads text out of an image using a HuggingFace-hosted vision model."""

    def __init__(
        self,
        api_key: str,
        client: Any | None = None,
        model: str = _MODEL,
        base_url: str = _BASE_URL,
    ):
        self._client = client or AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    async def extract_text(self, image_bytes: bytes, mime_type: str) -> str:
        encoded = base64.b64encode(image_bytes).decode("ascii")
        data_uri = f"data:{mime_type};base64,{encoded}"

        try:
            response = await self._client.chat.completions.create(
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
        except Exception as exc:
            raise ImageExtractionError(str(exc)) from exc

        content = response.choices[0].message.content
        return content.strip() if content else ""
