#!/usr/bin/env python3
"""Refresh the Google Fonts catalog from official, reviewable inputs."""

import argparse
import ast
import csv
import io
import json
import math
import os
import re
import sys
import urllib.parse
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path
import tempfile

API_URL = "https://www.googleapis.com/webfonts/v1/webfonts"
MAX_INPUT_BYTES = 25_000_000
CSV_FIELDS = [
    "Family", "Category", "Stroke", "Classifications", "Keywords", "Styles",
    "Variable Axes", "Subsets", "Designers", "Popularity Rank", "Trending Rank",
    "Is Noto", "Date Added", "Last Modified", "Google Fonts URL",
]
MANUAL_FIELDS = {
    "Stroke", "Classifications", "Keywords", "Popularity Rank", "Trending Rank", "Is Noto",
}
CATALOG_FIELDS = {
    "family", "displayName", "category", "stroke", "classifications", "size", "subsets",
    "fonts", "axes", "designers", "lastModified", "dateAdded", "popularity", "trending",
    "defaultSort", "androidFragment", "isNoto", "colorCapabilities", "primaryScript",
    "primaryLanguage", "isOpenSource", "isBrandFont", "languages",
}
LICENSES = {"OFL", "APACHE2", "UFL"}
CATEGORIES = {
    "display": "Display", "handwriting": "Handwriting", "monospace": "Monospace",
    "sans-serif": "Sans Serif", "serif": "Serif",
}
VARIANT_RE = re.compile(r"^(regular|italic|(?:[1-9]00|1000)(?:italic)?)$")
METADATA_FIELD_RE = re.compile(
    r'^(name|designer|license|date_added):\s*("(?:[^"\\]|\\.)*")\s*$', re.M
)
METADATA_REVISION_RE = re.compile(r"^(?:[0-9a-f]{40}|fixture-[a-z0-9][a-z0-9.-]{0,63})$")


def fail(message):
    raise ValueError(message)


def read_json(path, max_bytes=MAX_INPUT_BYTES):
    if path.stat().st_size > max_bytes:
        fail(f"{path}: input exceeds {max_bytes} bytes")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{path}: invalid JSON: {exc}")


def checked_date(value, label):
    if not isinstance(value, str):
        fail(f"{label}: date must be YYYY-MM-DD")
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        fail(f"{label}: invalid date {value!r}")
    if parsed.year <= 1970 or parsed > date.today():
        fail(f"{label}: suspicious date {value!r}")
    return value


def valid_exclusion_source(value):
    if not isinstance(value, str):
        return False
    try:
        parsed = urllib.parse.urlparse(value)
        has_credentials_or_port = bool(parsed.username or parsed.password or parsed.port)
    except ValueError:
        return False
    if parsed.scheme != "https" or has_credentials_or_port:
        return False
    if parsed.hostname == "fonts.google.com":
        return bool(parsed.path)
    return parsed.hostname == "github.com" and (
        parsed.path == "/google/fonts" or parsed.path.startswith("/google/fonts/")
    )


def fetch_live_catalog():
    key = os.environ.get("GOOGLE_FONTS_API_KEY")
    if not key:
        fail("GOOGLE_FONTS_API_KEY is required for --live; use --api-input for offline CI")
    url = API_URL + "?" + urllib.parse.urlencode({"key": key, "capability": "VF"})
    with urllib.request.urlopen(url, timeout=30) as response:
        length = response.headers.get("Content-Length")
        if length and int(length) > MAX_INPUT_BYTES:
            fail(f"Google Fonts response exceeds {MAX_INPUT_BYTES} bytes")
        raw = response.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        fail(f"Google Fonts response exceeds {MAX_INPUT_BYTES} bytes")
    return json.loads(raw)


