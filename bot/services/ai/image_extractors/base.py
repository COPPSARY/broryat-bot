from abc import ABC, abstractmethod

INSTRUCTION = (
    "Extract all text from this image exactly as it appears, preserving the original "
    "language. Output only the extracted text with no commentary. If the image contains "
    "no text, output nothing."
)


class ImageExtractionError(Exception):
    pass


class ImageExtractor(ABC):
    @abstractmethod
    async def extract_text(self, image_bytes: bytes, mime_type: str) -> str: ...
