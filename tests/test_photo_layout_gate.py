import tempfile
import unittest
from pathlib import Path

from tools.photo_layout_gate import PhotoLayoutError, validate_photo_layouts


def write_html(root: Path, body: str) -> Path:
    path = root / "index.html"
    path.write_text(f"<html><body>{body}</body></html>", encoding="utf-8")
    return path


class PhotoLayoutGateTests(unittest.TestCase):
    def test_accepts_safe_portrait_landscape_and_cover_contracts(self):
        with tempfile.TemporaryDirectory() as raw:
            path = write_html(Path(raw), (
                '<article data-layout="subject-safe" data-overlay="forbid" '
                'data-image-zone="0,0,100,64" data-copy-zone="0,64,100,36"></article>'
                '<figure data-layout="portrait-full" data-overlay="forbid"><img></figure>'
                '<figure data-layout="landscape-split" data-image-zone="0,0,100,66" '
                'data-copy-zone="0,66,100,34"><img><figcaption>x</figcaption></figure>'
            ))
            self.assertEqual(validate_photo_layouts(path)["layouts"], 3)

    def test_rejects_overlapping_image_and_copy_zones(self):
        with tempfile.TemporaryDirectory() as raw:
            path = write_html(Path(raw), '<figure data-layout="landscape-split" '
                              'data-image-zone="0,0,100,75" data-copy-zone="0,65,100,35"></figure>')
            with self.assertRaisesRegex(PhotoLayoutError, "overlap"):
                validate_photo_layouts(path)

    def test_rejects_visible_caption_on_portrait_full(self):
        with tempfile.TemporaryDirectory() as raw:
            path = write_html(Path(raw), '<figure data-layout="portrait-full" data-overlay="forbid">'
                              '<img><figcaption>bad</figcaption></figure>')
            with self.assertRaisesRegex(PhotoLayoutError, "portrait-full caption"):
                validate_photo_layouts(path)


if __name__ == "__main__":
    unittest.main()
