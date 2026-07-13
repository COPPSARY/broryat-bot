import io
from pathlib import Path

import pillow_heif
from PIL import Image

pillow_heif.register_heif_opener()

_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".heic", ".heif"}
_HEIC_EXTENSIONS = {".heic", ".heif"}


def _extension(file_name: str | None) -> str:
    return Path(file_name).suffix.lower() if file_name else ""


def is_image_document(file_name: str | None, mime_type: str | None) -> bool:
    """True if a Telegram document is an image we can run OCR on."""
    if mime_type and mime_type.startswith("image/"):
        return True
    return _extension(file_name) in _IMAGE_EXTENSIONS


def is_gif(file_name: str | None, mime_type: str | None) -> bool:
    """True if a Telegram document is a GIF — we never scan these."""
    if mime_type and mime_type.lower() == "image/gif":
        return True
    return _extension(file_name) == ".gif"


def _is_heic(file_name: str | None, mime_type: str | None) -> bool:
    if mime_type and mime_type.lower() in ("image/heic", "image/heif"):
        return True
    return _extension(file_name) in _HEIC_EXTENSIONS


def prepare_image_for_ocr(
    image_bytes: bytes, mime_type: str | None, file_name: str | None
) -> tuple[bytes, str]:
    """Return image bytes and a mime type the vision model accepts, converting
    HEIC/HEIF (which vision APIs don't support) to JPEG."""
    if _is_heic(file_name, mime_type):
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        return buffer.getvalue(), "image/jpeg"
    return image_bytes, mime_type or "image/jpeg"
