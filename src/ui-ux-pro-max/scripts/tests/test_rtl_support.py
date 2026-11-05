#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RTL support contracts: rtl_level data, --rtl filtering, and CLI wiring.

The filter must run before BM25 ranking and before max_results truncation --
otherwise `--rtl=full -n 1` can report zero results while compatible rows
exist. These tests pin that behaviour plus the data contract.

Run with:
    python -m unittest discover -s scripts/tests -v
"""

import csv
import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = SCRIPTS_DIR.parent / "data"
sys.path.insert(0, str(SCRIPTS_DIR))

from core import CSV_CONFIG, RTL_LEVELS, search  # noqa: E402

RTL_COLUMN = "rtl_level"
RTL_DOMAINS = ("style", "product")


def read_rows(name):
    with (DATA_DIR / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class RtlDataContractTest(unittest.TestCase):
    def test_both_domains_declare_rtl_level_in_output_columns(self):
        for domain in RTL_DOMAINS:
            self.assertIn(RTL_COLUMN, CSV_CONFIG[domain]["output_cols"], domain)
            self.assertNotIn(
                RTL_COLUMN, CSV_CONFIG[domain]["search_cols"],
                f"{domain}: rtl_level is metadata, not a search signal",
            )

    def test_every_row_declares_a_supported_rtl_level(self):
        for name in ("styles.csv", "products.csv"):
            rows = read_rows(name)
            self.assertTrue(rows, name)
            missing = [row["No"] for row in rows if not row.get(RTL_COLUMN)]
            invalid = sorted({
                row.get(RTL_COLUMN) for row in rows
                if row.get(RTL_COLUMN) and row[RTL_COLUMN] not in RTL_LEVELS
            })
            self.assertEqual([], missing, f"{name}: rows without rtl_level")
            self.assertEqual([], invalid, f"{name}: unsupported rtl_level values")

    def test_known_layouts_keep_their_expected_level(self):
        expected_styles = {
            "apple-native-experience": "full",
            "minimalism-and-swiss-style": "full",
            "data-dense-dashboard": "partial",
            "kinetic-typography": "caveats",
            "terminal-cli-mobile": "caveats",
            "editorial-grid-magazine": "caveats",
            "fluent-2": "full",
        }
        styles = {row["Style ID"]: row for row in read_rows("styles.csv")}
        for style_id, level in expected_styles.items():
            self.assertIn(style_id, styles)
            self.assertEqual(level, styles[style_id][RTL_COLUMN], style_id)

        expected_products = {
            "Hotel/Hospitality": "full",
            "Financial Dashboard": "partial",
            "Developer Tool / IDE": "caveats",
            "Calendar & Scheduling App": "caveats",
        }
        products = {row["Product Type"]: row for row in read_rows("products.csv")}
        for product_type, level in expected_products.items():
            self.assertIn(product_type, products)
            self.assertEqual(level, products[product_type][RTL_COLUMN], product_type)


class RtlFilterTest(unittest.TestCase):
    def test_rtl_all_returns_results_for_every_level(self):
        result = search("mobile", "style", 20, rtl="all")
        self.assertGreater(result["count"], 0)
        levels = {row[RTL_COLUMN] for row in result["results"]}
        self.assertGreater(len(levels), 1, levels)

    def test_rtl_level_is_projected_into_results(self):
        result = search("dashboard", "style", 1, rtl="partial")
        self.assertEqual(1, result["count"])
        self.assertEqual("partial", result["results"][0][RTL_COLUMN])
        unfiltered = search("dashboard", "style", 1)
        self.assertIn(RTL_COLUMN, unfiltered["results"][0])

    def test_rtl_level_filter_matches_the_csv(self):
        for domain, query in (("style", "mobile"), ("product", "hotel")):
            for level in ("full", "partial", "caveats"):
                expected = {
                    row.get("Style ID") or row.get("Product Type")
                    for row in read_rows(CSV_CONFIG[domain]["file"])
                    if row.get(RTL_COLUMN) == level
                }
                result = search(query, domain, 20, rtl=level)
                for row in result["results"]:
                    self.assertEqual(level, row[RTL_COLUMN])
                    identity = row.get("Style ID") or row.get("Product Type")
                    self.assertIn(identity, expected)

    def test_filter_runs_before_result_truncation(self):
        """A narrow max_results must not hide the only matching row."""
        unfiltered = search("saas", "product", 1)
        self.assertEqual("partial", unfiltered["results"][0][RTL_COLUMN])
        filtered = search("saas", "product", 1, rtl="full")
        self.assertEqual(1, filtered["count"])
        self.assertEqual("full", filtered["results"][0][RTL_COLUMN])

    def test_omitting_rtl_keeps_previous_behaviour(self):
        without_rtl = search("mobile", "style", 3)
        with_all = search("mobile", "style", 3, rtl="all")
        self.assertEqual(
            [row["Style ID"] for row in without_rtl["results"]],
            [row["Style ID"] for row in with_all["results"]],
        )

    def test_rtl_rejects_domains_without_the_column(self):
        for domain in ("color", "ux", "typography", "chart", None):
            with self.assertRaises(ValueError):
                search("blue", domain, 3, rtl="full")


class RtlCliTest(unittest.TestCase):
    def run_search(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "search.py"), *args],
            capture_output=True, text=True, encoding="utf-8",
        )

    def test_cli_flag_filters_json_results(self):
        completed = self.run_search(
            "saas", "--domain", "product", "--rtl=full", "-n", "1", "--json",
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(1, payload["count"])
        self.assertEqual("full", payload["results"][0][RTL_COLUMN])

    def test_cli_flag_without_value_accepts_every_level(self):
        completed = self.run_search(
            "mobile", "--domain", "style", "--rtl", "-n", "20", "--json",
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertGreater(len({row[RTL_COLUMN] for row in payload["results"]}), 1)

    def test_cli_rejects_unsupported_domain(self):
        completed = self.run_search("blue", "--domain", "color", "--rtl", "--json")
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("style", completed.stderr)
        self.assertIn("product", completed.stderr)


if __name__ == "__main__":
    unittest.main()
