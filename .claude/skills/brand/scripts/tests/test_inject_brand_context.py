"""Regression test for inject-brand-context.cjs.

The prohibited-terms parser matched table cells with a single global regex
(`/\\|\\s*([^|]+)\\s*\\|/g`). That pattern consumes the pipe shared between two
columns, so successive matches alternated between the `Avoid` column and the
`Reason` column. For the bundled starter template the extracted ban list came
back as `Revolutionary, Overused, Seamless, Corporate jargon, Leverage` —
dropping real banned words and promoting prose from the Reason column. Since
this list is injected into prompts as a content guardrail, half the terms were
silently unenforced. These tests assert the first cell of every row is used.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent
SCRIPT = SCRIPTS / "inject-brand-context.cjs"
BRAND_STARTER = SCRIPTS.parent / "templates" / "brand-guidelines-starter.md"


def _run(tmp_path: Path, *args: str) -> subprocess.CompletedProcess:
    node = shutil.which("node")
    if not node:
        pytest.skip("node not available")
    return subprocess.run(
        [node, str(SCRIPT), *args],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def _context(tmp_path: Path) -> dict:
    result = _run(tmp_path, "--json")
    assert result.returncode == 0, result.stderr + result.stdout
    return json.loads(result.stdout)


def test_prohibited_terms_from_bundled_starter_template(tmp_path):
    """The Avoid column must be read without bleeding into Reason."""
    (tmp_path / "docs").mkdir()
    shutil.copy(BRAND_STARTER, tmp_path / "docs" / "brand-guidelines.md")

    prohibited = _context(tmp_path)["voice"]["prohibited"]

    assert prohibited == [
        "Revolutionary",
        "Best-in-class",
        "Seamless",
        "Synergy",
        "Leverage",
    ]


def test_prohibited_terms_exclude_reason_column(tmp_path):
    """Reason text must never be reported as a banned term."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "brand-guidelines.md").write_text(
        "## 4. Voice & Tone\n\n"
        "### Prohibited Terms\n\n"
        "| Avoid | Reason |\n"
        "|-------|--------|\n"
        "| Failed | Shames the user |\n"
        "| Lazy | Shames the user |\n"
        "| Simply | Minimizes real difficulty |\n"
        "| Seamless | Overused |\n"
    )

    prohibited = _context(tmp_path)["voice"]["prohibited"]

    assert prohibited == ["Failed", "Lazy", "Simply", "Seamless"]
    assert "Shames the user" not in prohibited
    assert "Overused" not in prohibited


def test_prohibited_terms_tolerate_bold_cells(tmp_path):
    """Authors bold the first column elsewhere in the template; allow it."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "brand-guidelines.md").write_text(
        "### Prohibited Terms\n\n"
        "| Avoid | Reason |\n"
        "|-------|--------|\n"
        "| **Disrupt** | Overused |\n"
        "| **Ninja** | Exclusionary |\n"
    )

    prohibited = _context(tmp_path)["voice"]["prohibited"]

    assert prohibited == ["Disrupt", "Ninja"]
