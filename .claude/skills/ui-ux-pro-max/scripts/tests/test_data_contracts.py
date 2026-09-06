#!/usr/bin/env python3
"""Cross-file semantic contracts for curated design data."""

import copy
import csv
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = SCRIPTS_DIR.parent / "data"
sys.path.insert(0, str(SCRIPTS_DIR))

from core import AVAILABLE_STACKS, STACK_CONFIG  # noqa: E402
from design_system import DesignSystemGenerator  # noqa: E402
from reasoning_contract import apply_decision_rules, parse_decision_rules  # noqa: E402
import validate_data  # noqa: E402
from validate_data import _check_reasoning_contract  # noqa: E402


def read_rows(name):
    with (DATA_DIR / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def split_values(value, delimiter):
    return [part.strip() for part in value.split(delimiter) if part.strip()]


def style_identities(row):
    return [
        row["Style ID"], row["Style Category"],
        *split_values(row["Aliases"], "|"),
    ]


class TestStyleIdentityContract(unittest.TestCase):
    def setUp(self):
        self.styles = read_rows("styles.csv")

    def test_ids_aliases_status_and_parents_are_unambiguous(self):
        ids = {row["Style ID"] for row in self.styles}
        self.assertEqual(len(ids), len(self.styles))
        aliases = {}
        for row in self.styles:
            style_id = row["Style ID"]
            self.assertRegex(style_id, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
            self.assertIn(row["Status"], {"active", "supplemental", "deprecated"})
            parent = row["Parent Style ID"]
            if parent:
                self.assertIn(parent, ids)
                self.assertNotEqual(parent, style_id)
            if row["Status"] == "supplemental":
                self.assertTrue(parent)
            if row["Status"] == "deprecated":
                has_redirect = bool(row["Replacement Domain"] and row["Replacement ID"])
                self.assertNotEqual(bool(parent), has_redirect)
            for alias in split_values(row["Aliases"], "|"):
                self.assertNotIn(alias.casefold(), aliases)
                aliases[alias.casefold()] = style_id

    def test_every_product_and_reasoning_style_reference_resolves(self):
        lookup = {}
        for row in self.styles:
            lookup.update(
                (identity.casefold(), row["Style ID"])
                for identity in style_identities(row)
            )

        references = []
        for row in read_rows("products.csv"):
            references.extend(split_values(row["Primary Style Recommendation"], "+"))
            references.extend(split_values(row["Secondary Styles"], ","))
        for row in read_rows("ui-reasoning.csv"):
            references.extend(split_values(row["Style_Priority"], "+"))
        unresolved = sorted({
            reference for reference in references
            if reference.casefold() not in lookup
        })
        self.assertEqual([], unresolved)


class TestReasoningContract(unittest.TestCase):
    def test_known_product_sets_match_exactly(self):
        product_rows = read_rows("products.csv")
        color_rows = read_rows("colors.csv")
        reasoning_rows = read_rows("ui-reasoning.csv")
        self.assertEqual([192, 192, 192], [
            len(product_rows), len(color_rows), len(reasoning_rows)])
        products = {row["Product Type"] for row in product_rows}
        colors = {row["Product Type"] for row in color_rows}
        reasoning = {row["UI_Category"] for row in reasoning_rows}
        self.assertEqual(products, colors)
        self.assertEqual(products, reasoning)
        self.assertEqual(len(products), 192)

    def test_decision_rules_use_closed_array_grammar(self):
        for row in read_rows("ui-reasoning.csv"):
            with self.subTest(category=row["UI_Category"]):
                parsed = parse_decision_rules(row["Decision_Rules"])
                self.assertTrue(all(isinstance(actions, list) for actions in parsed.values()))

    def test_duplicate_unknown_keys_and_unknown_actions_fail_closed(self):
        invalid = (
            '{"must_have":["constraint:first"],"must_have":["constraint:second"]}',
            '{"if_not_supported":["constraint:test"]}',
            '{"must_have":["execute:arbitrary"]}',
            '{"must_have":[["constraint:nested"]]}',
            '{"must_have":[{"constraint":"nested"}]}',
        )
        for raw in invalid:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                parse_decision_rules(raw)

    def test_must_have_and_explicit_signals_are_applied_and_reported(self):
        rules = parse_decision_rules(
            '{"must_have":["constraint:keyboard-navigation"],'
            '"if_mobile":["constraint:optimize-touch-targets"]}')
        desktop = apply_decision_rules(rules, "accessible government portal")
        mobile = apply_decision_rules(rules, "accessible mobile government portal")
        self.assertEqual(desktop["constraints"], ["keyboard-navigation"])
        self.assertEqual(
            mobile["constraints"], ["keyboard-navigation", "optimize-touch-targets"])
        self.assertEqual(
            [item["condition"] for item in mobile["activated"]],
            ["must_have", "if_mobile"],
        )

    def test_generator_matches_reasoning_exactly_and_defaults_only_for_unknown(self):
        generator = DesignSystemGenerator()
        categories = [row["Product Type"] for row in read_rows("products.csv")]
        for category in categories:
            with self.subTest(category=category):
                self.assertEqual(generator._find_reasoning_rule(category)["UI_Category"], category)
        self.assertEqual(generator._find_reasoning_rule("Government"), {})
        self.assertTrue(generator._apply_reasoning("External Unknown", "unknown")["is_default"])

    def test_reasoning_patterns_reference_landing_identities(self):
        patterns = set()
        for row in read_rows("landing.csv"):
            patterns.add(row["Pattern Name"])
            patterns.update(alias for alias in row["Aliases"].split("|") if alias)
        reasoning = read_rows("ui-reasoning.csv")
        self.assertEqual(192, len(reasoning))
        for row in reasoning:
            with self.subTest(category=row["UI_Category"]):
                self.assertIn(row["Recommended_Pattern"], patterns)

    def test_every_known_product_generates_a_traceable_landing_pattern(self):
        generator = DesignSystemGenerator()
        patterns = {row["Pattern Name"] for row in read_rows("landing.csv")}
        for category in (row["Product Type"] for row in read_rows("products.csv")):
            with self.subTest(category=category):
                result = generator.generate(category)
                self.assertIn(result["source_identities"]["landing"], patterns)

    def test_representative_new_products_generate_traceable_sources(self):
        generator = DesignSystemGenerator()
        styles = {row["Style ID"] for row in read_rows("styles.csv")}
        colors = {row["Product Type"] for row in read_rows("colors.csv")}
        typography = {row["Font Pairing Name"] for row in read_rows("typography.csv")}
        patterns = {row["Pattern Name"] for row in read_rows("landing.csv")}
        cases = {
            "government grant portal accessible trustworthy": "Grant / Funding Portal",
            "API developer portal documentation": "API Developer Portal",
            "academic journal scholarly publishing accessible": "Academic Journal / Scholarly Publishing",
            "patient portal mobile secure": "Patient Portal / Health Records",
            "status page outage monitoring": "Status Page / Incident Management",
        }
        for query, category in cases.items():
            with self.subTest(query=query):
                result = generator.generate(query)
                sources = result["source_identities"]
                self.assertEqual(category, result["category"])
                self.assertFalse(result["reasoning_default"])
                self.assertEqual(category, sources["product"])
                self.assertEqual(category, sources["reasoning"])
                self.assertIn(sources["style"], styles)
                self.assertIn(sources["color"], colors)
                self.assertIn(sources["typography"], typography)
                self.assertIn(sources["landing"], patterns)

    def test_constraints_reach_domain_queries(self):
        generator = DesignSystemGenerator()
        calls = []

        def capture(query, domain, max_results):
            calls.append((domain, query))
            return {"domain": domain, "count": 0, "results": []}

        reasoning = {
            "pattern": "Unmapped Pattern",
            "color_mood": "Trustworthy",
            "typography_mood": "Readable",
            "constraints": ["keyboard-navigation", "touch-targets"],
        }
        with patch("design_system.search", side_effect=capture):
            generator._multi_domain_search(
                "public portal", "Government Portal", reasoning, ["Minimalism"])
        queried = {domain: query for domain, query in calls}
        for domain in ("style", "color", "typography", "landing"):
            with self.subTest(domain=domain):
                self.assertIn("keyboard navigation", queried[domain])

    def test_canonical_style_priority_is_not_limited_to_bm25_top_three(self):
        generator = DesignSystemGenerator()
        unrelated = [
            generator._resolve_style("Kinetic Brutalism (Mobile)"),
            generator._resolve_style("Glassmorphism"),
        ]
        selected = generator._select_best_match(unrelated, ["Brutalism"])
        self.assertEqual("brutalism", selected["Style ID"])

    def test_duplicate_semantic_reasoning_labels_fail_validation(self):
        product = {"Product Type": "Duplicate"}
        color = {"Product Type": "Duplicate"}
        reasoning = {
            "UI_Category": "Duplicate", "Decision_Rules": "{}", "Confidence": ""
        }
        problems = []
        _check_reasoning_contract(
            [product, dict(product)], [color, dict(color)],
            [reasoning, dict(reasoning)], set(), set(), problems,
        )
        self.assertTrue(any("duplicate" in problem.lower() for problem in problems))

    def test_every_exact_product_label_resolves_to_itself(self):
        generator = DesignSystemGenerator()
        for row in read_rows("products.csv"):
            category = row["Product Type"]
            with self.subTest(category=category):
                result = generator.generate(category)
                reasoning = generator._apply_reasoning(category, category)
                expected = [
                    generator._resolve_style(priority).get("Style ID")
                    for priority in reasoning["style_priority"]
                ]
                expected = [style_id for style_id in expected if style_id]
                self.assertEqual(category, result["category"])
                self.assertFalse(result["reasoning_default"])
                self.assertTrue(expected)
                self.assertEqual(expected[0], result["style"]["id"])

    def test_style_aliases_have_one_exact_owner(self):
        generator = DesignSystemGenerator()
        self.assertEqual(
            generator._resolve_style("Minimalism")["Style ID"],
            "minimalism-and-swiss-style",
        )
        self.assertEqual(generator._resolve_style("Clean Science"), {})
        self.assertEqual(
            generator._resolve_style("Holographic/HUD")["Style ID"],
            "hud-sci-fi-fui",
        )


class TestLandingAndStackContract(unittest.TestCase):
    def test_landing_sections_use_one_delimiter(self):
        for row in read_rows("landing.csv"):
            with self.subTest(pattern=row["Pattern Name"]):
                sections = row["Section Order"].split(" > ")
                self.assertGreaterEqual(len(sections), 2)
                self.assertTrue(all(section.strip() for section in sections))
                self.assertFalse(any(re.match(r"^\d+\.\s", section) for section in sections))

    def test_stack_schema_is_additive_and_uniform(self):
        for stack in AVAILABLE_STACKS:
            path = DATA_DIR / STACK_CONFIG[stack]["file"]
            with path.open(encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                self.assertTrue({"Applies To", "Status", "Verified At"} <= set(reader.fieldnames or []))
                for row in reader:
                    self.assertIn(row["Status"], {"active", "supplemental", "deprecated", "unverified"})

    def test_provenance_sidecar_has_stable_shape(self):
        payload = json.loads((DATA_DIR / "data-provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["schemaVersion"], 1)
        self.assertIsInstance(payload["records"], list)
        for record in payload["records"]:
            self.assertTrue({"entityKind", "entityId", "sourceFile", "status", "verifiedAt", "sources"} <= set(record))
            self.assertIsInstance(record["sources"], list)
            source_types = {source.get("type") for source in record["sources"]}
            if source_types <= {"derived"}:
                self.assertEqual("needs-review", record["sla"])

    def test_provenance_rejects_bad_shapes_enums_and_hosts_without_crashing(self):
        canonical = json.loads(
            (DATA_DIR / "data-provenance.json").read_text(encoding="utf-8")
        )
        cases = [[], None, "invalid"]
        malformed_record = copy.deepcopy(canonical)
        malformed_record["records"].append(None)
        cases.append(malformed_record)
        malformed_source = copy.deepcopy(canonical)
        malformed_source["records"][0]["sources"] = [None]
        cases.append(malformed_source)
        unapproved_source = copy.deepcopy(canonical)
        official = next(
            record for record in unapproved_source["records"]
            if any(source.get("type") == "official" for source in record["sources"])
        )
        official["sources"] = [
            {"type": "official", "ref": "https://evil.example/fake"}
        ]
        cases.append(unapproved_source)
        invalid_enums = copy.deepcopy(canonical)
        invalid_enums["records"][0].update(
            status="invented", sla="whenever", confidence=float("nan")
        )
        cases.append(invalid_enums)

        reasoning, styles = read_rows("ui-reasoning.csv"), read_rows("styles.csv")
        for index, payload in enumerate(cases):
            with self.subTest(case=index), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "data-provenance.json").write_text(
                    json.dumps(payload), encoding="utf-8"
                )
                problems = []
                with patch.object(validate_data, "DATA_DIR", root):
                    validate_data._check_provenance(reasoning, styles, problems)
                self.assertTrue(problems)

    def test_dataset_provenance_scope_binds_real_rows_and_fields(self):
        problems = []
        valid = validate_data._valid_dataset_source_key(
            "colors.csv", {"Scope": "No 1-192; Notes field"},
            ("dataset-contract", "valid"), problems,
        )
        self.assertTrue(valid)
        self.assertEqual([], problems)
        stack_problems = []
        self.assertTrue(validate_data._valid_dataset_source_key(
            "stacks/html-tailwind.csv", {"Scope": "No 57-59; Guideline field"},
            ("dataset-contract", "valid-stack"), stack_problems,
        ))
        self.assertEqual([], stack_problems)
        for source_file, source_key in (
            ("unknown.csv", {"Scope": "No 1; Notes field"}),
            ("colors.csv", {"Scope": "No 999; Notes field"}),
            ("colors.csv", {"Scope": "No 1; Invented Field"}),
        ):
            with self.subTest(source_file=source_file, source_key=source_key):
                problems = []
                self.assertFalse(validate_data._valid_dataset_source_key(
                    source_file, source_key, ("dataset-contract", "bad"), problems
                ))
                self.assertTrue(problems)


class TestGeneratedCatalogContract(unittest.TestCase):
    def load_json(self, name):
        return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))

    def test_canonical_catalogs_and_provenance_are_release_ready(self):
        problems = validate_data.validate()
        self.assertEqual([], [problem for problem in problems if "catalog" in problem])

    def test_font_license_and_typography_drift_fail_closed(self):
        fonts = read_rows("google-fonts.csv")
        licenses = self.load_json("google-font-licenses.json")
        licenses["families"][0]["license"] = "UNKNOWN"
        problems = []
        validate_data._check_font_catalog(
            fonts, licenses, read_rows("typography.csv"), problems
        )
        self.assertTrue(any("invalid active family" in problem for problem in problems))

        missing_font = copy.deepcopy(read_rows("typography.csv"))
        missing_font[0]["Google Fonts URL"] = (
            "https://fonts.googleapis.com/css2?family=Invented+Sans:wght@400"
        )
        problems = []
        validate_data._check_font_catalog(
            fonts, self.load_json("google-font-licenses.json"), missing_font, problems
        )
        self.assertTrue(any("absent from approved catalog" in problem for problem in problems))

    def test_font_source_revision_and_exclusion_policy_fail_closed(self):
        fonts = read_rows("google-fonts.csv")
        typography = read_rows("typography.csv")
        licenses = self.load_json("google-font-licenses.json")
        licenses["excludedFamilies"][0]["source"] = "https://github.com/google/fonts"
        problems = []
        validate_data._check_font_catalog(fonts, licenses, typography, problems)
        self.assertFalse(any("invalid exclusion" in problem for problem in problems))

        licenses["excludedFamilies"][0]["source"] = "https://github.com/other/fonts"
        licenses["source"]["revision"] = "main"
        problems = []
        validate_data._check_font_catalog(fonts, licenses, typography, problems)
        self.assertTrue(any("invalid exclusion" in problem for problem in problems))
        self.assertTrue(any("invalid source revision" in problem for problem in problems))

    def test_curated_icon_and_summary_drift_fail_closed(self):
        manifest = self.load_json("phosphor-icons-upstream.json")
        manifest["icons"][0]["clientImport"] = (
            'import { Wrong } from "@phosphor-icons/react"'
        )
        problems = []
        validate_data._check_phosphor_catalog(read_rows("icons.csv"), manifest, problems)
        self.assertTrue(any("invalid identity or imports" in problem for problem in problems))

        summary = self.load_json("catalog-summary.json")
        summary["counts"]["googleFonts"] -= 1
        problems = []
        validate_data._check_catalog_summary(
            summary,
            self.load_json("google-font-licenses.json"),
            self.load_json("phosphor-icons-upstream.json"),
            problems,
        )
        self.assertTrue(any("stale count for googleFonts" in problem for problem in problems))


if __name__ == "__main__":
    unittest.main(verbosity=2)
