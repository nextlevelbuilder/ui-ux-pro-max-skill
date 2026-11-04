# Repository Map (as of 2026-10-15, commit 56ea9cf on `main`)

Produced by direct inspection of the checkout before any change was made. Every path below was read, not inferred.

## Workspace state at start

| Item | Value |
|------|-------|
| Checkout | `ui-ux-pro-max-skill/` (clone of `nextlevelbuilder/ui-ux-pro-max-skill`) |
| Branch / cleanliness | `main`, up to date with `origin/main`, working tree clean |
| Work branch created | `feat/visual-design-pro-max` (never push to `main`, per `CLAUDE.md`) |
| Baseline tests | `python3 -m pytest .claude/skills -q` → **300 passed**; `python3 -m unittest discover -s src/ui-ux-pro-max/scripts/tests` → **164 OK** |
| Local toolchain | Python 3.14.8 (Pillow 11.3, pytest 8.4), Node 26, Bun, Playwright, Flutter + Dart, Unity Hub, Xcode, Android Studio |

## Top-level layout

```
ui-ux-pro-max-skill/
├── src/ui-ux-pro-max/            # SOURCE OF TRUTH for the core skill
│   ├── data/                     # 13 CSV datasets + 4 JSON catalogs (+ data/stacks/*.csv, 22 stacks)
│   ├── scripts/                  # search.py (CLI), core.py (BM25+regex), design_system.py,
│   │                             # reasoning_contract.py, validate_data.py, tests/ (unittest, 164 tests)
│   └── templates/                # base/skill-content.md, base/quick-reference.md, platforms/*.json (23)
├── .claude/skills/               # The 7 skills a plugin install loads
│   ├── ui-ux-pro-max/            # Orchestrator: hand-authored SKILL.md + references/ + MIRROR of src data/ & scripts/
│   ├── design/  design-system/  brand/  ui-styling/  slides/  banner-design/   # 6 bundled sub-skills (claudekit origin)
├── cli/                          # npm `ui-ux-pro-max-cli` (`uipro init --ai <platform>`)
│   ├── assets/                   # MIRROR of src/ (data, scripts, templates) + skills/<6 sub-skills>
│   ├── scripts/sync-assets.mjs   # the only sync mechanism; `subSkills` list is hard-coded here
│   ├── src/utils/template.ts     # renders orchestrator SKILL.md; copies bundled sub-skills (listBundledSubSkills)
│   └── tests/e2e/*.spec.ts       # Playwright specs: path contracts, dry-run, detect, copilot
├── .claude-plugin/               # plugin.json / marketplace.json (`"skills": "./.claude/skills/"`)
├── .github/workflows/            # tests.yml, check-asset-sync.yml (path + bundled-skill contracts), release.yml, …
├── scripts/                      # repo-level validators: validate-csv.py, validate-agent-guide.py,
│                                 # generate-catalog-summary.py, smoke-domains.sh, smoke-stacks.sh, evaluate-relevance.py
├── docs/journals/                # dated engineering journals (format: YAML header + Context/What happened/Decisions)
├── gallery/                      # Next.js style gallery (reads styles.csv) — untouched by this work
├── projects/, preview/, screenshots/   # demo HTML pages and repo-owned screenshots
└── stack/                        # separate "website design stack" starter — untouched
```

## How the pieces work

### Search engine (`src/ui-ux-pro-max/scripts/core.py`)
- `CSV_CONFIG` maps 12 domains → CSV file + search/output columns. `STACK_CONFIG` maps 22 stacks.
- BM25 (k1=1.5, b=0.75) over tokenized columns + regex identity matching, stopwords, synonyms, per-domain score floors, query rewrites, domain auto-detection, 0-result suggestions, legacy-style redirects.
- Index cache keyed by file signature; stdlib only; no network.

### Design system generator (`design_system.py`)
- `DesignSystemGenerator.generate(query, project_name, variance, motion, density)` → dict with keys
  `project_name, category, pattern, style, colors, typography, key_effects, anti_patterns, decision_rules, activated_rules, constraints, reasoning_default, source_identities, source_derivations, severity, dials, motion_snippet, spacing_scale`.
