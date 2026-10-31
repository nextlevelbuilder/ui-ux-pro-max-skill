"""Packaging contracts for the reference-analysis skill (mirrors the CI path and
bundled-skill greps in check-asset-sync.yml, scoped to this skill's directory).

The forbidden path patterns are assembled from fragments so that this file itself
never contains a literal that the repository-wide grep would flag.
"""

import ast
import re
import sys
from pathlib import Path

import pytest

REPO = next(p for p in Path(__file__).resolve().parents if (p / "scripts" / "generate-catalog-summary.py").is_file())
SKILL_DIR = Path(__file__).resolve().parents[2]
SKILL = SKILL_DIR.name  # "reference-analysis"
TREES = [REPO / ".claude" / "skills" / SKILL, REPO / "cli" / "assets" / "skills" / SKILL]
INVOCATION = re.compile(r'(?<![\w/.-])(?:python3?|node|bash)\s+"?([^\s"`\']+\.(?:py|cjs|js|mjs|sh))')
_DOT_SKILLS = r"\." + "claude/skills/"
HOME_ROOTED = re.compile(r"~/" + _DOT_SKILLS + r"[A-Za-z0-9_-]+\b")
_VAR = "CLAUDE_PLUGIN" + "_ROOT"
PROJECT_ROOTED = re.compile(r"(?<![/\w])" + _DOT_SKILLS + r"[A-Za-z0-9_-]+\b|(?<!~)(?<!\$" + _VAR + r")(?<!\$\{" + _VAR
                            + r"\})/" + _DOT_SKILLS + r"[A-Za-z0-9_-]+\b")
PLUGIN_ROOT = re.compile(_VAR)
CK_NAMESPACE = re.compile(r"(?<![\w/])/ckm?:")
FORBIDDEN_NAMES = re.compile(r"\b(frontend-design|ai-artist|ai-multimodal|chrome-devtools|assets-organizing|project-management)\b", re.I)
SKILL_REF = re.compile(r"`([a-z0-9-]+)`(?:\*\*)?(?=(?:(?:,\s+|\s+and\s+|,\s+and\s+|\s+or\s+|,\s+or\s+|/|\s+→\s+|\s+->\s+)"
                       r"(?:\*\*)?`[a-z0-9-]+`(?:\*\*)?)*\s+(?:sub-)?[Ss]kills?\b)")
SUBCOMMANDS_WITH_JSON = ["validate", "merge", "extract-colors", "to-profile"]


def existing_trees():
    return [t for t in TREES if t.is_dir()]


def text_files(root):
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix in {".md", ".py", ".json", ".txt", ".csv", ".yml", ".yaml"}:
            yield p


def markdown_files(root):
    return sorted(root.rglob("*.md"))


def resolve(skill_dir, path):
    """Return (target, None) for a skill-relative path, or (None, reason)."""
    if path.startswith("scripts/"):
        return skill_dir / path, None
    if path.startswith("../"):
        parts = path.split("/")
        if len(parts) > 3 and parts[2] == "scripts" and (skill_dir.parent / parts[1]).is_dir():
            return skill_dir.parent / parts[1] / "/".join(parts[2:]), None
        return None, "a sibling invocation must be ../<skill>/scripts/<file> and the sibling must ship"
    return None, "not skill-relative (expected scripts/<file> or ../<skill>/scripts/<file>)"


def test_rc01_every_markdown_invocation_resolves():
    problems, pending_siblings, seen = [], [], 0
    for tree in existing_trees():
        for md in markdown_files(tree):
            for lineno, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
                for m in INVOCATION.finditer(line):
                    seen += 1
                    path = m.group(1)
                    target, reason = resolve(tree, path)
                    if reason is None and not target.is_file():
                        if path.startswith("../"):
                            pending_siblings.append("%s:%d: %s" % (md.relative_to(REPO), lineno, path))
                            continue
                        reason = "no such file: %s" % target
                    if reason:
                        problems.append("%s:%d: %s -- %s" % (md.relative_to(REPO), lineno, path, reason))
    assert seen >= 1, "the extractor found no documented invocations"
    assert problems == [], "\n" + "\n".join(problems)
    if pending_siblings:
        pytest.xfail("sibling scripts not shipped yet (owned by another skill):\n" + "\n".join(pending_siblings))


