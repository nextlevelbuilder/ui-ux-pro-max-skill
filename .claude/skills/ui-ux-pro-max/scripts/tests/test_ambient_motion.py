#!/usr/bin/env python3
"""Contract and search tests for ambient / continuous-decoration motion presets."""

import csv
import re
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = SCRIPTS_DIR.parent / "data"
sys.path.insert(0, str(SCRIPTS_DIR))

from core import search  # noqa: E402

AMBIENT_CATEGORY = "Ambient / Continuous Decoration"
EXPECTED_SELECTORS_BY_TIER = {
    "Subtle": {".ambient-glow"},
    "Standard": {".orb-core", ".orb-drift"},
    "Complex": {".nebula-filaments", ".nebula-clusters", ".cluster-pulse"},
}


def read_ambient_rows():
    with (DATA_DIR / "motion.csv").open(encoding="utf-8", newline="") as handle:
        return [row for row in csv.DictReader(handle) if row["Category"] == AMBIENT_CATEGORY]


class TestAmbientMotionPresets(unittest.TestCase):
    def test_ambient_presets_present_across_all_intensity_tiers(self):
        ambient = read_ambient_rows()
        self.assertEqual(len(ambient), 3)
        self.assertEqual(
            {row["Intensity Tier"] for row in ambient},
            {"Subtle", "Standard", "Complex"},
        )
        for row in ambient:
            self.assertIn("always-on", row["Trigger"].casefold())
            self.assertIn("no user trigger", row["Trigger"].casefold())

    def test_ambient_presets_encode_perceptual_frame_and_opt_out_constraints(self):
        by_tier = {row["Intensity Tier"]: row for row in read_ambient_rows()}
        self.assertEqual(set(by_tier), {"Subtle", "Standard", "Complex"})

        for tier, row in by_tier.items():
            notes = row["Framework Notes"].casefold()
            perf = row["Performance Notes"].casefold()
            do_text = row["Do"].casefold()
            snippet = row["GSAP Snippet"]
            with self.subTest(tier=tier):
                self.assertIn("60 fps", perf)
                self.assertIn("ms/frame", perf)
                self.assertIn("offscreen", perf)
                self.assertIn("hidden", perf)
                self.assertIn("intersectionobserver", notes)
                self.assertIn("visibilitychange", notes)
                self.assertIn("observer.observe(", snippet)
                self.assertIn("visibilitychange", snippet)
                self.assertIn("sync()", snippet)
                self.assertIn(".kill()", snippet)
                self.assertNotIn("gsap.timeline(", snippet)
                self.assertEqual(
                    set(re.findall(r"'\.[a-z0-9-]+'", snippet)),
                    {f"'{sel}'" for sel in EXPECTED_SELECTORS_BY_TIER[tier]},
                )
                self.assertIn("prefers-reduced-motion", notes)
                self.assertIn("user-controlled", notes)
                self.assertIn("amplitude", do_text)
                self.assertIn("period", do_text)
                self.assertIn("perceptual threshold", do_text)
                self.assertIn("frame-difference", notes)
                self.assertRegex(notes, r"\d+%")

        for tier in ("Standard", "Complex"):
            row = by_tier[tier]
            notes = row["Framework Notes"].casefold()
            duration = row["Duration"].casefold()
            with self.subTest(rule="speed-layering", tier=tier):
                self.assertIn("speed layering", notes)
                self.assertRegex(duration, r"[34]-8s/rev")
                self.assertRegex(duration, r"20(?:-\d+)?s")
                self.assertIn("pulse", duration)

        complex_do = by_tier["Complex"]["Do"].casefold()
        self.assertIn("filament", complex_do)
        self.assertIn("cluster", complex_do)
        self.assertIn("falloff", complex_do)

    def test_ambient_queries_surface_continuous_decoration_presets(self):
        for query in (
            "ambient living status orb continuous decoration",
            "looping nebula filament particles always-on",
        ):
            with self.subTest(query=query):
                result = search(query, domain="gsap", max_results=3)
                results = result.get("results", [])
                self.assertTrue(results, f"expected matches for {query!r}")
                self.assertEqual(results[0]["Category"], AMBIENT_CATEGORY)

    def test_event_driven_motion_rankings_remain_intact(self):
        cases = (
            ("GSAP reveal elements when they enter the viewport on scroll", "Scroll Reveal"),
            ("skeleton shimmer loader while async content waits", "Loading / Skeleton"),
            ("hover button opacity lift", "Hover Micro-interaction"),
        )
        for query, expected_category in cases:
            with self.subTest(query=query):
                result = search(query, domain="gsap", max_results=3)
                results = result.get("results", [])
                self.assertTrue(results)
                self.assertEqual(results[0]["Category"], expected_category)


if __name__ == "__main__":
    unittest.main()
