# Contributing to UI/UX Pro Max

Thank you for taking the time to contribute! 🎉  
This guide will help you get started quickly.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Ways to Contribute](#ways-to-contribute)
- [Development Workflow](#development-workflow)
- [Commit Message Format](#commit-message-format)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Reporting Bugs](#reporting-bugs)
- [Code of Conduct](#code-of-conduct)

---

## Getting Started

### Prerequisites

- **Node.js** 18+ and **npm**
- **Python 3.x**
- **Bun** (for building the CLI)
- **Git**

### Fork & Clone

```bash
# 1. Fork the repo on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/ui-ux-pro-max-skill.git
cd ui-ux-pro-max-skill

# 2. Add the upstream remote
git remote add upstream https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git

# 3. Install CLI dependencies
cd cli && npm install && cd ..
```

---

## Project Structure

```
ui-ux-pro-max-skill/
├── src/ui-ux-pro-max/          # Source of truth — edit here, not in .claude/
│   ├── data/                   # CSV databases (styles, colors, typography, rules)
│   ├── scripts/                # Python search engine & design system generator
│   └── templates/              # Platform-specific skill templates
├── cli/                        # npm CLI installer (ui-ux-pro-max-cli)
├── .claude/                    # Local dev/test files for Claude Code
├── .factory/                   # Local dev/test files for Droid (Factory)
├── docs/                       # Documentation
└── preview/                    # Preview screenshots and demos
```

> **Important:** Always make data/script changes in `src/ui-ux-pro-max/`, then sync to the CLI (see below). Do not edit `.claude/` or `.factory/` directly for permanent changes.

---

## Ways to Contribute

### 🐛 Bug Fixes
Check the [Issues tab](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/issues) for bugs labeled `bug`. Comment on the issue before starting so we don't duplicate work.

### ✨ New UI Styles
Add a new entry to `src/ui-ux-pro-max/data/styles.csv`. Each row needs:
- Style name
- Description
- Best for (use cases)
- Key CSS properties/effects

### 🎨 New Color Palettes
Add entries to `src/ui-ux-pro-max/data/colors.csv`. Match the existing format (primary, secondary, CTA, background, text, notes).

### 🏭 New Industry Reasoning Rules
Add rules to `src/ui-ux-pro-max/data/rules.csv`. Each rule needs a product type, recommended pattern, style priority, color mood, typography mood, key effects, and anti-patterns.

### 🌍 Translations
Translate `README.md` into your language and save it as `README.[lang].md` (e.g., `README.zh.md`, `README.es.md`).

### 📝 Documentation Improvements
Fix typos, clarify confusing sections, or add missing examples in `README.md` or `docs/`.

### 🔧 CLI Improvements
Improvements to the `cli/` installer. Run `cd cli && bun run build` to test locally.

---

## Development Workflow

```bash
# 1. Create a feature branch from main
git checkout -b feat/your-feature-name

# 2. Make your changes in src/ui-ux-pro-max/

# 3. Sync changes to CLI assets and the Claude Code skill
cd cli && npm run sync:assets && cd ..

# 4. Build and test the CLI locally
cd cli && bun run build
mkdir /tmp/test-project && cd /tmp/test-project
node /path/to/cli/dist/index.js init --ai claude --offline

# 5. Test the Python search script
cd /path/to/repo
python3 src/ui-ux-pro-max/scripts/search.py "your query" --design-system

# 6. Push your branch
git push -u origin feat/your-feature-name
```

---

## Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <short description>

Types:
  feat     → New feature or content (new style, rule, palette)
  fix      → Bug fix
  docs     → Documentation only
  refactor → Code change without new feature or fix
  chore    → Build process, dependency updates
  test     → Adding or fixing tests
```

**Examples:**
```
feat: add Skeuomorphism 2.0 style to general styles
fix: correct color palette for fintech industry rule
docs: translate README to Spanish
chore: update ui-ux-pro-max-cli to v2.6.0
```

---

## Pull Request Guidelines

1. **One PR per change** — keep PRs focused and small
2. **Reference related issues** — use `Closes #123` in the PR description
3. **Fill out the PR template** — describe what you changed and why
4. **Never push directly to `main`** — always use a feature branch
5. **Wait for review** — a maintainer will review within a few days

---

## Reporting Bugs

Please [open an issue](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/issues/new) and include:

- Your OS and terminal
- The AI assistant you're using (Claude Code, Cursor, etc.)
- The exact command or prompt that triggered the bug
- Expected vs. actual behavior
- Any error messages or screenshots

---

## Code of Conduct

Be kind, constructive, and respectful. We're all here to build something useful together.  
Harassment, spam, or low-effort contributions will be closed without review.

---

## Questions?

Open a [Discussion](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/discussions) or check the [README](README.md) first.

Happy contributing! 🚀