def test_rc02_no_home_rooted_paths():
    hits = [str(p.relative_to(REPO)) for t in existing_trees() for p in text_files(t)
            if HOME_ROOTED.search(p.read_text(encoding="utf-8", errors="replace"))]
    assert hits == []


def test_rc03_no_project_or_variable_rooted_paths():
    hits = []
    for t in existing_trees():
        for p in text_files(t):
            text = p.read_text(encoding="utf-8", errors="replace")
            if PROJECT_ROOTED.search(text) or PLUGIN_ROOT.search(text):
                hits.append(str(p.relative_to(REPO)))
    assert hits == []


def test_rc04_no_claudekit_namespaces():
    hits = [str(p.relative_to(REPO)) for t in existing_trees() for p in markdown_files(t)
            if CK_NAMESPACE.search(p.read_text(encoding="utf-8"))]
    assert hits == []


def test_rc05_skill_references_are_bundled():
    bundled = {d.name for d in (REPO / ".claude" / "skills").iterdir() if d.is_dir()}
    offending = []
    for t in existing_trees():
        for p in markdown_files(t):
            text = re.sub(r"\s+", " ", p.read_text(encoding="utf-8"))
            for m in SKILL_REF.finditer(text):
                if m.group(1) not in bundled:
                    offending.append("%s: `%s`" % (p.relative_to(REPO), m.group(1)))
    assert offending == []


def test_rc06_no_claudekit_only_names():
    hits = []
    for t in existing_trees():
        for p in markdown_files(t):
            m = FORBIDDEN_NAMES.search(p.read_text(encoding="utf-8"))
            if m:
                hits.append("%s: %s" % (p.relative_to(REPO), m.group(0)))
    assert hits == []


def parse_frontmatter(text):
    assert text.startswith("---\n"), "SKILL.md must start with a frontmatter block"
    block = text.split("\n---", 1)[0].split("\n", 1)[1]
    data, current = {}, None
    for line in block.splitlines():
        if not line.strip():
            continue
        if line.startswith("  ") and current:
            k, v = line.strip().split(":", 1)
            data[current][k.strip()] = v.strip().strip('"')
        else:
            k, v = line.split(":", 1)
            if v.strip() == "":
                data[k.strip()] = {}
                current = k.strip()
            else:
                data[k.strip()] = v.strip().strip('"')
                current = None
    return data


def test_rc07_skill_frontmatter():
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    assert fm["name"] == SKILL
    assert len(fm["description"]) >= 40
    for phrase in ("screenshot", "reference", "visual-direction"):
        assert phrase in fm["description"].lower()
    assert fm["argument-hint"]
    assert fm["license"] == "MIT"
    assert fm["metadata"] == {"author": "ui-ux-pro-max", "version": "1.0.0"}


def test_rc07b_skill_body_length_and_sections():
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    body = text.split("\n---", 1)[1]
    assert len(body.strip().splitlines()) <= 220
    for needle in ("never claim", "viewed_by", "observed", "not-derivable", "../visual-direction/scripts/vd.py profile",
                   "never upload", "| `validate", "| `merge", "| `extract-colors", "| `to-profile", "| `summary"):
        assert needle in text.lower(), needle
    for label in ("OBSERVED", "HIGH", "ASSUMPTION", "NOT-DERIVABLE"):
        assert label in text, label


def test_rc08_script_paths_paragraph():
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "## Script Paths" in text
    assert "relative to the directory that contains this SKILL.md" in text


def test_rc09_references_exist_and_are_mentioned():
    skill_md = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    refs = sorted((SKILL_DIR / "references").glob("*.md"))
    assert {r.name for r in refs} >= {"analysis-workflow.md", "extraction-schema.md",
                                      "multi-reference-reconciliation.md", "confidence-levels.md"}
    corpus = skill_md + "".join(r.read_text(encoding="utf-8") for r in refs)
    for r in refs:
        assert r.name in skill_md, "%s is not mentioned in SKILL.md" % r.name
    for mentioned in re.findall(r"references/([a-z0-9-]+\.md)", corpus):
        assert (SKILL_DIR / "references" / mentioned).is_file(), mentioned
    for mentioned in re.findall(r"templates/([a-z0-9.-]+)", corpus):
        assert (SKILL_DIR / "templates" / mentioned).is_file(), mentioned


