import unittest

from strava_photobook.editorial import build_year_review, select_cover
from strava_photobook.model import Activity, Photo


def ride(identifier, month, *, name="Ride", **values):
    return Activity(
        id=identifier, name=name, date=f"2026-{month:02d}-01T08:00:00Z", year="2026",
        **values,
    )


class CoverSelectionTests(unittest.TestCase):
    def test_prefers_landscape_photo_from_stronger_activity(self):
        portrait = ride("1", 4, kudos=80, photos=[Photo("portrait.jpg", landscape=False)])
        landscape = ride(
            "2", 5, name="Mountain Classic", kudos=65, pr_count=5,
            distance_km=160, elev_m=1900, photos=[Photo("landscape.jpg", landscape=True)],
        )

        selected = select_cover([portrait, landscape])

        self.assertEqual(selected.photo.web_path, "landscape.jpg")
        self.assertEqual(selected.activity.name, "Mountain Classic")
        self.assertEqual(selected.object_position, "center")

    def test_equal_scores_are_stable_by_newer_date_then_id(self):
        older = ride("9", 4, photos=[Photo("older.jpg", landscape=True)])
        newer = ride("2", 6, photos=[Photo("newer.jpg", landscape=True)])
        self.assertEqual(select_cover([older, newer]).photo.web_path, "newer.jpg")

    def test_returns_none_without_photos(self):
        self.assertIsNone(select_cover([ride("1", 1)]))


class YearReviewTests(unittest.TestCase):
    def test_builds_monthly_rhythm_and_records(self):
        activities = [
            ride("jan", 1, name="Short", distance_km=20, elev_m=200, moving_time=3600, kudos=5, pr_count=1),
            ride("aug-a", 8, name="Longest Story", distance_km=175, elev_m=2200, moving_time=7200, kudos=10, pr_count=3),
            ride("aug-b", 8, distance_km=25, elev_m=300, moving_time=1800, kudos=7, pr_count=2),
        ]

        review = build_year_review(activities)

        self.assertEqual([(m.month, m.distance_km) for m in review.months], [(1, 20), (8, 200)])
        self.assertEqual(review.active_months, 2)
        self.assertEqual(review.peak_month.month, 8)
        self.assertEqual(review.longest_ride.name, "Longest Story")
        self.assertEqual(review.moving_hours, 4)
        self.assertEqual(review.kudos, 22)
        self.assertEqual(review.pr_count, 6)


if __name__ == "__main__":
    unittest.main()
