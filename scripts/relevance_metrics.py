"""Pure metric, schema, and threshold helpers for relevance evaluation."""

import math
import re

REQUIRED_METRICS = {
    "routingAccuracy", "precisionAt1", "precisionAt3", "mrrAt3", "ndcgAt3",
    "negativeAbstention", "typoRecoveryAt3", "designSystemCoherence",
}


def precision_at_k(grades, k):
    return sum(grade > 0 for grade in grades[:k]) / k if k else 0.0


def reciprocal_rank(grades, k=3):
    for rank, grade in enumerate(grades[:k], start=1):
        if grade > 0:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(grades, ideal_grades, k=3):
    def dcg(values):
        return sum((2 ** grade - 1) / math.log2(rank + 1)
                   for rank, grade in enumerate(values[:k], start=1))
    ideal = dcg(sorted(ideal_grades, reverse=True))
    return dcg(grades) / ideal if ideal else 0.0


def grades_for_results(results, judgments):
    def matches(result, identity):
        return all(str(result.get(field, "")) == str(value)
                   for field, value in identity.items())
    return [max((item["grade"] for item in judgments
                 if matches(result, item["identity"])), default=0)
            for result in results]


def validate_fixture(fixture, domains, stacks, require_coverage=True):
    errors, seen, domain_coverage, stack_coverage = [], set(), set(), set()
    cases = fixture.get("cases", [])
    if fixture.get("schemaVersion") != 1:
        errors.append("schemaVersion must be 1")
    if not 60 <= len(cases) <= 100:
        errors.append("fixture must contain 60-100 cases")
    applicability = fixture.get("globalNegativeApplicability", {})
    if set(applicability.get("domains", [])) != set(domains):
        errors.append("hard-negative domain applicability must cover every registered domain")
    if set(applicability.get("stacks", [])) != set(stacks):
        errors.append("hard-negative stack applicability must cover every registered stack")
    for case in cases:
        case_id = case.get("id", "<missing>")
        if case_id in seen:
            errors.append(f"duplicate case id: {case_id}")
        seen.add(case_id)
        if case.get("split") not in {"calibration", "held_out"}:
            errors.append(f"{case_id}: invalid split")
        if case.get("mode") not in {"domain", "stack", "auto", "design-system"}:
            errors.append(f"{case_id}: invalid mode")
        if case.get("domain") and case["domain"] not in domains:
            errors.append(f"{case_id}: unknown domain {case['domain']}")
        if case.get("stack") and case["stack"] not in stacks:
            errors.append(f"{case_id}: unknown stack {case['stack']}")
        if case.get("judgments"):
            domain_coverage.update([case["domain"]] if case.get("mode") == "domain" else [])
            stack_coverage.update([case["stack"]] if case.get("mode") == "stack" else [])
        for judgment in case.get("judgments", []):
            if judgment.get("grade") not in {1, 2} or not judgment.get("identity"):
                errors.append(f"{case_id}: judgment needs identity and grade 1 or 2")
    if require_coverage:
        missing_domains = sorted(set(domains) - domain_coverage)
        missing_stacks = sorted(set(stacks) - stack_coverage)
        if missing_domains:
            errors.append(f"positive coverage missing domains: {', '.join(missing_domains)}")
        if missing_stacks:
            errors.append(f"positive coverage missing stacks: {', '.join(missing_stacks)}")
    return errors


