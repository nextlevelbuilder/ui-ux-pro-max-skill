#!/usr/bin/env python3
"""Deterministic, stdlib-only relevance evaluator for the shipped search data."""

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "src/ui-ux-pro-max/scripts"
FIXTURE_DIR = RUNTIME_DIR / "tests/fixtures"
sys.path.insert(0, str(RUNTIME_DIR))
sys.path.insert(0, str(ROOT / "scripts"))

from core import (AVAILABLE_STACKS, CSV_CONFIG, DATA_DIR, STACK_CONFIG,
                  search, search_stack)  # noqa: E402
from design_system import DesignSystemGenerator, _palette_is_dark  # noqa: E402
from relevance_metrics import (REQUIRED_METRICS, check_thresholds, grades_for_results, ndcg_at_k,
                               precision_at_k, reciprocal_rank, validate_fixture,
                               validate_manifest)  # noqa: E402


def load_json(path):
    def reject_constant(value):
        raise ValueError(f"non-RFC JSON numeric constant: {value}")
    try:
        return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant)
    except (json.JSONDecodeError, OSError, ValueError) as error:
        raise SystemExit(f"Invalid JSON file {path}: {error}") from error


def runtime_fingerprint():
    paths = [
        RUNTIME_DIR / "core.py",
        RUNTIME_DIR / "design_system.py",
        RUNTIME_DIR / "reasoning_contract.py",
    ]
    paths += sorted(DATA_DIR.rglob("*.csv"))
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.relative_to(ROOT).as_posix().encode() + b"\0")
        digest.update(path.read_bytes() + b"\0")
    return digest.hexdigest()


def oracle_fingerprint(cases_path=None):
    """Bind approvals to the judgments and the code that grades them."""
    paths = [
        (Path(__file__), "scripts/evaluate-relevance.py"),
        (ROOT / "scripts/relevance_metrics.py", "scripts/relevance_metrics.py"),
        (cases_path or FIXTURE_DIR / "relevance-cases.json", "relevance-cases.json"),
    ]
    digest = hashlib.sha256()
    for path, logical_name in paths:
        digest.update(logical_name.encode() + b"\0")
        digest.update(path.read_bytes() + b"\0")
    return digest.hexdigest()


def validate_identities(fixture):
    errors, cache = [], {}
    for case in fixture["cases"]:
        if not case.get("judgments"):
            continue
        mode = case["mode"]
        domain = (case.get("domain") if mode == "domain" else case.get("expectedRoute"))
        if mode == "stack":
            path = DATA_DIR / STACK_CONFIG[case["stack"]]["file"]
        else:
            path = DATA_DIR / CSV_CONFIG[domain if mode != "design-system" else "product"]["file"]
        if path not in cache:
            with path.open(encoding="utf-8") as handle:
                cache[path] = list(csv.DictReader(handle))
        for judgment in case["judgments"]:
            identity = judgment["identity"]
            matches = [row for row in cache[path]
                       if all(str(row.get(key, "")) == str(value) for key, value in identity.items())]
            if len(matches) != 1:
                errors.append(f"{case['id']}: identity resolves to {len(matches)} rows in {path.name}: {identity}")
    return errors


def _result_identity(result):
    fields = ("Style Category", "Product Type", "Data Type", "Pattern Name",
              "Font Pairing Name", "Family", "Category", "Issue", "Icon Name",
              "Intensity Tier", "Trigger", "Guideline")
    return {field: result[field] for field in fields if result.get(field)}


def _mean(values):
    return sum(values) / len(values) if values else 0.0


def _design_coherence(case, result):
    expected = case.get("coherence", {})
    checks = []
    if expected.get("productCategory"):
        checks.append(result.get("category") == expected["productCategory"])
    if expected.get("styleNames"):
        checks.append(result.get("style", {}).get("name") in expected["styleNames"])
    if expected.get("patternNames"):
        checks.append(result.get("pattern", {}).get("name") in expected["patternNames"])
    if expected.get("colorMode"):
        actual = "dark" if _palette_is_dark(
            {"Background": result.get("colors", {}).get("background", "")}) else "light"
        checks.append(actual == expected["colorMode"])
    if expected.get("colorProductTypes"):
        checks.append(
            result.get("source_identities", {}).get("color")
            in expected["colorProductTypes"]
        )
    return checks


def _stats():
    return {"retrieval": [], "routes": [], "typo": [], "coherence": [],
            "negativePasses": 0, "negativeChecks": 0, "cases": 0}


def _summarize(stats):
    retrieval = stats["retrieval"]
    metrics = {
        "routingAccuracy": _mean(stats["routes"]),
        "precisionAt1": _mean([item["p1"] for item in retrieval]),
        "precisionAt3": _mean([item["p3"] for item in retrieval]),
        "mrrAt3": _mean([item["mrr3"] for item in retrieval]),
        "ndcgAt3": _mean([item["ndcg3"] for item in retrieval]),
        "negativeAbstention": (stats["negativePasses"] / stats["negativeChecks"]
                                if stats["negativeChecks"] else 0.0),
        "typoRecoveryAt3": _mean(stats["typo"]),
        "designSystemCoherence": _mean(stats["coherence"]),
    }
    samples = {"cases": stats["cases"], "retrieval": len(retrieval),
               "routing": len(stats["routes"]), "negativeChecks": stats["negativeChecks"],
               "typo": len(stats["typo"]), "designSystem": len(stats["coherence"])}
    return {"metrics": metrics, "samples": samples}