def validate_api(payload, expected_count):
    if not isinstance(payload, dict) or payload.get("kind") != "webfonts#webfontList":
        fail("Google Fonts response must be a webfonts#webfontList object")
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        fail("Google Fonts response items must be a non-empty array")
    if expected_count is not None and len(items) != expected_count:
        fail(f"Google Fonts response expected {expected_count} items, got {len(items)}")
    required = {"family", "variants", "subsets", "version", "lastModified", "files", "category", "kind"}
    seen = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict) or not required <= item.keys():
            fail(f"Google Fonts item {index}: missing required Developer API fields")
        family = item["family"]
        if not isinstance(family, str) or not family.strip() or family in seen:
            fail(f"Google Fonts item {index}: invalid or duplicate family")
        seen.add(family)
        if item["kind"] != "webfonts#webfont" or item["category"] not in CATEGORIES:
            fail(f"{family}: invalid kind or category")
        for field in ("variants", "subsets"):
            if not isinstance(item[field], list) or not item[field] or not all(isinstance(v, str) and v for v in item[field]):
                fail(f"{family}: {field} must be a non-empty string array")
        if not all(VARIANT_RE.fullmatch(v) for v in item["variants"]):
            fail(f"{family}: invalid variant")
        if not isinstance(item["files"], dict) or set(item["files"]) != set(item["variants"]):
            fail(f"{family}: files must match variants exactly")
        for file_url in item["files"].values():
            parsed_url = urllib.parse.urlparse(file_url) if isinstance(file_url, str) else None
            if not parsed_url or parsed_url.scheme != "https" or parsed_url.hostname != "fonts.gstatic.com" or not parsed_url.path:
                fail(f"{family}: font files must use https://fonts.gstatic.com")
        checked_date(item["lastModified"], family)
        axes = item.get("axes", [])
        if not isinstance(axes, list) or not all(
            isinstance(a, dict) and set(a) == {"tag", "start", "end"}
            and isinstance(a["tag"], str) and isinstance(a["start"], (int, float))
            and not isinstance(a["start"], bool) and isinstance(a["end"], (int, float))
            and not isinstance(a["end"], bool) and a["start"] <= a["end"] for a in axes
        ):
            fail(f"{family}: invalid axes")
        if len({axis["tag"] for axis in axes}) != len(axes):
            fail(f"{family}: duplicate axis tags")
    return items


def validate_metadata(payload, families):
    allowed_top = {"schemaVersion", "source", "familyCount", "families", "excludedFamilies"}
    if not isinstance(payload, dict) or set(payload) - allowed_top or not {"families", "excludedFamilies"} <= set(payload) or not isinstance(payload["families"], list):
        fail("google/fonts metadata must contain families and excludedFamilies arrays")
    result = {}
    for index, item in enumerate(payload["families"]):
        required = {"name", "license", "date_added", "designer"}
        allowed = required | {"status", "verifiedAt"}
        if not isinstance(item, dict) or set(item) - allowed or not required <= item.keys():
            fail(f"google/fonts metadata item {index}: missing required fields")
        name = item["name"]
        if not isinstance(name, str) or name in result:
            fail(f"google/fonts metadata item {index}: invalid or duplicate name")
        if item["license"] not in LICENSES:
            fail(f"{name}: invalid or missing official license {item['license']!r}")
        checked_date(item["date_added"], name)
        if item.get("status", "active") != "active":
            fail(f"{name}: covered license metadata status must be active")
        if "verifiedAt" in item:
            checked_date(item["verifiedAt"], f"{name}.verifiedAt")
        designers = item["designer"] if isinstance(item["designer"], list) else [item["designer"]]
        if not designers or not all(isinstance(value, str) and value.strip() for value in designers):
            fail(f"{name}: invalid designer metadata")
        result[name] = {**item, "designer": designers}
    exclusions = {}
    if not isinstance(payload["excludedFamilies"], list):
        fail("google/fonts excludedFamilies must be an array")
    for index, item in enumerate(payload["excludedFamilies"]):
        if not isinstance(item, dict) or set(item) - {"name", "reason", "source", "status", "verifiedAt"} or not {"name", "reason", "source"} <= set(item):
            fail(f"excludedFamilies item {index}: invalid schema")
        name = item["name"]
        if not isinstance(name, str) or not name or name in exclusions or name in result:
            fail(f"excludedFamilies item {index}: invalid, duplicate, or covered name")
        if not isinstance(item["reason"], str) or not item["reason"].strip() or not valid_exclusion_source(item["source"]):
            fail(f"{name}: exclusion needs a reason and an official Google Fonts source")
        if item.get("status", "needs-review") != "needs-review":
            fail(f"{name}: exclusion status must be needs-review")
        if "verifiedAt" in item:
            checked_date(item["verifiedAt"], f"{name}.verifiedAt")
        exclusions[name] = item
    expected, covered = set(families), set(result) | set(exclusions)
    missing, unexpected = sorted(expected - covered), sorted(covered - expected)
    if missing:
        fail(f"google/fonts metadata missing families: {', '.join(missing[:5])}")
    if unexpected:
        fail(f"google/fonts metadata has unexpected families: {', '.join(unexpected[:5])}")
    return result, exclusions


