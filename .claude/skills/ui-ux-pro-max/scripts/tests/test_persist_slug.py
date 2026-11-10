#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regression tests for project/page slugs used by persist_design_system.

Non-ASCII project names (e.g. Chinese or Japanese) used to collapse to the
"default" slug, so two different projects shared design-system/default/.

Run with:
    python -m unittest discover -s scripts/tests -v
"""

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from design_system import DesignSystemGenerator, persist_design_system, safe_slug  # noqa: E402


class TestPersistSlug(unittest.TestCase):
    def test_non_ascii_projects_get_separate_folders(self):
        gen = DesignSystemGenerator()
        with tempfile.TemporaryDirectory() as out:
            first = persist_design_system(gen.generate("saas dashboard", "电商平台"), output_dir=out)
            second = persist_design_system(gen.generate("fintech app", "銀行アプリ"), output_dir=out)
            self.assertEqual(second["status"], "success")
            self.assertNotEqual(first["design_system_dir"], second["design_system_dir"])

    def test_slug_stays_a_single_safe_segment(self):
        for name in ("../../etc", "a/b\\c", "..", "电商/../平台"):
            slug = safe_slug(name)
            self.assertNotIn("/", slug)
            self.assertNotIn("\\", slug)
            self.assertNotIn(".", slug)
            self.assertTrue(slug)


if __name__ == "__main__":
    unittest.main()
