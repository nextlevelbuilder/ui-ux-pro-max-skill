#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stdlib-only regression tests for core.py / design_system.py (unittest, not
pytest -- this project ships with zero external dependencies and the tests
shouldn't add one).

Run with:
    python -m unittest discover -s scripts/tests -v
or directly:
    python scripts/tests/test_core.py
"""

import os
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import core
from core import BM25, detect_domain, search, search_stack, CSV_CONFIG, AVAILABLE_STACKS
from design_system import DesignSystemGenerator, generate_design_system


class TestTokenizer(unittest.TestCase):
    def test_short_domain_terms_are_kept(self):
        bm25 = BM25()
        tokens = bm25.tokenize("UI and UX design with 3D and AI")
        self.assertIn("ui", tokens)
        self.assertIn("3d", tokens)
        self.assertIn("ai", tokens)

    def test_stopwords_removed(self):
        bm25 = BM25()
        tokens = bm25.tokenize("this is for the team to do")
        for stopword in ("is", "for", "the", "to", "do"):
            self.assertNotIn(stopword, tokens)

    def test_synonym_normalization(self):
        bm25 = BM25()
        self.assertEqual(bm25.tokenize("e-commerce store"), bm25.tokenize("ecommerce store"))
        self.assertEqual(bm25.tokenize("dark-mode toggle"), bm25.tokenize("dark toggle"))

    def test_boundary_safe_nav_normalization_preserves_existing_words(self):
        bm25 = BM25()
        tokens = bm25.tokenize("nav navigation navbar")
        self.assertIn("navigation", tokens)
        self.assertIn("navbar", tokens)
        self.assertNotIn("navigationigation", tokens)
        self.assertNotIn("navigationbar", tokens)

    def test_punctuation_and_uk_variants_normalize_to_canonical_tokens(self):
        bm25 = BM25()
        tokens = bm25.tokenize("colour, organisation; behaviour customisation")
        for expected in ("color", "organization", "behavior", "customization"):
            self.assertIn(expected, tokens)


class TestBm25CoreBehavior(unittest.TestCase):
    def test_empty_documents_produce_no_scores_or_vocab(self):
        bm25 = BM25()
        bm25.fit([])
        self.assertEqual(bm25.score("anything"), [])
        self.assertEqual(bm25.vocabulary(), [])

    def test_bm25_cache_rebuilds_after_file_mtime_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "search.csv"
            path.write_text("Name,Keywords\nAlpha,alpha token\n", encoding="utf-8")
            results_a, bm25_a = core._search_csv(path, ["Name", "Keywords"], ["Name"], "alpha", 1)
            self.assertEqual(results_a[0]["Name"], "Alpha")

            path.write_text("Name,Keywords\nBeta,beta token\n", encoding="utf-8")
            stat = path.stat()
            os.utime(path, ns=(stat.st_atime_ns + 1_000_000_000, stat.st_mtime_ns + 1_000_000_000))

            results_b, bm25_b = core._search_csv(path, ["Name", "Keywords"], ["Name"], "beta", 1)
            self.assertEqual(results_b[0]["Name"], "Beta")
            self.assertIsNot(bm25_a, bm25_b)

    def test_search_uses_one_verified_rows_and_index_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "search.csv"
            path.write_text("Name,Keywords\nAlpha,alpha token\n", encoding="utf-8")
            original_get_bm25 = core._get_bm25
            replaced = False

            def replace_after_read(filepath, search_cols, data, signature=None,
                                   cache_variant=""):
                nonlocal replaced
                if not replaced:
                    path.write_text("Name,Keywords\nBeta,beta token\n", encoding="utf-8")
                    replaced = True
                return original_get_bm25(
                    filepath, search_cols, data, signature, cache_variant)

            with patch.object(core, "_get_bm25", side_effect=replace_after_read):
                results, _, _ = core._search_csv_detailed(
                    path, ["Name", "Keywords"], ["Name"], "alpha", 1)
            self.assertEqual(results[0]["Name"], "Alpha")

            results, _, _ = core._search_csv_detailed(
                path, ["Name", "Keywords"], ["Name"], "beta", 1)
            self.assertEqual(results[0]["Name"], "Beta")


class TestSearchDomains(unittest.TestCase):
    def test_read_failure_is_not_reported_as_a_search_result(self):
        failure = UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid")
        with patch("core._load_csv_snapshot", side_effect=failure):
            domain = search("palette", domain="color", max_results=1)
            stack = search_stack("component", "react", max_results=1)
        for result in (domain, stack):
            self.assertEqual(0, result["count"])
            self.assertEqual([], result["results"])
            self.assertRegex(result["error"], r"^Unable to read search data:")
            self.assertNotIn("invalid", result["error"])

    def test_ui_is_searchable_in_style_domain(self):
        result = search("ui minimalism", domain="style", max_results=1)
        self.assertGreater(result["count"], 0, "literal 'ui' token must be searchable, not filtered by tokenizer")

    def test_accessibility_query_hits_ux(self):
        result = search("accessibility contrast wcag keyboard", domain="ux", max_results=3)
        self.assertGreater(result["count"], 0)

    def test_zero_result_query_reports_suggestions_not_error(self):
        result = search("zzqqxx totally made up gibberish", domain="ux", max_results=2)
        self.assertEqual(result["count"], 0)
        self.assertIn("suggestions", result)
        self.assertNotIn("error", result)

    def test_hard_negative_query_abstains_across_registered_domains_and_stacks(self):
        query = "sourdough starter crumb fermentation"
        for domain in CSV_CONFIG:
            with self.subTest(kind="domain", name=domain):
                self.assertEqual(search(query, domain=domain, max_results=1)["count"], 0)
        for stack in AVAILABLE_STACKS:
            with self.subTest(kind="stack", name=stack):
                self.assertEqual(search_stack(query, stack, max_results=1)["count"], 0)

    def test_typo_suggestions_are_deterministic_and_retryable(self):
        first = search("testimonal", domain="landing", max_results=3)
        second = search("testimonal", domain="landing", max_results=3)
        self.assertEqual(first["count"], 0)
        self.assertEqual(first.get("suggestions"), second.get("suggestions"))
        self.assertTrue(first["suggestions"], "typo path should return at least one deterministic suggestion")

        retry = search(first["suggestions"][0], domain="landing", max_results=3)
        self.assertGreater(retry["count"], 0)

    def test_suggestions_never_repeat_the_input_or_offer_a_dead_first_retry(self):
        pricing = search("pricing", domain="landing", max_results=3)
        self.assertNotIn("pricing", pricing.get("suggestions", []))

        minimal = search("minimal", domain="style", max_results=3)
        self.assertEqual(1, minimal["count"])
        self.assertEqual(
            "minimalism-and-swiss-style", minimal["results"][0]["Style ID"]
        )

    def test_unknown_programmatic_domain_keeps_legacy_style_fallback(self):
        result = search("minimalism", domain="unknown", max_results=1)
        self.assertEqual(result["domain"], "unknown")
        self.assertEqual(result["file"], CSV_CONFIG["style"]["file"])
        self.assertGreater(result["count"], 0)

    def test_unsupported_icon_library_abstains_instead_of_returning_other_library(self):
        result = search("lucide icon", diagnostics=True)
        self.assertEqual(result["domain"], "icons")
        self.assertEqual(result["count"], 0)
        self.assertEqual(result["diagnostics"]["reason"], "unsupported-library")

    def test_every_configured_domain_file_exists_and_is_searchable(self):
        for domain, config in CSV_CONFIG.items():
            with self.subTest(domain=domain):
                result = search("design", domain=domain, max_results=1)
                self.assertNotIn("error", result, f"domain '{domain}' failed: {result.get('error')}")

    def test_chart_output_keeps_legacy_grade_during_risk_migration(self):
        result = search("time series chart", domain="chart", max_results=1)
        self.assertEqual(result["count"], 1)
        self.assertEqual(
            result["results"][0]["Accessibility Grade"],
            "deprecated: use Accessibility Risk",
        )
        self.assertIn("Accessibility Risk", result["results"][0])

    def test_every_stack_file_exists_and_is_searchable(self):
        for stack in AVAILABLE_STACKS:
            with self.subTest(stack=stack):
                result = search_stack("performance", stack, max_results=1)
                self.assertNotIn("error", result, f"stack '{stack}' failed: {result.get('error')}")


class TestDomainDetection(unittest.TestCase):
    def test_style_keywords_route_to_style(self):
        self.assertEqual(detect_domain("glassmorphism dark ui"), "style")

    def test_accessibility_keywords_route_to_ux(self):
        self.assertEqual(detect_domain("accessibility contrast wcag"), "ux")

    def test_ambiguous_query_returns_runner_up(self):
        domain, _ = detect_domain("font pairing elegant crypto", return_scores=True)
        self.assertIsNotNone(domain)

    def test_empty_query_falls_back_to_style(self):
        self.assertEqual(detect_domain("...!!!???"), "style")

    def test_router_prioritizes_color_intent_over_generic_product_terms(self):
        self.assertEqual(detect_domain("semantic color tokens palette"), "color")

    def test_router_prioritizes_icons_when_icon_library_and_icon_intent_present(self):
        self.assertEqual(detect_domain("lucide search icon outline"), "icons")

    def test_router_prioritizes_typography_for_font_pairing_queries(self):
        self.assertEqual(detect_domain("font pairing elegant serif body font"), "typography")

    def test_router_prioritizes_chart_queries_over_generic_product_keywords(self):
        self.assertEqual(detect_domain("time series chart forecast"), "chart")

    def test_hash_only_routes_color_for_a_valid_hex_literal(self):
        self.assertNotEqual(detect_domain("C# WPF desktop app"), "color")
        self.assertEqual(detect_domain("use #ff00aa as the accent"), "color")

    def test_product_router_keeps_high_signal_service_aliases(self):
        self.assertEqual(detect_domain("beauty spa"), "product")
        self.assertEqual(detect_domain("salon booking"), "product")

    def test_native_drag_intent_beats_generic_react_token(self):
        self.assertEqual(detect_domain("drag reorder react native"), "web")

    def test_every_router_term_is_searchable_or_has_a_corpus_rewrite(self):
        for domain, keywords in core._domain_keywords().items():
            config = CSV_CONFIG[domain]
            path = core.DATA_DIR / config["file"]
            index = core._get_bm25(path, config["search_cols"], core._load_csv(path))
            vocabulary = set(index.vocabulary())
            for keyword in keywords:
                with self.subTest(domain=domain, keyword=keyword):
                    searchable = bool(set(index.tokenize(keyword)) & vocabulary)
                    explicitly_routing_only = keyword in core._DOMAIN_QUERY_REWRITES.get(domain, {})
                    self.assertTrue(searchable or explicitly_routing_only)


class TestPersistence(unittest.TestCase):
    def test_concurrent_non_force_persist_has_one_writer(self):
        with tempfile.TemporaryDirectory() as tmp:
            search_script = SCRIPTS_DIR / "search.py"
            processes = [subprocess.Popen(
                [sys.executable, str(search_script), f"saas dashboard {index}",
                 "--design-system", "--persist", "--project-name", "Race Probe",
                 "--output-dir", tmp, "--json"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            ) for index in range(8)]
            statuses = []
            for process in processes:
                stdout, stderr = process.communicate(timeout=30)
                self.assertEqual(process.returncode, 0, stderr)
                statuses.append(json.loads(stdout)["persistence"]["status"])

            self.assertEqual(statuses.count("success"), 1)
            self.assertEqual(statuses.count("skipped_exists"), 7)

    def test_persist_then_skip_then_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = generate_design_system("saas dashboard", "Test Project", persist=True, output_dir=tmp)
            self.assertEqual(result["persistence"]["status"], "success")
            master = Path(result["persistence"]["master_file"])
            self.assertTrue(master.exists())
            original_content = master.read_text(encoding="utf-8")

            # Second persist without force must not overwrite.
            result2 = generate_design_system("saas dashboard", "Test Project", persist=True, output_dir=tmp)
            self.assertEqual(result2["persistence"]["status"], "skipped_exists")
            self.assertEqual(master.read_text(encoding="utf-8"), original_content)

            # A new page override may be added without rewriting the existing Master.
            page_result = generate_design_system(
                "checkout form", "Test Project", persist=True, page="Checkout", output_dir=tmp
            )
            self.assertEqual(page_result["persistence"]["status"], "success")
            self.assertEqual(master.read_text(encoding="utf-8"), original_content)
            page_file = Path(tmp) / "design-system" / "test-project" / "pages" / "checkout.md"
            self.assertEqual(page_result["persistence"]["created_files"], [str(page_file)])
            self.assertTrue(page_file.exists())

            # Existing page overrides are protected by the same default no-overwrite rule.
            page_content = page_file.read_text(encoding="utf-8")
            page_result2 = generate_design_system(
                "different checkout", "Test Project", persist=True, page="Checkout", output_dir=tmp
            )
            self.assertEqual(page_result2["persistence"]["status"], "skipped_exists")
            self.assertEqual(page_file.read_text(encoding="utf-8"), page_content)

            # With force=True it must overwrite.
            result3 = generate_design_system("ecommerce luxury", "Test Project", persist=True, output_dir=tmp, force=True)
            self.assertEqual(result3["persistence"]["status"], "success")

    def test_persist_writes_only_under_output_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            generate_design_system("saas dashboard", "Scoped Project", persist=True, output_dir=tmp)
            expected = Path(tmp) / "design-system" / "scoped-project" / "MASTER.md"
            self.assertTrue(expected.exists())


class TestReasoningMatch(unittest.TestCase):
    def test_known_category_matches_exactly(self):
        gen = DesignSystemGenerator()
        rule = gen._find_reasoning_rule("SaaS (General)")
        self.assertTrue(rule, "exact-match category lookup should not fall through to fuzzy matching")

    def test_unknown_category_falls_back_gracefully(self):
        gen = DesignSystemGenerator()
        rule = gen._find_reasoning_rule("Totally Unknown Category XYZ")
        # Should not raise; may return {} which _apply_reasoning handles with defaults.
        self.assertIsInstance(rule, dict)


class TestDiagnosticsContracts(unittest.TestCase):
    def test_diagnostics_opt_in_is_additive_for_domain_search(self):
        baseline = search("minimalism", domain="style", max_results=1)
        diagnosed = search("minimalism", domain="style", max_results=1, diagnostics=True)
        self.assertEqual(set(baseline.keys()), set(diagnosed.keys()) - {"diagnostics"})
        self.assertIn("diagnostics", diagnosed)
        self.assertIn("top_score", diagnosed["diagnostics"])
        self.assertIn("query_rewrites", diagnosed["diagnostics"])

    def test_diagnostics_opt_in_is_additive_for_stack_search(self):
        baseline = search_stack("performance", "react", max_results=1)
        diagnosed = search_stack("performance", "react", max_results=1, diagnostics=True)
        self.assertEqual(set(baseline.keys()), set(diagnosed.keys()) - {"diagnostics"})
        self.assertIn("diagnostics", diagnosed)


if __name__ == "__main__":
    unittest.main()
