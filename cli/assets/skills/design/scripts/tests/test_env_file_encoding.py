"""load_env() runs at import time and must read .env files as UTF-8.

Without an explicit encoding, open() uses the locale encoding (cp1252 on Windows,
ASCII under LC_ALL=C on POSIX) and a UTF-8 .env containing a byte that encoding
cannot decode raises UnicodeDecodeError, which stops the script before argument
parsing.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

DESIGN_SCRIPTS = Path(__file__).resolve().parent.parent

# Import the script under an offline google.genai stub, as the other tests do,
# and print what load_env() put in the environment. GOOGLE_API_KEY is the probe:
# it is one of the keys the scripts take from a .env, and its value comes from the
# temporary .env written below.
RUNNER = """
import importlib.util, os, sys, types
for name in ("google", "google.genai", "google.genai.types"):
    sys.modules[name] = types.ModuleType(name)
sys.modules["google"].genai = sys.modules["google.genai"]
sys.modules["google.genai"].types = sys.modules["google.genai.types"]
spec = importlib.util.spec_from_file_location("under_test", sys.argv[1])
spec.loader.exec_module(importlib.util.module_from_spec(spec))
print(os.environ.get("GOOGLE_API_KEY"))
"""


@pytest.mark.parametrize("script", ["logo", "cip", "icon"])
def test_load_env_reads_a_utf8_env_file(script, tmp_path):
    (tmp_path / ".claude").mkdir()
    # The comment holds U+201D, U+010D and U+50CF. Their UTF-8 bytes include 0x9d,
    # 0x8d and 0x8f, which cp1252 leaves undefined, and none of them is ASCII.
    (tmp_path / ".claude" / ".env").write_bytes(
        b"# \xe2\x80\x9d \xc4\x8d \xe5\x83\x8f\nGOOGLE_API_KEY=ok\n"
    )
    env = dict(os.environ)
    # load_env() also reads ~/.claude/.env, so point the home directory at tmp_path:
    # the only .env it can find is the one above, and no request is made.
    env.update({
        "HOME": str(tmp_path),
        "USERPROFILE": str(tmp_path),
        "APPDATA": str(tmp_path),
        "GEMINI_API_KEY": "",
        "ATLASCLOUD_API_KEY": "",
        "MUAPI_API_KEY": "",
        "UBERLLM_API_KEY": "",
        # Not UTF-8 on any platform: cp1252 on Windows, ASCII with LC_ALL=C on POSIX.
        "PYTHONUTF8": "0",
        "LC_ALL": "C",
        "PYTHONCOERCECLOCALE": "0",
        "PYTHONIOENCODING": "cp1252",
    })
    env.pop("GOOGLE_API_KEY", None)
    result = subprocess.run(
        [sys.executable, "-c", RUNNER, str(DESIGN_SCRIPTS / script / "generate.py")],
        capture_output=True,
        stdin=subprocess.DEVNULL,
        env=env,
        cwd=tmp_path,
        encoding="utf-8",
        errors="replace",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "ok"
