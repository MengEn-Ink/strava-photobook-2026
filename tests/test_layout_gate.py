import unittest
from pathlib import Path

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

    def test_theme_variables_cover_book_and_picker_surfaces(self):
        css = (FEATURE_CSS + THEME_CSS).replace(" ", "")
        runtime = Path("runtime/styles.css").read_text(encoding="utf-8").replace(" ", "")
        for variable in ("--theme-primary", "--theme-accent", "--theme-accent-ink", "--theme-paper"):
            self.assertIn(variable, css + runtime)
        for token in ("min-height:44px", "max-height:55dvh", "overflow:auto"):
            self.assertIn(token, runtime)
        for token in (".month-timeline{", ".month-jump{", "min-width:44px", "overflow-x:auto"):
            self.assertIn(token, runtime)
        for selector in (".cloth{", ".feat-reason{", ".routecircle{"):
            self.assertIn(selector, css)
        self.assertNotIn(".photo-kicker{", css)


if __name__ == "__main__":
    unittest.main()
