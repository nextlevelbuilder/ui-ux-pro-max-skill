#!/usr/bin/env python3
"""Offline contract tests for deterministic upstream catalog refreshes."""

import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = next(
    parent for parent in Path(__file__).resolve().parents
    if all((parent / "scripts" / script).is_file() for script in (
        "refresh-google-fonts.py", "refresh-icon-catalog.py",
    ))
)
FIXTURES = Path(__file__).parent / "fixtures" / "catalogs"
FONT_SCRIPT = REPO / "scripts" / "refresh-google-fonts.py"
ICON_SCRIPT = REPO / "scripts" / "refresh-icon-catalog.py"


class CatalogRefreshTest(unittest.TestCase):
    def run_command(self, *args, env=None):
        return subprocess.run(
            [sys.executable, *map(str, args)],
            cwd=REPO,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    def font_args(self, directory, api=None, metadata=None, approve=True, existing=None, overrides=None):
        args = [
            FONT_SCRIPT,
            "--api-input", api or FIXTURES / "google-api.json",
            "--metadata-input", metadata or FIXTURES / "google-metadata.json",
            "--existing-csv", existing or FIXTURES / "google-existing.csv",
            "--overrides", overrides or FIXTURES / "google-overrides.json",
            "--output-csv", directory / "google-fonts.csv",
            "--license-output", directory / "google-font-licenses.json",
            "--verified-at", "2026-08-13",
            "--metadata-revision", "fixture-catalogs-v1",
            "--expected-count", "2",
        ]
        if approve:
            args.append("--approve-changes")
        return args

    def icon_args(self, directory, source=None, curated=None, package=None, react_exports=None):
        return [
            ICON_SCRIPT,
            "--input", source or FIXTURES / "phosphor-core.json",
            "--package-json", package or FIXTURES / "phosphor-package.json",
            "--react-package-json", FIXTURES / "phosphor-react-package.json",
            "--react-exports-input", react_exports or FIXTURES / "phosphor-react-exports.json",
            "--curated-csv", curated or FIXTURES / "icons-curated.csv",
            "--output", directory / "phosphor-icons-upstream.json",
            "--verified-at", "2026-08-13",
            "--expected-count", "2",
        ]

    def test_live_font_refresh_requires_environment_key(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            args = self.font_args(directory)
            args[1:3] = ["--live"]
            env = dict(os.environ)
            env.pop("GOOGLE_FONTS_API_KEY", None)
            result = self.run_command(*args, env=env)
        self.assertEqual(2, result.returncode)
        self.assertIn("GOOGLE_FONTS_API_KEY is required for --live", result.stderr)
        self.assertIn("use --api-input for offline CI", result.stderr)

    def test_font_refresh_is_deterministic_and_preserves_reviewed_fields(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            first_path, second_path = Path(first), Path(second)
            self.assertEqual(0, self.run_command(*self.font_args(first_path)).returncode)
            self.assertEqual(0, self.run_command(*self.font_args(second_path)).returncode)
            self.assertEqual(
                (first_path / "google-fonts.csv").read_bytes(),
                (second_path / "google-fonts.csv").read_bytes(),
            )
            self.assertEqual(
                (first_path / "google-font-licenses.json").read_bytes(),
                (second_path / "google-font-licenses.json").read_bytes(),
            )
            with (first_path / "google-fonts.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            csv_bytes = (first_path / "google-fonts.csv").read_bytes()
            license_bytes = (first_path / "google-font-licenses.json").read_bytes()
            licenses = json.loads(license_bytes)
        self.assertEqual(["Alpha Sans", "Zeta Serif"], [row["Family"] for row in rows])
        self.assertEqual("Sans Serif", rows[0]["Stroke"])
        self.assertEqual("approved override keywords", rows[0]["Keywords"])
        self.assertEqual("400 | 400i | 500", rows[0]["Styles"])
        self.assertEqual("wght: 100..900", rows[0]["Variable Axes"])
        self.assertEqual(["OFL", "APACHE2"], [item["license"] for item in licenses["families"]])
        self.assertEqual(["Alpha Sans", "Zeta Serif"], [item["name"] for item in licenses["families"]])
        self.assertEqual("fixture-catalogs-v1", licenses["source"]["revision"])
        self.assertTrue(all(item["status"] == "active" for item in licenses["families"]))
        self.assertTrue(all(item["verifiedAt"] == "2026-08-13" for item in licenses["families"]))
        with tempfile.TemporaryDirectory() as raw:
            reused = Path(raw)
            metadata_path = reused / "metadata.json"
            metadata_path.write_bytes(license_bytes)
            result = self.run_command(*self.font_args(
                reused, metadata=metadata_path
            ))
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(
                csv_bytes, (reused / "google-fonts.csv").read_bytes(),
            )

    def test_font_refresh_rejects_schema_size_dates_and_licenses(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            api = json.loads((FIXTURES / "google-api.json").read_text())
            metadata = json.loads((FIXTURES / "google-metadata.json").read_text())
            cases = []
            wrong_schema = dict(api)
            wrong_schema["kind"] = "unexpected"
            cases.append((wrong_schema, metadata, "webfonts#webfontList"))
            cases.append(({**api, "items": api["items"][:1]}, metadata, "expected 2 items"))
            bad_url = json.loads(json.dumps(api))
            bad_url["items"][0]["files"]["regular"] = "https://example.com/font.ttf"
            cases.append((bad_url, metadata, "https://fonts.gstatic.com"))
            bad_date = json.loads(json.dumps(api))
            bad_date["items"][0]["lastModified"] = "1970-01-01"
            cases.append((bad_date, metadata, "suspicious date"))
            bad_license = json.loads(json.dumps(metadata))
            bad_license["families"][0]["license"] = "UNKNOWN"
            cases.append((api, bad_license, "invalid or missing official license"))
            for index, (api_value, metadata_value, error) in enumerate(cases):
                api_path, metadata_path = directory / f"api-{index}.json", directory / f"metadata-{index}.json"
                api_path.write_text(json.dumps(api_value))
                metadata_path.write_text(json.dumps(metadata_value))
                result = self.run_command(*self.font_args(directory, api_path, metadata_path))
                with self.subTest(error=error):
                    self.assertEqual(2, result.returncode)
                    self.assertIn(error, result.stderr)

    def test_font_refresh_fails_closed_on_concurrency_or_interrupted_pair(self):
        for sentinel, error in (
            (".google-font-refresh.lock", "another refresh is already running"),
            (".google-font-refresh.incomplete.json", "incomplete prior refresh"),
        ):
            with self.subTest(sentinel=sentinel), tempfile.TemporaryDirectory() as raw:
                directory = Path(raw)
                (directory / sentinel).write_text("occupied\n", encoding="utf-8")
                result = self.run_command(*self.font_args(directory))
                self.assertEqual(2, result.returncode)
                self.assertIn(error, result.stderr)
                self.assertFalse((directory / "google-fonts.csv").exists())
                self.assertFalse((directory / "google-font-licenses.json").exists())

    def test_catalog_cross_check_uses_explicit_schema_without_font_file_urls(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            args = self.font_args(directory)
            args[1:3] = ["--catalog-input", FIXTURES / "google-catalog.json"]
            result = self.run_command(*args)
            with (directory / "google-fonts.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(["Alpha Sans", "Zeta Serif"], [row["Family"] for row in rows])
        self.assertEqual("Geometric", rows[0]["Classifications"])
        self.assertEqual("42", rows[0]["Popularity Rank"])
        self.assertEqual("latin | vietnamese", rows[0]["Subsets"])

    def test_official_metadata_checkout_is_strict_and_reusable(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            metadata_root = directory / "google-fonts"
            family_dir = metadata_root / "ofl" / "alphasans"
            family_dir.mkdir(parents=True)
            (family_dir / "METADATA.pb").write_text(
                'name: "Alpha Sans"\n'
                'designer: "Alpha Designer"\n'
                'license: "OFL"\n'
                'date_added: "2024-01-02"\n',
                encoding="utf-8",
            )
            args = self.font_args(directory)
            metadata_index = args.index("--metadata-input")
            args[metadata_index:metadata_index + 2] = ["--metadata-root", metadata_root]
            result = self.run_command(*args)
        self.assertEqual(2, result.returncode)
        self.assertIn("fewer than 90%", result.stderr)

        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            metadata_root = directory / "google-fonts"
            for slug, family, license_name in (
                ("alphasans", "Alpha Sans", "OFL"),
                ("zetaserif", "Zeta Serif", "APACHE2"),
            ):
                family_dir = metadata_root / "ofl" / slug
                family_dir.mkdir(parents=True)
                (family_dir / "METADATA.pb").write_text(
                    f'name: "{family}"\n'
                    f'designer: "{family} Designer"\n'
                    f'license: "{license_name}"\n'
                    'date_added: "2024-01-02"\n',
                    encoding="utf-8",
                )
            args = self.font_args(directory)
            metadata_index = args.index("--metadata-input")
            args[metadata_index:metadata_index + 2] = ["--metadata-root", metadata_root]
            result = self.run_command(*args)
            licenses = json.loads((directory / "google-font-licenses.json").read_text())
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(["Alpha Sans", "Zeta Serif"], [item["name"] for item in licenses["families"]])

    def test_catalog_rejects_bool_rank_duplicate_axis_and_unreviewed_addition(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            catalog = json.loads((FIXTURES / "google-catalog.json").read_text())
            invalid_rank = json.loads(json.dumps(catalog))
            invalid_rank["familyMetadataList"][0]["popularity"] = True
            rank_path = directory / "rank.json"
            rank_path.write_text(json.dumps(invalid_rank))
            rank_args = self.font_args(directory)
            rank_args[1:3] = ["--catalog-input", rank_path]
            rank_result = self.run_command(*rank_args)
            invalid_axis = json.loads(json.dumps(catalog))
            axis = invalid_axis["familyMetadataList"][1]["axes"][0]
            invalid_axis["familyMetadataList"][1]["axes"].append(dict(axis))
            axis_path = directory / "axis.json"
            axis_path.write_text(json.dumps(invalid_axis))
            axis_args = self.font_args(directory)
            axis_args[1:3] = ["--catalog-input", axis_path]
            axis_result = self.run_command(*axis_args)
            existing = directory / "existing.csv"
            lines = (FIXTURES / "google-existing.csv").read_text().splitlines()
            existing.write_text("\n".join(lines[:2]) + "\n")
            approval_result = self.run_command(*self.font_args(directory, approve=False, existing=existing))
            bad_overrides = directory / "overrides.json"
            bad_overrides.write_text('{"families":{"Unknown Font":{"Keywords":"bad"}}}')
            override_result = self.run_command(*self.font_args(directory, overrides=bad_overrides))
        self.assertIn("invalid popularity", rank_result.stderr)
        self.assertIn("duplicate axis tags", axis_result.stderr)
        self.assertIn("family-set changes require --approve-changes", approval_result.stderr)
        self.assertIn("Zeta Serif", approval_result.stdout)
        self.assertFalse((directory / "google-fonts.csv").exists())
        self.assertIn("overrides target unknown families", override_result.stderr)

    def test_explicit_license_exclusion_is_reported_and_not_promoted(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            metadata = json.loads((FIXTURES / "google-metadata.json").read_text())
            metadata["families"] = metadata["families"][:1]
            metadata["excludedFamilies"] = [{
                "name": "Alpha Sans", "reason": "No matching official METADATA.pb",
                "source": "https://github.com/google/fonts",
            }]
            metadata_path = directory / "metadata.json"
            metadata_path.write_text(json.dumps(metadata))
            result = self.run_command(*self.font_args(directory, metadata=metadata_path))
            report = json.loads(result.stdout)
            licenses = json.loads((directory / "google-font-licenses.json").read_text())
            with (directory / "google-fonts.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(["Zeta Serif"], [row["Family"] for row in rows])
        self.assertEqual("needs-review", report["excludedFamilies"][0]["status"])
        self.assertEqual("needs-review", licenses["excludedFamilies"][0]["status"])

    def test_exclusion_sources_match_offline_validator_policy(self):
        metadata = json.loads((FIXTURES / "google-metadata.json").read_text())
        allowed = (
            "https://fonts.google.com/specimen/Alpha+Sans",
            "https://github.com/google/fonts",
            "https://github.com/google/fonts/tree/main/ofl/alphasans",
        )
        rejected = (
            "https://example.com/google/fonts",
            "https://github.com/other/fonts",
            "https://fonts.google.com:444/specimen/Alpha+Sans",
        )
        for index, source in enumerate((*allowed, *rejected)):
            with self.subTest(source=source), tempfile.TemporaryDirectory() as raw:
                directory = Path(raw)
                candidate = json.loads(json.dumps(metadata))
                candidate["families"] = candidate["families"][1:]
                candidate["excludedFamilies"] = [{
                    "name": "Zeta Serif",
                    "reason": "No matching official METADATA.pb",
                    "source": source,
                }]
                metadata_path = directory / f"metadata-{index}.json"
                metadata_path.write_text(json.dumps(candidate))
                result = self.run_command(*self.font_args(directory, metadata=metadata_path))
                self.assertEqual(source in allowed, result.returncode == 0, result.stderr)

    def test_icon_manifest_normalizes_and_records_all_import_forms(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            first_path, second_path = Path(first), Path(second)
            self.assertEqual(0, self.run_command(*self.icon_args(first_path)).returncode)
            self.assertEqual(0, self.run_command(*self.icon_args(second_path)).returncode)
            output = first_path / "phosphor-icons-upstream.json"
            self.assertEqual(output.read_bytes(), (second_path / output.name).read_bytes())
            manifest = json.loads(output.read_text())
        self.assertEqual("2.1.1", manifest["source"]["version"])
        self.assertEqual(("active", "2026-08-13"), (manifest["status"], manifest["verifiedAt"]))
        self.assertEqual(["thin", "light", "regular", "bold", "fill", "duotone"], manifest["weights"])
        self.assertEqual(["acorn", "arrow-left"], [icon["name"] for icon in manifest["icons"]])
        arrow = manifest["icons"][1]
        self.assertEqual(["arrows", "navigation"], arrow["categories"])
        self.assertIn('from "@phosphor-icons/react"', arrow["clientImport"])
        self.assertIn('from "@phosphor-icons/react/ssr"', arrow["ssrImport"])
        self.assertEqual(2, manifest["curatedValidatedCount"])

    def test_icon_refresh_rejects_invalid_schema_size_and_curated_import(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            icons = json.loads((FIXTURES / "phosphor-core.json").read_text())
            invalid = json.loads(json.dumps(icons))
            del invalid[0]["pascal_name"]
            source = directory / "invalid.json"
            source.write_text(json.dumps(invalid))
            schema_result = self.run_command(*self.icon_args(directory, source))
            size_args = self.icon_args(directory)
            size_args[-1] = "3"
            size_result = self.run_command(*size_args)
            curated = (FIXTURES / "icons-curated.csv").read_text().replace("{ Acorn }", "{ Horse }")
            curated_path = directory / "icons.csv"
            curated_path.write_text(curated)
            import_result = self.run_command(*self.icon_args(directory, curated=curated_path))
            package_path = directory / "package.json"
            package_path.write_text('{"name":"@phosphor-icons/core","version":"2.2.0"}')
            version_result = self.run_command(*self.icon_args(directory, package=package_path))
            alias_collision = json.loads(json.dumps(icons))
            alias_collision[1]["alias"] = {"name": "acorn", "pascal_name": "BackArrow"}
            alias_path = directory / "alias.json"
            alias_path.write_text(json.dumps(alias_collision))
            alias_result = self.run_command(*self.icon_args(directory, source=alias_path))
            exports = json.loads((FIXTURES / "phosphor-react-exports.json").read_text())
            exports["ssr"].remove("Acorn")
            exports_path = directory / "exports.json"
            exports_path.write_text(json.dumps(exports))
            exports_result = self.run_command(*self.icon_args(directory, react_exports=exports_path))
        self.assertIn("invalid official IconEntry schema", schema_result.stderr)
        self.assertIn("expected 3 icons", size_result.stderr)
        self.assertIn("import component does not match", import_result.stderr)
        self.assertIn("version must be 2.1.1", version_result.stderr)
        self.assertIn("alias collides", alias_result.stderr)
        self.assertIn("React exports missing", exports_result.stderr)


if __name__ == "__main__":
    unittest.main()
