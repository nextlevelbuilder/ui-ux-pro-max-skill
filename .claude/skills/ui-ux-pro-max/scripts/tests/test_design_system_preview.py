#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for --preview HTML output of the design system generator.

Stdlib-only (unittest, not pytest) to match test_core.py.

Run with:
    python -m unittest discover -s scripts/tests -v
or directly:
    python scripts/tests/test_design_system_preview.py
"""

import json
import subprocess
import sys
import tempfile
import unittest
from html import escape
from html.parser import HTMLParser
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from design_system import (  # noqa: E402
    SEMANTIC_COLOR_ENTRIES,
    _contrast_ratio,
    _palette_is_dark,
    generate_design_system,
)
from preview import format_preview_html, write_preview_html  # noqa: E402

SEARCH = SCRIPTS_DIR / "search.py"
HOSTILE_NAME = '<script>alert(1)</script>'
DARK_QUERY = "SaaS invoicing fintech B2B professional dark mode"


class _TagCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text.append(data)


def _parse(html):
    parser = _TagCollector()
    parser.feed(html)
    return parser


def _run_search(*args):
    return subprocess.run(
        [sys.executable, str(SEARCH), *map(str, args)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


class TestPreviewStructure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = generate_design_system("fintech dashboard", "Ledger")
        cls.ds = cls.result["design_system"]
        cls.html = format_preview_html(cls.ds)
        cls.parsed = _parse(cls.html)

    def test_lang_landmark_and_labels(self):
        html_tag = next(attrs for tag, attrs in self.parsed.tags if tag == "html")
        self.assertEqual(html_tag.get("lang"), "en")
        tags = [tag for tag, _attrs in self.parsed.tags]
        self.assertIn("main", tags)
        self.assertIn("header", tags)
        labels = [attrs for tag, attrs in self.parsed.tags if tag == "label"]
        inputs = [attrs for tag, attrs in self.parsed.tags if tag == "input"]
        self.assertGreaterEqual(len(labels), 2)
        self.assertGreaterEqual(len(inputs), 2)
        for attrs in inputs:
            self.assertTrue(attrs.get("id"), attrs)
            matching = [label for label in labels if label.get("for") == attrs["id"]]
            self.assertTrue(matching, attrs)

    def test_palette_swatches_cover_every_present_role(self):
        for label, key, _css_var in SEMANTIC_COLOR_ENTRIES:
            hex_val = self.ds["colors"].get(key, "")
            if hex_val:
                self.assertIn(hex_val, self.html)
                self.assertIn(label, self.html)

    def test_type_buttons_card_form_style_and_anti_patterns(self):
        self.assertIn(self.ds["typography"]["heading"], self.html)
        self.assertIn(self.ds["typography"]["body"], self.html)
        self.assertIn("btn-primary", self.html)
        self.assertIn("btn-secondary", self.html)
        self.assertIn("btn-accent", self.html)
        self.assertIn("btn-destructive", self.html)
        self.assertIn("is-hover", self.html)
        self.assertIn("is-focus", self.html)
        self.assertIn("disabled", self.html)
        self.assertIn("preview-card", self.html)
        self.assertIn("aria-invalid", self.html)
        self.assertIn(self.ds["style"]["name"], self.html)
        self.assertIn("prefers-reduced-motion", self.html)
        self.assertIn(":focus-visible", self.html)
        if self.ds["key_effects"]:
            self.assertIn(self.ds["key_effects"].split("+")[0].strip()[:20], self.html)
        for clause in self.ds["anti_patterns"].split("+"):
            clause = clause.strip()
            if clause:
                self.assertIn(clause, self.html)

    def test_google_fonts_link_when_pairing_has_a_url(self):
        url = self.ds["typography"].get("google_fonts_url") or ""
        if url:
            self.assertIn(escape(url, quote=True), self.html)
            self.assertIn('rel="stylesheet"', self.html)
        self.assertIn("system-ui", self.html)


class TestPreviewEscaping(unittest.TestCase):
    def test_hostile_project_name_is_escaped(self):
        ds = generate_design_system("kids education app", HOSTILE_NAME)["design_system"]
        html = format_preview_html(ds)
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertIn("<html lang=", html)

    def test_cli_hostile_project_name_is_escaped(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = _run_search(
                "kids education app", "--design-system", "--preview",
                "--project-name", HOSTILE_NAME, "--output-dir", tmp, "--json",
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            path = Path(payload["preview"]["preview_file"])
            html = path.read_text(encoding="utf-8")
            self.assertNotIn("<script>alert(1)</script>", html)
            self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)


class TestPreviewContrast(unittest.TestCase):
    def test_printed_ratios_match_generator(self):
        ds = generate_design_system("fintech dashboard", "Ledger")["design_system"]
        html = format_preview_html(ds)
        pairs = (
            ("primary", "on_primary"),
            ("secondary", "on_secondary"),
            ("accent", "on_accent"),
            ("background", "foreground"),
            ("card", "card_foreground"),
            ("muted", "muted_foreground"),
            ("destructive", "on_destructive"),
        )
        for surface, on in pairs:
            ratio = _contrast_ratio(ds["colors"][surface], ds["colors"][on])
            self.assertIsNotNone(ratio)
            self.assertIn(f"{ratio:.2f}:1", html)
            level = "AAA" if ratio >= 7 else "AA" if ratio >= 4.5 else "Fail"
            self.assertIn(level, html)


class TestPreviewDarkMode(unittest.TestCase):
    def test_dark_system_renders_on_its_dark_surfaces(self):
        ds = generate_design_system(DARK_QUERY, "Night Ledger")["design_system"]
        self.assertEqual(ds["color_mode"], "dark")
        self.assertTrue(_palette_is_dark({"Background": ds["colors"]["background"]}))
        html = format_preview_html(ds)
        self.assertIn(f'background: {ds["colors"]["background"]}', html)
        self.assertIn(f'color: {ds["colors"]["foreground"]}', html)
        self.assertIn('content="dark"', html)


class TestPreviewCli(unittest.TestCase):
    def test_preview_without_design_system_errors(self):
        proc = _run_search("fintech dashboard", "--preview")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("--design-system", proc.stderr)

    def test_preview_with_persist_writes_next_to_master(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = _run_search(
                "fintech dashboard", "--design-system", "--persist", "--preview",
                "--project-name", "Ledger", "--output-dir", tmp, "--json",
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            preview = Path(payload["preview"]["preview_file"])
            master = Path(payload["persistence"]["master_file"])
            self.assertEqual(preview.parent, master.parent)
            self.assertEqual(preview.name, "preview.html")
            self.assertTrue(preview.exists())
            self.assertTrue(master.exists())

    def test_preview_without_persist_uses_output_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = _run_search(
                "fintech dashboard", "--design-system", "--preview",
                "--project-name", "Ledger", "--output-dir", tmp, "--json",
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            payload = json.loads(proc.stdout)
            preview = Path(payload["preview"]["preview_file"])
            self.assertEqual(preview, Path(tmp) / "preview.html")
            self.assertTrue(preview.exists())
            self.assertFalse((Path(tmp) / "design-system").exists())

    def test_preview_without_output_dir_uses_temp_file(self):
        proc = _run_search(
            "fintech dashboard", "--design-system", "--preview",
            "--project-name", "Temp Ledger", "--json",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        preview = Path(payload["preview"]["preview_file"])
        self.assertTrue(preview.exists())
        self.assertTrue(preview.name.startswith("design-system-preview-"))
        preview.unlink()

    def test_preview_respects_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = write_preview_html(
                generate_design_system("fintech dashboard", "Ledger")["design_system"],
                output_dir=tmp,
            )
            path = Path(first["preview_file"])
            path.write_text("stale", encoding="utf-8")
            skipped = write_preview_html(
                generate_design_system("fintech dashboard", "Ledger")["design_system"],
                output_dir=tmp,
            )
            self.assertEqual(skipped["status"], "skipped_exists")
            self.assertEqual(path.read_text(encoding="utf-8"), "stale")
            overwritten = write_preview_html(
                generate_design_system("fintech dashboard", "Ledger")["design_system"],
                output_dir=tmp, force=True,
            )
            self.assertEqual(overwritten["status"], "success")
            self.assertIn("<html lang=", path.read_text(encoding="utf-8"))

    def test_preview_still_writes_when_master_already_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            generate_design_system(
                "fintech dashboard", "Ledger", persist=True, output_dir=tmp
            )
            result = generate_design_system(
                "fintech dashboard", "Ledger", persist=True, preview=True, output_dir=tmp
            )
            self.assertEqual(result["persistence"]["status"], "skipped_exists")
            self.assertEqual(result["preview"]["status"], "success")
            self.assertTrue(Path(result["preview"]["preview_file"]).exists())


class TestPreviewNoScriptInjectionInCss(unittest.TestCase):
    def test_invalid_hex_is_not_emitted_as_css_color(self):
        ds = generate_design_system("fintech dashboard", "Ledger")["design_system"]
        ds = dict(ds)
        ds["colors"] = dict(ds["colors"])
        ds["colors"]["primary"] = "red; } body { background: url(javascript:alert(1))"
        html = format_preview_html(ds)
        self.assertNotIn("javascript:alert", html)
        self.assertNotIn("red; } body", html)


if __name__ == "__main__":
    unittest.main(verbosity=2)
