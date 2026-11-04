"""Repository packaging contracts for the visual-direction skill (mirrors the CI greps + script-path test).

Scoped to this skill's directory in both trees so a failure names the skill.
"""

import ast
import re
import sys
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[2]
SKILL = SKILL_DIR.name
REPO = next((p for p in SKILL_DIR.parents if (p / "scripts" / "generate-catalog-summary.py").is_file()), None)
TREES = [SKILL_DIR]
if REPO is not None and (REPO / "cli" / "assets" / "skills" / SKILL).is_dir():
    TREES.append(REPO / "cli" / "assets" / "skills" / SKILL)

INVOCATION = re.compile(r'(?<![\w/.-])(?:python3?|node|bash)\s+"?([^\s"`\']+\.(?:py|cjs|js|mjs|sh))')
ALLOWED_SKILLS = {"ui-ux-pro-max", "design", "design-system", "brand", "ui-styling", "slides", "banner-design",
                  "visual-direction", "reference-analysis", "visual-audit"}
FORBIDDEN_NAMES = re.compile(r"\b(frontend-design|ai-artist|ai-multimodal|chrome-devtools|assets-organizing|project-management)\b", re.I)
HOME_ROOTED = re.compile(r"~/\.claude/skills/[A-Za-z0-9_-]+\b")
_PR = "CLAUDE" + "_PLUGIN_" + "ROOT"  # spelled in pieces: CI greps the literal token in every shipped file
PROJECT_ROOTED = re.compile(r"(?<![/\w])\.claude/skills/[A-Za-z0-9_-]+\b|(?<!~)(?<!\$%s)(?<!\$\{%s\})/\.claude/skills/[A-Za-z0-9_-]+\b" % (_PR, _PR))
PLUGIN_ROOT = re.compile(_PR)
CK_NAMESPACE = re.compile(r"(?<![\w/])/ckm?:")
SKILL_REF = re.compile(r"`([a-z0-9-]+)`(?:\*\*)?(?=(?:(?:,\s+|\s+and\s+|,\s+and\s+|\s+or\s+|,\s+or\s+|/|\s+→\s+|\s+->\s+)(?:\*\*)?`[a-z0-9-]+`(?:\*\*)?)*\s+(?:sub-)?[Ss]kills?\b)")
TEXT_SUFFIXES = {".md", ".py", ".csv", ".json", ".txt", ".cjs", ".js", ".mjs", ".sh", ".yml", ".yaml", ".toml", ".tmpl"}
STDLIB = getattr(sys, "stdlib_module_names", None) or {
    "argparse", "ast", "collections", "colorsys", "csv", "datetime", "difflib", "hashlib", "json", "math", "os", "re", "sys", "pathlib"}


def text_files(tree):
    for path in sorted(tree.rglob("*")):
        if path.is_file() and path.suffix in TEXT_SUFFIXES and ".pytest_cache" not in path.parts and "__pycache__" not in path.parts:
            yield path


def markdown_files(tree):
    return [p for p in text_files(tree) if p.suffix == ".md"]


def resolve(skill_dir, path):
    if path.startswith("scripts/"):
        return skill_dir / path, None
    if path.startswith("../"):
        parts = path.split("/")
        if len(parts) > 3 and parts[2] == "scripts" and (skill_dir.parent / parts[1]).is_dir():
            return skill_dir.parent / parts[1] / "/".join(parts[2:]), None
        return None, "a sibling invocation must be ../<skill>/scripts/<file> and the sibling must ship"
    return None, "not skill-relative (expected scripts/<file> or ../<skill>/scripts/<file>)"


def parse_frontmatter(text):
    assert text.startswith("---\n"), "SKILL.md must start with frontmatter"
    block = text.split("\n---", 1)[0].split("\n", 1)[1]
    data, nested = {}, None
    for line in block.splitlines():
        if not line.strip():
            continue
        if line.startswith("  ") and nested:
            key, _, value = line.strip().partition(":")
            data[nested][key.strip()] = value.strip().strip('"')
        else:
            key, _, value = line.partition(":")
            if value.strip() == "":
                nested = key.strip()
                data[nested] = {}
            else:
                nested = None
                data[key.strip()] = value.strip().strip('"')
    return data


@pytest.mark.parametrize("tree", TREES, ids=lambda t: str(t.relative_to(REPO)) if REPO else t.name)
def test_rc01_every_markdown_invocation_resolves(tree):
    problems, seen = [], 0
    for md in markdown_files(tree):
        for lineno, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            for match in INVOCATION.finditer(line):
                seen += 1
                target, reason = resolve(tree, match.group(1))
                if reason is None and not target.is_file():
                    reason = "no such file: %s" % target
                if reason:
                    problems.append("%s:%d: %s -- %s" % (md.relative_to(tree), lineno, match.group(1), reason))
    assert seen >= 1, "extractor found no invocations"
    assert problems == [], "\n" + "\n".join(problems)


