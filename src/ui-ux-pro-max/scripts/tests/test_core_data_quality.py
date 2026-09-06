#!/usr/bin/env python3
"""Semantic quality contracts for the core UI/UX datasets."""

import csv
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = SCRIPTS_DIR.parent / "data"
sys.path.insert(0, str(SCRIPTS_DIR))

from core import search  # noqa: E402
from validate_data import (  # noqa: E402
    CHART_NON_COLOR_GUIDANCE,
    CHART_RISKS,
    CHART_TEXT_FALLBACK,
    COLOR_CONTRAST_PAIRS,
    CSS_IMPORT,
    ICON_CONTEXTS,
    ICON_ROLES,
    ICON_USAGE_REQUIREMENTS,
    WCAG_GRADE,
    _check_chart_contract,
    _check_icon_contract,
    _check_typography_contract,
    _configured_font_names,
    _font_families,
    _font_names,
    contrast_ratio,
)


def read_rows(name):
    with (DATA_DIR / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class TestSemanticColors(unittest.TestCase):
    def test_declared_text_and_ui_pairs_meet_role_thresholds(self):
        for row in read_rows("colors.csv"):
            for foreground, (background, role, minimum) in COLOR_CONTRAST_PAIRS.items():
                with self.subTest(
                        product=row["Product Type"], pair=foreground, role=role):
                    self.assertGreaterEqual(
                        contrast_ratio(row[foreground], row[background]), minimum)

    def test_destructive_tokens_are_not_success_green(self):
        for row in read_rows("colors.csv"):
            value = row["Destructive"].lstrip("#")
            red, green, blue = (int(value[index:index + 2], 16)
                                for index in (0, 2, 4))
            with self.subTest(product=row["Product Type"]):
                self.assertFalse(green > red * 1.1 and green > blue * 1.1)


class TestAccessibilityGuidance(unittest.TestCase):
    def test_wcag_22_topics_have_explicit_rows_and_are_retrievable(self):
        rows = read_rows("ux-guidelines.csv")
        issues = {row["Issue"] for row in rows}
        expected_platforms = {
            "Focus Not Obscured (Minimum)": "Web",
            "Focus Not Obscured (Enhanced)": "Web",
            "Focus Appearance": "Web",
            "Dragging Movements": "All",
            "Target Size (Minimum)": "Web",
            "Consistent Help": "All",
            "Redundant Entry": "All",
            "Accessible Authentication (Minimum)": "All",
            "Auto-Rotating Content Controls": "All",
        }
        self.assertTrue(expected_platforms.keys() <= issues)
        for issue, expected_platform in expected_platforms.items():
            with self.subTest(issue=issue):
                row = next(row for row in rows if row["Issue"] == issue)
                self.assertEqual(row["Platform"], expected_platform)
                self.assertIn(row["Severity"], {"Medium", "High", "Critical"})
                self.assertNotEqual(row["Do"], row["Description"])
                result = search(issue, domain="ux", max_results=3)
                self.assertTrue(any(row.get("Issue") == issue for row in result["results"]))

    def test_native_and_web_target_sizes_remain_distinct(self):
        native = next(row for row in read_rows("app-interface.csv")
                      if row["Issue"] == "Touch Target Size")
        web = next(row for row in read_rows("ux-guidelines.csv")
                   if row["Issue"] == "Target Size (Minimum)")
        native_text = " ".join(native.values())
        web_text = " ".join(web.values())
        self.assertIn("44pt", native_text)
        self.assertIn("48dp", native_text)
        self.assertIn("24 CSS px", web_text)

    def test_motion_recipes_offer_reduced_motion_or_user_control(self):
        for row in read_rows("motion.csv"):
            text = " ".join(row.values()).casefold()
            with self.subTest(row=row["No"], category=row["Category"]):
                self.assertTrue(
                    "reduced-motion" in text or "user-controlled" in text,
                    "every motion recipe needs an explicit opt-out",
                )


class TestChartsTypographyAndIcons(unittest.TestCase):
    def test_mutated_accessibility_and_import_contracts_fail(self):
        mutations = []
        chart = dict(read_rows("charts.csv")[0])
        chart["A11y Fallback"] = "A visible table is available."
        mutations.append((_check_chart_contract, chart, "keyboard"))
        typography = dict(read_rows("typography.csv")[0])
        typography["CSS Import"] = (
            "@import url('https://fonts.googleapis.com/css2?family=Comic+Sans');"
        )
        mutations.append((_check_typography_contract, typography, "differ"))
        missing_weight = dict(read_rows("typography.csv")[0])
        missing_weight["Notes"] += " Recommended weight 900."
        mutations.append((_check_typography_contract, missing_weight, "weights"))
        icon = dict(read_rows("icons.csv")[0])
        icon["Import Code"] = "import { IconName } from '@phosphor-icons/react'"
        mutations.append((_check_icon_contract, icon, "import"))
        for checker, row, expected in mutations:
            with self.subTest(checker=checker.__name__):
                problems = []
                checker([row], problems)
                self.assertTrue(any(expected in problem for problem in problems))

    def test_chart_risk_is_not_a_conformance_grade(self):
        for row in read_rows("charts.csv"):
            with self.subTest(data_type=row["Data Type"]):
                self.assertIn(row["Accessibility Risk"], CHART_RISKS)
                self.assertEqual(
                    row["Accessibility Grade"],
                    "deprecated: use Accessibility Risk",
                )
                text = " ".join((row["Accessibility Notes"], row["A11y Fallback"]))
                self.assertIsNone(WCAG_GRADE.search(text))
                self.assertIsNotNone(CHART_TEXT_FALLBACK.search(text.casefold()))
                self.assertIsNotNone(
                    CHART_NON_COLOR_GUIDANCE.search(text.casefold())
                )
                self.assertIn("keyboard", text.casefold())

    def test_named_fonts_match_google_import_css_import_and_tailwind_config(self):
        for row in read_rows("typography.csv"):
            url_families = _font_families(row["Google Fonts URL"])
            families = _font_names(url_families)
            configured = _configured_font_names(row["Tailwind Config"])
            named = {row["Heading Font"], row["Body Font"]}
            with self.subTest(pairing=row["Font Pairing Name"]):
                self.assertTrue(named <= families)
                self.assertTrue(named <= configured)
                match = CSS_IMPORT.fullmatch(row["CSS Import"])
                self.assertIsNotNone(match)
                self.assertEqual(
                    sorted(url_families),
                    sorted(_font_families(match.group(2))),
                )

    def test_icon_semantics_are_explicit_and_imports_are_concrete(self):
        for row in read_rows("icons.csv"):
            with self.subTest(icon=row["Icon Name"]):
                self.assertIn(row["Semantic Role"], ICON_ROLES)
                self.assertEqual(set(row["Allowed Contexts"].split("|")), ICON_CONTEXTS)
                self.assertNotRegex(row["Usage"], r"[\u3400-\u9fff]")
                self.assertNotIn("IconName", row["Import Code"])
                for requirement in ICON_USAGE_REQUIREMENTS:
                    self.assertRegex(row["Usage"].casefold(), requirement)

    def test_natural_accessibility_queries_are_retrievable(self):
        cases = {
            "chart": ("keyboard accessible chart", "keyboard"),
            "landing": ("accessible drag interaction", "keyboard controls"),
            "icons": ("decorative icon aria hidden", "aria-hidden"),
            "gsap": ("stop animation offscreen", "visibility"),
            "ux": ("error summary validation", "error summary"),
        }
        for domain, (query, expected) in cases.items():
            with self.subTest(domain=domain, query=query):
                result = search(query, domain=domain, max_results=3)
                self.assertGreater(result["count"], 0)
                self.assertIn(
                    expected.casefold(),
                    " ".join(str(value) for value in result["results"][0].values()).casefold(),
                )


class TestCurrentReactGuidance(unittest.TestCase):
    def test_effect_event_is_scoped_and_community_use_latest_is_removed(self):
        rows = read_rows("react-performance.csv")
        effect_event = next(row for row in rows if row["Issue"] == "Effect Events")
        text = " ".join(effect_event.values()).casefold()
        self.assertIn("inside effects", text)
        self.assertIn("dependencies", text)
        self.assertFalse(any("uselatest" in " ".join(row.values()).casefold()
                             for row in rows))


if __name__ == "__main__":
    unittest.main()
