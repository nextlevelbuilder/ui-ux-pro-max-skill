#!/usr/bin/env python3
"""Freshness and migration contracts for native, desktop, and 3D stacks."""

import csv
import sys
import unittest
from pathlib import Path
from urllib.parse import urlsplit

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from core import (DATA_DIR, STACK_CONFIG, STACK_CURRENT_APPLICABILITY,
                  search_stack)  # noqa: E402
from validate_data import STACK_OFFICIAL_HOSTS  # noqa: E402

STACKS = {
    "react-native", "flutter", "swiftui", "jetpack-compose", "avalonia",
    "uwp", "winui", "wpf", "uno", "javafx", "threejs", "laravel",
}


def _rows(stack):
    path = DATA_DIR / STACK_CONFIG[stack]["file"]
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class TestNativeDesktopStackFreshness(unittest.TestCase):
    def test_rows_have_final_freshness_metadata(self):
        for stack in STACKS:
            for row in _rows(stack):
                with self.subTest(stack=stack, row=row["No"]):
                    expected = "deprecated" if stack == "uwp" else "active"
                    self.assertEqual(row["Status"], expected)
                    self.assertTrue(row["Applies To"].startswith(
                        STACK_CURRENT_APPLICABILITY[stack]))
                    self.assertRegex(row["Verified At"], r"^\d{4}-\d{2}-\d{2}$")
                    self.assertEqual("legacy" in row["Applies To"], stack == "uwp")

    def test_high_impact_rows_use_official_sources(self):
        for stack in STACKS:
            for row in _rows(stack):
                if row["Severity"] not in {"Critical", "High"}:
                    continue
                with self.subTest(stack=stack, row=row["No"]):
                    parsed = urlsplit(row["Docs URL"])
                    self.assertEqual(parsed.scheme, "https")
                    self.assertIn(parsed.hostname, STACK_OFFICIAL_HOSTS[stack])

    def test_current_mobile_contracts(self):
        cases = {
            ("react-native", "Hermes bundled default engine"): "hermes",
            ("flutter", "predictive back result callback"): "onpopinvokedwithresult",
            ("flutter", "accessible nonlinear text scaling"): "textscaler",
            ("swiftui", "multicolumn navigation sidebar detail"): "navigationsplitview",
        }
        for (stack, query), expected in cases.items():
            with self.subTest(stack=stack):
                result = search_stack(query, stack, max_results=1)
                self.assertEqual(result["count"], 1)
                recommended = " ".join(
                    result["results"][0][field]
                    for field in ("Guideline", "Do", "Code Good")
                ).casefold()
                self.assertIn(expected, recommended)

    def test_windows_current_and_maintenance_lanes_are_visible(self):
        current = search_stack("new Windows desktop app Windows App SDK", "winui")
        legacy = search_stack("UWP maintenance x:Bind migration", "uwp")
        self.assertGreater(current["count"], 0)
        self.assertGreater(legacy["count"], 0)
        self.assertEqual({row["Status"] for row in current["results"]}, {"active"})
        self.assertEqual({row["Status"] for row in legacy["results"]}, {"deprecated"})
        self.assertTrue(any("winui" in " ".join(row.values()).casefold()
                            for row in legacy["results"]))
        successor = search_stack(
            "which Windows UI framework should a brand new app choose instead of legacy UWP",
            "uwp", max_results=1,
        )
        self.assertEqual("Prefer WinUI 3 for new projects", successor["results"][0]["Guideline"])

    def test_old_version_without_curated_rows_abstains(self):
        cases = {
            "react-native": "React Native 0.75 Hermes",
            "flutter": "Flutter SDK 3.22 back navigation",
            "swiftui": "iOS 15 SwiftUI navigation",
            "avalonia": "Avalonia UI v11 storage picker",
            "winui": "WinUI SDK 2 desktop app",
            "javafx": "JavaFX SDK 21 table view",
            "threejs": "Three.js r128 OrbitControls",
            "laravel": "Laravel 12 validation",
        }
        for stack, query in cases.items():
            with self.subTest(stack=stack):
                self.assertEqual(search_stack(query, stack)["count"], 0)

    def test_migration_intent_returns_current_replacements(self):
        cases = {
            "flutter": "replace deprecated WillPopScope with current Flutter API",
            "react-native": "upgrade legacy Hermes configuration",
            "threejs": "replace deprecated outputEncoding with current color space",
        }
        for stack, query in cases.items():
            with self.subTest(stack=stack):
                result = search_stack(query, stack)
                self.assertGreater(result["count"], 0)
                self.assertEqual({row["Status"] for row in result["results"]}, {"active"})

        versioned_cases = {
            "react-native": "upgrade React Native 0.75 to React Native 0.86 Hermes",
            "flutter": "upgrade Flutter 3.22 to Flutter 3.44 predictive back",
            "threejs": "upgrade Three.js r128 to r185 outputColorSpace",
        }
        for stack, query in versioned_cases.items():
            with self.subTest(stack=stack, query=query):
                result = search_stack(query, stack)
                self.assertGreater(result["count"], 0)
                self.assertEqual({row["Status"] for row in result["results"]}, {"active"})

    def test_standalone_current_and_deprecated_identifiers_resolve_replacement(self):
        cases = {
            ("flutter", "onPopInvokedWithResult"): "PopScope",
            ("flutter", "TextScaler"): "large fonts",
            ("threejs", "outputColorSpace"): "Color Space",
            ("threejs", "outputEncoding"): "Color Space",
        }
        for (stack, query), guideline in cases.items():
            with self.subTest(stack=stack, query=query):
                result = search_stack(query, stack, max_results=1)
                self.assertEqual(result["count"], 1)
                self.assertIn(guideline.casefold(), result["results"][0]["Guideline"].casefold())

    def test_current_threejs_uses_supported_module_and_color_apis(self):
        cases = {
            "Three.js current OrbitControls addon import": "three/addons/",
            "Three.js current renderer color space": "outputcolorspace",
        }
        for query, expected in cases.items():
            with self.subTest(query=query):
                result = search_stack(query, "threejs", max_results=1)
                self.assertEqual(result["count"], 1)
                recommended = " ".join(
                    result["results"][0][field]
                    for field in ("Guideline", "Do", "Code Good")
                ).casefold()
                self.assertIn(expected, recommended)

    def test_deprecated_symbols_are_not_recommended_by_current_rows(self):
        forbidden = {
            "react-native": ("hermes_enabled",),
            "flutter": ("willpopscope", "onpopinvoked:", "textscalefactor"),
            "swiftui": ("navigationview", "presentationmode"),
            "winui": ("dispatcher.runasync", "system.windows"),
            "uno": ("system.windows", 'requestedtheme="default"'),
            "javafx": ("fxpermission", "javadoc/21"),
            "threejs": (
                "r128", "three.orbitcontrols", "outputencoding",
                "three.srgbencoding", "examples/js/controls",
            ),
        }
        for stack, tokens in forbidden.items():
            for row in _rows(stack):
                if row["Status"] != "active":
                    continue
                recommended = " ".join(
                    row[field] for field in ("Guideline", "Do", "Code Good")
                ).casefold()
                for token in tokens:
                    with self.subTest(stack=stack, row=row["No"], token=token):
                        self.assertNotIn(token, recommended)


if __name__ == "__main__":
    unittest.main()
