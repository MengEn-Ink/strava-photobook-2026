import unittest

from strava_photobook.book import _activity_photo_page, _feature_page
from strava_photobook.model import Activity, Highlight, Photo


class BookRenderingTests(unittest.TestCase):
    def setUp(self):
        self.activity = Activity(
            id="42", name="A very long ride title " * 20, date="2026-08-16T06:01:05Z", year="2026",
            description="A long description " * 100, kudos=60, pr_count=4,
            distance_km=161.2, elev_m=1952, moving_time=22000,
        )
        self.highlight = Highlight(self.activity, 88.0, "照片与骑行故事完整")

    def test_photo_page_keeps_activity_context(self):
        photo = Photo("assets/photos/42.jpg", "Rain and mountains")
        rendered = _activity_photo_page("recto", self.highlight, photo, "7")
        self.assertIn('data-activity-id="42"', rendered)
        self.assertIn("161 km", rendered)
        self.assertIn("照片与骑行故事完整", rendered)
        self.assertIn("Rain and mountains", rendered)

    def test_long_feature_copy_is_bounded_before_render(self):
        rendered = _feature_page("recto", self.highlight)
        self.assertLess(len(rendered), 3000)
        self.assertIn("…", rendered)


if __name__ == "__main__":
    unittest.main()
