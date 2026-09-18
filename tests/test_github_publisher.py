import tempfile
import unittest
from pathlib import Path

from strava_photobook.github.publisher import Publisher, PublishError
from strava_photobook.github.client import GitHubAPIError


class FakeClient:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def request(self, method, path, **kwargs):
        self.calls.append((method, path, kwargs))
        value = self.responses[(method, path)]
        return value() if callable(value) else value


class PublisherTests(unittest.TestCase):
    def test_refuses_unmarked_existing_repository(self):
        client = FakeClient({
            ("GET", "/user"): {"login": "alice"},
            ("GET", "/repos/alice/book"): {"name": "book", "owner": {"login": "alice"}, "description": "mine"},
        })
        with tempfile.TemporaryDirectory() as root:
            Path(root, "index.html").write_text('<html data-strava-photobook="1">', encoding="utf-8")
            with self.assertRaises(PublishError):
                Publisher(client, sleeper=lambda _: None).publish(Path(root), "book")

    def test_publishes_and_verifies_new_repository(self):
        responses = {
            ("GET", "/user"): {"login": "alice"},
            ("GET", "/repos/alice/book"): None,
            ("POST", "/user/repos"): {"name": "book", "html_url": "https://github.com/alice/book", "owner": {"login": "alice"}, "description": "[strava-photobook]"},
            ("GET", "/repos/alice/book/git/ref/heads/gh-pages"): None,
            ("POST", "/repos/alice/book/git/blobs"): {"sha": "blob"},
            ("POST", "/repos/alice/book/git/trees"): {"sha": "tree"},
            ("POST", "/repos/alice/book/git/commits"): {"sha": "commit"},
            ("POST", "/repos/alice/book/git/refs"): {},
            ("GET", "/repos/alice/book/pages"): None,
            ("POST", "/repos/alice/book/pages"): {"html_url": "https://alice.github.io/book/"},
            ("GET", "/repos/alice/book/pages/builds/latest"): {"status": "built"},
        }
        client = FakeClient(responses)
        with tempfile.TemporaryDirectory() as root:
            Path(root, "index.html").write_text('<html data-strava-photobook="1">', encoding="utf-8")
            publisher = Publisher(client, sleeper=lambda _: None, public_fetch=lambda _: '<html data-strava-photobook="1">')
            result = publisher.publish(Path(root), "book")
        self.assertEqual(result.commit_sha, "commit")
        self.assertEqual(result.pages_url, "https://alice.github.io/book/")

    def test_rejects_oversized_file_before_remote_write(self):
        client = FakeClient({("GET", "/user"): {"login": "alice"}})
        with tempfile.TemporaryDirectory() as root:
            Path(root, "index.html").write_text('<html data-strava-photobook="1">', encoding="utf-8")
            Path(root, "large.bin").write_bytes(b"12345")
            with self.assertRaises(PublishError):
                Publisher(client, upload_limit_bytes=4).publish(Path(root), "book")

    def test_empty_repository_409_is_treated_as_missing_pages_ref(self):
        class EmptyRepoClient(FakeClient):
            initialized = False

            def request(self, method, path, **kwargs):
                if path.endswith("/git/ref/heads/gh-pages") and not self.initialized:
                    raise GitHubAPIError(409, method, path, "Git Repository is empty")
                if path.endswith("/contents/.strava-photobook"):
                    self.initialized = True
                    return {"commit": {"sha": "bootstrap"}}
                return super().request(method, path, **kwargs)

        client = EmptyRepoClient({
            ("POST", "/repos/alice/book/git/blobs"): {"sha": "blob"},
            ("POST", "/repos/alice/book/git/trees"): {"sha": "tree"},
            ("POST", "/repos/alice/book/git/commits"): {"sha": "commit"},
            ("POST", "/repos/alice/book/git/refs"): {},
            ("GET", "/repos/alice/book/git/ref/heads/main"): {"object": {"sha": "bootstrap"}},
        })
        with tempfile.TemporaryDirectory() as root:
            Path(root, "index.html").write_text('<html data-strava-photobook="1">', encoding="utf-8")
            sha = Publisher(client)._publish_branch(Path(root), [Path(root, "index.html")], "alice", "book")
        self.assertEqual(sha, "commit")
        self.assertTrue(client.initialized)

    def test_pages_create_conflict_is_reconciled_by_reading_site(self):
        class ConflictClient(FakeClient):
            def request(self, method, path, **kwargs):
                if method == "GET" and path.endswith("/pages") and not self.calls:
                    self.calls.append((method, path, kwargs))
                    raise GitHubAPIError(404, method, path, "Not Found")
                if method == "POST" and path.endswith("/pages"):
                    raise GitHubAPIError(409, method, path, "GitHub Pages is already enabled")
                return super().request(method, path, **kwargs)

        path = "/repos/alice/book/pages"
        client = ConflictClient({
            ("GET", path): {"html_url": "https://alice.github.io/book/", "source": {"branch": "gh-pages", "path": "/"}},
        })
        url = Publisher(client)._ensure_pages("alice", "book")
        self.assertEqual(url, "https://alice.github.io/book/")
