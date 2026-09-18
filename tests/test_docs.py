import unittest
from pathlib import Path


class BeginnerDocsTests(unittest.TestCase):
    def test_setup_covers_complete_first_run(self):
        text = Path("docs/setup.md").read_text("utf-8")
        for phrase in (
            "Python 3", "Strava API", "Authorization Callback Domain", "github-auth",
            "publish 2026", "预期", "常见问题", "公开",
        ):
            self.assertIn(phrase, text)

    def test_docs_explain_theme_switching_and_reset(self):
        setup = Path("docs/setup.md").read_text("utf-8")
        readme = Path("README.md").read_text("utf-8")
        for phrase in ("19 种主题", "黑白橙", "自动保存", "strava-photobook.theme"):
            self.assertIn(phrase, setup + readme)


if __name__ == "__main__":
    unittest.main()