@pytest.mark.parametrize("pattern,label", [(HOME_ROOTED, "home-rooted"), (PROJECT_ROOTED, "project-rooted"), (PLUGIN_ROOT, "plugin-root variable")])
def test_rc02_rc03_no_install_specific_paths_in_any_file(pattern, label):
    hits = []
    for tree in TREES:
        for path in text_files(tree):
            if path.name == Path(__file__).name:
                continue
            for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if pattern.search(line):
                    hits.append("%s:%d: %s" % (path.relative_to(tree), lineno, line.strip()[:100]))
    assert hits == [], "%s paths:\n%s" % (label, "\n".join(hits))


def test_rc04_no_claudekit_namespaces():
    hits = [str(md) for tree in TREES for md in markdown_files(tree) if CK_NAMESPACE.search(md.read_text(encoding="utf-8"))]
    assert hits == []


def test_rc05_skill_references_are_bundled():
    offending = []
    for tree in TREES:
        for md in markdown_files(tree):
            for match in SKILL_REF.finditer(md.read_text(encoding="utf-8")):
                if match.group(1) not in ALLOWED_SKILLS:
                    offending.append("%s: `%s`" % (md.relative_to(tree), match.group(1)))
    assert offending == []


def test_rc06_no_claudekit_only_names():
    hits = []
    for tree in TREES:
        for md in markdown_files(tree):
            for lineno, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
                if FORBIDDEN_NAMES.search(line):
                    hits.append("%s:%d" % (md.relative_to(tree), lineno))
    assert hits == []


def test_rc07_skill_frontmatter():
    data = parse_frontmatter((SKILL_DIR / "SKILL.md").read_text(encoding="utf-8"))
    assert data["name"] == SKILL
    assert len(data["description"]) >= 40 and "art style" in data["description"]
    assert data["argument-hint"] and data["license"] == "MIT"
    assert data["metadata"]["author"] == "ui-ux-pro-max" and data["metadata"]["version"] == "1.0.0"


def test_rc08_script_paths_paragraph_present():
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "## Script Paths" in text
    assert "relative to the directory that contains this SKILL.md" in text
    assert len(text.splitlines()) <= 250


def test_rc09_references_exist_and_no_orphans():
    skill_md = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    for ref in re.findall(r"`(references/[^`]+\.md)`", skill_md):
        assert (SKILL_DIR / ref).is_file(), ref
    corpus = skill_md + "".join(p.read_text(encoding="utf-8") for p in (SKILL_DIR / "references").rglob("*.md"))
    for doc in (SKILL_DIR / "references").rglob("*.md"):
        assert doc.name in corpus, "orphan reference: %s" % doc.relative_to(SKILL_DIR)


def test_rc10_scripts_are_stdlib_only():
    for script in (SKILL_DIR / "scripts").glob("*.py"):
        tree = ast.parse(script.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                names = [node.module.split(".")[0]]
            for name in names:
                assert name in STDLIB or name in ("vd_core", "vd_tokens"), "%s imports %s" % (script.name, name)


@pytest.mark.parametrize("script,subcommands", [("vd.py", ["styles", "genres", "components", "profile", "init", "page", "validate"])])
def test_rc11_json_flag_documented(script, subcommands):
    import subprocess
    for sub in subcommands:
        proc = subprocess.run([sys.executable, str(SKILL_DIR / "scripts" / script), sub, "--help"], capture_output=True, text=True, timeout=60)
        assert proc.returncode == 0 and "--json" in proc.stdout, sub


def test_rc12_cli_mirror_identical_when_present():
    if REPO is None or len(TREES) < 2:
        pytest.skip("not synced yet - run npm --prefix cli run sync:assets")
    src, dst = TREES
    src_files = {p.relative_to(src) for p in text_files(src) if "tests" not in p.parts}
    dst_files = {p.relative_to(dst) for p in text_files(dst) if "tests" not in p.parts}
    assert src_files <= dst_files, src_files - dst_files
    for rel in sorted(src_files):
        a = (src / rel).read_bytes().replace(b"\r\n", b"\n")
        b = (dst / rel).read_bytes().replace(b"\r\n", b"\n")
        assert a == b, "mirror differs: %s" % rel


def test_rc13_rc14_fixtures_clean_and_small():
    for path in (SKILL_DIR / "scripts" / "tests" / "fixtures").iterdir():
        assert path.stat().st_size < 200 * 1024, path.name
        assert path.suffix != ".png", path.name
        text = path.read_text(encoding="utf-8", errors="replace")
        assert not HOME_ROOTED.search(text) and not PROJECT_ROOTED.search(text), path.name


def test_rc15_test_module_names_unique_across_skills():
    skills_root = SKILL_DIR.parent
    names = {}
    for test in skills_root.glob("*/scripts/tests/test_*.py"):
        names.setdefault(test.name, []).append(test.parent.parent.parent.name)
    duplicates = dict((n, s) for n, s in names.items() if len(s) > 1)
    assert duplicates == {}, duplicates
    assert not (SKILL_DIR / "scripts" / "tests" / "conftest.py").exists()


def test_data_files_present_with_lf():
    for name in ("visual-styles.csv", "genre-profiles.csv", "component-catalog.csv"):
        raw = (SKILL_DIR / "data" / name).read_bytes()
        assert raw and b"\r" not in raw, name
    assert (SKILL_DIR / "templates" / "master-template.md").is_file()
