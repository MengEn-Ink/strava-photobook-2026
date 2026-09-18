import tempfile
import unittest
from pathlib import Path

from PIL import Image

from strava_photobook.config import Config, GitHubConfig, StravaCreds
from strava_photobook.model import Activity
from strava_photobook.source import fetch_activities, hydrate_activity


class EmptyPhotoClient:
    def activity_detail(self, activity_id):
        return {}

    def activity_photos(self, activity_id, size=2000):
        return []


class ActivityListClient:
    def __init__(self):
        self.calls = []

    def iter_activities(self, **kwargs):
        self.calls.append(kwargs)
        yield {"id": 1, "start_date_local": "2026-01-01T00:00:00Z", "map": {}}


class PhotoCacheTests(unittest.TestCase):
    def test_fetch_can_limit_list_requests_to_one_year(self):
        with tempfile.TemporaryDirectory() as raw_root:
            root = Path(raw_root)
            runtime = root / "runtime"
            runtime.mkdir()
            cfg = Config(root, root / "data", root / "books", runtime, StravaCreds(), GitHubConfig())
            client = ActivityListClient()

            fetch_activities(cfg, year="2026", client=client)

            kwargs = client.calls[0]
            self.assertEqual(kwargs["after"], 1767225600)
            self.assertEqual(kwargs["before"], 1798761600)

    def test_hydrate_uses_cached_activity_photos_when_api_returns_none(self):
        with tempfile.TemporaryDirectory() as raw_root:
            root = Path(raw_root)
            runtime = root / "runtime"
            runtime.mkdir()
            cache = root / "data" / "photo-cache"
            cache.mkdir(parents=True)
            Image.new("RGB", (800, 600), "blue").save(cache / "42-00.jpg")
            out = root / "book" / "assets" / "photos"
            cfg = Config(root, root / "data", root / "books", runtime, StravaCreds(), GitHubConfig())
            activity = Activity(
                id="42", name="Cached Ride", date="2026-01-02T08:00:00Z",
                year="2026", photo_count=1,
            )

            hydrate_activity(cfg, EmptyPhotoClient(), activity, out, 1)

            self.assertEqual([photo.web_path for photo in activity.photos], ["assets/photos/42-00.jpg"])
            self.assertTrue(activity.photos[0].landscape)
            self.assertTrue((out / "42-00.jpg").is_file())


if __name__ == "__main__":
    unittest.main()
