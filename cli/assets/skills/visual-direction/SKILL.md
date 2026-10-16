---
name: visual-direction
description: Choose or define an art style and visual direction for games and apps, then turn it into a design contract. Use when the user asks to pick, define, compare or document an art style, game UI direction, HUD/popup/reward look, style profile, design contract, design tokens, motion direction or research provenance for a product — mobile casual games (Flutter/Flame, Unity), web apps (React/Next/Vue/Svelte/Tailwind) and native apps (SwiftUI/Compose). Produces style-profile.json (vdp/1), tokens.json and design-system/<slug>/ via scripts/vd.py. Hands images to reference-analysis and code checks to visual-audit.
argument-hint: "[style, genre or 'from references'] [--platform mobile-ios,mobile-android] [--stack flutter-flame]"
license: MIT
metadata:
  author: ui-ux-pro-max
  version: "1.0.0"
---

# Visual Direction

Art direction as a contract: a searchable style and genre catalog, a **Visual Direction Profile** (`style-profile.json`, schema `vdp/1`), deterministic three-layer tokens, and the project folder `design-system/<slug>/` with a master file, component catalog, asset/interaction guidelines, QA checklist and per-page overrides. Works for games (HUD, boards, popups, reward loops) and apps.

## When to Use

- "Pick / define / compare an art style" for a game or app (cute Japanese puzzle, anime RPG, minimal finance app, …)
- Game UI direction: HUD, tiles, popups, shop, reward beats, motion class
- Create or maintain a style profile, design contract, `tokens.json`, `MASTER.md`, page overrides
- Motion direction (durations, easings, reduced motion) and asset/research provenance rules
- Platform mapping of the contract to Flutter/Flame, Unity, web or native code (`references/platforms/`)

## When Not to Use

- Analysing screenshots or images → `reference-analysis` skill first (its JSON feeds `vd.py profile --reference`)
- Auditing existing code or screenshots for drift → `visual-audit` skill
- Generic web token CSS or slide decks without an art-direction decision → `design-system` skill
- Marketing landing-page structure or copy → the `ui-ux-pro-max` skill's own search

## Script Paths

Script paths in this skill and its `references/` are relative to the directory that contains this SKILL.md, not to the project: `scripts/<file>` is this skill's own `scripts/` folder, and `../<skill>/scripts/<file>` is a sibling sub-skill installed alongside it. Build the full path from that directory (Claude Code reports it as the skill's base directory when the skill loads) and keep the working directory at the project root — the scripts read and write project files such as `style-profile.json` and `design-system/<slug>/` relative to it.

## Four Selection Routes

| Route | Input | Command |
|---|---|---|
| **A — catalog** | a look, mood or style id | `python3 scripts/vd.py styles "<query>"` → `profile --style <id>` |
| **B — genre** | a genre or app category | `python3 scripts/vd.py genres "<query>"` → `profile --genre <id>` |
| **C — single reference** | one image analysed by `reference-analysis` | `profile --reference reference-analysis.json` |
| **D — multi-reference with roles** | several images, each owning roles (colour, buttons, hud, …) | `profile --reference merged.json [--style <id>]` |

