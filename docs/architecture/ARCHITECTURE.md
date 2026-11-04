# Visual Design Pro Max — Target Architecture

**Umbrella name:** *Visual Design Pro Max* (documentation name only). Skills ship as three kebab-case sub-skills so they install through the same mechanism as the existing six (`uipro init`, plugin marketplace, manual copy). No existing namespace collides: `.claude/skills/` has no `visual-*` directory and the user-level `~/.claude/skills/` has none either (checked 2026-10-15).

## Design principles (from the brief, mapped to this repo)
1. **Extend, don't fork.** Keep `src/ui-ux-pro-max` untouched except additive, backward-compatible changes. New capability lives in sub-skills that follow the bundled-skill conventions (see REPOSITORY_MAP §"Existing sub-skill conventions").
2. **One design contract per project.** Reuse `design-system/<slug>/` (already produced by `search.py --persist`). Add sibling files; never replace `MASTER.md` that already exists.
3. **Platform-specific profiles.** Game HUD/touch/motion/asset rules are separate data, not web rules relabelled.
4. **Evidence-graded output.** Reference analysis and audit findings carry confidence / severity / evidence fields; no claim without a source.
5. **Small, runnable, tested.** Stdlib-only Python (Pillow optional, degraded gracefully), pytest under `scripts/tests/`, fixtures in-repo.

## Skill decomposition (10 capabilities → 3 skills)

| Brief capability | Home | Why merged here |
|---|---|---|
| A Visual Art Direction | `visual-direction` | style catalog + profile builder are one data model |
| C Game UI Design | `visual-direction` (references/game-ui-patterns.md, data/component-catalog.csv) | genre profile drives component set |
| F Asset & Reference Research | `visual-direction/references/research-and-provenance.md` | research is an input to the profile; no tool code needed |
| G UI Implementation (platform adapters) | `visual-direction/references/platforms/*.md` | contract → code mapping is defined where the contract is |
| I Animation & Interaction Direction | `visual-direction` (motion class in profile + references/motion-direction.md) | motion is a token group of the contract |
| J Design System Maintainer | `visual-direction` (`vd.py init/validate/page`, references/design-contract.md) | owner of the folder layout |
| B Reference Image Analysis | `reference-analysis` | distinct inputs (images), distinct schema, optional Pillow |
| D UI/UX Audit | `visual-audit` | shares scanner + finding format with E |
| E Visual Consistency Audit | `visual-audit` (`audit.py`) | |
| H Screenshot & Visual Regression QA | `visual-audit` (`visual_qa.py`) | |

Routing between skills is documented in the orchestrator `ui-ux-pro-max/SKILL.md` (one new section) and in each skill's "When to use / hand-off" table.

## Data flow

```
user intent ──► (A) catalog style ─┐
            ──► (B) genre ─────────┤  vd.py profile  ──► style-profile.json (Visual Direction Profile)
            ──► (C/D) reference images ──► reference_analysis.py ──► reference-analysis.json ─┘
                                                                              │
                                                                   vd.py init ▼
                                   design-system/<slug>/ {MASTER.md, tokens.json, style-profile.json,
                                        component-catalog.md, asset-guidelines.md, interaction-guidelines.md,
                                        visual-qa-checklist.md, pages/, CHANGELOG.md}
                                                                              │
          project code ──► audit.py scan --contract tokens.json ──► findings.json / .md ──► fix plan ──► implement
                                                                              │
          screenshots ──► visual_qa.py diff / checklist ──► PASS / FAIL / BLOCKED / NOT RUN report
```

Optional seed: `search.py "<query>" --design-system --json` output can be passed to `vd.py profile --seed-design-system <file>` so the orchestrator's palette/typography reasoning is reused instead of re-implemented.

## Platform scope
- **Game (mobile casual, 2D cartoon/anime, Japanese casual):** profiles + HUD/reward/touch rules.
- **Flutter / Flame, Unity (uGUI, UI Toolkit USS/UXML), Web (React/Next/Vue/Svelte/Tailwind), mobile native (SwiftUI/Compose):** scanner patterns + implementation adapters. Flutter/Unity are **fixture-tested only** unless the final report says otherwise.

## Runtime differences (documented in `docs/VISUAL_DESIGN_PRO_MAX.md`)
- Claude Code: skill auto-loads from `.claude/skills/` or plugin cache; `Read` tool can view images → reference analysis runs natively.
- Claude Desktop (Cowork/Code tab): same skill files; image viewing depends on the attached tools; if no vision, the workflow accepts a human-written description file (`reference-analysis.json` with `viewed_by: "human-description"`).
- Other assistants via `uipro init --ai <x>`: sub-skills are copied as static folders; scripts are invoked by skill-relative path.

## Key assumptions recorded
- A1: Adding directories to `.claude/skills/` and to `subSkills` in `sync-assets.mjs` is the sanctioned way to ship a new bundled skill (the CLI discovers them dynamically via `listBundledSubSkills`).
- A2: Pillow may be absent on user machines → every image operation must degrade to an explicit `BLOCKED` result, never a crash.
- A3: No network access is assumed by any script; web research is a model/browser activity governed by the provenance rules, not a script.
- A4: `design-system/<slug>/MASTER.md` produced by `search.py` stays the global contract; our generator writes its own MASTER.md only when none exists and otherwise prints the section to add.
