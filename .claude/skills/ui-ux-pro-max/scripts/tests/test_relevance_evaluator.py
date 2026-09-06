#!/usr/bin/env python3
"""Unit tests for metric math and relevance fixture validation."""

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = next(parent for parent in Path(__file__).resolve().parents
            if (parent / "scripts/evaluate-relevance.py").exists())
MODULE_PATH = ROOT / "scripts/evaluate-relevance.py"
SPEC = importlib.util.spec_from_file_location("evaluate_relevance", MODULE_PATH)
evaluator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evaluator)


class TestMetricMath(unittest.TestCase):
    def test_precision_counts_missing_ranks_as_non_relevant(self):
        self.assertEqual(evaluator.precision_at_k([2], 1), 1.0)
        self.assertAlmostEqual(evaluator.precision_at_k([2], 3), 1 / 3)
        self.assertEqual(evaluator.precision_at_k([], 3), 0.0)
        self.assertEqual(evaluator.precision_at_k([2], 0), 0.0)

    def test_reciprocal_rank_stops_at_k(self):
        self.assertEqual(evaluator.reciprocal_rank([0, 2, 0]), 0.5)
        self.assertEqual(evaluator.reciprocal_rank([0, 0, 0, 2]), 0.0)
        self.assertEqual(evaluator.reciprocal_rank([]), 0.0)

    def test_ndcg_uses_graded_gain_and_handles_empty_ideal(self):
        self.assertEqual(evaluator.ndcg_at_k([2, 1], [2, 1]), 1.0)
        self.assertLess(evaluator.ndcg_at_k([1, 2], [2, 1]), 1.0)
        self.assertEqual(evaluator.ndcg_at_k([], [], 3), 0.0)

    def test_result_grades_match_identity_subsets(self):
        results = [
            {"Category": "State", "Guideline": "Use useState", "Severity": "Medium"},
            {"Category": "State", "Guideline": "Use useReducer", "Severity": "Medium"},
        ]
        judgments = [
            {"identity": {"Guideline": "Use useReducer"}, "grade": 2},
            {"identity": {"Category": "State"}, "grade": 1},
        ]
        self.assertEqual(evaluator.grades_for_results(results, judgments), [1, 2])


class TestFixtureValidation(unittest.TestCase):
    @staticmethod
    def valid_fixture():
        case = {
            "id": "domain-style-minimal",
            "split": "calibration",
            "mode": "domain",
            "domain": "style",
            "query": "minimal grid",
            "judgments": [{"identity": {"Style Category": "Minimalism"}, "grade": 2}],
        }
        return {
            "schemaVersion": 1,
            "globalNegativeApplicability": {"domains": ["style"], "stacks": []},
            "cases": [dict(case, id=f"case-{index}") for index in range(60)],
        }

    def test_valid_schema(self):
        self.assertEqual(evaluator.validate_fixture(self.valid_fixture(), {"style": {}}, []), [])

    def test_rejects_bad_count_duplicate_id_and_grade(self):
        fixture = self.valid_fixture()
        fixture["cases"] = fixture["cases"][:2]
        fixture["cases"][1]["id"] = fixture["cases"][0]["id"]
        fixture["cases"][0]["judgments"][0]["grade"] = 3
        errors = "\n".join(evaluator.validate_fixture(fixture, {"style": {}}, []))
        self.assertIn("60-100", errors)
        self.assertIn("duplicate case id", errors)
        self.assertIn("grade 1 or 2", errors)