def test_rc09b_human_description_template_is_verbatim_in_workflow_and_template():
    workflow = (SKILL_DIR / "references" / "analysis-workflow.md").read_text(encoding="utf-8")
    template = (SKILL_DIR / "templates" / "human-description-template.md").read_text(encoding="utf-8")
    block = re.search(r"```\n(Describe <label>.*?)```", template, re.S).group(1)
    assert block in workflow
    assert block.count("\n") == 9  # intro line + 8 numbered paragraphs


def test_rc10_scripts_are_stdlib_only_with_lazy_pil():
    stdlib = getattr(sys, "stdlib_module_names", None) or {
        "argparse", "copy", "json", "math", "os", "re", "sys", "subprocess", "pathlib", "io", "typing"}
    for script in sorted((SKILL_DIR / "scripts").glob("*.py")):
        tree = ast.parse(script.read_text(encoding="utf-8"))
        parents = {}
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                parents[child] = node
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [(node.module or "").split(".")[0]]
            for name in names:
                if name == "PIL":
                    assert isinstance(parents.get(node), ast.Try), "PIL must be imported inside try/except"
                    handlers = parents[node].handlers
                    assert any(getattr(h.type, "id", None) == "ImportError" for h in handlers)
                else:
                    assert name in stdlib, "%s imports non-stdlib module %s" % (script.name, name)


def test_rc10b_python38_syntax():
    for script in sorted((SKILL_DIR / "scripts").glob("*.py")):
        src = script.read_text(encoding="utf-8")
        assert not re.search(r"^\s*match\s+\w+.*:\s*$", src, re.M), "match statement is 3.10+"
        assert ".removeprefix(" not in src and ".removesuffix(" not in src
        ast.parse(src, feature_version=(3, 8))


def test_rc11_json_flag_documented_in_help():
    import subprocess
    script = SKILL_DIR / "scripts" / "reference_analysis.py"
    for sub in SUBCOMMANDS_WITH_JSON:
        r = subprocess.run([sys.executable, str(script), sub, "--help"], capture_output=True, text=True, timeout=60)
        assert r.returncode == 0 and "--json" in r.stdout, sub


def test_rc12_both_trees_identical_when_synced():
    mirror = TREES[1]
    if not mirror.is_dir():
        pytest.skip("not synced yet - run npm --prefix cli run sync:assets")
    src = TREES[0]
    for sub in ("scripts", "references", "templates"):
        src_files = {p.relative_to(src) for p in (src / sub).rglob("*") if p.is_file()}
        dst_files = {p.relative_to(mirror) for p in (mirror / sub).rglob("*") if p.is_file()}
        assert src_files == dst_files, sub
        for rel in src_files:
            a = (src / rel).read_bytes().replace(b"\r\n", b"\n")
            b = (mirror / rel).read_bytes().replace(b"\r\n", b"\n")
            assert a == b, str(rel)


def test_rc13_fixtures_carry_no_forbidden_content():
    for p in (SKILL_DIR / "scripts" / "tests" / "fixtures").rglob("*"):
        if p.is_file():
            text = p.read_text(encoding="utf-8", errors="replace")
            assert not HOME_ROOTED.search(text) and not PROJECT_ROOTED.search(text), p.name


def test_rc14_fixtures_small_and_no_images():
    for p in (SKILL_DIR / "scripts" / "tests" / "fixtures").rglob("*"):
        if p.is_file():
            assert p.stat().st_size < 200 * 1024, p.name
            assert p.suffix.lower() not in {".png", ".jpg", ".jpeg", ".gif", ".webp"}, p.name


def test_rc15_test_module_names_are_unique_across_skills():
    names = {}
    for test in (REPO / ".claude" / "skills").rglob("scripts/tests/test_*.py"):
        names.setdefault(test.name, []).append(str(test.relative_to(REPO)))
    dups = {k: v for k, v in names.items() if len(v) > 1}
    assert dups == {}, dups
    assert not (SKILL_DIR / "scripts" / "tests" / "conftest.py").exists()


def test_rc16_fixtures_are_marked_synthetic_and_valid():
    import json
    for p in sorted((SKILL_DIR / "scripts" / "tests" / "fixtures").glob("*.json")):
        doc = json.loads(p.read_text(encoding="utf-8"))
        assert "synthetic" in doc.get("project", "").lower(), p.name
        assert doc["schema"] == "vdp-reference-analysis/1"
