from typing import Any

from google import genai
from google.genai import types

from bot.services.ai.image_extractors.base import INSTRUCTION, ImageExtractionError, ImageExtractor

_MODEL = "gemini-2.5-flash"


class GeminiImageExtractor(ImageExtractor):
    """Reads text out of an image using a Gemini vision model."""

    def __init__(self, api_key: str, client: Any | None = None, model: str = _MODEL):
        self._client = client or genai.Client(api_key=api_key)
        self._model = model

    async def extract_text(self, image_bytes: bytes, mime_type: str) -> str:
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=[INSTRUCTION, types.Part.from_bytes(data=image_bytes, mime_type=mime_type)],
            )
        except Exception as exc:
            raise ImageExtractionError(str(exc)) from exc

        text = response.text
        return text.strip() if text else ""