def metadata_from_repository(root, families):
    """Normalize exact-family METADATA.pb records from an official google/fonts checkout."""
    if not root.is_dir():
        fail(f"{root}: google/fonts metadata root is missing")
    records = {}
    for path in root.rglob("METADATA.pb"):
        values = {}
        try:
            fields = METADATA_FIELD_RE.findall(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError) as exc:
            fail(f"{path}: unreadable METADATA.pb: {exc}")
        for key, raw in fields:
            values.setdefault(key, []).append(ast.literal_eval(raw))
        names = values.get("name", [])
        if not names:
            continue
        family = names[0]
        record = {
            "name": family,
            "designer": values.get("designer", []),
            "license": (values.get("license") or [""])[0],
            "date_added": (values.get("date_added") or [""])[0],
        }
        if family in records and records[family] != record:
            fail(f"conflicting official metadata for {family}")
        records[family] = record
    if not records:
        fail(f"{root}: no METADATA.pb family records found")

    requested = list(families)
    covered = [records[family] for family in requested if family in records]
    if len(covered) < max(1, math.ceil(len(requested) * 0.9)):
        fail(f"{root}: official metadata covers fewer than 90% of requested families")
    excluded = [{
        "name": family,
        "reason": "No exact-family METADATA.pb entry in the official google/fonts snapshot",
        "source": "https://fonts.google.com/specimen/" + urllib.parse.quote_plus(family),
    } for family in requested if family not in records]
    return {"families": covered, "excludedFamilies": excluded}