def evaluate(fixture, oracle=None):
    records, coverage = [], {}
    buckets = {name: _stats() for name in ("all", "calibration", "held_out")}
    applicability = fixture.get("globalNegativeApplicability")
    global_negatives = applicability == "all-domains-and-stacks" or isinstance(applicability, dict)
    for case in fixture["cases"]:
        targets = (buckets["all"], buckets[case["split"]])
        for stats in targets:
            stats["cases"] += 1
        mode, query = case["mode"], case["query"]
        judgments, tags = case.get("judgments", []), case.get("tags", [])
        if "hard-negative" in tags and global_negatives:
            labels = [f"domain:{domain}" for domain in CSV_CONFIG]
            labels += [f"stack:{stack}" for stack in AVAILABLE_STACKS]
            outputs = [search(query, domain, 3) for domain in CSV_CONFIG]
            outputs += [search_stack(query, stack, 3) for stack in AVAILABLE_STACKS]
            counts = [output.get("count", 0) for output in outputs]
            for stats in targets:
                stats["negativeChecks"] += len(counts)
                stats["negativePasses"] += sum(count == 0 for count in counts)
            records.append({"id": case["id"], "negativeChecks": len(counts),
                            "falsePositives": sum(count > 0 for count in counts),
                            "falsePositiveTargets": [label for label, count in zip(labels, counts) if count]})
            continue
        if mode == "design-system":
            result = DesignSystemGenerator().generate(query)
            checks = _design_coherence(case, result)
            for stats in targets:
                stats["coherence"].append(_mean(checks))
            records.append({"id": case["id"], "coherence": checks,
                            "actual": {"category": result.get("category"),
                                       "style": result.get("style", {}).get("name"),
                                       "pattern": result.get("pattern", {}).get("name")}})
            continue
        if mode == "stack":
            output = search_stack(query, case["stack"], 3, diagnostics=True)
            coverage[f"stack:{case['stack']}"] = coverage.get(f"stack:{case['stack']}", 0) + 1
        else:
            output = search(query, None if mode == "auto" else case["domain"], 3,
                            diagnostics=True)
            if mode == "domain":
                coverage[f"domain:{case['domain']}"] = coverage.get(f"domain:{case['domain']}", 0) + 1
        if case.get("expectedRoute"):
            actual_route = output.get("domain")
            for stats in targets:
                stats["routes"].append(actual_route == case["expectedRoute"])
        grades = grades_for_results(output.get("results", []), judgments)
        if judgments:
            ideal = [item["grade"] for item in judgments]
            scores = {"p1": precision_at_k(grades, 1), "p3": precision_at_k(grades, 3),
                      "mrr3": reciprocal_rank(grades), "ndcg3": ndcg_at_k(grades, ideal)}
            for stats in targets:
                stats["retrieval"].append(scores)
            if "typo" in tags:
                for stats in targets:
                    stats["typo"].append(any(grade > 0 for grade in grades[:3]))
        records.append({"id": case["id"], "route": output.get("domain"),
                        "expectedRoute": case.get("expectedRoute"), "grades": grades,
                        "scores": scores if judgments else {},
                        "diagnostics": output.get("diagnostics", {}),
                        "actual": [_result_identity(item) for item in output.get("results", [])]})
    summary = _summarize(buckets["all"])
    samples = summary["samples"]
    samples.update(coverage)
    splits = {name: _summarize(buckets[name]) for name in ("calibration", "held_out")}
    return {"schemaVersion": 1, "runtimeFingerprint": runtime_fingerprint(),
            "oracleFingerprint": oracle or oracle_fingerprint(),
            "metrics": summary["metrics"], "samples": samples,
            "splits": splits, "cases": records}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=FIXTURE_DIR / "relevance-cases.json")
    parser.add_argument("--thresholds", type=Path, default=FIXTURE_DIR / "relevance-thresholds.json")
    parser.add_argument("--baseline", type=Path, default=FIXTURE_DIR / "relevance-baseline.json")
    parser.add_argument("--split", choices=("all", "calibration", "held_out"), default="all")
    parser.add_argument("--write-baseline", type=Path)
    parser.add_argument("--no-thresholds", action="store_true")
    args = parser.parse_args()
    fixture = load_json(args.cases)
    fingerprint = runtime_fingerprint()
    oracle = oracle_fingerprint(args.cases)
    errors = validate_fixture(fixture, CSV_CONFIG, AVAILABLE_STACKS) + validate_identities(fixture)
    if errors:
        raise SystemExit("Invalid relevance fixture:\n- " + "\n- ".join(errors))
    selected_split = args.split
    if selected_split != "all":
        fixture = {**fixture, "cases": [case for case in fixture["cases"]
                                        if case["split"] == selected_split]}
    report = evaluate(fixture, oracle)
    if args.write_baseline:
        args.write_baseline.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("metrics", "samples", "splits")},
                     indent=2, sort_keys=True))
    manifest = load_json(args.thresholds)
    manifest_errors = validate_manifest(manifest, fingerprint, oracle)
    if manifest_errors and not args.no_thresholds:
        raise SystemExit("Invalid threshold manifest:\n- " + "\n- ".join(manifest_errors))
    failures = [] if args.no_thresholds else check_thresholds(report, manifest, selected_split)
    if failures:
        baseline = load_json(args.baseline)
        old = {record["id"]: record for record in baseline["cases"]}
        suspect = [record for record in report["cases"] if old.get(record["id"]) != record]
        if not suspect:
            suspect = [record for record in report["cases"]
                       if (record.get("grades") and record["grades"][0] < 2)
                       or record.get("falsePositives", 0)
                       or ("coherence" in record and not all(record["coherence"]))]
        detail = "\n".join(f"  {item['id']}: {item.get('actual', item)}"
                           for item in suspect)
        raise SystemExit("Relevance gate failed:\n- " + "\n- ".join(failures)
                         + ("\nProblem cases:\n" + detail if detail else ""))


if __name__ == "__main__":
    main()
