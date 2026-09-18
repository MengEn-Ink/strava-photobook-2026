import unittest

from strava_photobook import book
from strava_photobook.book import _activity_photo_page, _document, _feature_page
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
        self.assertIn("8月16日", rendered)
        self.assertIn("161 km", rendered)
        self.assertIn("爬升 1952 m", rendered)
        self.assertIn("Rain and mountains", rendered)
        self.assertNotIn("照片与骑行故事完整", rendered)
        self.assertNotIn("photo-kicker", rendered)

    def test_selected_activity_blocks_are_sorted_by_date(self):
        january = Highlight(
            Activity(id="jan", name="January Ride", date="2026-01-20T08:00:00Z", year="2026"),
            10,
            "影像记录",
        )
        march = Highlight(
            Activity(id="mar", name="March Ride", date="2026-03-01T08:00:00Z", year="2026"),
            99,
            "年度最多点赞",
        )
        december = Highlight(
            Activity(id="dec", name="December Ride", date="2026-12-02T08:00:00Z", year="2026"),
            80,
            "年度 PR 高光",
        )

        timeline = book._chronological_activity_blocks([december, march], [january, march])

        self.assertEqual(
            [(item.activity.id, featured) for item, featured in timeline],
            [("jan", False), ("mar", True), ("dec", True)],
        )

    def test_long_feature_copy_is_bounded_before_render(self):
        rendered = _feature_page("recto", self.highlight)
        self.assertLess(len(rendered), 3000)
        self.assertIn("…", rendered)

    def test_document_renders_accessible_theme_picker_and_scripts(self):
        rendered = _document("2026", "<article></article>")
        self.assertIn('id="theme-toggle"', rendered)
        self.assertIn('aria-expanded="false"', rendered)
        self.assertIn('id="theme-popover"', rendered)
        self.assertEqual(rendered.count('data-theme-id="'), 19)
        self.assertIn('aria-pressed="true"', rendered)
        self.assertIn('strava-photobook.theme', rendered)
        self.assertIn("style.setProperty('--theme-primary'", rendered)
        self.assertLess(rendered.index('theme-catalog.js'), rendered.index('flipbook.js'))


if __name__ == "__main__":
    unittest.main()