class TestThresholdGate(unittest.TestCase):
    def test_runtime_fingerprint_binds_reasoning_contract(self):
        original = evaluator.ROOT, evaluator.RUNTIME_DIR, evaluator.DATA_DIR
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runtime = root / "src/ui-ux-pro-max/scripts"
            data = root / "src/ui-ux-pro-max/data"
            runtime.mkdir(parents=True)
            data.mkdir(parents=True)
            for name in ("core.py", "design_system.py", "reasoning_contract.py"):
                (runtime / name).write_text(name, encoding="utf-8")
            (data / "styles.csv").write_text("No,Style\n1,Test\n", encoding="utf-8")
            evaluator.ROOT, evaluator.RUNTIME_DIR, evaluator.DATA_DIR = root, runtime, data
            try:
                before = evaluator.runtime_fingerprint()
                (runtime / "reasoning_contract.py").write_text("changed", encoding="utf-8")
                self.assertNotEqual(before, evaluator.runtime_fingerprint())
            finally:
                evaluator.ROOT, evaluator.RUNTIME_DIR, evaluator.DATA_DIR = original

    def test_oracle_fingerprint_hashes_the_selected_cases_file(self):
        canonical = evaluator.FIXTURE_DIR / "relevance-cases.json"
        with tempfile.TemporaryDirectory() as tmp:
            selected = Path(tmp) / "cases.json"
            selected.write_bytes(canonical.read_bytes())
            self.assertEqual(
                evaluator.oracle_fingerprint(selected), evaluator.oracle_fingerprint(canonical))
            selected.write_bytes(canonical.read_bytes() + b" ")
            self.assertNotEqual(
                evaluator.oracle_fingerprint(selected), evaluator.oracle_fingerprint(canonical))

    def test_metric_sample_and_locked_case_failures_are_actionable(self):
        report = {
            "metrics": {"precisionAt1": 0.5},
            "samples": {"retrieval": 1},
            "cases": [{"id": "locked", "grades": [0], "actual": [{"Style Category": "Wrong"}]}],
        }
        manifest = {
            "metrics": {"precisionAt1": {"floor": 0.8, "tolerance": 0.01}},
            "sampleMinimums": {"retrieval": 2},
            "lockedCases": {"locked": {"withinTop": 1, "minimumGrade": 2}},
        }
        manifest["splits"] = {"calibration": {"metrics": {}, "sampleMinimums": {}},
                              "held_out": {"metrics": {}, "sampleMinimums": {}}}
        report["splits"] = {"calibration": {"metrics": {}, "samples": {}},
                            "held_out": {"metrics": {}, "samples": {}}}
        failures = evaluator.check_thresholds(report, manifest)
        self.assertEqual(len(failures), 3)
        self.assertTrue(any("Wrong" in failure for failure in failures))

    def test_manifest_rejects_missing_contract_sections(self):
        errors = evaluator.validate_manifest({}, "fingerprint")
        self.assertTrue(any("missing sections" in error for error in errors))
        self.assertTrue(any("missing metrics" in error for error in errors))

    def test_manifest_rejects_non_finite_and_invalid_sample_values(self):
        manifest = {
            "schemaVersion": 1,
            "status": "approved",
            "approvingMaintainer": "maintainer",
            "units": "ratios",
            "splitPolicy": {},
            "runtimeFingerprint": "fingerprint",
            "oracleFingerprint": "oracle",
            "baselineRevision": "97eb2a2",
            "metrics": {name: {"floor": float("nan")} for name in evaluator.REQUIRED_METRICS},
            "sampleMinimums": {"cases": True},
            "lockedCases": {"case": {}},
            "splits": {
                split: {
                    "metrics": {name: {"floor": 0.0} for name in evaluator.REQUIRED_METRICS},
                    "sampleMinimums": {"cases": 1},
                } for split in ("calibration", "held_out")
            },
        }
        errors = evaluator.validate_manifest(manifest, "fingerprint", "oracle")
        self.assertTrue(any("finite" in error for error in errors))
        self.assertTrue(any("non-negative integer" in error for error in errors))

    def test_manifest_binds_oracle_and_validates_baseline_revision(self):
        manifest = {
            "schemaVersion": 1,
            "status": "approved",
            "approvingMaintainer": "maintainer",
            "units": "ratios",
            "splitPolicy": {},
            "runtimeFingerprint": "runtime",
            "oracleFingerprint": "wrong",
            "baselineRevision": "not-a-revision",
            "metrics": {name: {"floor": 0.0} for name in evaluator.REQUIRED_METRICS},
            "sampleMinimums": {"cases": 1},
            "lockedCases": {"case": {}},
            "splits": {
                split: {
                    "metrics": {name: {"floor": 0.0} for name in evaluator.REQUIRED_METRICS},
                    "sampleMinimums": {"cases": 1},
                } for split in ("calibration", "held_out")
            },
        }
        errors = evaluator.validate_manifest(manifest, "runtime", "expected")
        self.assertTrue(any("oracleFingerprint" in error for error in errors))
        self.assertTrue(any("baselineRevision" in error for error in errors))


if __name__ == "__main__":
    unittest.main(verbosity=2)
