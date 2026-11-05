"""Helpers for validating image payloads received from external providers."""

from __future__ import annotations

import io
import struct
from pathlib import Path

from PIL import Image, UnidentifiedImageError

MAX_IMAGE_PIXELS = 16_000_000


def _has_safe_dimensions(image: Image.Image) -> bool:
    return image.width * image.height <= MAX_IMAGE_PIXELS


def is_valid_image_data(data: bytes | bytearray | memoryview | None) -> bool:
    """Return whether *data* contains a fully decodable raster image.

    Image endpoints can occasionally return an HTML error page, a Git LFS
    pointer, or a truncated response with HTTP 200. Pillow raises
    ``UnidentifiedImageError`` for many of these payloads. Validate the full
    image before caching so one bad response cannot abort an SD-card scan.
    """
    if not isinstance(data, (bytes, bytearray, memoryview)) or not data:
        return False

    try:
        # load() forces decoding rather than checking only the header. A
        # successful Image.open() alone does not detect every truncated file.
        with Image.open(io.BytesIO(bytes(data))) as image:
            if not _has_safe_dimensions(image):
                return False
            image.load()
        return True
    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
        SyntaxError,
        Image.DecompressionBombError,
    ):
        return False


def is_valid_image_file(path: str | Path, expected_size: tuple[int, int] | None = None) -> bool:
    """Return whether a local image file fully decodes and optionally has a size.

    Existing output images are only reused when their pixels are readable. When
    expected_size is supplied, malformed/stale thumbnails of the wrong dimensions
    are rebuilt instead of being mistaken for completed output.
    """
    try:
        with Image.open(Path(path)) as image:
            if not _has_safe_dimensions(image):
                return False
            image.load()
            return expected_size is None or image.size == expected_size
    except (
        FileNotFoundError,
        PermissionError,
        UnidentifiedImageError,
        OSError,
        ValueError,
        SyntaxError,
        Image.DecompressionBombError,
    ):
        return False


def is_valid_kernel_thumbnail_file(path: str | Path, expected_size: tuple[int, int]) -> bool:
    """Return whether a file matches the kernel's uncompressed top-down RGB555 BMP contract."""
    image_path = Path(path)
    if not is_valid_image_file(image_path, expected_size):
        return False

    try:
        with image_path.open("rb") as image_file:
            header = image_file.read(54)
            actual_size = image_path.stat().st_size
        if len(header) != 54 or header[:2] != b"BM":
            return False

        file_size, pixel_offset = struct.unpack_from("<IxxxxI", header, 2)
        dib_size, width, height, planes, bits_per_pixel, compression = struct.unpack_from(
            "<IiiHHI", header, 14
        )
        pixel_data_size = expected_size[0] * expected_size[1] * 2
        return (
            dib_size == 40
            and width == expected_size[0]
            and height == -expected_size[1]
            and planes == 1
            and bits_per_pixel == 16
            and compression == 0
            and pixel_offset == 54
            and file_size >= pixel_offset + pixel_data_size
            and actual_size >= pixel_offset + pixel_data_size
        )
    except (OSError, struct.error, ValueError):
        return False
