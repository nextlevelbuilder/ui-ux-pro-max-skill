#!/usr/bin/env python3
"""Normalize the pinned Phosphor catalog and validate curated recommendations."""

import argparse
import csv
import json
import os
import re
import sys
import tempfile
from datetime import date
from pathlib import Path

PACKAGE = "@phosphor-icons/core"
PACKAGE_VERSION = "2.1.1"
REACT_PACKAGE = "@phosphor-icons/react"
REACT_VERSION = "2.1.10"
WEIGHTS = ["thin", "light", "regular", "bold", "fill", "duotone"]
CLIENT_MODULE = "@phosphor-icons/react"
SSR_MODULE = "@phosphor-icons/react/ssr"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PASCAL_RE = re.compile(r"^[A-Z][A-Za-z0-9]*$")
IMPORT_RE = re.compile(
    r"^import \{ ([A-Z][A-Za-z0-9]*) \} from ['\"](@phosphor-icons/react)['\"];?$"
)


def fail(message):
    raise ValueError(message)


def read_json(path, max_bytes=25_000_000):
    if path.stat().st_size > max_bytes:
        fail(f"{path}: input exceeds {max_bytes} bytes")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{path}: invalid JSON: {exc}")


def string_list(value, label):
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        fail(f"{label} must be a string array")
    return sorted(set(value), key=str.casefold)


def normalize_alias(value, label):
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) != {"name", "pascal_name"}:
        fail(f"{label}: alias must contain name and pascal_name")
    if not NAME_RE.fullmatch(value["name"]) or not PASCAL_RE.fullmatch(value["pascal_name"]):
        fail(f"{label}: invalid alias")
    return {"name": value["name"], "component": value["pascal_name"]}


def normalize_catalog(payload, expected_count):
    if not isinstance(payload, list) or len(payload) != expected_count:
        fail(f"Phosphor catalog expected {expected_count} icons, got {len(payload) if isinstance(payload, list) else 'non-list'}")
    required = {
        "name", "pascal_name", "codepoint", "categories", "figma_category", "tags",
        "published_in", "updated_in",
    }
    allowed = required | {"alias"}
    normalized = []
    names, components = set(), set()
    for index, item in enumerate(payload):
        if not isinstance(item, dict) or set(item) - allowed or not required <= item.keys():
            fail(f"Phosphor item {index}: invalid official IconEntry schema")
        name, component, codepoint = item["name"], item["pascal_name"], item["codepoint"]
        if not isinstance(name, str) or not NAME_RE.fullmatch(name):
            fail(f"Phosphor item {index}: invalid name")
        if not isinstance(component, str) or not PASCAL_RE.fullmatch(component):
            fail(f"{name}: invalid pascal_name")
        if not isinstance(codepoint, int) or isinstance(codepoint, bool) or codepoint < 0:
            fail(f"{name}: invalid codepoint")
        if name in names or component in components:
            fail(f"{name}: duplicate name or component")
        for field in ("published_in", "updated_in"):
            if not isinstance(item[field], (int, float)) or isinstance(item[field], bool) or item[field] <= 0:
                fail(f"{name}: invalid {field}")
        names.add(name)
        components.add(component)
        entry = {
            "name": name,
            "component": component,
            "codepoint": codepoint,
            "categories": string_list(item["categories"], f"{name}.categories"),
            "figmaCategory": item["figma_category"],
            "tags": string_list(item["tags"], f"{name}.tags"),
            "publishedIn": item["published_in"],
            "updatedIn": item["updated_in"],
            "clientImport": f'import {{ {component} }} from "{CLIENT_MODULE}"',
            "ssrImport": f'import {{ {component} }} from "{SSR_MODULE}"',
        }
        if not isinstance(entry["figmaCategory"], str) or not entry["figmaCategory"]:
            fail(f"{name}: invalid figma_category")
        alias = normalize_alias(item.get("alias"), name)
        if alias:
            entry["alias"] = alias
        normalized.append(entry)
    canonical_names = {item["name"] for item in normalized}
    canonical_components = {item["component"] for item in normalized}
    alias_names, alias_components = set(), set()
    for item in normalized:
        alias = item.get("alias")
        if not alias:
            continue
        if alias["name"] in canonical_names | alias_names or alias["component"] in canonical_components | alias_components:
            fail(f"{item['name']}: alias collides with a canonical or alias identity")
        alias_names.add(alias["name"])
        alias_components.add(alias["component"])
    return sorted(normalized, key=lambda item: item["name"])


