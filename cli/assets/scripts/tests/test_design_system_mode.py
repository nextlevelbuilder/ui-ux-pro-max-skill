#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regression tests for color-mode coherence in design_system.py (issue #428).

Style, palette and anti-patterns used to be resolved independently, so a
dark-primary style could be returned alongside a light palette and a
"Dark mode by default" anti-pattern.

Stdlib-only (unittest, not pytest) to match test_core.py -- this project ships
with zero external dependencies.

Run with:
    python -m unittest discover -s scripts/tests -v
or directly:
    python scripts/tests/test_design_system_mode.py
"""

import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from design_system import (  # noqa: E402
    _filter_anti_patterns_for_mode,
    _contrast_ratio,
    _palette_is_dark,
    _query_wants_dark,
    _relative_luminance,
    _resolve_color_mode,
    _select_palette_for_mode,
    _style_is_dark_primary,
    DesignSystemGenerator,
)  # noqa: I001 - private helpers first, public class last

LIGHT_PALETTE = {"Product Type": "SaaS", "Background": "#F8FAFC", "Foreground": "#020617"}
DARK_PALETTE = {"Product Type": "Fintech/Crypto", "Background": "#0F172A", "Foreground": "#F8FAFC"}

# Verbatim from styles.csv row "Modern Dark (Cinema Mobile)".
DARK_PRIMARY_STYLE = {
    "Style Category": "Modern Dark (Cinema Mobile)",
    "Light Mode ✓": "✓ Light mode only as exception",
    "Dark Mode ✓": "✓ Dark Mode Primary",
}
DUAL_MODE_STYLE = {
    "Style Category": "Minimalism",
    "Light Mode ✓": "✓ Full",
    "Dark Mode ✓": "✓ Full",
}


class TestLuminance(unittest.TestCase):
    def test_parses_six_and_three_digit_hex(self):
        self.assertAlmostEqual(_relative_luminance("#FFFFFF"), 1.0, places=6)
        self.assertAlmostEqual(_relative_luminance("#000000"), 0.0, places=6)
        self.assertAlmostEqual(_relative_luminance("#FFF"), 1.0, places=6)

    def test_returns_none_for_unparseable(self):
        for value in ("", "nope", "#12", "#GGGGGG", None):
            self.assertIsNone(_relative_luminance(value))

    def test_classifies_backgrounds_from_the_shipped_data(self):
        # Lightest dark background and darkest light background in colors.csv.
        self.assertTrue(_palette_is_dark({"Background": "#1F2937"}))
        self.assertFalse(_palette_is_dark({"Background": "#E8ECF1"}))

    def test_missing_background_is_not_dark(self):
        self.assertFalse(_palette_is_dark({}))
        self.assertFalse(_palette_is_dark(None))


class TestModeResolution(unittest.TestCase):
    def test_dark_primary_style_detected(self):
        self.assertTrue(_style_is_dark_primary(DARK_PRIMARY_STYLE))

    def test_dual_mode_style_is_not_dark_primary(self):
        self.assertFalse(_style_is_dark_primary(DUAL_MODE_STYLE))
        self.assertFalse(_style_is_dark_primary({}))

    def test_query_keywords(self):
        self.assertTrue(_query_wants_dark("fintech B2B professional dark mode"))
        self.assertTrue(_query_wants_dark("gaming app OLED"))
        self.assertFalse(_query_wants_dark("healthcare clinic booking app"))
        self.assertFalse(_query_wants_dark(""))

    def test_either_signal_resolves_dark(self):
        self.assertEqual(_resolve_color_mode("saas dark mode", DUAL_MODE_STYLE), "dark")
        self.assertEqual(_resolve_color_mode("saas", DARK_PRIMARY_STYLE), "dark")
        self.assertEqual(_resolve_color_mode("saas", DUAL_MODE_STYLE), "light")


class TestPaletteSelection(unittest.TestCase):
    def test_dark_mode_skips_light_palettes(self):
        chosen = _select_palette_for_mode([LIGHT_PALETTE, DARK_PALETTE], "dark")
        self.assertEqual(chosen["Background"], "#0F172A")

    def test_dark_mode_falls_back_to_top_hit_when_no_dark_ramp_exists(self):
        chosen = _select_palette_for_mode([LIGHT_PALETTE], "dark")
        self.assertEqual(chosen["Background"], "#F8FAFC")

    def test_light_mode_keeps_the_existing_top_hit_behaviour(self):
        chosen = _select_palette_for_mode([DARK_PALETTE, LIGHT_PALETTE], "light")
        self.assertEqual(chosen["Background"], "#0F172A")

    def test_empty_results(self):
        self.assertEqual(_select_palette_for_mode([], "dark"), {})

    def test_category_identity_wins_over_unrelated_dark_palette(self):
        chosen = _select_palette_for_mode(
            [LIGHT_PALETTE, DARK_PALETTE], "dark", "SaaS")
        self.assertEqual("SaaS", chosen["Product Type"])
        self.assertEqual("derived-dark", chosen["_mode_derivation"])
        self.assertTrue(_palette_is_dark(chosen))
        self.assertGreaterEqual(
            _contrast_ratio(chosen["Ring"], chosen["Background"]), 3.0)


class TestAntiPatternGating(unittest.TestCase):
    def test_dark_clause_dropped_others_kept(self):
        result = _filter_anti_patterns_for_mode(
            "Excessive animation + Dark mode by default", "dark")
        self.assertEqual(result, "Excessive animation")

    def test_light_mode_is_a_no_op(self):
        original = "Excessive animation + Dark mode by default"
        self.assertEqual(_filter_anti_patterns_for_mode(original, "light"), original)

    def test_unrelated_anti_patterns_survive_dark_mode(self):
        original = "Complex jargon + Tiny tap targets"
        self.assertEqual(_filter_anti_patterns_for_mode(original, "dark"), original)

    def test_empty_input(self):
        self.assertEqual(_filter_anti_patterns_for_mode("", "dark"), "")


class TestEndToEndCoherence(unittest.TestCase):
    """The exact reproduction from issue #428."""

    QUERY = "SaaS invoicing fintech B2B professional dark mode"

    def test_dark_query_gets_a_dark_background(self):
        ds = DesignSystemGenerator().generate(self.QUERY)
        background = ds["colors"]["background"]
        self.assertTrue(
            _palette_is_dark({"Background": background}),
            "dark-mode query returned a light background: {}".format(background),
        )

    def test_generator_exports_every_semantic_foreground_pair(self):
        colors = DesignSystemGenerator().generate("SaaS dashboard")["colors"]
        pairs = (
            ("on_primary", "primary"),
            ("on_secondary", "secondary"),
            ("on_accent", "accent"),
            ("foreground", "background"),
            ("card_foreground", "card"),
            ("muted_foreground", "muted"),
            ("on_destructive", "destructive"),
        )
        for foreground, background in pairs:
            with self.subTest(pair=foreground):
                self.assertTrue(colors[foreground])
                self.assertTrue(colors[background])
                self.assertGreaterEqual(
                    _contrast_ratio(colors[foreground], colors[background]), 4.5
                )
        self.assertEqual(colors["on_cta"], colors["on_accent"])

    def test_dark_query_foreground_is_lighter_than_background(self):
        ds = DesignSystemGenerator().generate(self.QUERY)
        background = _relative_luminance(ds["colors"]["background"])
        foreground = _relative_luminance(ds["colors"]["foreground"])
        self.assertIsNotNone(background)
        self.assertIsNotNone(foreground)
        self.assertGreater(foreground, background)

    def test_dark_query_does_not_advise_against_dark_mode(self):
        ds = DesignSystemGenerator().generate(self.QUERY)
        self.assertNotIn("dark mode", ds["anti_patterns"].lower())

    def test_light_query_keeps_a_light_background(self):
        ds = DesignSystemGenerator().generate("healthcare clinic booking app")
        self.assertFalse(_palette_is_dark({"Background": ds["colors"]["background"]}))


