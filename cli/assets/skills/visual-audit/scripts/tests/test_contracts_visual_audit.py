"""Packaging / repository-contract tests for the visual-audit skill, scoped to its
own directory: script invocations resolve, no install-specific paths, only bundled
skill names, frontmatter, Script Paths paragraph, stdlib-only scripts, fixtures clean.
Patterns are assembled from fragments so this file never carries the forbidden
tokens it looks for."""
import ast
import re
import subprocess
import sys
from pathlib import Path

import pytest

SKILL_DIR = Path(__file__).resolve().parents[2]
SKILL = SKILL_DIR.name
SKILLS_ROOT = SKILL_DIR.parent
SCRIPTS = SKILL_DIR / "scripts"
REFERENCES = SKILL_DIR / "references"
FIXTURES = SCRIPTS / "tests" / "fixtures"

DOT_SKILLS = "." + "claude/skills/"
INVOCATION = re.compile(r'(?<![\w/.-])(?:python3?|node|bash)\s+"?([^\s"`\']+\.(?:py|cjs|js|mjs|sh))')
ALLOWED_SKILLS = {"ui-ux-pro-max", "design", "design-system", "brand", "ui-styling", "slides", "banner-design",
                  "visual-direction", "reference-analysis", "visual-audit"}
FORBIDDEN_NAMES = re.compile(r"\b(" + "|".join(["frontend-" + "design", "ai-" + "artist", "ai-" + "multimodal",
                                                 "chrome-" + "devtools", "assets-" + "organizing", "project-" + "management"]) + r")\b", re.I)
HOME_ROOTED = re.compile(r"~/\." + r"claude/skills/[A-Za-z0-9_-]+\b")
PROJECT_ROOTED = re.compile(r"(?<![/\w])\." + r"claude/skills/[A-Za-z0-9_-]+\b|(?<!~)/\." + r"claude/skills/[A-Za-z0-9_-]+\b")
PLUGIN_ROOT = re.compile("CLAUDE_PLUGIN" + "_ROOT")
CK_NAMESPACE = re.compile(r"(?<![\w/])/ckm?:")
SKILL_REF = re.compile(r"`([a-z0-9-]+)`(?:\*\*)?(?=(?:(?:,\s+|\s+and\s+|,\s+and\s+|\s+or\s+|,\s+or\s+|/|\s+→\s+|\s+->\s+)(?:\*\*)?`[a-z0-9-]+`(?:\*\*)?)*\s+(?:sub-)?[Ss]kills?\b)")


