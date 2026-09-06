#!/usr/bin/env python3
"""Validate UI/UX Pro Max CSV data files.

Checks every CSV under src/ui-ux-pro-max/data for structural issues that
csv.DictReader otherwise accepts silently:
- duplicate or blank header names
- rows with too many fields (unquoted commas)
- rows with too few fields (missing trailing columns)
- unexpected empty rows inside the dataset
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "src" / "ui-ux-pro-max" / "data"

# Every CSV under data/ is a runtime dataset loaded by core.py.
# (Former reference-only notes design.csv/draft.csv were removed: they were
# unused by the runtime and contained prompt-shaped free-form text.)
REFERENCE_ONLY: set[Path] = set()


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    rel = path.relative_to(REPO_ROOT)

    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        try:
            header = next(reader)
        except StopIteration:
            errors.append(f"{rel}: empty file")
            return errors

        if not header or all(not col.strip() for col in header):
            errors.append(f"{rel}: missing header")
            return errors

        blank_headers = [idx + 1 for idx, col in enumerate(header) if not col.strip()]
        if blank_headers:
            errors.append(f"{rel}: blank header columns {blank_headers}")

        duplicates = sorted({col for col in header if col and header.count(col) > 1})
        if duplicates:
            errors.append(f"{rel}: duplicate headers {duplicates}")

        expected = len(header)
        for line_no, row in enumerate(reader, start=2):
            if not row or all(not cell.strip() for cell in row):
                errors.append(f"{rel}:{line_no}: blank row")
                continue
            actual = len(row)
            if actual != expected:
                errors.append(
                    f"{rel}:{line_no}: expected {expected} fields, got {actual}"
                )

    return errors


def main() -> int:
    if not DATA_DIR.exists():
        print(f"CSV data directory not found: {DATA_DIR}", file=sys.stderr)
        return 2

    errors: list[str] = []
    checked = 0
    for path in sorted(DATA_DIR.rglob("*.csv")):
        if path in REFERENCE_ONLY:
            continue
        checked += 1
        errors.extend(validate_file(path))

    if errors:
        print("CSV validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        print(f"\nChecked {checked} runtime CSV files.", file=sys.stderr)
        return 1

    print(f"CSV validation passed: {checked} runtime CSV files checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
