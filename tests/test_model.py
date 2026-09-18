import unittest

from strava_photobook.model import Activity, select_editorial_highlights


def ride(identifier, name, month, **values):
    return Activity(id=identifier, name=name, date=f"2026-{month:02d}-01T08:00:00Z", year="2026", **values)


class EditorialSelectionTests(unittest.TestCase):
    def test_photo_story_outranks_bare_kudos_when_signals_are_close(self):
        bare = ride("1", "Morning Ride", 1, kudos=60)
        story = ride("2", "Mountain Story", 2, kudos=52, photo_count=5, description="A memorable mountain day", pr_count=3)
        selected = select_editorial_highlights([bare, story], limit=1)
        self.assertEqual(selected[0].activity.id, "2")
        self.assertIn("照片", selected[0].reason)

    def test_selection_spreads_months_and_repeated_titles(self):
        rides = [
            ride("1", "黑分解 Ride", 4, kudos=70, photo_count=3),
            ride("2", "黑分解Ride", 4, kudos=69, photo_count=3),
            ride("3", "雨战百里画廊", 8, kudos=60, photo_count=4, description="雨中骑完百里"),
        ]
        selected = select_editorial_highlights(rides, limit=2)
        self.assertEqual([x.activity.id for x in selected], ["3", "1"])

    def test_reason_can_explain_pr_highlight(self):
        selected = select_editorial_highlights([ride("1", "Race", 9, pr_count=12, photo_count=1)], limit=1)
        self.assertIn("PR", selected[0].reason)


if __name__ == "__main__":
    unittest.main()
