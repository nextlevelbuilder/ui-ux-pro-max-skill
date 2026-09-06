# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Legal UI/UX Pro Max is an AI-powered design intelligence toolkit **specialized for the law industry** — law firms, attorneys, and legal-tech products. It provides searchable databases of legal product types, color palettes, font pairings, landing-page patterns, chart types, and UX guidelines, all tuned for trust, authority, accessibility, and conversion (free consultation / case evaluation). It works as a skill/workflow for AI coding assistants (Claude Code, Windsurf, Cursor, etc.).

The dataset is law-only: 82 legal product types (practice areas such as personal injury, criminal defense, family, immigration, estate planning, corporate, IP, tax, and litigation firms; firm types from solo to BigLaw; plus legal-tech/SaaS like case management, e-discovery, CLM, and client intake), 82 matching color palettes, 42 professional font pairings (including multilingual pairings for immigration/legal-aid), 22 legal landing-page patterns, 25 chart types framed for legal analytics, and 99 UX guidelines — across 16 technology stacks. The internal skill id and all paths remain `ui-ux-pro-max`.

## Search Command

```bash
python3 src/ui-ux-pro-max/scripts/search.py "<query>" --domain <domain> [-n <max_results>]
```

**Domain search:**
- `product` - Legal product type recommendations (personal injury firm, criminal defense, family law, immigration, estate planning, corporate/IP/tax law, legal-tech SaaS, attorney directory)
- `style` - UI styles (trust & authority, minimalism, editorial, glassmorphism, swiss modernism) + AI prompts and CSS keywords
- `typography` - Legal-appropriate font pairings with Google Fonts imports
- `color` - Legal color palettes by product type (navy/gold, charcoal/burgundy, forest/camel, emerald/gold)
- `landing` - Legal landing patterns (free case evaluation, practice areas, attorney bio, client intake) and CTA strategies
- `chart` - Chart types for legal analytics (billable hours, caseload, matter status, settlements) and library recommendations
- `ux` - Best practices and anti-patterns for legal sites & apps

**Stack search:**
```bash
python3 src/ui-ux-pro-max/scripts/search.py "<query>" --stack <stack>
```
Available stacks: `html-tailwind` (default), `react`, `nextjs`, `astro`, `vue`, `nuxtjs`, `nuxt-ui`, `svelte`, `swiftui`, `react-native`, `flutter`, `shadcn`, `jetpack-compose`

## Architecture

```
src/ui-ux-pro-max/                # Source of Truth
├── data/                         # Canonical CSV databases
│   ├── products.csv, styles.csv, colors.csv, typography.csv, ...
│   └── stacks/                   # Stack-specific guidelines
├── scripts/
│   ├── search.py                 # CLI entry point
│   ├── core.py                   # BM25 + regex hybrid search engine
│   └── design_system.py          # Design system generation
└── templates/
    ├── base/                     # Base templates (skill-content.md, quick-reference.md)
    └── platforms/                # Platform configs (claude.json, cursor.json, ...)

cli/                              # CLI installer (uipro-cli on npm)
├── src/
│   ├── commands/init.ts          # Install command with template generation
│   └── utils/template.ts         # Template rendering engine
└── assets/                       # Bundled assets (~564KB)
    ├── data/                     # Copy of src/ui-ux-pro-max/data/
    ├── scripts/                  # Copy of src/ui-ux-pro-max/scripts/
    └── templates/                # Copy of src/ui-ux-pro-max/templates/

.claude/skills/ui-ux-pro-max/     # Claude Code skill (symlinks to src/)
.factory/skills/ui-ux-pro-max/   # Droid (Factory) skill (symlinks to src/)
.shared/ui-ux-pro-max/            # Symlink to src/ui-ux-pro-max/
.claude-plugin/                   # Claude Marketplace publishing
```

The search engine uses BM25 ranking combined with regex matching. Domain auto-detection is available when `--domain` is omitted.

## Sync Rules

**Source of Truth:** `src/ui-ux-pro-max/`

When modifying files:

1. **Data & Scripts** - Edit in `src/ui-ux-pro-max/`:
   - `data/*.csv` and `data/stacks/*.csv`
   - `scripts/*.py`
   - Changes automatically available via symlinks in `.claude/`, `.factory/`, `.shared/`

2. **Templates** - Edit in `src/ui-ux-pro-max/templates/`:
   - `base/skill-content.md` - Common SKILL.md content
   - `base/quick-reference.md` - Quick reference section (Claude only)
   - `platforms/*.json` - Platform-specific configs

3. **CLI Assets** - Run sync before publishing:
   ```bash
   cp -r src/ui-ux-pro-max/data/* cli/assets/data/
   cp -r src/ui-ux-pro-max/scripts/* cli/assets/scripts/
   cp -r src/ui-ux-pro-max/templates/* cli/assets/templates/
   ```

4. **Reference Folders** - No manual sync needed. The CLI generates these from templates during `uipro init`.

## Prerequisites

Python 3.x (no external dependencies required)

## Git Workflow

Never push directly to `main`. Always:

1. Create a new branch: `git checkout -b feat/...` or `fix/...`
2. Commit changes
3. Push branch: `git push -u origin <branch>`
4. Create PR: `gh pr create`
