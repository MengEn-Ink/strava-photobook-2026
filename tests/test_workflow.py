import unittest
from pathlib import Path


class NightlyWorkflowTests(unittest.TestCase):
    def test_nightly_workflow_has_safe_refresh_and_publish_contract(self):
        text = Path(".github/workflows/nightly-photobook.yml").read_text(encoding="utf-8")
        for token in (
            "cron: '0 13 * * *'",
            "workflow_dispatch:",
            "contents: write",
            "cancel-in-progress: true",
            "STRAVA_CLIENT_ID",
            "STRAVA_CLIENT_SECRET",
            "STRAVA_REFRESH_TOKEN",
            "SECRETS_ADMIN_TOKEN",
            "Retry Strava fetch after rate limit",
            "900 - $(date +%s) % 900 + 60",
            "if: always()",
            "tools/validate_release.py",
            "--require-heatmap",
            "refs/heads/gh-pages",
        ):
            self.assertIn(token, text)
        self.assertLess(text.index("tools/validate_release.py"), text.index("refs/heads/gh-pages"))


if __name__ == "__main__":
    unittest.main()
