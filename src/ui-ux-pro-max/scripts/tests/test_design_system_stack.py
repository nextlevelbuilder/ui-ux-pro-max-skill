#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regression tests for the dropped --stack flag in --design-system mode (issue #484).

`search.py "<query>" --design-system --stack nextjs` used to exit successfully
without any indication that the stack was never applied, so a caller following
SKILL.md's "never assume a stack" guidance could believe stack guidance was
part of the generated design system. The combination must stay valid, but it
must say that --stack was ignored.

Stdlib-only (unittest, not pytest) to match test_core.py -- this project ships
with zero external dependencies.

Run with:
    python -m unittest discover -s scripts/tests -v
or directly:
    python scripts/tests/test_design_system_stack.py
"""

import subprocess
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
SEARCH = SCRIPTS_DIR / "search.py"


class TestStackFlagWithDesignSystem(unittest.TestCase):
    def run_search(self, *args):
        # The child forces UTF-8 on its streams (search.py), so decode as UTF-8
        # regardless of the parent's locale on Windows.
        return subprocess.run(
            [sys.executable, str(SEARCH), *map(str, args)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    def test_design_system_with_stack_succeeds_and_says_stack_is_ignored(self):
        proc = self.run_search("platform engineer dashboard", "--design-system", "--stack", "nextjs")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("--stack", proc.stderr)
        self.assertIn("ignored", proc.stderr.lower())

    def test_design_system_without_stack_stays_quiet(self):
        proc = self.run_search("platform engineer dashboard", "--design-system")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertNotIn("ignored", proc.stderr.lower())

    def test_stack_search_alone_never_warns(self):
        proc = self.run_search("dashboard table density", "--stack", "nextjs")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertNotIn("ignored", proc.stderr.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
