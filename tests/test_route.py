import unittest

from strava_photobook.route import route_heatmap_svg


class RouteHeatmapTests(unittest.TestCase):
    def test_combines_valid_routes_with_theme_aware_layers(self):
        demo = "_p~iF~ps|U_ulLnnqC_mqNvxq`@"
        rendered = route_heatmap_svg([demo, demo])

        self.assertIn('class="route-heatmap"', rendered)
        self.assertEqual(rendered.count('class="heat-route base"'), 2)
        self.assertEqual(rendered.count('class="heat-route hot"'), 2)
        self.assertIn('var(--theme-primary)', rendered)
        self.assertIn('var(--theme-accent)', rendered)

    def test_skips_malformed_routes_and_returns_empty_without_valid_data(self):
        demo = "_p~iF~ps|U_ulLnnqC_mqNvxq`@"

        self.assertEqual(route_heatmap_svg(["broken", ""]), "")
        self.assertEqual(route_heatmap_svg(["broken", demo]).count('class="heat-route hot"'), 1)

    def test_limits_each_route_for_a_compact_static_page(self):
        # Repeating a valid three-point polyline creates a long decoded route.
        rendered = route_heatmap_svg(["_p~iF~ps|U_ulLnnqC_mqNvxq`@" * 120])
        hot_path = rendered.split('class="heat-route hot"', 1)[1].split('/>', 1)[0]
        self.assertLessEqual(hot_path.count(" L") + 1, 180)

    def test_keeps_the_dominant_region_readable_when_one_route_is_remote(self):
        beijing_a = "_p~iF~ps|U_ulLnnqC_mqNvxq`@"
        beijing_b = "_p~iF~ps|U_ulLnnqC_mqNvxq`@"
        remote = "_ibE_seK_seK_seK"

        rendered = route_heatmap_svg([beijing_a, beijing_b, remote])

        self.assertIn('data-plotted-routes="2"', rendered)
        self.assertIn('data-remote-routes="1"', rendered)
        self.assertEqual(rendered.count('class="heat-route hot"'), 2)


if __name__ == "__main__":
    unittest.main()
