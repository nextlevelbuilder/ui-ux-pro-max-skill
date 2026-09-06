#!/usr/bin/env python3
"""Canonical regression contracts for resilient UI text layouts."""

import csv
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = SCRIPTS_DIR.parent / "data"
sys.path.insert(0, str(SCRIPTS_DIR))

from core import search, search_stack  # noqa: E402


def read_rows(relative_path):
    with (DATA_DIR / relative_path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


UX_PHRASES = {
    "Heading Line Balance": ("progressive visual heuristic", "natural-wrap fallback"),
    "Long Token Wrapping": ("overflow-wrap anywhere", "text children shrink"),
    "Text Reflow and Spacing": ("narrow widths zoom", "content-driven height"),
    "Essential Text Truncation": ("complete access", "visible full-detail path"),
    "Compact Label Semantics": ("badges communicate state", "meaning and ownership"),
    "Chip Collection Reflow": ("filter chips", "operable +n disclosure"),
    "Compact Label Overflow": ("stay whole on one line", "keyboard pointer and touch"),
    "Compact Control Semantics": ("native role", "pressed or selected state"),
    "Contextual Live Badge Updates": ("meaningful contextual status", "atomic status"),
    "Cancellable State Transitions": ("interrupt an in-flight transition", "final semantic state"),
}

TAILWIND_PHRASES = {
    "Balanced heading wrapping": ("text-balance", "natural wrapping fallback"),
    "Long token resilience": ("wrap-anywhere", "min-w-0"),
    "Compact label layout": ("flex flex-wrap gap-2", "whitespace-nowrap", "shrink-0"),
}


class TestTextLayoutRetrieval(unittest.TestCase):
    def test_locked_queries_return_the_canonical_identity_first(self):
        cases = (
            ("orphan heading line balance", "Heading Line Balance"),
            ("long url token breaks layout", "Long Token Wrapping"),
            ("badge chip label wraps to second line", "Compact Label Overflow"),
            ("filter chip collection reflow hidden values", "Chip Collection Reflow"),
            ("live badge count screen reader", "Contextual Live Badge Updates"),
            ("rapid chip animation interrupted", "Cancellable State Transitions"),
        )
        for query, expected in cases:
            with self.subTest(query=query):
                result = search(query, domain="ux", max_results=3, diagnostics=True)
                actual = [row.get("Issue") for row in result["results"]]
                self.assertTrue(actual, result.get("diagnostics"))
                self.assertEqual(expected, actual[0], f"ranking={actual!r}")

    def test_tailwind_query_returns_compact_label_layout_first(self):
        result = search_stack(
            "chip badge overflow nowrap", "html-tailwind",
            max_results=3, diagnostics=True,
        )
        actual = [row.get("Guideline") for row in result["results"]]
        self.assertTrue(actual, result.get("diagnostics"))
        self.assertEqual("Compact label layout", actual[0], f"ranking={actual!r}")


class TestTextLayoutDataContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ux = read_rows("ux-guidelines.csv")
        cls.tailwind = read_rows("stacks/html-tailwind.csv")

    def test_new_ux_rows_are_unique_sequential_and_keep_critical_guidance(self):
        matches = [row for row in self.ux if row["Issue"] in UX_PHRASES]
        self.assertEqual(len(UX_PHRASES), len(matches))
        self.assertEqual(len(matches), len({row["Issue"] for row in matches}))
        self.assertEqual(list(range(110, 120)), [int(row["No"]) for row in matches])
        for row in matches:
            with self.subTest(issue=row["Issue"]):
                text = " ".join(row.values()).casefold()
                for phrase in UX_PHRASES[row["Issue"]]:
                    self.assertIn(phrase.casefold(), text)
                self.assertIn(row["Severity"], {"Medium", "High", "Critical"})

    def test_new_tailwind_rows_are_unique_current_and_keep_required_utilities(self):
        matches = [row for row in self.tailwind if row["Guideline"] in TAILWIND_PHRASES]
        self.assertEqual(len(TAILWIND_PHRASES), len(matches))
        self.assertEqual(len(matches), len({row["Guideline"] for row in matches}))
        self.assertEqual([57, 58, 59], [int(row["No"]) for row in matches])
        for row in matches:
            with self.subTest(guideline=row["Guideline"]):
                text = " ".join(row.values()).casefold()
                for phrase in TAILWIND_PHRASES[row["Guideline"]]:
                    self.assertIn(phrase.casefold(), text)
                self.assertEqual("active", row["Status"])
                self.assertEqual("html-tailwind 4.3", row["Applies To"])
                self.assertEqual("2026-08-13", row["Verified At"])

    def test_refined_rows_are_context_sensitive_not_universal_recipes(self):
        expected = {
            "8": ("depends on distance complexity platform", "shared motion tokens"),
            "14": ("match how an element changes speed", "linear for constant-rate progress"),
            "19": ("badges validation text", "stable content-driven container"),
            "78": ("avoid flashing for near-instant work", "platform and component guidance"),
        }
        forbidden = ("use 150-300ms", "operations > 300ms", "linear motion feels robotic")
        by_number = {row["No"]: row for row in self.ux}
        for number, phrases in expected.items():
            with self.subTest(row=number):
                row = by_number[number]
                guidance = " ".join((row["Description"], row["Do"])).casefold()
                for phrase in phrases:
                    self.assertIn(phrase, guidance)
                for claim in forbidden:
                    self.assertNotIn(claim, guidance)


if __name__ == "__main__":
    unittest.main()
