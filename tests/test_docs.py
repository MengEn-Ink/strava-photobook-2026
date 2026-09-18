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


if __name__ == "__main__":
    unittest.main()
