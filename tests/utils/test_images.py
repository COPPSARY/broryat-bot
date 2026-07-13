import io

import pillow_heif
import pytest
from PIL import Image

from bot.utils.images import is_gif, is_image_document, prepare_image_for_ocr

pillow_heif.register_heif_opener()


@pytest.mark.parametrize(
    "file_name,mime_type,expected",
    [
        ("photo.png", "image/png", True),
        ("photo.jpg", "image/jpeg", True),
        ("photo.jpeg", None, True),
        ("photo.webp", None, True),
        ("photo.gif", "image/gif", True),
        ("photo.heic", None, True),
        ("photo.HEIC", None, True),
        ("scan.pdf", "application/pdf", False),
        ("malware.exe", "application/octet-stream", False),
        ("archive.zip", None, False),
        (None, "image/png", True),
        (None, None, False),
    ],
)
def test_is_image_document(file_name, mime_type, expected):
    assert is_image_document(file_name, mime_type) is expected


@pytest.mark.parametrize(
    "file_name,mime_type,expected",
    [
        ("funny.gif", "image/gif", True),
        ("funny.GIF", None, True),
        ("funny.gif", None, True),
        (None, "image/gif", True),
        ("photo.png", "image/png", False),
        ("scan.pdf", "application/pdf", False),
        ("malware.exe", "application/octet-stream", False),
        (None, None, False),
    ],
)
def test_is_gif(file_name, mime_type, expected):
    assert is_gif(file_name, mime_type) is expected


def test_prepare_image_for_ocr_passes_through_non_heic_images():
    data = b"\x89PNG not really but fine"
    out_bytes, out_mime = prepare_image_for_ocr(data, "image/png", "photo.png")
    assert out_bytes == data
    assert out_mime == "image/png"


def test_prepare_image_for_ocr_defaults_mime_when_missing():
    data = b"bytes"
    _, out_mime = prepare_image_for_ocr(data, None, "photo.jpg")
    assert out_mime == "image/jpeg"


def _make_heic_bytes() -> bytes:
    image = Image.new("RGB", (8, 8), color=(120, 60, 200))
    buffer = io.BytesIO()
    image.save(buffer, format="HEIF")
    return buffer.getvalue()


def test_prepare_image_for_ocr_converts_heic_to_jpeg():
    heic = _make_heic_bytes()

    out_bytes, out_mime = prepare_image_for_ocr(heic, "image/heic", "photo.heic")

    assert out_mime == "image/jpeg"
    # The converted bytes must decode as a JPEG.
    decoded = Image.open(io.BytesIO(out_bytes))
    assert decoded.format == "JPEG"
