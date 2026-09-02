"""Every script invocation in the shipped skill markdown resolves from the skill directory.

Regression test for #474. The sub-skills ship in two copies (.claude/skills/<skill>/
for the plugin, cli/assets/skills/<skill>/ for CLI installs) and land in layouts where
neither the project root nor ~/.claude/skills/ is a valid anchor: the plugin cache, a
project's .claude/skills/, ~/.claude/skills/ (--global), or a manual copy. The one anchor
that exists in all of them is the skill's own directory, so documented commands use
`scripts/<file>` for the skill's own scripts and `../<skill>/scripts/<file>` for a
sibling sub-skill (the sub-skills are always installed side by side).

This test extracts every `python|python3|node|bash <path>` invocation from every
markdown file under both trees and asserts that the path is skill-relative and names a
file that ships. The core skill's `${CLAUDE_PLUGIN_ROOT}/.claude/skills/...` form is
resolved against the repository root, which is what that variable denotes under a
plugin install - and accepted only in that file, because the sub-skills also ship
through the CLI, where the variable does not exist. The grep-based path contract in check-asset-sync.yml is the negative
side (no home-, project- or variable-rooted paths anywhere, code included); this is
the positive side (every documented invocation points at a real file).
"""

import re
import unittest
from pathlib import Path

REPO = next(
    parent for parent in Path(__file__).resolve().parents
    if (parent / "scripts" / "generate-catalog-summary.py").is_file()
)
SKILL_TREES = ("cli/assets/skills", ".claude/skills")
# The only file that may use the plugin-root form: hand-authored for the plugin install
# and not shipped by the CLI (sync-assets.mjs mirrors data/ and scripts/, never SKILL.md).
# (Built from segments: the path contract in check-asset-sync.yml scans this file too.)
PLUGIN_ONLY_FILE = Path(".claude") / "skills" / "ui-ux-pro-max" / "SKILL.md"
INVOCATION = re.compile(r'(?<![\w/.-])(?:python3?|node|bash)\s+"?([^\s"`\']+\.(?:py|cjs|js|mjs|sh))')
PLUGIN_ROOT = "${CLAUDE_PLUGIN_ROOT}/"


def shipped_invocations():
    for tree in SKILL_TREES:
        for skill_dir in sorted((REPO / tree).iterdir()):
            if not skill_dir.is_dir():
                continue
            for md in sorted(skill_dir.rglob("*.md")):
                for lineno, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
                    for match in INVOCATION.finditer(line):
                        yield skill_dir, md, lineno, match.group(1)


def resolve(skill_dir, md, path):
    """Return (target, None) for a skill-relative path, or (None, reason)."""
    if path.startswith(PLUGIN_ROOT):
        if md.relative_to(REPO) != PLUGIN_ONLY_FILE:
            return None, "the ${CLAUDE_PLUGIN_ROOT} form is only valid in the plugin-only core SKILL.md"
        return REPO / path[len(PLUGIN_ROOT):], None
    if path.startswith("scripts/"):
        return skill_dir / path, None
    if path.startswith("../"):
        parts = path.split("/")
        if len(parts) > 3 and parts[2] == "scripts" and (skill_dir.parent / parts[1]).is_dir():
            return skill_dir.parent / parts[1] / "/".join(parts[2:]), None
        return None, "a sibling invocation must be ../<skill>/scripts/<file> and the sibling must ship"
    return None, "not skill-relative (expected scripts/<file> or ../<skill>/scripts/<file>)"


class SkillScriptPathsTest(unittest.TestCase):
    def test_every_shipped_markdown_invocation_resolves_from_the_skill_directory(self):
        problems, seen = [], 0
        for skill_dir, md, lineno, path in shipped_invocations():
            seen += 1
            target, reason = resolve(skill_dir, md, path)
            if reason is None and not target.is_file():
                reason = f"no such file: {target}"
            if reason:
                problems.append(f"{md.relative_to(REPO)}:{lineno}: {path} -- {reason}")
        # Guard against a silently broken extractor: the two trees carry well over
        # a hundred documented invocations between them.
        self.assertGreater(seen, 100, f"extractor found only {seen} invocations")
        self.assertEqual(problems, [], "\n" + "\n".join(problems))


if __name__ == "__main__":
    unittest.main()
