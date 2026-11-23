"""Batch mode prints check marks; it must not crash when stdout is a cp1252 pipe or file."""

import os
import subprocess
import sys
from pathlib import Path

GENERATE = Path(__file__).resolve().parents[1] / "generate.py"


def test_batch_survives_non_utf8_stdout(tmp_path):
    # load_env() reads .env files from the skill folder and from ~/.claude and never
    # overrides a variable that is already set. Point the home directory at tmp_path
    # and set every provider key to an empty string (treated as unset) so no local
    # key can be picked up and no request is ever made: each variant fails offline
    # and the loop reaches its "failed" line.
    env = dict(os.environ)
    env.update({
        "HOME": str(tmp_path),
        "USERPROFILE": str(tmp_path),
        "APPDATA": str(tmp_path),
        "GEMINI_API_KEY": "",
        "GOOGLE_API_KEY": "",
        "ATLASCLOUD_API_KEY": "",
        "MUAPI_API_KEY": "",
        "UBERLLM_API_KEY": "",
        # PYTHONIOENCODING=cp1252 reproduces a Windows console/pipe on any platform.
        "PYTHONUTF8": "0",
        "PYTHONIOENCODING": "cp1252",
    })
    result = subprocess.run(
        [sys.executable, str(GENERATE), "--brand", "Cafe", "--batch", "1",
         "--output-dir", str(tmp_path / "logos")],
        capture_output=True,
        stdin=subprocess.DEVNULL,
        env=env,
        cwd=tmp_path,
        encoding="utf-8",
        errors="replace",
    )

    assert "UnicodeEncodeError" not in result.stderr, result.stderr
    assert "Failed: minimalist" in result.stdout
    assert "BATCH COMPLETE: 0/1 logos generated" in result.stdout
    assert "✗" in result.stdout
    assert result.returncode == 1
