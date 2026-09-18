import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from strava_photobook.config import Config
from strava_photobook.github.client import GitHubAPIError, GitHubClient


class GitHubConfigTests(unittest.TestCase):
    def test_gh_token_overrides_dotenv_github_token(self):
        with tempfile.TemporaryDirectory() as raw_root:
            root = Path(raw_root)
            (root / ".env").write_text(
                "GITHUB_TOKEN=stored-token\nGITHUB_CLIENT_ID=client-123\n", encoding="utf-8"
            )
            with patch.dict(os.environ, {"GH_TOKEN": "automation-token"}, clear=True):
                cfg = Config.load(root)

            self.assertEqual(cfg.github.token, "automation-token")
            self.assertEqual(cfg.github.client_id, "client-123")
            self.assertEqual(cfg.github.api_url, "https://api.github.com")
            self.assertNotIn("automation-token", repr(cfg.github))

    def test_missing_token_is_empty(self):
        with tempfile.TemporaryDirectory() as raw_root:
            with patch.dict(os.environ, {}, clear=True):
                cfg = Config.load(raw_root)
            self.assertEqual(cfg.github.token, "")


class _Response:
    def __init__(self, status, payload=None, text=""):
        self.status_code = status
        self._payload = payload
        self.text = text

    def json(self):
        return self._payload


class _Session:
    def __init__(self, response):
        self.response = response
        self.last = None

    def request(self, **kwargs):
        self.last = kwargs
        return self.response


class GitHubClientTests(unittest.TestCase):
    def test_request_adds_auth_and_returns_json(self):
        session = _Session(_Response(200, {"login": "alice"}))
        client = GitHubClient("secret-token", session=session)
        self.assertEqual(client.request("GET", "/user"), {"login": "alice"})
        self.assertEqual(session.last["headers"]["Authorization"], "Bearer secret-token")

    def test_error_is_sanitized(self):
        session = _Session(_Response(403, {"message": "denied"}, "secret-token"))
        client = GitHubClient("secret-token", session=session)
        with self.assertRaises(GitHubAPIError) as caught:
            client.request("GET", "/user")
        self.assertIn("denied", str(caught.exception))
        self.assertNotIn("secret-token", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