def validate_package(payload):
    if not isinstance(payload, dict) or payload.get("name") != PACKAGE:
        fail(f"package metadata must identify {PACKAGE}")
    if payload.get("version") != PACKAGE_VERSION:
        fail(f"{PACKAGE} version must be {PACKAGE_VERSION}, got {payload.get('version')!r}")
    exports = payload.get("exports")
    if not isinstance(exports, dict) or not all(f"./{weight}/*.svg" in exports for weight in WEIGHTS):
        fail(f"{PACKAGE} package exports must contain all six weight asset paths")


def validate_react(package_payload, exports_payload, icons):
    if not isinstance(package_payload, dict) or package_payload.get("name") != REACT_PACKAGE:
        fail(f"React package metadata must identify {REACT_PACKAGE}")
    if package_payload.get("version") != REACT_VERSION:
        fail(f"{REACT_PACKAGE} version must be {REACT_VERSION}, got {package_payload.get('version')!r}")
    if not isinstance(exports_payload, dict) or set(exports_payload) != {"client", "ssr"}:
        fail("React exports input must contain only client and ssr arrays")
    client = set(string_list(exports_payload["client"], "client exports"))
    ssr = set(string_list(exports_payload["ssr"], "ssr exports"))
    components = {icon["component"] for icon in icons}
    missing_client, missing_ssr = sorted(components - client), sorted(components - ssr)
    if missing_client or missing_ssr:
        fail(f"React exports missing client={missing_client[:5]} ssr={missing_ssr[:5]}")


def checked_date(value):
    try:
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError):
        fail("verified-at must use YYYY-MM-DD")
    if parsed.year <= 1970 or parsed > date.today():
        fail(f"verified-at has suspicious date {value!r}")
    return value


def validate_curated(path, icons):
    by_name = {icon["name"]: icon for icon in icons}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"Icon Name", "Library", "Import Code"}
        if not reader.fieldnames or not required <= set(reader.fieldnames):
            fail(f"{path}: missing curated icon columns")
        validated = 0
        for line, row in enumerate(reader, start=2):
            if row["Library"] != "Phosphor":
                continue
            name = row["Icon Name"]
            if name not in by_name:
                fail(f"{path}:{line}: curated icon {name!r} is absent upstream")
            import_code = row["Import Code"]
            if not isinstance(import_code, str):
                fail(f"{path}:{line}: missing Phosphor client import")
            match = IMPORT_RE.fullmatch(import_code.strip())
            if not match or match.group(2) != CLIENT_MODULE:
                fail(f"{path}:{line}: invalid Phosphor client import")
            if match.group(1) != by_name[name]["component"]:
                fail(f"{path}:{line}: import component does not match {name!r}")
            validated += 1
    return validated


def write_manifest(path, icons, curated_count, verified_at):
    manifest = {
        "schemaVersion": 1,
        "source": {
            "package": PACKAGE,
            "version": PACKAGE_VERSION,
            "repository": "https://github.com/phosphor-icons/core",
            "reactPackage": REACT_PACKAGE,
            "reactVersion": REACT_VERSION,
        },
        "status": "active",
        "verifiedAt": verified_at,
        "iconCount": len(icons),
        "weights": WEIGHTS,
        "reactImports": {"clientModule": CLIENT_MODULE, "ssrModule": SSR_MODULE},
        "curatedValidatedCount": curated_count,
        "icons": icons,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                     prefix=f".{path.name}.", delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="JSON serialization of core's icons export")
    parser.add_argument("--package-json", type=Path, required=True, help="official core package.json")
    parser.add_argument("--react-package-json", type=Path, required=True)
    parser.add_argument("--react-exports-input", type=Path, required=True)
    parser.add_argument("--curated-csv", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verified-at", required=True, help="review date in YYYY-MM-DD form")
    parser.add_argument("--expected-count", type=int, default=1512)
    args = parser.parse_args()
    try:
        validate_package(read_json(args.package_json, max_bytes=1_000_000))
        icons = normalize_catalog(read_json(args.input), args.expected_count)
        validate_react(
            read_json(args.react_package_json, max_bytes=1_000_000),
            read_json(args.react_exports_input), icons,
        )
        write_manifest(
            args.output, icons, validate_curated(args.curated_csv, icons), checked_date(args.verified_at)
        )
    except (ValueError, OSError) as exc:
        print(f"refresh-icon-catalog: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