class TestRTLSupport(unittest.TestCase):
    def test_design_system_generator_rtl_flag(self):
        generator = DesignSystemGenerator()
        ds_rtl = generator.generate("Fintech dashboard", rtl=True)
        self.assertTrue(ds_rtl["rtl"])

        ds_ltr = generator.generate("Fintech dashboard", rtl=False)
        self.assertFalse(ds_ltr["rtl"])

    def test_format_ascii_and_markdown_with_rtl(self):
        from design_system import format_ascii_box, format_markdown

        generator = DesignSystemGenerator()
        ds_rtl = generator.generate("Fintech dashboard", rtl=True)

        ascii_out = format_ascii_box(ds_rtl)
        self.assertIn("RTL GUIDELINES", ascii_out)
        self.assertIn("direction: rtl", ascii_out)

        md_out = format_markdown(ds_rtl)
        self.assertIn("### RTL (Right-to-Left) Guidelines", md_out)
        self.assertIn("direction: rtl", md_out)

    def test_format_without_rtl_omits_rtl_sections(self):
        from design_system import format_ascii_box, format_markdown

        generator = DesignSystemGenerator()
        ds_ltr = generator.generate("Fintech dashboard", rtl=False)

        ascii_out = format_ascii_box(ds_ltr)
        self.assertNotIn("RTL GUIDELINES", ascii_out)

        md_out = format_markdown(ds_ltr)
        self.assertNotIn("### RTL (Right-to-Left) Guidelines", md_out)


if __name__ == "__main__":
    unittest.main(verbosity=2)