def text_files():
    for p in sorted(SKILL_DIR.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts and p.suffix not in (".png", ".pyc"):
            yield p


def md_files():
    return sorted(p for p in SKILL_DIR.rglob("*.md"))


def read(p):
    return p.read_text(encoding="utf-8", errors="replace")


def test_rc01_markdown_invocations_resolve():
    problems, seen = [], 0
    for md in md_files():
        for n, line in enumerate(read(md).splitlines(), 1):
            for m in INVOCATION.finditer(line):
                seen += 1
                path = m.group(1)
                if path.startswith("scripts/"):
                    target = SKILL_DIR / path
                elif path.startswith("../"):
                    parts = path.split("/")
                    if len(parts) < 4 or parts[2] != "scripts" or parts[1] not in ALLOWED_SKILLS:
                        problems.append("%s:%d: %s -- not ../<skill>/scripts/<file>" % (md, n, path))
                        continue
                    target = SKILLS_ROOT / path[3:]
                else:
                    problems.append("%s:%d: %s -- not skill-relative" % (md, n, path))
                    continue
                if not target.is_file():
                    problems.append("%s:%d: %s -- file does not exist (%s)" % (md, n, path, target))
    assert problems == [], "\n".join(problems)
    assert seen >= 5


def test_rc02_no_home_rooted_paths_in_any_file():
    hits = ["%s: %s" % (p, m.group(0)) for p in text_files() for m in HOME_ROOTED.finditer(read(p))]
    assert hits == []


def test_rc03_no_project_rooted_paths_or_plugin_root_token():
    hits = ["%s: %s" % (p, m.group(0)) for p in text_files() for m in PROJECT_ROOTED.finditer(read(p))]
    assert hits == []
    hits = [str(p) for p in text_files() if PLUGIN_ROOT.search(read(p)) and p.name != Path(__file__).name]
    assert hits == []


def test_rc04_no_claudekit_namespaces_in_markdown():
    assert [str(p) for p in md_files() if CK_NAMESPACE.search(read(p))] == []


def test_rc05_skill_references_are_bundled_names():
    bad = []
    for md in md_files():
        flat = re.sub(r"\s+", " ", read(md))
        for m in SKILL_REF.finditer(flat):
            if m.group(1) not in ALLOWED_SKILLS:
                bad.append("%s: `%s`" % (md.name, m.group(1)))
    assert bad == []
    skill_md = read(SKILL_DIR / "SKILL.md")
    assert "`visual-direction` skill" in skill_md and "`reference-analysis` skill" in skill_md and "`design-system` skill" in skill_md


def test_rc06_no_forbidden_skill_names_in_markdown():
    hits = ["%s: %s" % (p.name, m.group(0)) for p in md_files() for m in FORBIDDEN_NAMES.finditer(read(p))]
    assert hits == []


def parse_frontmatter(text):
    assert text.startswith("---\n")
    block = text.split("---\n", 2)[1]
    data, current = {}, None
    for line in block.splitlines():
        if not line.strip():
            continue
        if line.startswith("  ") and current:
            k, v = line.strip().split(":", 1)
            data[current][k.strip()] = v.strip().strip('"')
        else:
            k, v = line.split(":", 1)
            v = v.strip()
            if v == "":
                data[k.strip()] = {}
                current = k.strip()
            else:
                data[k.strip()] = v.strip('"')
                current = None
    return data


def test_rc07_frontmatter():
    fm = parse_frontmatter(read(SKILL_DIR / "SKILL.md"))
    assert fm["name"] == SKILL == "visual-audit"
    assert len(fm["description"]) >= 40
    for phrase in ("audit UI", "inconsistent", "style drift", "which screens are off-style", "screenshot compare"):
        assert phrase in fm["description"], phrase
    assert fm["argument-hint"] and fm["license"] == "MIT"
    assert fm["metadata"] == {"author": "ui-ux-pro-max", "version": "1.0.0"}


def test_rc08_script_paths_paragraph_and_body_length():
    text = read(SKILL_DIR / "SKILL.md")
    assert "## Script Paths" in text
    assert "relative to the directory that contains this SKILL.md" in text
    body = text.split("---\n", 2)[2]
    assert len(body.splitlines()) <= 250
    for section in ("## When to Use", "## Workflow", "## Commands", "## Hand-offs", "## Limitations", "PASS / FAIL / BLOCKED / NOT RUN"):
        assert section in text, section


def test_rc09_references_exist_and_are_mentioned():
    text = "\n".join(read(p) for p in md_files())
    expected = {"audit-workflow.md", "finding-format.md", "drift-rules.md", "severity.md", "ux-audit-checklist.md",
                "screenshot-qa.md", "visual-qa-without-runtime.md"}
    present = {p.name for p in REFERENCES.glob("*.md")}
    assert present == expected
    skill_md = read(SKILL_DIR / "SKILL.md")
    for name in expected:
        assert ("references/%s" % name) in skill_md, name
    for m in re.finditer(r"references/([a-z0-9-]+\.md)", text):
        assert (REFERENCES / m.group(1)).is_file(), m.group(1)


def test_rc10_scripts_are_stdlib_only_with_guarded_pil():
    stdlib = getattr(sys, "stdlib_module_names", None)
    if stdlib is None:
        pytest.skip("sys.stdlib_module_names needs Python 3.10+")
    for script in sorted(SCRIPTS.glob("*.py")):
        tree = ast.parse(read(script))
        parents = {}
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                parents[child] = node
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
                for name in names:
                    top = name.split(".")[0]
                    if top == "PIL":
                        p = parents.get(node)
                        while p is not None and not isinstance(p, ast.Try):
                            p = parents.get(p)
                        assert p is not None, "%s: PIL import must sit inside try/except ImportError" % script.name
                        assert any(isinstance(h.type, ast.Name) and h.type.id == "ImportError" for h in p.handlers)
                    else:
                        assert top in stdlib, "%s imports non-stdlib %s" % (script.name, name)
    audit_src = read(SCRIPTS / "audit.py")
    assert "PIL" not in audit_src.replace("PILL", "")


@pytest.mark.parametrize("script,subcommands", [
    ("audit.py", ["scan", "compare", "rules"]),
    ("visual_qa.py", ["diff", "checklist", "manifest", "devices"]),
])
def test_rc11_json_flag_documented(script, subcommands):
    for sub in subcommands:
        r = subprocess.run([sys.executable, str(SCRIPTS / script), sub, "--help"], capture_output=True, text=True, timeout=60)
        assert r.returncode == 0 and "--json" in r.stdout, (script, sub)


def test_rc12_synced_copy_matches_if_present():
    repo = SKILLS_ROOT.parent.parent
    mirror = repo / "cli" / "assets" / "skills" / SKILL
    if not mirror.is_dir():
        pytest.skip("not synced yet - run npm --prefix cli run sync:assets")
    ours = {p.relative_to(SKILL_DIR) for p in text_files()}
    theirs = {p.relative_to(mirror) for p in mirror.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    assert ours == theirs
    for rel in ours:
        assert read(SKILL_DIR / rel).replace("\r\n", "\n") == read(mirror / rel).replace("\r\n", "\n"), rel


def test_rc13_fixtures_clean_small_and_labelled():
    for p in FIXTURES.rglob("*"):
        if p.is_file():
            assert p.stat().st_size < 200 * 1024, p
            assert p.suffix != ".png", p
            txt = read(p)
            assert not HOME_ROOTED.search(txt) and not PROJECT_ROOTED.search(txt) and not PLUGIN_ROOT.search(txt), p
    readme = read(FIXTURES / "drift-project" / "README.md")
    assert "STATIC AUDIT FIXTURE" in readme and "not a runnable app" in readme
    assert (FIXTURES / "expected-findings.md").is_file()


def test_rc14_test_file_names_are_unique_across_skills():
    names = {}
    for p in SKILLS_ROOT.rglob("scripts/tests/test_*.py"):
        names.setdefault(p.name, []).append(str(p))
    dupes = {k: v for k, v in names.items() if len(v) > 1}
    assert dupes == {}, dupes
    assert not (SCRIPTS / "tests" / "conftest.py").exists()


def test_rc15_layout():
    assert (SKILL_DIR / "SKILL.md").is_file() and (SCRIPTS / "audit.py").is_file() and (SCRIPTS / "visual_qa.py").is_file()
    assert (FIXTURES / "drift-project" / "tokens.json").is_file() and (FIXTURES / "qa" / "profile-with-qa.json").is_file()
    assert sorted(p.name for p in SKILL_DIR.iterdir() if not p.name.startswith(".")) == ["SKILL.md", "references", "scripts"]
