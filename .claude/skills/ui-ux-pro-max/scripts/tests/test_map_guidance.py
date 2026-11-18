"""Retrieve the web map guidelines and keep generic queries on generic rows."""

import csv
from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
from core import search  # noqa: E402

DATA = SCRIPTS.parent / "data"

MAP_QUERIES = {
    "map attribution": "Map Attribution Visible",
    "hide mapbox logo": "Map Attribution Visible",
    "map screen reader text alternative": "Map Text Alternative",
    "map keyboard pan zoom": "Map Keyboard and Non-Drag Navigation",
    "map markers color alone": "Map Symbology Not Color Alone",
    "choropleth raw counts": "Normalized Choropleth Map",
    "rainbow map color ramp": "Perceptual Map Color Ramps",
    "map popup xss": "Safe Map Popup Content",
    "cluster map points": "Cluster Dense Map Points",
    "large geojson": "Large Geodata as Vector Tiles",
    "map flyTo reduced motion": "Map Camera Reduced Motion",
}

# Generic questions must keep returning the general guideline first.
GENERIC_QUERIES = {
    "color alone": "Color Only",
    "keyboard navigation": "Keyboard Navigation",
    "reduced motion": "Reduced Motion",
    "dragging movements": "Dragging Movements",
}


class TestMapGuidance(unittest.TestCase):
    def test_map_queries_retrieve_the_map_row_first(self):
        for query, issue in MAP_QUERIES.items():
            with self.subTest(query=query):
                result = search(query, domain="ux", max_results=3)
                self.assertEqual(issue, result["results"][0]["Issue"])

    def test_generic_queries_keep_the_generic_row_first(self):
        for query, issue in GENERIC_QUERIES.items():
            with self.subTest(query=query):
                result = search(query, domain="ux", max_results=3)
                self.assertEqual(issue, result["results"][0]["Issue"])

    def test_map_rows_are_complete(self):
        with (DATA / "ux-guidelines.csv").open(encoding="utf-8", newline="") as handle:
            rows = [row for row in csv.DictReader(handle) if row["Category"] == "Maps"]
        self.assertEqual(set(MAP_QUERIES.values()), {row["Issue"] for row in rows})
        for row in rows:
            with self.subTest(issue=row["Issue"]):
                self.assertEqual("Web", row["Platform"])
                self.assertIn(row["Severity"], {"Critical", "High", "Medium"})
                for field in ("Description", "Do", "Don't",
                              "Code Example Good", "Code Example Bad"):
                    self.assertTrue(row[field].strip(), field)

    def test_geographic_chart_requires_normalized_choropleths(self):
        with (DATA / "charts.csv").open(encoding="utf-8", newline="") as handle:
            row, = [row for row in csv.DictReader(handle)
                    if row["Data Type"] == "Geographic Data"]
        self.assertIn("normalized", row["Color Guidance"])
        self.assertIn("proportional symbols", row["When NOT to Use"])

    def test_quick_references_include_the_map_rules(self):
        repo = next((parent for parent in SCRIPTS.parents
                     if (parent / "src/ui-ux-pro-max/templates/base").is_dir()), None)
        if not repo:
            self.skipTest("Repository quick references are not installed with scripts")
        for relative in (
            Path("src/ui-ux-pro-max/templates/base/quick-reference.md"),
            Path("cli/assets/templates/base/quick-reference.md"),
            Path(".claude", "skills", "ui-ux-pro-max", "references", "quick-reference.md"),
        ):
            with self.subTest(path=relative):
                text = (repo / relative).read_text(encoding="utf-8")
                for rule_id in ("`map-attribution`", "`normalized-choropleth`",
                                "`map-popup-text`"):
                    self.assertTrue(rule_id in text, f"{rule_id} missing from {relative}")


if __name__ == "__main__":
    unittest.main()
