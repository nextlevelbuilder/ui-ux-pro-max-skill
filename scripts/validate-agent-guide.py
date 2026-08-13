#!/usr/bin/env python3
"""Validate agent guide claims and run its locked semantic examples."""

import csv
import json
import re
import shlex
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "src/ui-ux-pro-max/data"
TEMPLATES = ROOT / "src/ui-ux-pro-max/templates"
PLATFORMS = TEMPLATES / "platforms"
GUIDE = TEMPLATES / "base/skill-content.md"
CLAUDE_GUIDE = ROOT / ".claude/skills/ui-ux-pro-max/SKILL.md"
README = ROOT / "README.md"
README_ZH = ROOT / "README.zh.md"
DOMAINS = {
    "product", "style", "typography", "color", "landing", "chart", "ux",
    "gsap", "react", "web", "icons", "google-fonts",
}
FLAGS = {
    "--domain", "-d", "--stack", "-s", "--max-results", "-n", "--json",
    "--full", "--design-system", "-ds", "--project-name", "-p", "--format",
    "-f", "--persist", "--page", "--output-dir", "-o", "--force",
    "--variance", "--motion", "--density",
}
PLATFORM_COUNT = 20
GUIDE_REQUIREMENTS = (
    "## Query Contract", "one dominant intent", "Retry once",
    "Do not persist unverified output", "explicit accessibility outcome terms",
)
SEARCH_COMMAND = re.compile(r"search\.py|\{\{SCRIPT_PATH\}\}")
QUOTED_QUERY = re.compile(r'search\.py"?\s+"[^"]+"')
DOMAIN_FLAG = re.compile(r"--domain\s+(\S+)")
STACK_FLAG = re.compile(r"--stack\s+(\S+)")


