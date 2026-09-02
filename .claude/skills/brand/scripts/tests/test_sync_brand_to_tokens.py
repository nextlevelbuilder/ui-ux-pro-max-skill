"""Regression test for sync-brand-to-tokens.cjs.

The color parser required a parenthesized name in the Quick Reference row
(`#2563EB (name)`) and a bolded label in the color tables (`**Primary Blue**`),
neither of which the bundled starter template uses. As a result the base hex
came back `undefined` and `adjustBrightness(undefined)` threw a TypeError —
i.e. the script crashed on its own documented happy path. This test runs the
sync against the bundled starter template and asserts it completes and writes
the expected base colors. It is pytest-based so the existing pytest CI runs it.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent
SCRIPT = SCRIPTS / "sync-brand-to-tokens.cjs"
BRAND_STARTER = SCRIPTS.parent / "templates" / "brand-guidelines-starter.md"
TOKENS_STARTER = (
    SCRIPTS.parent.parent / "design-system" / "templates" / "design-tokens-starter.json"
)


def _run(tmp_path: Path) -> subprocess.CompletedProcess:
    node = shutil.which("node")
    if not node:
        pytest.skip("node not available")
    return subprocess.run(
        [node, str(SCRIPT)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        # sync-brand-to-tokens.cjs prints emoji. Without an explicit encoding,
        # `text=True` decodes the pipe with the locale codec, and several of
        # those emoji have UTF-8 bytes that cp1252 has no character for
        # (0x8F in the warning, 0x9D in the error, 0x8F in the dry-run notice).
        # Decoding then raises inside subprocess's reader thread, the stream
        # comes back as None, and assertions against it fail with a TypeError
        # that hides the real result.
        encoding="utf-8",
    )


def test_sync_parses_bundled_starter_template(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "assets").mkdir()
    shutil.copy(BRAND_STARTER, tmp_path / "docs" / "brand-guidelines.md")
    shutil.copy(TOKENS_STARTER, tmp_path / "assets" / "design-tokens.json")

    result = _run(tmp_path)

    # Must not crash (the bug raised an unhandled TypeError).
    assert "TypeError" not in result.stderr, result.stderr
    assert result.returncode == 0, result.stderr + result.stdout

    tokens = json.loads((tmp_path / "assets" / "design-tokens.json").read_text())
    primitive = tokens["primitive"]["color"]
    assert primitive["primary"]["500"]["$value"] == "#2563EB"
    assert primitive["secondary"]["500"]["$value"] == "#8B5CF6"
    assert primitive["accent"]["500"]["$value"] == "#10B981"

    # #474: the sibling design-system script is resolved from this skill's own
    # location, so the CSS regeneration must run even though tmp_path has no
    # .claude/skills/ tree. Before the fix it was resolved from the working
    # directory and silently skipped in every layout but a project install.
    assert "Regenerated" in result.stdout, result.stdout
    css = tmp_path / "assets" / "design-tokens.css"
    assert css.exists() and css.stat().st_size > 0


def test_reports_missing_guidelines_without_breaking_the_harness(tmp_path):
    """The missing-guidelines path is the one that breaks a locale-decoded pipe.

    It is also the default state of any project that has not run the brand skill
    yet, so it is the path a contributor hits first. The script prints its error
    with a leading emoji whose UTF-8 encoding contains 0x9D; cp1252 has no
    character there, so on Windows this test fails with
    ``TypeError: argument of type 'NoneType' is not a container`` unless the
    subprocess pipe is pinned to UTF-8.
    """
    result = _run(tmp_path)

    assert result.returncode == 1
    assert result.stderr is not None
    assert "Brand guidelines not found" in result.stderr
