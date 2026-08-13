#!/usr/bin/env python3
"""Generate or verify deterministic catalog counts and snapshot hashes."""

import argparse
import csv
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "src/ui-ux-pro-max/data"
OUTPUT = DATA / "catalog-summary.json"


def rows(name):
    with (DATA / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def checked_date(value):
    try:
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("verified-at must use YYYY-MM-DD") from exc
    if parsed.year <= 1970 or parsed > date.today():
        raise ValueError(f"verified-at has suspicious date {value!r}")
    return value


def build(verified_at):
    styles = rows("styles.csv")
    stack_paths = sorted((DATA / "stacks").glob("*.csv"))
    licenses = load_json("google-font-licenses.json")
    icons = load_json("phosphor-icons-upstream.json")
    excluded = licenses.get("excludedFamilies", [])
    counts = {
        "styles": {
            "total": len(styles),
            "searchable": sum(row.get("Status") != "deprecated" for row in styles),
            "active": sum(row.get("Status") == "active" for row in styles),
            "supplemental": sum(row.get("Status") == "supplemental" for row in styles),
            "deprecated": sum(row.get("Status") == "deprecated" for row in styles),
        },
        "products": len(rows("products.csv")),
        "palettes": len(rows("colors.csv")),
        "reasoningProfiles": len(rows("ui-reasoning.csv")),
        "fontPairings": len(rows("typography.csv")),
        "googleFonts": len(rows("google-fonts.csv")),
        "curatedIcons": len(rows("icons.csv")),
        "upstreamPhosphorIcons": icons.get("iconCount"),
        "uxGuidelines": len(rows("ux-guidelines.csv")),
        "motionPresets": len(rows("motion.csv")),
        "chartTypes": len(rows("charts.csv")),
        "stacks": len(stack_paths),
        "stackGuidelines": sum(len(rows(f"stacks/{path.name}")) for path in stack_paths),
    }
    return {
        "schemaVersion": 1,
        "verifiedAt": checked_date(verified_at),
        "counts": counts,
        "snapshots": {
            name: {"sha256": digest(DATA / name)}
            for name in (
                "google-fonts.csv", "google-font-licenses.json",
                "icons.csv", "phosphor-icons-upstream.json",
            )
        },
        "promotionPolicy": {
            "changedFamilySetRequiresExplicitApproval": True,
            "relevanceGateRequired": True,
            "unlicensedFamiliesExcluded": True,
        },
        "pendingCandidates": sorted(
            ({"family": item["name"], "reason": item["reason"]} for item in excluded),
            key=lambda item: item["family"].casefold(),
        ),
    }


def check_readme_counts(summary):
    counts = summary["counts"]
    exclusions = len(summary["pendingCandidates"])
    expected = {
        "README.md": (
            f"**{counts['googleFonts']:,} approved Google Fonts**",
            f"**{exclusions} review exclusions**",
            f"**{counts['curatedIcons']} curated rows**",
            f"**{counts['upstreamPhosphorIcons']:,}-icon upstream Phosphor manifest**",
        ),
        "README.zh.md": (
            f"**{counts['googleFonts']:,} 个已批准的 Google Fonts**",
            f"**{exclusions} 个待审核的排除项**",
            f"**{counts['curatedIcons']} 条精选记录**",
            f"**{counts['upstreamPhosphorIcons']:,}-icon Phosphor upstream manifest**",
        ),
    }
    for name, tokens in expected.items():
        text = (ROOT / name).read_text(encoding="utf-8")
        missing = [token for token in tokens if token not in text]
        if missing:
            raise ValueError(f"{name} catalog counts are stale: {', '.join(missing)}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verified-at")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        verified_at = args.verified_at
        if args.check and not verified_at:
            if not OUTPUT.exists():
                raise ValueError("catalog-summary.json is missing")
            verified_at = json.loads(OUTPUT.read_text(encoding="utf-8")).get("verifiedAt")
        if not verified_at:
            raise ValueError("--verified-at is required when generating the summary")
        summary = build(verified_at)
        content = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
        if args.check:
            if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content:
                raise ValueError("catalog-summary.json is stale; regenerate it")
            check_readme_counts(summary)
        else:
            OUTPUT.write_text(content, encoding="utf-8")
    except (KeyError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"generate-catalog-summary: {exc}", file=sys.stderr)
        return 2
    print("Catalog summary is current." if args.check else "Generated catalog summary.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
