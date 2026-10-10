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


def _run(tmp_path: Path, *args: str) -> subprocess.CompletedProcess:
    node = shutil.which("node")
    if not node:
        pytest.skip("node not available")
    return subprocess.run(
        [node, str(SCRIPT), *args],
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

    result = _run(tmp_path, "--force")

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


def test_dark_base_color_does_not_collapse_shades_to_black(tmp_path):
    """adjustBrightness() used to add/subtract a flat 255*percent per channel.

    For a dark base color (channels already close to 0), darkening by
    -0.3/-0.45/-0.6 clamped every channel to 0, so shades 700, 800, and 900
    all came back as the identical, useless #000000 instead of a graded dark
    scale. This runs the sync against a dark, coffee-roastery-style brand
    color and asserts the three shades stay distinct and non-black.
    """
    (tmp_path / "docs").mkdir()
    (tmp_path / "assets").mkdir()
    shutil.copy(TOKENS_STARTER, tmp_path / "assets" / "design-tokens.json")
    (tmp_path / "docs" / "brand-guidelines.md").write_text(
        "## Quick Reference\n\n"
        "| Element | Value |\n"
        "|---------|-------|\n"
        "| Primary Color | #4A3228 |\n"
        "| Secondary Color | #C08A3E |\n"
        "| Accent Color | #6B8F71 |\n"
    )

    result = _run(tmp_path, "--force")
    assert result.returncode == 0, result.stderr + result.stdout

    tokens = json.loads((tmp_path / "assets" / "design-tokens.json").read_text())
    primary = tokens["primitive"]["color"]["primary"]
    dark_shades = [primary[shade]["$value"] for shade in ("700", "800", "900")]

    assert len(set(dark_shades)) == 3, (
        f"expected three distinct dark shades, got {dark_shades}"
    )
    assert "#000000" not in dark_shades, dark_shades


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


def test_creates_default_output_directory_when_missing(tmp_path):
    """A first sync should create assets/ instead of failing with ENOENT."""
    (tmp_path / "docs").mkdir()
    shutil.copy(BRAND_STARTER, tmp_path / "docs" / "brand-guidelines.md")

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr + result.stdout
    assert (tmp_path / "assets" / "design-tokens.json").exists()
    assert (tmp_path / "assets" / "design-tokens.css").exists()


def test_refuses_existing_design_tokens_without_force(tmp_path):
    """The script must not silently replace its own existing token source."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "assets").mkdir()
    shutil.copy(BRAND_STARTER, tmp_path / "docs" / "brand-guidelines.md")
    tokens_path = tmp_path / "assets" / "design-tokens.json"
    existing = '{"existing": true}\n'
    tokens_path.write_text(existing)

    result = _run(tmp_path)

    assert result.returncode == 1
    assert "assets/design-tokens.json" in result.stderr
    assert "--force" in result.stderr
    assert tokens_path.read_text() == existing


def test_refuses_css_custom_property_source_without_force(tmp_path):
    """Common app CSS token sources must be named instead of duplicated."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "src").mkdir()
    shutil.copy(BRAND_STARTER, tmp_path / "docs" / "brand-guidelines.md")
    (tmp_path / "src" / "index.css").write_text(
        ":root {\n  --primary: #2563eb;\n  --foreground: #0f172a;\n}\n"
    )

    result = _run(tmp_path)

    assert result.returncode == 1
    assert "src/index.css" in result.stderr
    assert "--force" in result.stderr
    assert not (tmp_path / "assets" / "design-tokens.json").exists()


def test_refuses_grouped_root_selector_without_force(tmp_path):
    """A :root selector list is still an existing project token source."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "src").mkdir()
    shutil.copy(BRAND_STARTER, tmp_path / "docs" / "brand-guidelines.md")
    (tmp_path / "src" / "index.css").write_text(
        ':root, [data-theme="light"] {\n  --primary: #2563eb;\n}\n'
    )

    result = _run(tmp_path)

    assert result.returncode == 1
    assert "src/index.css" in result.stderr
    assert not (tmp_path / "assets" / "design-tokens.json").exists()


def test_ignores_commented_root_custom_properties(tmp_path):
    """Commented examples must not block a first token sync."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "src").mkdir()
    shutil.copy(BRAND_STARTER, tmp_path / "docs" / "brand-guidelines.md")
    (tmp_path / "src" / "index.css").write_text(
        "/* Example only:\n:root {\n  --primary: #2563eb;\n}\n*/\n"
    )

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr + result.stdout
    assert (tmp_path / "assets" / "design-tokens.json").exists()


def test_ignores_custom_properties_outside_root(tmp_path):
    """Component-local variables alone are not a project token source."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "src").mkdir()
    shutil.copy(BRAND_STARTER, tmp_path / "docs" / "brand-guidelines.md")
    (tmp_path / "src" / "index.css").write_text(
        ":root {\n  color-scheme: light;\n}\n\n"
        ".progress {\n  --progress-value: 50%;\n}\n"
    )

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr + result.stdout
    assert (tmp_path / "assets" / "design-tokens.json").exists()


def test_refuses_tailwind_theme_colors_without_force(tmp_path):
    """Tailwind theme colors are an existing project token source."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "assets").mkdir()
    shutil.copy(BRAND_STARTER, tmp_path / "docs" / "brand-guidelines.md")
    (tmp_path / "tailwind.config.js").write_text(
        "module.exports = { theme: { extend: { colors: { brand: '#2563eb' } } } }\n"
    )

    result = _run(tmp_path)

    assert result.returncode == 1
    assert "tailwind.config.js" in result.stderr
    assert "--force" in result.stderr
    assert not (tmp_path / "assets" / "design-tokens.json").exists()


def test_refuses_tailwind_v4_theme_source_without_force(tmp_path):
    """Tailwind v4 @theme variables are an existing project token source."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "src").mkdir()
    shutil.copy(BRAND_STARTER, tmp_path / "docs" / "brand-guidelines.md")
    (tmp_path / "src" / "index.css").write_text(
        "@theme {\n  --color-brand-500: #2563eb;\n}\n"
    )

    result = _run(tmp_path)

    assert result.returncode == 1
    assert "src/index.css" in result.stderr
    assert not (tmp_path / "assets" / "design-tokens.json").exists()


def test_refuses_token_source_imported_by_common_css_entry(tmp_path):
    """Local CSS imports must be followed to their actual token source."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "src" / "styles").mkdir(parents=True)
    shutil.copy(BRAND_STARTER, tmp_path / "docs" / "brand-guidelines.md")
    (tmp_path / "src" / "index.css").write_text(
        '@import "./styles/theme.css";\n'
    )
    (tmp_path / "src" / "styles" / "theme.css").write_text(
        "@theme {\n  --color-brand-500: #2563eb;\n}\n"
    )

    result = _run(tmp_path)

    assert result.returncode == 1
    assert "src/styles/theme.css" in result.stderr
    assert not (tmp_path / "assets" / "design-tokens.json").exists()


def test_ignores_external_css_imports(tmp_path):
    """Remote and package imports are not project-owned token sources."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "src").mkdir()
    shutil.copy(BRAND_STARTER, tmp_path / "docs" / "brand-guidelines.md")
    (tmp_path / "src" / "index.css").write_text(
        '@import "https://example.com/theme.css";\n'
        '@import "tailwindcss";\n'
    )

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr + result.stdout
    assert (tmp_path / "assets" / "design-tokens.json").exists()


def test_refuses_tailwind_config_with_sibling_preset_without_force(tmp_path):
    """A delegated Tailwind theme must not be treated as token-free."""
    (tmp_path / "docs").mkdir()
    shutil.copy(BRAND_STARTER, tmp_path / "docs" / "brand-guidelines.md")
    (tmp_path / "tailwind.config.js").write_text(
        "const preset = require('./tailwind.preset');\n"
        "module.exports = { presets: [preset] };\n"
    )
    (tmp_path / "tailwind.preset.js").write_text(
        "module.exports = { theme: { colors: { brand: '#2563eb' } } };\n"
    )

    result = _run(tmp_path)

    assert result.returncode == 1
    assert "tailwind.config.js" in result.stderr
    assert not (tmp_path / "assets" / "design-tokens.json").exists()


def test_force_allows_sync_with_existing_css_token_source(tmp_path):
    """The explicit force flag overrides token-source detection."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "src").mkdir()
    shutil.copy(BRAND_STARTER, tmp_path / "docs" / "brand-guidelines.md")
    (tmp_path / "src" / "index.css").write_text(
        ":root {\n  --primary: #2563eb;\n}\n"
    )

    result = _run(tmp_path, "--force")

    assert result.returncode == 0, result.stderr + result.stdout
    assert (tmp_path / "assets" / "design-tokens.json").exists()


@pytest.mark.parametrize(
    "relative_path",
    [
        "src/styles/global.css",
        "src/global.css",
        "src/main.css",
        "src/styles/theme.css",
        "styles/variables.css",
    ],
)
def test_refuses_token_source_under_unlisted_css_filename(tmp_path, relative_path):
    """Token detection must not hinge on an exact filename.

    The candidate list only held the plural `globals.css` spellings, so a
    project whose entry point is `src/styles/global.css` — one letter apart —
    was never scanned and the guard silently passed, leaving the generated
    `assets/design-tokens.*` to compete with an existing palette.
    """
    (tmp_path / "docs").mkdir()
    shutil.copy(BRAND_STARTER, tmp_path / "docs" / "brand-guidelines.md")
    css = tmp_path / relative_path
    css.parent.mkdir(parents=True, exist_ok=True)
    css.write_text(":root {\n  --dawn: #f5a524;\n  --ink: #1c1626;\n}\n")

    result = _run(tmp_path)

    assert result.returncode == 1, result.stdout + result.stderr
    assert relative_path in result.stderr
    assert "--force" in result.stderr
    assert not (tmp_path / "assets" / "design-tokens.json").exists()


def test_discovered_css_without_tokens_does_not_block_sync(tmp_path):
    """Scanning extra CSS files must not introduce false positives.

    Plain stylesheets carry no custom properties, so they are not token
    sources and must leave the sync path alone.
    """
    (tmp_path / "docs").mkdir()
    shutil.copy(BRAND_STARTER, tmp_path / "docs" / "brand-guidelines.md")
    styles = tmp_path / "src" / "styles"
    styles.mkdir(parents=True)
    (styles / "global.css").write_text(".btn {\n  color: red;\n}\n")
    (styles / "reset.css").write_text("* {\n  margin: 0;\n}\n")

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr + result.stdout
    assert (tmp_path / "assets" / "design-tokens.json").exists()