@lru_cache(maxsize=None)
def row_count(name):
    with (DATA / name).open(encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


@lru_cache(maxsize=1)
def style_counts():
    with (DATA / "styles.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {
        "searchable": sum(row.get("Status") != "deprecated" for row in rows),
        "active": sum(row.get("Status") == "active" for row in rows),
    }


@lru_cache(maxsize=1)
def stack_names():
    return frozenset(path.stem for path in (DATA / "stacks").glob("*.csv"))


def expected_description():
    styles = style_counts()
    return (
        "UI/UX design intelligence for web, mobile, and desktop. This skill should be used when designing, "
        "building, reviewing, or fixing interfaces, including pages, components, design "
        "systems, accessibility, interaction, responsive layout, typography, color, "
        "charts, and stack-specific UI implementation. Searchable local data: "
        f"{styles['searchable']} searchable styles ({styles['active']} active), "
        f"{row_count('colors.csv')} product palettes "
        f"and reasoning profiles, {row_count('typography.csv')} font pairings, "
        f"{row_count('ux-guidelines.csv')} UX guidelines, {row_count('icons.csv')} icons, "
        f"{row_count('motion.csv')} GSAP presets, {row_count('charts.csv')} chart types, "
        f"and {len(stack_names())} stacks."
    )


def run_json(*args):
    command = [
        sys.executable, str(ROOT / "src/ui-ux-pro-max/scripts/search.py"),
        *args, "--json",
    ]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def validate_commands(label, text):
    errors = []
    commands = []
    for line in text.splitlines():
        command = line.strip()
        if command.startswith(("python ", "python3 ")) and (
                SEARCH_COMMAND.search(command)):
            commands.append(command.replace("{{SCRIPT_PATH}}", "search.py"))
    if not commands:
        errors.append(f"{label}: no documented search commands found")
    for command in commands:
        if not QUOTED_QUERY.search(command):
            errors.append(f"{label}: query must immediately follow search.py: {command}")
        try:
            tokens = shlex.split(command.replace("[", "").replace("]", ""))
        except ValueError as exc:
            errors.append(f"{label}: invalid shell command ({exc}): {command}")
            continue
        unknown_flags = sorted({token for token in tokens if token.startswith("-") and token not in FLAGS})
        if unknown_flags:
            errors.append(f"{label}: unknown flags {unknown_flags}: {command}")
        domain = DOMAIN_FLAG.search(command)
        if domain and domain.group(1) not in DOMAINS | {"<domain>"}:
            errors.append(f"{label}: unknown domain {domain.group(1)!r}")
        stack = STACK_FLAG.search(command)
        if stack and stack.group(1) not in stack_names() | {"<stack>"}:
            errors.append(f"{label}: unknown stack {stack.group(1)!r}")
        if "--persist" in command and "--output-dir" not in command:
            errors.append(f"{label}: persisted command lacks --output-dir")
    return errors


def validate():
    errors = []
    product_counts = {
        "products": row_count("products.csv"),
        "palettes": row_count("colors.csv"),
        "reasoning profiles": row_count("ui-reasoning.csv"),
    }
    if len(set(product_counts.values())) != 1:
        errors.append(f"product/palette/reasoning counts differ: {product_counts}")
    description = expected_description()
    claude_text = CLAUDE_GUIDE.read_text(encoding="utf-8")
    if description not in claude_text:
        errors.append("claude: frontmatter description/counts differ from canonical metadata")
    styles = style_counts()
    guide_claims = (
        f"{styles['searchable']} searchable styles ({styles['active']} active)",
        f"{row_count('typography.csv')} font pairings",
        f"{row_count('ux-guidelines.csv')} UX guidelines",
        f"{row_count('icons.csv')} curated icons",
        f"{row_count('motion.csv')} GSAP presets",
        f"{row_count('charts.csv')} chart types",
        f"{len(stack_names())} technology stacks",
    )
    for claim in guide_claims:
        if claim not in claude_text:
            errors.append(f"claude: missing live count claim {claim!r}")
    reasoning_count = row_count("ui-reasoning.csv")
    public_claims = (
        (README, (f"{reasoning_count} Reasoning Rules",
                  f"{row_count('ux-guidelines.csv')} UX Guidelines")),
        (README_ZH, (f"{reasoning_count} 条推理规则",
                     f"{row_count('ux-guidelines.csv')} 条 UX 指南")),
    )
    for path, claims in public_claims:
        text = path.read_text(encoding="utf-8")
        for claim in claims:
            if claim not in text:
                errors.append(f"{path.name}: missing live count claim {claim!r}")
    configs = sorted(PLATFORMS.glob("*.json"))
    if len(configs) != PLATFORM_COUNT:
        errors.append(f"expected {PLATFORM_COUNT} platform configs, got {len(configs)}")
    for path in configs:
        config = json.loads(path.read_text(encoding="utf-8"))
        if config.get("description") != description:
            errors.append(f"{path.name}: stale description")
        frontmatter = config.get("frontmatter") or {}
        if frontmatter.get("description") and frontmatter["description"] != description:
            errors.append(f"{path.name}: stale frontmatter description")
    for label, path in (("canonical", GUIDE), ("claude", CLAUDE_GUIDE)):
        text = path.read_text(encoding="utf-8")
        for phrase in GUIDE_REQUIREMENTS:
            if phrase not in text:
                errors.append(f"{label}: missing {phrase!r}")
        errors.extend(validate_commands(label, text))
    design = run_json("beauty spa wellness service", "--design-system")
    if design["design_system"]["category"] != "Beauty/Spa/Wellness Service":
        errors.append("design-system example resolved wrong product category")
    ux = run_json("keyboard focus modal", "--domain", "ux")
    if ux.get("domain") != "ux" or not ux.get("results"):
        errors.append("focused UX example did not return an explicit UX match")
    stack = run_json("virtualized list", "--stack", "react-native")
    if stack.get("stack") != "react-native" or not stack.get("results"):
        errors.append("React Native stack example did not return a stack match")
    return errors


if __name__ == "__main__":
    problems = validate()
    if problems:
        print("Agent guide validation failed:\n- " + "\n- ".join(problems), file=sys.stderr)
        raise SystemExit(1)
    print(
        f"Agent guide validation passed: {PLATFORM_COUNT} platforms "
        "and 3 locked examples checked."
    )