def validate_catalog(payload, expected_count):
    if not isinstance(payload, dict) or set(payload) != {"axisRegistry", "familyMetadataList", "promotedScript"}:
        fail("Fonts catalog cross-check must contain axisRegistry, familyMetadataList, and promotedScript")
    items = payload["familyMetadataList"]
    if not isinstance(items, list) or not items:
        fail("Fonts catalog items must be a non-empty array")
    if expected_count is not None and len(items) != expected_count:
        fail(f"Fonts catalog expected {expected_count} items, got {len(items)}")
    seen = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict) or set(item) != CATALOG_FIELDS:
            fail(f"Fonts catalog item {index}: invalid familyMetadataList schema")
        family = item["family"]
        if not isinstance(family, str) or not family or family in seen:
            fail(f"Fonts catalog item {index}: invalid or duplicate family")
        seen.add(family)
        if item["category"] not in CATEGORIES.values():
            fail(f"{family}: invalid catalog category")
        for field in ("subsets", "designers", "classifications"):
            if not isinstance(item[field], list) or not all(isinstance(value, str) and value for value in item[field]):
                fail(f"{family}: invalid {field}")
        if not item["designers"] or not isinstance(item["fonts"], dict) or not item["fonts"]:
            fail(f"{family}: designers and fonts must be non-empty")
        if not isinstance(item["size"], int) or isinstance(item["size"], bool) or item["size"] < 0:
            fail(f"{family}: invalid catalog size")
        for metrics in item["fonts"].values():
            if not isinstance(metrics, dict) or set(metrics) != {"thickness", "slant", "width", "lineHeight"}:
                fail(f"{family}: invalid catalog font metrics")
            if not all(value is None or (
                isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
            ) for value in metrics.values()):
                fail(f"{family}: invalid catalog font metric value")
        # The live catalog uses `1`/`1i` for a small set of variable families.
        if not all(isinstance(key, str) and re.fullmatch(r"(?:1|[1-9]00|1000)i?", key) for key in item["fonts"]):
            fail(f"{family}: invalid catalog font variants")
        if not all(isinstance(item[field], int) and not isinstance(item[field], bool) and item[field] >= 0
                   for field in ("popularity", "trending")) or not isinstance(item["isNoto"], bool):
            fail(f"{family}: invalid popularity, trending, or isNoto")
        checked_date(item["dateAdded"], family)
        checked_date(item["lastModified"], family)
        if not isinstance(item["axes"], list) or not all(
            isinstance(axis, dict) and {"tag", "min", "max", "defaultValue"} == set(axis)
            and isinstance(axis["tag"], str) and isinstance(axis["min"], (int, float))
            and not isinstance(axis["min"], bool) and isinstance(axis["max"], (int, float))
            and not isinstance(axis["max"], bool) and isinstance(axis["defaultValue"], (int, float))
            and not isinstance(axis["defaultValue"], bool) and axis["min"] <= axis["defaultValue"] <= axis["max"]
            and all(math.isfinite(axis[field]) for field in ("min", "max", "defaultValue"))
            for axis in item["axes"]
        ):
            fail(f"{family}: invalid catalog axes")
        if len({axis["tag"] for axis in item["axes"]}) != len(item["axes"]):
            fail(f"{family}: duplicate axis tags")
    return items


def variant_key(value):
    weight = 400 if value in {"regular", "italic"} else int(re.match(r"\d+", value).group())
    return weight, value.endswith("italic") or value == "italic"


def variant_label(value):
    if value == "regular":
        return "400"
    if value == "italic":
        return "400i"
    return value.replace("italic", "i")


def load_existing(path):
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != CSV_FIELDS:
            fail(f"{path}: unexpected Google Fonts CSV schema")
        return {row["Family"]: row for row in reader}


def load_overrides(path):
    if not path:
        return {}
    payload = read_json(path)
    if not isinstance(payload, dict) or set(payload) != {"families"} or not isinstance(payload["families"], dict):
        fail("override file must contain only a families object")
    for family, values in payload["families"].items():
        if not isinstance(values, dict) or not set(values) <= MANUAL_FIELDS or not all(isinstance(v, str) for v in values.values()):
            fail(f"{family}: overrides may only contain string-valued reviewed fields")
    return payload["families"]


def normalize(items, metadata, existing, overrides):
    rows = []
    for item in sorted(items, key=lambda value: value["family"].casefold()):
        family = item["family"]
        old = existing.get(family, {})
        reviewed = {field: old.get(field, "") for field in MANUAL_FIELDS}
        reviewed.update(overrides.get(family, {}))
        axes = sorted(item.get("axes", []), key=lambda value: value["tag"])
        rows.append({
            "Family": family, "Category": CATEGORIES[item["category"]], **reviewed,
            "Styles": " | ".join(variant_label(v) for v in sorted(set(item["variants"]), key=variant_key)),
            "Variable Axes": " | ".join(f"{a['tag']}: {a['start']:g}..{a['end']:g}" for a in axes),
            "Subsets": " | ".join(sorted(set(item["subsets"]))),
            "Designers": " | ".join(metadata[family]["designer"]),
            "Date Added": metadata[family]["date_added"], "Last Modified": item["lastModified"],
            "Google Fonts URL": "https://fonts.google.com/specimen/" + urllib.parse.quote_plus(family),
        })
    return rows