def validate_manifest(manifest, runtime_fingerprint, oracle_fingerprint=None):
    errors = []
    required = {"schemaVersion", "status", "approvingMaintainer", "units", "splitPolicy",
                "runtimeFingerprint", "oracleFingerprint", "baselineRevision",
                "metrics", "sampleMinimums", "lockedCases", "splits"}
    missing = sorted(required - set(manifest))
    if missing:
        errors.append(f"threshold manifest missing sections: {', '.join(missing)}")
    if manifest.get("schemaVersion") != 1:
        errors.append("threshold schemaVersion must be 1")
    if manifest.get("status") not in {"provisional-baseline-regression-gate", "approved"}:
        errors.append("threshold status must explicitly be provisional or approved")
    if not manifest.get("approvingMaintainer"):
        errors.append("approvingMaintainer must be recorded")
    if manifest.get("runtimeFingerprint") != runtime_fingerprint:
        errors.append("runtimeFingerprint does not match canonical runtime/data")
    if oracle_fingerprint is not None and manifest.get("oracleFingerprint") != oracle_fingerprint:
        errors.append("oracleFingerprint does not match judgments/evaluator logic")
    revision = manifest.get("baselineRevision")
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{7,40}", revision):
        errors.append("baselineRevision must be a 7-40 character lowercase git revision")
    for label, rules in [("aggregate", manifest.get("metrics", {}))] + [
            (name, manifest.get("splits", {}).get(name, {}).get("metrics", {}))
            for name in ("calibration", "held_out")]:
        absent = sorted(REQUIRED_METRICS - set(rules))
        if absent:
            errors.append(f"{label} thresholds missing metrics: {', '.join(absent)}")
    for name in ("calibration", "held_out"):
        if not manifest.get("splits", {}).get(name, {}).get("sampleMinimums"):
            errors.append(f"{name} sample minimums are required")
    if not manifest.get("sampleMinimums") or not manifest.get("lockedCases"):
        errors.append("aggregate sampleMinimums and lockedCases must not be empty")
    rule_sets = [("aggregate", manifest.get("metrics", {}))] + [
        (name, manifest.get("splits", {}).get(name, {}).get("metrics", {}))
        for name in ("calibration", "held_out")]
    for label, rules in rule_sets:
        for metric, rule in rules.items():
            if set(rule) - {"floor", "tolerance"} or "floor" not in rule:
                errors.append(f"{label}.{metric}: rule allows only floor and tolerance")
                continue
            floor, tolerance = rule.get("floor"), rule.get("tolerance", 0)
            if (isinstance(floor, bool) or not isinstance(floor, (int, float))
                    or not math.isfinite(floor) or not 0 <= floor <= 1):
                errors.append(f"{label}.{metric}: floor must be finite in [0,1]")
            if (isinstance(tolerance, bool) or not isinstance(tolerance, (int, float))
                    or not math.isfinite(tolerance) or not 0 <= tolerance <= 1):
                errors.append(f"{label}.{metric}: tolerance must be finite in [0,1]")
    sample_sets = [("aggregate", manifest.get("sampleMinimums", {}))] + [
        (name, manifest.get("splits", {}).get(name, {}).get("sampleMinimums", {}))
        for name in ("calibration", "held_out")]
    for label, samples in sample_sets:
        for sample, minimum in samples.items():
            if isinstance(minimum, bool) or not isinstance(minimum, int) or minimum < 0:
                errors.append(f"{label}.{sample}: sample minimum must be a non-negative integer")
    return errors


def _check_rules(report, rules, prefix=""):
    failures = []
    for metric, rule in rules["metrics"].items():
        value = report["metrics"].get(metric)
        if value is None or value + rule.get("tolerance", 0) < rule["floor"]:
            failures.append(f"{prefix}{metric}: {value!r} below floor {rule['floor']}")
    for sample, minimum in rules["sampleMinimums"].items():
        if report["samples"].get(sample, 0) < minimum:
            failures.append(f"{prefix}{sample}: sample count below {minimum}")
    return failures


def check_thresholds(report, manifest, selected_split="all"):
    if selected_split != "all":
        rules = manifest["splits"][selected_split]
        return _check_rules(report, rules, f"{selected_split}.")
    failures = _check_rules(report, manifest)
    for split, rules in manifest["splits"].items():
        failures += _check_rules(report["splits"][split], rules, f"{split}.")
    records = {record["id"]: record for record in report["cases"]}
    for case_id, rule in manifest.get("lockedCases", {}).items():
        record = records.get(case_id, {})
        grades = record.get("grades", [])
        if max(grades[:rule.get("withinTop", 1)], default=0) < rule.get("minimumGrade", 2):
            failures.append(f"{case_id}: locked result missing from top {rule.get('withinTop', 1)}; actual={record.get('actual', [])}")
    return failures