- Flow: product search → reasoning rule (`ui-reasoning.csv`) → multi-domain search with style priority → colour-mode-coherent palette → typography → landing pattern.
- `persist_design_system()` writes `design-system/<slug>/MASTER.md` and optional `pages/<page>.md`; refuses to overwrite without `--force`; `safe_slug()` prevents path escape. `format_master_md()` / `format_page_override_md()` are the file formats.

### Skill packaging contracts (enforced by CI)
1. **Sync contract** (`check-asset-sync.yml`, `npm --prefix cli run check:assets`): `cli/assets/{data,scripts,templates}` and `.claude/skills/ui-ux-pro-max/{data,scripts}` must hash-match `src/`; `cli/assets/skills/<name>` must match `.claude/skills/<name>` for every name in `subSkills` (sync-assets.mjs). Binary/font files excluded; CRLF normalised.
2. **Path contract**: inside `.claude/skills` and `cli/assets/skills` no `~/.claude/skills/…`, no `.claude/skills/<x>` project-rooted paths, no `CLAUDE_PLUGIN_ROOT` except the orchestrator SKILL.md. Documented invocations must be `scripts/<file>` or `../<sibling-skill>/scripts/<file>` and the file must exist (`test_skill_script_paths.py`, needs >100 invocations total).
3. **Bundled-skill contract**: any `` `name` `` followed by "skill(s)" in shipped markdown must be a directory under `.claude/skills`; claudekit names (`frontend-design`, `chrome-devtools`, …) and `/ck:` namespaces are forbidden.
4. **Data contract**: `scripts/validate-csv.py` (structure), `validate_data.py` (semantics), `generate-catalog-summary.py --check` (counts + sha256 snapshots), `validate-agent-guide.py` (SKILL.md claims vs data, locked examples). These scan `src/ui-ux-pro-max/data` only.
5. **Test contract**: `tests.yml` runs `verify:data`, then `python3 -m pytest .claude/skills -v`, then Playwright e2e.

### Existing sub-skill conventions (observed in the 6 bundled skills)
- Frontmatter: `name`, `description` (trigger text), optional `argument-hint`, `license: MIT`, `metadata.author/version`.
- A "Script Paths" paragraph explaining skill-relative resolution.
- `references/*.md` loaded on demand; `data/*.csv` + a private BM25 core per skill (`design/scripts/logo/core.py`, 175 lines; `design-system/scripts/slide_search_core.py`) — skills do **not** import the orchestrator's `core.py`.
- Tests under `scripts/tests/test_*.py` (pytest), offline, mocking any network SDK.

### Persisted design-system folder (what projects already get)
```
design-system/<project-slug>/
├── MASTER.md          # generated by search.py --design-system --persist
└── pages/<page>.md    # overrides only
```
`design-system/` is **not** gitignored in this repo (only `/plans/`, `.claude/settings.local.json`, build output are).

## Coverage gaps relevant to the mission (measured)
- `styles.csv` (79 searchable): game/illustration-adjacent rows are only Claymorphism, Pixel Art, HUD / Sci-Fi FUI. No anime, cartoon, kawaii, storybook, toy-3D, cozy-pastel rows. `--domain style "puzzle casual mobile game"` returns Material 3 / Bauhaus / Claymorphism.
- `products.csv` (192): game rows = Gaming, Casual Puzzle Game, Trivia & Quiz, Card & Board, Idle & Clicker, Word & Crossword, Arcade & Retro, Kids Learning. `"game" --domain product` → 0 results (score floor).
- No reference-image workflow, no consistency audit, no screenshot QA, no Unity stack, no Flame guidance anywhere in the repo.
- `design-system` sub-skill has `validate-tokens.cjs` (hex/px detection, web only) and `generate-tokens.cjs` (three-layer `$value` JSON → CSS/Tailwind) — reusable for web token output.

## Third-party provenance to preserve
- Sub-skills carry `metadata.author: claudekit`, MIT. Google Fonts and Phosphor catalogs carry provenance in `data-provenance.json` / `catalog-summary.json`. None of these are modified by this work.
