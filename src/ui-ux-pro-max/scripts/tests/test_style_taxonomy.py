#!/usr/bin/env python3
"""Regression tests for the public style taxonomy and search contract."""

import csv
import json
import statistics
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = SCRIPTS_DIR.parent / "data"
sys.path.insert(0, str(SCRIPTS_DIR))

from core import search  # noqa: E402
from design_system import _style_is_dark_primary  # noqa: E402


def read_rows(name):
    with (DATA_DIR / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class TestStyleTaxonomy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.styles = read_rows("styles.csv")
        cls.by_id = {row["Style ID"]: row for row in cls.styles}

    def test_curated_state_distribution_is_explicit(self):
        counts = {
            status: sum(row["Status"] == status for row in self.styles)
            for status in ("active", "supplemental", "deprecated")
        }
        self.assertEqual(
            {"active": 50, "supplemental": 29, "deprecated": 9}, counts
        )

    def test_every_style_name_and_alias_has_a_deterministic_destination(self):
        for row in self.styles:
            queries = [row["Style Category"]]
            queries.extend(alias for alias in row["Aliases"].split("|") if alias)
            for query in queries:
                with self.subTest(style=row["Style ID"], query=query):
                    result = search(query, max_results=1)
                    if (row["Status"] == "deprecated"
                            and row["Replacement Domain"] == "landing"):
                        self.assertEqual(0, result["count"])
                        self.assertEqual(
                            {
                                "domain": row["Replacement Domain"],
                                "id": row["Replacement ID"],
                            },
                            result.get("redirect"),
                        )
                    else:
                        expected_id = (
                            row["Replacement ID"]
                            if row["Status"] == "deprecated"
                            else row["Style ID"]
                        )
                        self.assertEqual(expected_id, result["results"][0]["Style ID"])

    def test_deprecated_rows_never_appear_in_generic_results(self):
        for query in ("modern interface", "marketing page", "trust design"):
            with self.subTest(query=query):
                result = search(query, domain="style", max_results=20)
                self.assertLessEqual(
                    {row["Status"] for row in result["results"]}, {"active"}
                )

    def test_style_arbitration_does_not_steal_product_intent(self):
        result = search("design a financial dashboard for my bank", max_results=1)
        self.assertEqual("product", result["domain"])

    def test_family_variants_and_mobile_intent_remain_distinct(self):
        expected_parents = {
            "gradient-mesh-aurora-evolved": "aurora-ui",
            "swiss-modernism-2-0": "minimalism-and-swiss-style",
            "neumorphism-mobile": "neumorphism",
            "claymorphism-mobile": "claymorphism",
            "spectrum-2": "spectrum-design-system",
        }
        for style_id, parent_id in expected_parents.items():
            with self.subTest(style=style_id):
                row = self.by_id[style_id]
                self.assertEqual(parent_id, row["Parent Style ID"])
                self.assertIn(row["Status"], {"supplemental", "deprecated"})

        self.assertEqual("style", self.by_id["bento-grids"]["Replacement Domain"])
        self.assertEqual(
            "bento-box-grid", self.by_id["bento-grids"]["Replacement ID"]
        )

        self.assertEqual(
            "neumorphism-mobile",
            search("Neumorphism (Mobile)", "style", 1)["results"][0]["Style ID"],
        )
        self.assertEqual(
            "claymorphism-mobile",
            search("Claymorphism (Mobile)", "style", 1)["results"][0]["Style ID"],
        )
        self.assertEqual(
            "material-you-md3-mobile",
            search("M3 Expressive", "style", 1)["results"][0]["Style ID"],
        )
        self.assertEqual(
            "neumorphism-mobile",
            search("mobile neumorphism UI", "style", 1)["results"][0]["Style ID"],
        )
        self.assertEqual(
            "claymorphism-mobile",
            search("mobile app with claymorphism", "style", 1)["results"][0]["Style ID"],
        )
        self.assertEqual(
            "spectrum-2",
            search("design system for Spectrum 2", "style", 1)["results"][0]["Style ID"],
        )

    def test_claim_fields_use_controlled_non_guarantee_language(self):
        allowed_performance = {"cost:low", "cost:moderate", "cost:high"}
        allowed_accessibility = {"risk:low", "risk:conditional", "risk:high"}
        allowed_mode = {"supported", "conditional", "not-recommended"}
        for row in self.styles:
            with self.subTest(style=row["Style ID"]):
                self.assertIn(row["Performance"].split("|", 1)[0], allowed_performance)
                self.assertIn(row["Accessibility"].split("|", 1)[0], allowed_accessibility)
                self.assertIn(row["Light Mode ✓"], allowed_mode)
                self.assertIn(row["Dark Mode ✓"], allowed_mode)
                self.assertIn(row["Preferred Mode"], {"auto", "light", "dark"})
                claim_text = " ".join(row.values())
                self.assertNotRegex(claim_text, r"(?i)\bWCAG\s+A{2,3}\+?\b")
                self.assertNotRegex(
                    claim_text,
                    r"(?i)\bWCAG\b.{0,40}\b(?:compliant|compliance)\b",
                )
                self.assertNotRegex(row["Framework Compatibility"], r"\d+/10")

        self.assertTrue(_style_is_dark_primary(self.by_id["dark-mode-oled"]))
        self.assertFalse(
            _style_is_dark_primary(self.by_id["minimalism-and-swiss-style"])
        )

    def test_searchable_prompt_lengths_are_balanced(self):
        lengths_by_type = {}
        for row in self.styles:
            length = len(row["AI Prompt Keywords"].split())
            self.assertLessEqual(length, 40, row["Style ID"])
            lengths_by_type.setdefault(row["Type"], []).append(length)
        general_median = statistics.median(lengths_by_type["General"])
        mobile_median = statistics.median(lengths_by_type["Mobile"])
        self.assertLessEqual(mobile_median, general_median * 1.6)

    def test_new_rows_have_first_party_provenance(self):
        payload = json.loads(
            (DATA_DIR / "data-provenance.json").read_text(encoding="utf-8")
        )
        records = {
            record["entityId"]: record
            for record in payload["records"]
            if record["entityKind"] == "style"
        }
        new_rows = [row for row in self.styles if int(row["No"]) > 85]
        self.assertGreaterEqual(len(new_rows), 4)
        for row in new_rows:
            with self.subTest(style=row["Style ID"]):
                record = records[row["Style ID"]]
                self.assertTrue(record["sources"])
                self.assertTrue(
                    any(source["type"] == "official" for source in record["sources"])
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
