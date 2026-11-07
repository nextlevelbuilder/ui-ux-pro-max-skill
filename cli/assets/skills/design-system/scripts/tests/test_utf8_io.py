"""Regression tests: sub-skill scripts must read and write text as UTF-8.

``open()``, ``Path.read_text()`` and ``Path.write_text()`` without an explicit
``encoding`` use the locale codec, which is cp1252 on Windows. A UTF-8 file
containing a byte cp1252 does not map (0x81, as in "ā" or most CJK text) made
html-token-validator.py crash, and generate-slide.py --json silently turned
"Café" into "CafÃ©" (mojibake). The subprocess tests below force a non-UTF-8
locale codec (cp1252 on Windows, ASCII on POSIX) so they fail the same way on
any platform.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent

# "ā" is UTF-8 C4 81: byte 0x81 is undefined in cp1252, so reading it with the
# locale codec raises. "Café" is C3 A9: every byte decodes in cp1252, so reading
# it with the locale codec silently yields "CafÃ©".
CRASH_TEXT = "ā 你好"
MOJIBAKE_TEXT = "Café"


def _run(*args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.pop("PYTHONIOENCODING", None)
    env.update({"PYTHONUTF8": "0", "LC_ALL": "C", "PYTHONCOERCECLOCALE": "0"})
    return subprocess.run(
        [sys.executable, *args],
        capture_output=True,
        env=env,
        encoding="utf-8",
        errors="replace",
    )


def test_html_token_validator_reads_utf8_html(tmp_path):
    page = tmp_path / "page.html"
    page.write_text(
        f"<html><body><h1>{CRASH_TEXT}</h1></body></html>", encoding="utf-8"
    )

    result = _run(str(SCRIPTS / "html-token-validator.py"), str(page))

    assert "Traceback" not in result.stderr, result.stderr
    # The page is validated and reported (it has no token import), not skipped.
    assert result.returncode == 1, result.stderr
    assert "HTML DESIGN TOKEN VALIDATION SUMMARY" in result.stdout, result.stdout
    assert "page.html" in result.stdout, result.stdout


def test_generate_slide_json_keeps_non_ascii_text(tmp_path):
    spec = tmp_path / "deck.json"
    spec.write_text(
        json.dumps(
            {
                "title": MOJIBAKE_TEXT,
                "slides": [{"type": "title", "title": MOJIBAKE_TEXT}],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    out = tmp_path / "deck.html"

    result = _run(
        str(SCRIPTS / "generate-slide.py"), "--json", str(spec), "--output", str(out)
    )

    assert result.returncode == 0, result.stderr
    html = out.read_text(encoding="utf-8")
    assert MOJIBAKE_TEXT in html
    assert "Ã" not in html  # UTF-8 bytes decoded as cp1252 leave "Ã" behind