def normalize_catalog(items, existing, overrides):
    rows = []
    for item in sorted(items, key=lambda value: value["family"].casefold()):
        family = item["family"]
        old = existing.get(family, {})
        reviewed = {field: old.get(field, "") for field in MANUAL_FIELDS}
        reviewed.update({
            "Stroke": item["stroke"] or "",
            "Classifications": " | ".join(sorted(set(item["classifications"]))),
            "Popularity Rank": str(item["popularity"]),
            "Trending Rank": str(item["trending"]),
            "Is Noto": "Yes" if item["isNoto"] else "No",
        })
        reviewed.update(overrides.get(family, {}))
        axes = sorted(item["axes"], key=lambda value: value["tag"])
        rows.append({
            "Family": family, "Category": item["category"], **reviewed,
            "Styles": " | ".join(sorted(item["fonts"], key=variant_key)),
            "Variable Axes": " | ".join(f"{a['tag']}: {a['min']:g}..{a['max']:g}" for a in axes),
            "Subsets": " | ".join(sorted(set(item["subsets"]) - {"menu"})),
            "Designers": " | ".join(item["designers"]), "Date Added": item["dateAdded"],
            "Last Modified": item["lastModified"],
            "Google Fonts URL": "https://fonts.google.com/specimen/" + urllib.parse.quote_plus(family),
        })
    return rows


def write_outputs(rows, metadata, exclusions, csv_path, license_path, verified_at, metadata_revision):
    csv_buffer = io.StringIO(newline="")
    writer = csv.DictWriter(csv_buffer, CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    licenses = {
        "schemaVersion": 1,
        "source": {
            "repository": "https://github.com/google/fonts",
            "metadataFile": "METADATA.pb",
            "revision": metadata_revision,
        },
        "familyCount": len(rows),
        "families": [{
            "name": row["Family"], "license": metadata[row["Family"]]["license"],
            "date_added": metadata[row["Family"]]["date_added"],
            "designer": metadata[row["Family"]]["designer"],
            "status": "active", "verifiedAt": verified_at,
        } for row in rows],
        "excludedFamilies": [{
            "name": exclusions[name]["name"], "reason": exclusions[name]["reason"],
            "source": exclusions[name]["source"], "status": "needs-review", "verifiedAt": verified_at,
        } for name in sorted(exclusions, key=str.casefold)],
    }
    outputs = (
        (license_path, json.dumps(licenses, ensure_ascii=False, indent=2) + "\n"),
        (csv_path, csv_buffer.getvalue()),
    )
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = csv_path.parent / ".google-font-refresh.lock"
    marker_path = csv_path.parent / ".google-font-refresh.incomplete.json"
    if marker_path.exists():
        fail(f"{marker_path}: incomplete prior refresh requires review")
    try:
        lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        fail(f"{lock_path}: another refresh is already running")
    with os.fdopen(lock_fd, "w", encoding="utf-8") as lock:
        lock.write(f"verifiedAt={verified_at}\n")
        lock.flush()
        os.fsync(lock.fileno())
    staged = []
    published = False
    complete = False
    marker_created = False
    try:
        for target, content in outputs:
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=target.parent,
                                             prefix=f".{target.name}.", delete=False) as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
                staged.append((Path(handle.name), target))
        with marker_path.open("x", encoding="utf-8") as marker:
            marker_created = True
            marker.write(json.dumps({
                "schemaVersion": 1,
                "verifiedAt": verified_at,
                "targets": [str(target) for target, _ in outputs],
            }, sort_keys=True) + "\n")
            marker.flush()
            os.fsync(marker.fileno())
        for temporary, target in staged:
            os.replace(temporary, target)
            published = True
        complete = True
    finally:
        for temporary, _ in staged:
            temporary.unlink(missing_ok=True)
        if marker_created and (complete or not published):
            marker_path.unlink(missing_ok=True)
        lock_path.unlink(missing_ok=True)


