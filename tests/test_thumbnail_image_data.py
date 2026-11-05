import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

import thumbnail_image_data
from thumbnail_image_data import is_valid_image_data, is_valid_image_file


class ThumbnailImageDataTests(unittest.TestCase):
    def make_png(self) -> bytes:
        buffer = io.BytesIO()
        Image.new("RGB", (12, 8), (20, 80, 120)).save(buffer, format="PNG")
        return buffer.getvalue()

    def test_accepts_complete_png(self):
        self.assertTrue(is_valid_image_data(self.make_png()))

    def test_rejects_http_error_page(self):
        self.assertFalse(
            is_valid_image_data(b"<!doctype html><html><body>404 Not Found</body></html>")
        )

    def test_rejects_empty_or_missing_payload(self):
        self.assertFalse(is_valid_image_data(b""))
        self.assertFalse(is_valid_image_data(None))

    def test_rejects_truncated_png(self):
        data = self.make_png()
        self.assertFalse(is_valid_image_data(data[:24]))

    def test_rejects_arbitrary_text_payload(self):
        self.assertFalse(is_valid_image_data(b"version https://git-lfs.github.com/spec/v1\n"))

    def test_rejects_images_over_pixel_limit_before_decoding(self):
        image_data = self.make_png()
        with patch.object(thumbnail_image_data, "MAX_IMAGE_PIXELS", 95):
            self.assertFalse(is_valid_image_data(image_data))

            with tempfile.TemporaryDirectory() as temp:
                image_path = Path(temp) / "large.png"
                image_path.write_bytes(image_data)
                self.assertFalse(is_valid_image_file(image_path))


if __name__ == "__main__":
    unittest.main()
