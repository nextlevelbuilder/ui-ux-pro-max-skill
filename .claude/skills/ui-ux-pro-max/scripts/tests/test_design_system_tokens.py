#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for --tokens dtcg|css export from the design-system generator.

Stdlib-only (unittest, not pytest) to match test_core.py -- this project ships
with zero external dependencies. The generate-tokens.cjs round-trip is skipped
when Node is missing; CI has Node.

Run with:
    python -m unittest discover -s scripts/tests -v
or directly:
    python scripts/tests/test_design_system_tokens.py
"""

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from design_system import (  # noqa: E402
    SEMANTIC_COLOR_ENTRIES,
    _contrast_ratio,
    _HEX6,
    build_design_tokens,
    format_tokens_css,
    format_tokens_dtcg,
    generate_design_system,
)

ON_COLOR_PAIRS = (
    ("on_primary", "primary"),
    ("on_secondary", "secondary"),
    ("on_accent", "accent"),
    ("foreground", "background"),
    ("card_foreground", "card"),
    ("muted_foreground", "muted"),
    ("on_destructive", "destructive"),
)

SEARCH = SCRIPTS_DIR / "search.py"
REPO = next(
    parent for parent in Path(__file__).resolve().parents
    if (parent / "cli" / "assets" / "skills" / "design-system" / "scripts"
        / "generate-tokens.cjs").is_file()
)
GENERATE_TOKENS = (
    REPO / "cli" / "assets" / "skills" / "design-system" / "scripts"
    / "generate-tokens.cjs"
)
HEX_TOKEN = re.compile(r"^#[0-9A-Fa-f]{6}$")
CSS_VAR = re.compile(r"^\s+(--[a-z0-9-]+):\s*(.+);\s*$", re.MULTILINE)


def _node_available():
    return shutil.which("node") is not None


def _parse_css_vars(css: str) -> dict:
    return {name: value for name, value in CSS_VAR.findall(css)}


class TokenExportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = generate_design_system(
            "fintech dashboard", "Ledgerly", token_format="dtcg"
        )
        cls.ds = cls.result["design_system"]
        cls.tokens = cls.result["tokens"]

    def test_color_mode_is_recorded(self):
        self.assertIn(self.ds["color_mode"], ("light", "dark"))

    def test_dtcg_shape_matches_starter_conventions(self):
        tokens = self.tokens
        self.assertEqual(tokens["$schema"], "https://design-tokens.org/schema.json")
        self.assertIn("$description", tokens)
        self.assertIn(self.ds["color_mode"], tokens["$description"])
        self.assertIn("color", tokens)
        self.assertIn("font", tokens)
        self.assertIn("semantic", tokens)
        semantic_color = tokens["semantic"]["color"]
        for name in (
            "primary", "on-primary", "background", "foreground",
            "card", "muted", "border", "ring", "destructive",
        ):
            self.assertIn(name, semantic_color)
            self.assertEqual(semantic_color[name]["$type"], "color")
            self.assertEqual(semantic_color[name]["$value"], "{color.%s}" % name)
            self.assertEqual(tokens["color"][name]["$type"], "color")
            self.assertRegex(tokens["color"][name]["$value"], HEX_TOKEN)
        for role in ("heading", "body"):
            self.assertEqual(tokens["font"][role]["$type"], "fontFamily")
            self.assertTrue(tokens["font"][role]["$value"])
            self.assertEqual(
                tokens["semantic"]["font"][role]["$value"], "{font.%s}" % role
            )

    def test_every_exported_color_is_six_digit_hex(self):
        for name, token in self.tokens["color"].items():
            with self.subTest(color=name):
                self.assertEqual(token["$type"], "color")
                self.assertRegex(token["$value"], HEX_TOKEN)
                self.assertTrue(_HEX6.match(token["$value"]))

    def test_on_color_pairs_reuse_generator_contrast(self):
        colors = self.ds["colors"]
        for foreground, background in ON_COLOR_PAIRS:
            with self.subTest(pair=foreground):
                self.assertGreaterEqual(
                    _contrast_ratio(colors[foreground], colors[background]), 4.5
                )

    def test_css_uses_generate_tokens_variable_names(self):
        css = format_tokens_css(self.tokens)
        variables = _parse_css_vars(css)
        for _label, key, css_var in SEMANTIC_COLOR_ENTRIES:
            hex_val = self.ds["colors"].get(key)
            if not hex_val:
                continue
            self.assertEqual(variables[css_var], hex_val)
        self.assertIn("--font-heading", variables)
        self.assertIn("--font-body", variables)
        self.assertTrue(css.strip().startswith("/* Design Tokens"))
        self.assertIn(":root {", css)

    def test_dtcg_text_is_the_token_document(self):
        parsed = json.loads(self.result["text"])
        self.assertEqual(parsed["semantic"]["color"]["primary"]["$type"], "color")
        self.assertNotIn("TARGET:", self.result["text"])

    def test_css_token_format_prints_css(self):
        result = generate_design_system(
            "fintech dashboard", "Ledgerly", token_format="css"
        )
        self.assertIn("--color-primary:", result["text"])
        self.assertEqual(result["tokens"]["color"]["primary"]["$value"],
                         _parse_css_vars(result["text"])["--color-primary"])

    def test_spacing_tokens_only_when_density_is_set(self):
        plain = build_design_tokens(
            generate_design_system("fintech dashboard", "Ledgerly")["design_system"]
        )
        dense = build_design_tokens(
            generate_design_system(
                "fintech dashboard", "Ledgerly", density=9
            )["design_system"]
        )
        self.assertNotIn("space", plain)
        self.assertIn("space", dense)
        self.assertIn("xs", dense["semantic"]["space"])
        css_vars = _parse_css_vars(format_tokens_css(dense))
        self.assertIn("--space-xs", css_vars)


class DarkModeTokenTest(unittest.TestCase):
    def test_dark_query_marks_mode_and_emits_dark_surfaces(self):
        result = generate_design_system(
            "dark mode developer tool", "Nightshift", token_format="dtcg"
        )
        ds = result["design_system"]
        tokens = result["tokens"]
        self.assertEqual(ds["color_mode"], "dark")
        self.assertIn("dark", tokens["$description"].lower())
        background = tokens["color"]["background"]["$value"]
        foreground = tokens["color"]["foreground"]["$value"]
        self.assertRegex(background, HEX_TOKEN)
        self.assertGreater(
            _contrast_ratio(foreground, background), 4.5
        )
        css = format_tokens_css(tokens)
        self.assertEqual(_parse_css_vars(css)["--color-background"], background)


class PersistTokenTest(unittest.TestCase):
    def test_persist_dtcg_writes_tokens_json_beside_master(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = generate_design_system(
                "fintech dashboard", "Ledgerly", persist=True, output_dir=tmp,
                token_format="dtcg",
            )
            folder = Path(tmp) / "design-system" / "ledgerly"
            master = folder / "MASTER.md"
            tokens_json = folder / "tokens.json"
            self.assertTrue(master.exists())
            self.assertTrue(tokens_json.exists())
            self.assertFalse((folder / "tokens.css").exists())
            self.assertIn(str(tokens_json), result["persistence"]["created_files"])
            master_text = master.read_text(encoding="utf-8")
            self.assertIn("tokens.json", master_text)
            self.assertIn("master-level only", master_text)
            parsed = json.loads(tokens_json.read_text(encoding="utf-8"))
            self.assertEqual(parsed["semantic"]["color"]["primary"]["$type"], "color")

    def test_persist_css_writes_json_and_css(self):
        with tempfile.TemporaryDirectory() as tmp:
            generate_design_system(
                "fintech dashboard", "Ledgerly", persist=True, output_dir=tmp,
                token_format="css",
            )
            folder = Path(tmp) / "design-system" / "ledgerly"
            css_text = (folder / "tokens.css").read_text(encoding="utf-8")
            self.assertIn("--color-primary:", css_text)
            master = (folder / "MASTER.md").read_text(encoding="utf-8")
            self.assertIn("tokens.css", master)

    def test_page_overrides_do_not_write_page_tokens(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = generate_design_system(
                "fintech dashboard", "Ledgerly", persist=True, page="dashboard",
                output_dir=tmp, token_format="dtcg",
            )
            folder = Path(tmp) / "design-system" / "ledgerly"
            page = folder / "pages" / "dashboard.md"
            self.assertTrue(page.exists())
            self.assertTrue((folder / "tokens.json").exists())
            self.assertFalse((folder / "pages" / "tokens.json").exists())
            created = result["persistence"]["created_files"]
            self.assertTrue(any(path.endswith("tokens.json") for path in created))
            self.assertTrue(any(path.endswith("dashboard.md") for path in created))

    def test_skip_if_exists_then_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = generate_design_system(
                "fintech dashboard", "Ledgerly", persist=True, output_dir=tmp,
                token_format="dtcg",
            )
            tokens_json = Path(first["persistence"]["design_system_dir"]) / "tokens.json"
            original = tokens_json.read_text(encoding="utf-8")
            skipped = generate_design_system(
                "beauty spa", "Ledgerly", persist=True, output_dir=tmp,
                token_format="dtcg",
            )
            self.assertEqual(skipped["persistence"]["status"], "skipped_exists")
            self.assertEqual(tokens_json.read_text(encoding="utf-8"), original)
            forced = generate_design_system(
                "beauty spa", "Ledgerly", persist=True, output_dir=tmp,
                token_format="dtcg", force=True,
            )
            self.assertEqual(forced["persistence"]["status"], "success")
            self.assertNotEqual(tokens_json.read_text(encoding="utf-8"), original)


class TokenCliTest(unittest.TestCase):
    def run_search(self, *args):
        return subprocess.run(
            [sys.executable, str(SEARCH), *map(str, args)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    def test_tokens_without_design_system_is_an_argparse_error(self):
        proc = self.run_search("fintech dashboard", "--tokens", "dtcg")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("--tokens", proc.stderr)
        self.assertIn("--design-system", proc.stderr)

    def test_cli_dtcg_stdout_is_json(self):
        proc = self.run_search(
            "fintech dashboard", "--design-system", "--tokens", "dtcg",
            "-p", "Ledgerly",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["semantic"]["color"]["primary"]["$type"], "color")

    def test_cli_css_stdout_has_root_variables(self):
        proc = self.run_search(
            "fintech dashboard", "--design-system", "--tokens", "css",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn(":root {", proc.stdout)
        self.assertIn("--color-primary:", proc.stdout)

    def test_json_payload_includes_tokens(self):
        proc = self.run_search(
            "fintech dashboard", "--design-system", "--tokens", "dtcg", "--json",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertIn("design_system", payload)
        self.assertIn("tokens", payload)
        self.assertIn("primary", payload["tokens"]["color"])


@unittest.skipUnless(_node_available(), "Node.js is required to round-trip tokens through generate-tokens.cjs")
class GenerateTokensRoundTripTest(unittest.TestCase):
    def test_cjs_css_matches_tokens_css_output(self):
        result = generate_design_system(
            "fintech dashboard", "Ledgerly", token_format="css"
        )
        python_css = format_tokens_css(result["tokens"])
        self.assertEqual(python_css, result["text"])
        with tempfile.TemporaryDirectory() as tmp:
            json_path = Path(tmp) / "tokens.json"
            cjs_css_path = Path(tmp) / "from-cjs.css"
            json_path.write_text(format_tokens_dtcg(result["tokens"]), encoding="utf-8")
            proc = subprocess.run(
                ["node", str(GENERATE_TOKENS), "--config", str(json_path),
                 "-o", str(cjs_css_path)],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            cjs_css = cjs_css_path.read_text(encoding="utf-8")
            self.assertEqual(cjs_css, python_css)
            self.assertEqual(_parse_css_vars(cjs_css), _parse_css_vars(python_css))


if __name__ == "__main__":
    unittest.main(verbosity=2)