def change_report(rows, existing, exclusions):
    generated = {row["Family"]: row for row in rows}
    managed = [field for field in CSV_FIELDS if field not in MANUAL_FIELDS and field != "Family"]
    return {
        "addedFamilies": sorted(set(generated) - set(existing), key=str.casefold),
        "removedFamilies": sorted(set(existing) - set(generated), key=str.casefold),
        "metadataChangedFamilies": sorted(
            (family for family in set(existing) & set(generated)
             if any(existing[family].get(field, "") != generated[family][field] for field in managed)),
            key=str.casefold,
        ),
        "excludedFamilies": [
            {**exclusions[name], "status": "needs-review"}
            for name in sorted(exclusions, key=str.casefold)
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--api-input", type=Path, help="offline Developer API JSON snapshot")
    source.add_argument("--catalog-input", type=Path, help="official Fonts metadata bootstrap/cross-check JSON")
    source.add_argument("--live", action="store_true", help="fetch the official API explicitly")
    metadata_source = parser.add_mutually_exclusive_group(required=True)
    metadata_source.add_argument("--metadata-input", type=Path)
    metadata_source.add_argument(
        "--metadata-root", type=Path,
        help="official google/fonts checkout containing METADATA.pb files",
    )
    parser.add_argument("--existing-csv", type=Path, required=True)
    parser.add_argument("--overrides", type=Path)
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--license-output", type=Path, required=True)
    parser.add_argument("--verified-at", required=True, help="review date in YYYY-MM-DD form")
    parser.add_argument(
        "--metadata-revision", required=True,
        help="exact 40-character google/fonts commit or fixture-* revision",
    )
    parser.add_argument(
        "--expected-count", type=int,
        help="optional snapshot-size lock for deterministic offline verification",
    )
    parser.add_argument("--approve-changes", action="store_true", help="publish reviewed family-set changes")
    args = parser.parse_args()
    try:
        verified_at = checked_date(args.verified_at, "verified-at")
        if not METADATA_REVISION_RE.fullmatch(args.metadata_revision):
            fail("metadata-revision must be a 40-character lowercase commit or fixture-* token")
        payload = None
        if args.live:
            payload = fetch_live_catalog()
        elif args.api_input:
            payload = read_json(args.api_input)
        existing = load_existing(args.existing_csv)
        overrides = load_overrides(args.overrides)
        if args.catalog_input:
            items = validate_catalog(read_json(args.catalog_input), args.expected_count)
            metadata_payload = (read_json(args.metadata_input) if args.metadata_input else
                                metadata_from_repository(args.metadata_root,
                                                         [item["family"] for item in items]))
            metadata, exclusions = validate_metadata(
                metadata_payload, [item["family"] for item in items]
            )
            rows = normalize_catalog(
                [item for item in items if item["family"] not in exclusions], existing, overrides
            )
        else:
            items = validate_api(payload, args.expected_count)
            metadata_payload = (read_json(args.metadata_input) if args.metadata_input else
                                metadata_from_repository(args.metadata_root,
                                                         [item["family"] for item in items]))
            metadata, exclusions = validate_metadata(
                metadata_payload, [item["family"] for item in items]
            )
            rows = normalize(
                [item for item in items if item["family"] not in exclusions], metadata, existing, overrides
            )
        known = {item["family"] for item in items}
        unknown_overrides = sorted(set(overrides) - known)
        if unknown_overrides:
            fail(f"overrides target unknown families: {', '.join(unknown_overrides[:5])}")
        report = change_report(rows, existing, exclusions)
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        if (report["addedFamilies"] or report["removedFamilies"]) and not args.approve_changes:
            fail("family-set changes require --approve-changes after review; no outputs published")
        write_outputs(
            rows, metadata, exclusions, args.output_csv, args.license_output,
            verified_at, args.metadata_revision,
        )
    except (ValueError, OSError, json.JSONDecodeError, urllib.error.URLError) as exc:
        print(f"refresh-google-fonts: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
