"""Regression tests for validate-tokens.cjs.

The validator used to skip any line containing ``var(--`` outright, so a
hardcoded value sharing a line with a token reference (extremely common in
real CSS, and universal in minified CSS where everything is one line) went
undetected. These tests drive the CLI via ``node`` and assert it flags such
cases. They are pytest-based so the repository's existing pytest CI runs them.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "validate-tokens.cjs"


def _run(tmp_path: Path, css: str) -> subprocess.CompletedProcess:
    node = shutil.which("node")
    if not node:
        pytest.skip("node not available")
    (tmp_path / "sample.css").write_text(css, encoding="utf-8")
    return subprocess.run(
        [node, str(SCRIPT), "--dir", str(tmp_path)],
        capture_output=True,
        text=True,
        # validate-tokens.cjs prints emoji; without an explicit encoding Python
        # decodes the pipe with the locale codec (cp1252 on Windows), which
        # raises in the reader thread and leaves result.stdout set to None.
        encoding="utf-8",
    )


def test_flags_hardcoded_hex_sharing_line_with_token(tmp_path):
    """A hardcoded hex on the same line as a var() token is still a violation."""
    result = _run(
        tmp_path,
        ".btn { background: #FF6B6B; color: var(--color-primary); }\n",
    )
    assert "#FF6B6B" in result.stdout, result.stdout
    assert result.returncode == 1


def test_token_only_line_reports_no_violation(tmp_path):
    """A line that references only tokens produces no false positives."""
    result = _run(
        tmp_path,
        ".btn { background: var(--color-bg); color: var(--color-primary); }\n",
    )
    assert "No token violations" in result.stdout, result.stdout
    assert result.returncode == 0
