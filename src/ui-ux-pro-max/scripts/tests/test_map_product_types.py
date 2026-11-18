"""Map products route to the GIS and Earth-observation product types."""

from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
from core import search  # noqa: E402
from design_system import DesignSystemGenerator  # noqa: E402

GIS = "GIS / Web Map Dashboard"
EO = "Earth Observation / Satellite Imagery Viewer"

PRODUCT_QUERIES = {
    "GIS dashboard web map": GIS,
    "flood monitoring map dashboard": GIS,
    "geospatial analytics platform": GIS,
    "webgis maplibre": GIS,
    "satellite imagery viewer earth observation": EO,
    "remote sensing ndvi change detection": EO,
}

# Neighbouring product types must keep their own queries.
NEIGHBOUR_QUERIES = {
    "analytics dashboard": "Analytics Dashboard",
    "delivery tracking": "Logistics/Delivery",
    "public transit": "Public Transit Guide",
    "drone fleet": "Autonomous Drone Fleet Manager",
    "podcast platform": "Podcast Platform",
}


class TestMapProductTypes(unittest.TestCase):
    def test_map_queries_route_to_the_map_product_types(self):
        for query, product in PRODUCT_QUERIES.items():
            with self.subTest(query=query):
                result = search(query, domain="product", max_results=3)
                self.assertEqual(product, result["results"][0]["Product Type"])

    def test_neighbour_queries_keep_their_product_type(self):
        for query, product in NEIGHBOUR_QUERIES.items():
            with self.subTest(query=query):
                result = search(query, domain="product", max_results=3)
                self.assertEqual(product, result["results"][0]["Product Type"])

    def test_reasoning_requires_attribution_and_avoids_rainbow_ramps(self):
        generator = DesignSystemGenerator()
        for category in (GIS, EO):
            with self.subTest(category=category):
                rule = generator._find_reasoning_rule(category)
                self.assertEqual(category, rule["UI_Category"])
                self.assertIn("constraint:map-attribution", rule["Decision_Rules"])
                self.assertIn("rainbow", rule["Anti_Patterns"])


if __name__ == "__main__":
    unittest.main()
