# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Antigravity Kit is an AI-powered design intelligence toolkit providing searchable databases of UI styles, color palettes, font pairings, chart types, and UX guidelines. It works as a skill/workflow for AI coding assistants (Claude Code, Windsurf, Cursor, etc.).

## Search Command

```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "<query>" --domain <domain> [-n <max_results>]
```

**Domain search:**
- `product` - Product type recommendations (SaaS, e-commerce, portfolio)
- `style` - UI styles (glassmorphism, minimalism, brutalism)
- `typography` - Font pairings with Google Fonts imports
- `color` - Color palettes by product type
- `landing` - Page structure and CTA strategies
- `chart` - Chart types and library recommendations
- `ux` - Best practices and anti-patterns
- `prompt` - AI prompts and CSS keywords

**Stack search:**
```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "<query>" --stack <stack>
```
Available stacks: `html-tailwind` (default), `react`, `nextjs`, `vue`, `svelte`, `swiftui`, `react-native`, `flutter`

## Architecture

```
.claude/skills/ui-ux-pro-max/    # Claude Code skill
├── SKILL.md                      # Skill definition with workflow instructions
├── scripts/
│   ├── search.py                 # CLI entry point
│   └── core.py                   # BM25 + regex hybrid search engine
└── data/                         # CSV databases (styles, colors, typography, etc.)
    └── stacks/                   # Stack-specific guidelines (8 CSV files)

.github/                          # GitHub Copilot instructions
├── copilot-instructions.md       # Repository-wide instructions
├── instructions/                 # Path-specific instructions
│   ├── html.instructions.md      # For .html files
│   ├── react.instructions.md     # For .tsx/.jsx files
│   ├── vue.instructions.md       # For .vue files
│   ├── svelte.instructions.md    # For .svelte files
│   ├── swiftui.instructions.md   # For .swift files
│   ├── flutter.instructions.md   # For .dart files
│   ├── components.instructions.md # For components/pages/views folders
│   └── styling.instructions.md   # For .css/.scss files
└── prompts/                      # Reusable prompt files (slash commands)
    ├── ui-ux-pro-max.prompt.md   # Main workflow
    ├── build-landing.prompt.md   # Build landing page
    ├── build-dashboard.prompt.md # Build dashboard
    ├── build-component.prompt.md # Build UI component
    ├── review-ui.prompt.md       # Review UI code
    └── get-design-system.prompt.md # Generate design system

.windsurf/workflows/              # Windsurf workflow copy
.agent/workflows/ui-ux-pro-max/   # Generic agent workflow copy
.shared/ui-ux-pro-max/            # Shared data copy
```

The search engine uses BM25 ranking combined with regex matching. Domain auto-detection is available when `--domain` is omitted.

## Sync Rules

When modifying files, keep all agent workflows in sync:

- **Data & Scripts** (`data/`, `scripts/`): Copy changes to `.shared/ui-ux-pro-max/` and `cli/assets/.shared/ui-ux-pro-max/`
- **SKILL.md**: Update corresponding files in `.agent/`, `.cursor/`, `.windsurf/`
- **GitHub Copilot**: Update `.github/copilot-instructions.md` and `.github/instructions/` when changing workflow
- **CLI assets**: Copy all skill folders to `cli/assets/` (`.claude/`, `.cursor/`, `.windsurf/`, `.agent/`, `.github/`, `.shared/`)

## Prerequisites

Python 3.x (no external dependencies required)

## Git Workflow

Never push directly to `main`. Always:

1. Create a new branch: `git checkout -b feat/... ` or `fix/...`
2. Commit changes
3. Push branch: `git push -u origin <branch>`
4. Create PR: `gh pr create`
