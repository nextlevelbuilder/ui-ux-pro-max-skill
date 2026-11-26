"""cip scripts print emoji; they must not crash when stdout is a cp1252 pipe or file."""

import base64
import os
import subprocess
import sys
from pathlib import Path

CIP = Path(__file__).resolve().parent.parent / "cip"

# 1x1 transparent PNG
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


def _run(args, tmp_path):
    env = dict(os.environ)
    # generate.py's load_env() reads .env files from the skill folder and from
    # ~/.claude and never overrides a variable that is already set. Point the home
    # directory at tmp_path and set the keys to empty strings (treated as unset)
    # so no local key can be picked up and no request is ever made.
    env.update({
        "HOME": str(tmp_path),
        "USERPROFILE": str(tmp_path),
        "GEMINI_API_KEY": "",
        "GOOGLE_API_KEY": "",
    })
    # PYTHONIOENCODING=cp1252 reproduces a Windows console/pipe on any platform.
    env.update({"PYTHONUTF8": "0", "PYTHONIOENCODING": "cp1252"})
    return subprocess.run(
        [sys.executable, *map(str, args)],
        capture_output=True,
        stdin=subprocess.DEVNULL,
        env=env,
        cwd=tmp_path,
        encoding="utf-8",
        errors="replace",
    )


def test_render_html_survives_non_utf8_stdout(tmp_path):
    images = tmp_path / "cip"
    images.mkdir()
    (images / "a.png").write_bytes(PNG)
    out = tmp_path / "out.html"

    result = _run(
        [CIP / "render-html.py", "--brand", "Cafe", "--images", images, "--output", out],
        tmp_path,
    )

    assert result.returncode == 0, result.stderr
    assert "HTML presentation generated" in result.stdout
    assert "Cafe" in out.read_text(encoding="utf-8")


def test_generate_logo_warning_survives_non_utf8_stdout(tmp_path):
    # No --logo and no --no-logo-prompt: the script prints its emoji warning and
    # reads EOF from stdin. It then stops (exit 1) before any network call because
    # google-genai or the API key is missing, so this stays offline.
    result = _run([CIP / "generate.py", "--brand", "Cafe"], tmp_path)

    assert "UnicodeEncodeError" not in result.stderr, result.stderr
    assert "No logo image provided" in result.stdout
    assert result.returncode == 1


def test_search_brief_survives_non_utf8_stdout(tmp_path):
    # search.py --cip-brief prints emoji section headers; it only reads the bundled CSVs.
    result = _run([CIP / "search.py", "tech startup", "--cip-brief", "--brand", "Cafe"], tmp_path)

    assert "UnicodeEncodeError" not in result.stderr, result.stderr
    assert result.returncode == 0, result.stderr
    assert "INDUSTRY" in result.stdout