Routes combine: `--style` + `--genre` (style supplies the visual fields, genre supplies product kind/genre, core screens, HUD elements and touch rules — the usual "this game type in that style" request); `--reference` with either or both lets the references override only the roles they own (CC-3); `--seed-design-system ds.json` (from the orchestrator's `search.py "<query>" --design-system --json`) fills gaps only. Decision rules, what to ask the user and when, and the field mapping: `references/style-selection-workflow.md`.

## Workflow Position

```
DISCOVER  catalog search / genre / reference analysis (A–D)
DIRECT    vd.py profile  → style-profile.json  (review, fix unknowns with the user)
CONTRACT  vd.py init     → design-system/<slug>/ ; vd.py validate must exit 0
IMPLEMENT references/platforms/<stack>.md ; web: ../design-system/scripts/generate-tokens.cjs
AUDIT     visual-audit skill (audit.py scan --contract tokens.json ; visual_qa.py)
REPORT    what was derived vs assumed (unknowns), exceptions, validate/audit results
```

Only observed/high facts enter the contract; everything else is written to `unknowns` and asked, never invented.

## Commands

| Task | Command |
|---|---|
| Search styles | `python3 scripts/vd.py styles "cute japanese puzzle" [-n 5] [--family cute-cartoon] [--json]` |
| Search genres | `python3 scripts/vd.py genres "onet animal link" [-n 5] [--json]` |
| Search components | `python3 scripts/vd.py components "popup" [--kind game] [--json]` |
| Profile from style | `python3 scripts/vd.py profile --style japanese-cute-puzzle --platform mobile-ios,mobile-android --stack flutter-flame --project "Onet Garden" --out style-profile.json` |
| Profile from genre | `python3 scripts/vd.py profile --genre productivity-app --platform web --stack nextjs --out style-profile.json` |
| Genre + style (game type in a look) | `python3 scripts/vd.py profile --genre match-3 --style japanese-cute-puzzle --platform mobile-ios,mobile-android --stack flutter-flame --project "Candy Garden" --out style-profile.json` |
| Profile from references | `python3 scripts/vd.py profile --reference reference-analysis.json [--style <id>] [--seed-design-system ds.json] --platform mobile-android --out style-profile.json` |
| Create the contract | `python3 scripts/vd.py init --profile style-profile.json --output-dir . [--force] [--json]` (the output dir is created if missing) |
| Page overrides | `python3 scripts/vd.py page --dir design-system/<slug> --name shop --reason "promo layout"` |
| Validate | `python3 scripts/vd.py validate --dir design-system/<slug> [--json]` |
| Tokens only | `python3 scripts/vd_tokens.py --profile style-profile.json --out tokens.json` |
| Web CSS variables | `node ../design-system/scripts/generate-tokens.cjs --config design-system/<slug>/tokens.json -o tokens.css` |

Exit codes: `0` ok · `1` validation failed, unknown id (closest ids are listed) or malformed JSON · `2` usage error or missing file. Zero search results exit 0 with suggestions. `init` never overwrites silently: existing files are listed as skipped; an existing `MASTER.md` that this tool did not write is left untouched and the paste block goes to `MASTER.visual-direction.md`. `page` skips an existing page (exit 0) unless `--force`. `validate` rejects pages that restate ≥ 3 master values or copy the master.

## Output Folder (`design-system/<slug>/`)

`MASTER.md` (identity, visual direction, resolved token summary, page-override logic, intentional exceptions, anti-patterns, QA, unknowns) · `style-profile.json` · `tokens.json` (primitive → semantic → component, `$extensions.vdp`) · `component-catalog.md` (catalog rule first, then "Style modifier" — CC-11) · `asset-guidelines.md` (with the `## Provenance` skeleton) · `interaction-guidelines.md` · `visual-qa-checklist.md` · `CHANGELOG.md` (append-only) · `pages/<page>.md` (overrides only).

## Hand-offs

| Situation | Go to |
|---|---|
| User supplies screenshots, mockups or a competitor look | `reference-analysis` skill → `reference-analysis.json` → `vd.py profile --reference` |
| Check code or screenshots against the contract; drift, "inconsistent", before/after | `visual-audit` skill (`audit.py scan --contract design-system/<slug>/tokens.json`, `visual_qa.py`) |
| CSS variables / Tailwind theme from `tokens.json`, slide decks | `design-system` skill (`../design-system/scripts/generate-tokens.cjs`) |
| Landing-page structure, colour/typography search for the seed | `ui-ux-pro-max` skill (`search.py --design-system --json` → `--seed-design-system`) |

## References

| Topic | File |
|---|---|
| Selection routes A–D, decision rules, persistence | `references/style-selection-workflow.md` |
| Profile schema field by field (vdp/1, CC-3/4/5/9) | `references/visual-direction-profile.md` |
| Style families, confusables, drift smells | `references/visual-families.md` |
| Game screens, HUD, boards, popups, reward loops | `references/game-ui-patterns.md` |
| Motion tiers, class → durations/easings per platform | `references/motion-direction.md` |
| VDP → tokens.json derivation rules | `references/token-derivation.md` |
| Folder layout, MASTER.md, pages, CHANGELOG, drift budget | `references/design-contract.md` |
| Research tiers, licences, attribution records | `references/research-and-provenance.md` |
| Token → code per stack | `references/platforms/README.md`, `flutter-flame.md`, `unity.md`, `web.md`, `mobile-native.md` |

## Data

`data/visual-styles.csv` (20 styles, 29 columns incl. seed colours and button/panel/HUD/reward rules) · `data/genre-profiles.csv` (18 genres, default styles, screens, HUD, touch rules) · `data/component-catalog.csv` (55 app + game components, 13 columns). `templates/master-template.md` is the `MASTER.md` template.

## What the Scripts Never Do

- No network access, no downloads, no package installs — stdlib Python 3.8+ only; research is a model/human activity governed by `references/research-and-provenance.md`.
- No overwriting of a `MASTER.md` the tool did not write, of `pages/<page>.md`, or of `CHANGELOG.md` history.
- No invented values: unknown style ids list the closest ids and exit 1; non-derivable facts go to `unknowns`.
- No timestamps inside `style-profile.json` or `tokens.json` (same input ⇒ byte-identical output); timestamps live in `CHANGELOG.md` and `MASTER.md` headers only.
