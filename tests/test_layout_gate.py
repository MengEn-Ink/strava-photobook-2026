import unittest

from strava_photobook.theme import FEATURE_CSS, THEME_CSS


class LayoutContractTests(unittest.TestCase):
    def test_text_regions_are_clamped_and_clipped(self):
        css = (FEATURE_CSS + THEME_CSS).replace(" ", "")
        for selector in (".feature{", ".feat-title{", ".feat-desc{", ".bleed-cap{"):
            self.assertIn(selector, css)
        self.assertIn("overflow:hidden", css)
        self.assertIn("-webkit-line-clamp", css)

    def test_year_statistics_have_a_bounded_compact_layout(self):
        css = (FEATURE_CSS + THEME_CSS).replace(" ", "")
        self.assertIn(".year-stats{", css)
        self.assertIn("max-height:76%", css)
        self.assertIn("overflow:hidden", css)
        self.assertIn(".year-statsp{margin:002.6cqw}", css)


if __name__ == "__main__":
    unittest.main()
