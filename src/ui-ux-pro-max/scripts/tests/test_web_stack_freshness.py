#!/usr/bin/env python3
"""Freshness and generation-isolation contracts for web stack guidance."""

import csv
import sys
import unittest
from pathlib import Path
from urllib.parse import urlsplit

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from core import DATA_DIR, STACK_CONFIG, WEB_STACKS, search_stack  # noqa: E402
from validate_data import STACK_OFFICIAL_HOSTS  # noqa: E402

CURRENT_APPLICABILITY = {
    "react": "react 19.2.x",
    "nextjs": "nextjs 16.2",
    "vue": "vue 3.5.x",
    "svelte": "svelte 5",
    "astro": "astro 7.1.6",
    "angular": "angular 22.x",
    "html-tailwind": "html-tailwind 4.3",
    "shadcn": "shadcn cli 4",
    "nuxtjs": "nuxtjs 4.5",
    "nuxt-ui": "nuxt-ui 4.10",
}


def _rows(stack):
    path = DATA_DIR / STACK_CONFIG[stack]["file"]
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class TestWebStackFreshness(unittest.TestCase):
    def test_web_rows_have_explicit_freshness_metadata(self):
        for stack in WEB_STACKS:
            for row in _rows(stack):
                with self.subTest(stack=stack, row=row["No"]):
                    self.assertIn(row["Status"], {"active", "deprecated"})
                    self.assertTrue(row["Applies To"].startswith(stack))
                    self.assertRegex(row["Verified At"], r"^\d{4}-\d{2}-\d{2}$")
                    self.assertEqual(
                        "legacy" in row["Applies To"].casefold(),
                        row["Status"] == "deprecated",
                    )

    def test_high_impact_rows_use_official_sources(self):
        for stack in WEB_STACKS:
            for row in _rows(stack):
                if row["Severity"] not in {"Critical", "High"}:
                    continue
                with self.subTest(stack=stack, row=row["No"]):
                    parsed = urlsplit(row["Docs URL"])
                    self.assertEqual(parsed.scheme, "https")
                    self.assertIn(parsed.hostname, STACK_OFFICIAL_HOSTS[stack])

    def test_active_rows_use_the_verified_current_applicability(self):
        for stack, applicability in CURRENT_APPLICABILITY.items():
            for row in _rows(stack):
                if row["Status"] != "active":
                    continue
                with self.subTest(stack=stack, row=row["No"]):
                    self.assertTrue(row["Applies To"].startswith(applicability))

    def test_svelte_current_and_legacy_queries_do_not_mix_generations(self):
        current = search_stack("Svelte state props and events", "svelte")
        legacy = search_stack("Svelte 4 legacy props and events", "svelte")
        self.assertGreater(current["count"], 0)
        self.assertGreater(legacy["count"], 0)
        self.assertEqual({row["Status"] for row in current["results"]}, {"active"})
        self.assertEqual({row["Status"] for row in legacy["results"]}, {"deprecated"})
        self.assertTrue(all("legacy" in row["Applies To"] for row in legacy["results"]))

    def test_explicit_old_major_uses_only_curated_legacy_rows(self):
        cases = {
            "nextjs": "Next.js 15 middleware auth matcher",
            "html-tailwind": "Tailwind 3 JIT content configuration",
            "nuxtjs": "Nuxt 3 app config runtime config migration",
        }
        for stack, query in cases.items():
            with self.subTest(stack=stack):
                result = search_stack(query, stack)
                self.assertGreater(result["count"], 0)
                self.assertEqual(
                    {row["Status"] for row in result["results"]}, {"deprecated"}
                )

    def test_current_major_migration_query_stays_on_current_guidance(self):
        result = search_stack("Next.js 16 migration to proxy", "nextjs")
        self.assertGreater(result["count"], 0)
        self.assertEqual({row["Status"] for row in result["results"]}, {"active"})

    def test_shadcn_named_base_excludes_incompatible_composition_apis(self):
        result = search_stack("shadcn Base UI asChild composition", "shadcn")
        self.assertGreater(result["count"], 0)
        self.assertEqual(result["results"][0]["Guideline"],
                         "Use render for Base UI composition")
        self.assertTrue(all("base=radix" not in row["Applies To"]
                            for row in result["results"]))

    def test_common_old_major_syntaxes_select_legacy_guidance(self):
        cases = {
            "svelte": "svelte@4 props events",
            "nextjs": "Next.js (v15) middleware",
            "html-tailwind": "tailwindcss@3 JIT",
            "nuxtjs": "nuxt@3 app config",
        }
        for stack, query in cases.items():
            with self.subTest(stack=stack, query=query):
                result = search_stack(query, stack)
                self.assertGreater(result["count"], 0)
                self.assertEqual(
                    {row["Status"] for row in result["results"]}, {"deprecated"}
                )

    def test_old_major_without_curated_legacy_guidance_abstains(self):
        result = search_stack("Astro 5 content collections", "astro")
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["results"], [])

    def test_current_high_drift_queries_return_current_contracts(self):
        cases = {
            ("nextjs", "Next.js 16 request interception proxy"): "proxy",
            ("html-tailwind", "Tailwind 4 CSS-first source detection"): "source",
            ("react", "React Effect Event latest values inside an Effect"): "effect event",
        }
        for (stack, query), expected in cases.items():
            with self.subTest(stack=stack):
                result = search_stack(query, stack, max_results=1)
                self.assertEqual(result["count"], 1)
                row = result["results"][0]
                self.assertEqual(row["Status"], "active")
                self.assertIn(expected, row["Guideline"].casefold())

    def test_stack_without_curated_legacy_rows_keeps_nonlegacy_fallback(self):
        result = search_stack(
            "which Windows UI framework should a new app choose instead of legacy UWP",
            "uwp",
        )
        self.assertGreater(result["count"], 0)

    def test_stale_apis_are_not_recommended_by_active_rows(self):
        forbidden = {
            "svelte": ("$: ", "export let ", "on:click", "createeventdispatcher"),
            "nextjs": ("middleware.ts", "function middleware", "skipmiddleware"),
            "html-tailwind": (
                "content: [", "mode: 'jit'", "@tailwindcss/aspect-ratio",
                "tailwindcss-container-queries",
            ),
            "nuxt-ui": ("#cell-status", "sortable: true", "v-model:content"),
            "astro": (
                "output: 'hybrid'", "viewtransitions", "@astrojs/tailwind",
                "astro add prefetch",
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

        self.assertNotIn(
            "fetch(url {", _rows("nextjs")[12]["Code Good"].casefold()
        )
        self.assertNotIn("catch(e) {}", _rows("react")[39]["Code Good"].casefold())


if __name__ == "__main__":
    unittest.main()
