# Visual Design Pro Max

*Visual Design Pro Max* is the documentation name for three sibling skills that ship with UI/UX Pro Max and turn an art direction into a checkable contract: **`visual-direction`**, **`reference-analysis`** and **`visual-audit`**. They cover games (mobile casual, Flutter/Flame, Unity) and apps (web, SwiftUI/Compose) and share one project folder, `design-system/<slug>/`, which the orchestrator's `search.py --persist` already creates.

| Skill | Job | Entry scripts |
|---|---|---|
| `visual-direction` | search a catalog of 20 art styles, 18 genres and 55 components; build a Visual Direction Profile (`style-profile.json`, schema `vdp/1`); derive three-layer `tokens.json`; write and validate the design contract folder | `scripts/vd.py`, `scripts/vd_tokens.py` |
| `reference-analysis` | extract the visual language of screenshots or mockups into an evidence-graded `reference-analysis.json` (schema `vdp-reference-analysis/1`), merge several references with roles, extract a pixel-share palette, convert to a partial profile | `scripts/reference_analysis.py` |
| `visual-audit` | static drift scan of Flutter, Unity (USS/UXML/C#), web (CSS/TSX/Vue/Svelte/Tailwind) and native code against the contract; UX checklist; capture manifest; screenshot pixel diff; PASS / FAIL / BLOCKED / NOT RUN report | `scripts/audit.py`, `scripts/visual_qa.py` |

Each skill's `SKILL.md` is the authoritative command reference; its `references/*.md` hold the rules. This page is the map across the three and the orchestrator.

## Prerequisites

- **Python 3.8+**, standard library only. No package is installed by any script and none makes a network request.
- **Pillow** (optional). Needed only by `reference_analysis.py extract-colors` and `visual_qa.py diff`. Without it both report `BLOCKED` (stderr `BLOCKED: <reason>`, JSON `{"status": "BLOCKED", ...}` under `--json`, exit 3) instead of crashing. Every other command runs without it.
- **Node.js** (optional). Needed only for the web CSS generator of the `design-system` skill: `node ../design-system/scripts/generate-tokens.cjs --config design-system/<slug>/tokens.json -o tokens.css` (and its web-only hard-code check `validate-tokens.cjs`). No Python script calls Node.
- Flutter, Unity, Xcode or a browser are **not** required by any script. They are needed only if you choose to capture screenshots with the project's own tooling (see CAPTURE below).

## Install paths

The three skills are bundled sub-skills and install exactly like `design`, `design-system`, `brand`, `ui-styling`, `slides` and `banner-design`:

| Route | Where the three folders land |
|---|---|
| Claude Marketplace (`/plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill`, `/plugin install ui-ux-pro-max@ui-ux-pro-max-skill`) | the plugin's `.claude/skills/` (`plugin.json` points `skills` at that folder), next to `ui-ux-pro-max` |
| `uipro init --ai <platform>` (also `--global`) | the platform's skills folder (for example `.claude/skills/`, `.cursor/skills/`, `.agents/skills/`); the CLI copies **every** sub-skill found in its bundled `assets/skills/`, so all nine sub-skills arrive next to the rendered orchestrator. `uipro init --dry-run` lists them as "Would copy N sub-skills" |
| Manual copy | copy `.claude/skills/visual-direction`, `.claude/skills/reference-analysis` and `.claude/skills/visual-audit` **side by side** into the same parent folder (and `design-system` if you want the CSS generator) |

The side-by-side layout matters: the skills address each other with sibling paths of the form `../<skill>/scripts/<file>` relative to the skill's own directory, never with project- or home-rooted paths. Commands on this page are written for a project-level install under `.claude/skills/`; under another layout replace that prefix with the folder your assistant reports as the skill's base directory. Keep the **working directory at the project root**: the scripts read and write `style-profile.json`, `reference-analysis.json`, `design-system/<slug>/`, `qa-logs/` and your code tree relative to it.

## Runtime differences

| Runtime | What changes |
|---|---|
| **Claude Code** | Skills load from `.claude/skills/` or the plugin cache. The `Read` tool returns image content for `.png/.jpg/.webp/.gif`, so `reference-analysis` runs natively: the model views each image, writes observations with `viewed_by: "model-vision"`, and `extract-colors` adds the measured palette. |
| **Claude Desktop (Cowork / Code tab)** | Same skill files. Whether images can be viewed depends on the tools attached to the session, so `reference-analysis` Step 0 (capability check) is mandatory: try to view the image; if the tool returns bytes, base64, metadata or an error, do **not** describe it. Instead send `templates/human-description-template.md` to the user once per image and record the answers with `viewed_by: "human-description"`, capping every derived observation at `high` with evidence `"user description, paragraph N"`. No description at all → `viewed_by: "none"`, the reference owns no roles. |
| **Other assistants via `uipro init --ai <platform>`** | The sub-skills are static folders copied next to the orchestrator; there is no plugin variable, so the scripts are invoked by skill-relative path (`scripts/<file>` from the skill directory, `../<skill>/scripts/<file>` for a sibling) exactly as each `SKILL.md` documents. Image viewing follows the same capability check as above. |
| **Every runtime** | No runtime executes the app or captures screenshots for you. `visual_qa.py manifest` emits capture *instructions*; the capture itself is manual or CI work with the project's own tooling. Until a capture exists, every screenshot cell is **NOT RUN** with its reason, and BLOCKED / NOT RUN are never folded into PASS. |

## End-to-end workflow

```
DISCOVER → AUDIT (inventory) → EXTRACT STYLE → BUILD DESIGN CONTRACT → PLAN → IMPLEMENT → CAPTURE → COMPARE → VERIFY → REPORT
```

Set two shell variables once to keep the commands short:

```bash
VD=.claude/skills/visual-direction/scripts
RA=.claude/skills/reference-analysis/scripts
VA=.claude/skills/visual-audit/scripts
mkdir -p qa-logs      # every --out/--md below writes here
```

### 1. DISCOVER — what look, for what product

Catalog and genre search (BM25 over the skill's CSVs; zero results exit 0 with suggestions):

```bash
python3 $VD/vd.py genres "onet animal link" -n 5            # genre ids + default styles, screens, HUD rules
python3 $VD/vd.py styles "cute japanese puzzle" -n 5        # style ids; add --family cute-cartoon to filter, --json for machine output
python3 $VD/vd.py components "popup" --kind game            # component catalog rows (game | app)
```

Optionally reuse the orchestrator's product/palette/typography reasoning as a seed (it fills gaps only, never overrides a chosen style or a reference):

```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "casual puzzle game" --design-system --json > ds-seed.json
```

### 2. AUDIT — inventory an existing app before deciding anything

Run the scanner **without** a contract to see what the code actually uses (distinct colours, radii, font sizes, families, shadows, durations, icon libraries, component names, detected platform):

```bash
python3 $VA/audit.py scan . --json > qa-logs/inventory.json
```

Inventory mode reports `<category>.variant-explosion` findings plus the rules that need no contract (`icon.mixed-libraries`, `component.duplicate-implementation`, `touch.target-too-small`, `text.contrast-risk`) and tells you whether an existing contract is trustworthy. If there is no contract, build one (step 4) before auditing against anything. `--exclude <glob>` (repeatable) skips build output; `--platform flutter|unity|web|native|mixed` forces the platform when auto-detection is wrong.

### 3. EXTRACT STYLE — from reference images (only when the user supplies them)

```bash
python3 $RA/reference_analysis.py template --out reference-analysis.json          # empty skeleton with _help fields
python3 $RA/reference_analysis.py extract-colors refs/home.png --ref-id ref-1 --k 10 --json   # pixel-share palette (Pillow); paste into palette_observed
# ... view each image (capability check), write one-claim observations with confidence and evidence, derive rules ...
python3 $RA/reference_analysis.py validate reference-analysis.json [--strict] [--check-paths]   # every schema rule; --strict makes open conflicts errors
python3 $RA/reference_analysis.py summary reference-analysis.json                 # <= 12 lines for the user
```

Several images, each owning roles (`color, shapes, characters, buttons, hud, popup, icons, typography, layout, motion`; exactly one owner per role):

```bash
python3 $RA/reference_analysis.py merge ref-1.json ref-2.json --out reference-analysis.json --roles ref-1:color,shapes ref-2:buttons,popup
```

`merge` requires disjoint ids across inputs, re-derives rule confidence and writes only when the result validates. Same topic with a different class across images becomes a conflict (`resolved` when the role has an owner, `open` otherwise, with the question for the user). Only `observed` / `high` rules reach the contract; assumptions, open conflicts and `not_derivable` go to `unknowns` and are asked, never invented. Images stay on the user's machine: `extract-colors` reads the file locally and writes JSON only.

`to-profile` emits the same partial profile that `vd.py profile --reference` consumes, for inspection:

```bash
python3 $RA/reference_analysis.py to-profile reference-analysis.json --project "Onet Garden" --out partial-profile.json   # "_partial": true
```

### 4. BUILD DESIGN CONTRACT

Build the profile by one of the four routes (next section), then the folder:

```bash
python3 $VD/vd.py profile --style japanese-cute-puzzle --platform mobile-ios,mobile-android --stack flutter-flame --project "Onet Garden" --out style-profile.json
python3 $VD/vd.py init --profile style-profile.json --output-dir . --json      # creates design-system/onet-garden/
python3 $VD/vd.py validate --dir design-system/onet-garden                     # must exit 0 before implementation
python3 $VD/vd.py page --dir design-system/onet-garden --name shop --reason "promo layout"   # overrides-only page skeleton
```

`profile` prints JSON to stdout without `--out`; review it and fix misreads by hand — the JSON is the contract. `--platform` accepts a comma list of `mobile-ios, mobile-android, web, desktop, tablet`; `--stack` is one of `flutter, flutter-flame, unity-ugui, unity-ui-toolkit, react, nextjs, vue, svelte, html-tailwind, swiftui, jetpack-compose, react-native, other`; `--audience` is free text; `--project` is slugged for the folder name. Tokens alone: `python3 $VD/vd_tokens.py --profile style-profile.json --out tokens.json` (optional `--seeds` JSON object with `brand, secondary, accent, neutral, success, danger, warning?, reward?`; it is consulted only for seed slots the profile's own `palette.seeds` leaves empty — resolution order in `references/token-derivation.md` §0.2). Same input gives byte-identical `style-profile.json` and `tokens.json`; timestamps live only in `CHANGELOG.md` and `MASTER.md` headers.

Web stacks also generate CSS variables from the contract:

```bash
node .claude/skills/design-system/scripts/generate-tokens.cjs --config design-system/onet-garden/tokens.json -o src/styles/tokens.css
```

### 5. PLAN

Read, in this order: `design-system/<slug>/MASTER.md` (or the persisted Master plus `MASTER.visual-direction.md`), `component-catalog.md` (catalog rule first, then the style modifier), `interaction-guidelines.md`, `pages/<page>.md` for the screen at hand, and the platform adapter in the `visual-direction` skill: `references/platforms/flutter-flame.md`, `unity.md`, `web.md` or `mobile-native.md` (where tokens live, token group → code mapping, component reuse, migration order, what not to touch, capture guidance). For an existing app, group the step-2 findings by `files_to_change` and order the work **tokens → shared components → screens**. Generate the QA checklist now so the acceptance criteria are fixed before code changes:

```bash
python3 $VA/visual_qa.py checklist --profile design-system/onet-garden/style-profile.json --screen shop --out qa-logs/checklist-shop.md
```

Every item starts as NOT RUN with a label column (`RUNTIME-VERIFIED / STATIC-VERIFIED / TOOL-ANALYZED / NOT RUN`).

### 6. IMPLEMENT

Components read `component.*` leaves only; one shared implementation per group (`button`, `card`, `popup`, `hud.chip`, `tile`, `progress`); entering motion uses `primitive.easing.enter`, leaving motion `primitive.easing.exit`. Deviations for one screen go into `pages/<page>.md` as overrides, not into the code. For web, `node .claude/skills/design-system/scripts/validate-tokens.cjs --dir src/` flags raw hex/px literals in `.css .scss .ts .tsx .js .jsx .vue .svelte` files regardless of contract (it does not read `.html`); `audit.py` (step 9) compares against the contract instead.

### 7. CAPTURE

```bash
python3 $VA/visual_qa.py devices                                                       # phone-s / phone-m / phone-l / tablet / desktop matrix
python3 $VA/visual_qa.py manifest --stack flutter-flame --screens home,gameplay,shop --profile design-system/onet-garden/style-profile.json --out qa-logs/screens.json
```

The manifest lists one row per screen × device with the expected file name `<screen>_<device>.png` and the tool to use (Flutter `integration_test`, Unity screenshot API, Playwright for web), each marked "not executed". Stacks: `flutter, flutter-flame, unity-ugui, unity-ui-toolkit, web, swiftui, jetpack-compose`; `--devices` overrides the per-stack default rows. Capture with the project's own tooling, locally or in CI. If the app cannot be run where you are, keep the rows NOT RUN with the reason and apply the static procedure in the `visual-audit` skill's `references/visual-qa-without-runtime.md` (results are labelled `STATIC-VERIFIED`, never "looks correct").

### 8. COMPARE

```bash
python3 $VA/visual_qa.py diff baseline/home_phone-m.png current/home_phone-m.png --threshold 0.5 --tolerance 16 --ignore 0,0,390,60 --out qa-logs/home_phone-m.diff.png --json
```

`--threshold` is a **percent** of compared pixels (default 0.5 = 0.5 %); `--tolerance` is the per-channel difference that counts as a change (0–255, default 16); `--ignore x0,y0,x1,y1` masks regions such as clocks or ads (repeatable, exclusive max corner); `--out` writes a side-by-side `a | b | heat` image. Output carries `diff_ratio` (fraction), `diff_percent`, `bbox` and clusters. Exit 0 PASS, 1 FAIL, 3 BLOCKED (Pillow missing, unreadable image, size mismatch), 2 usage.

For code, compare two scans on `(rule, file, evidence)` — line numbers are ignored:

```bash
python3 $VA/audit.py compare qa-logs/findings.json qa-logs/after.json      # resolved / new / unchanged / changed_severity; exit 1 only on new findings at/above --fail-on
```

### 9. VERIFY

```bash
python3 $VD/vd.py validate --dir design-system/onet-garden --json
python3 $VA/audit.py scan . --contract design-system/onet-garden/tokens.json --profile design-system/onet-garden/style-profile.json --fail-on high --out qa-logs/after.json --md qa-logs/after.md
```

`validate` checks required keys and enums of the profile, the token layers, the Master, every page (a page that restates three or more master values, or copies the master, is an error) and the CHANGELOG. `scan` exits 1 when findings at or above `--fail-on` exist (`critical | high | medium | low | none`, default `high`), 2 on usage/IO errors, and also 1 for a malformed contract. `--profile` supplies `intentional_exceptions`, `anti_patterns`, duration/family fallbacks and the preferred icon library; `--primary <glob>` marks primary screens for the severity ladder; `--tolerance N` and `--near-threshold D` adjust scale and colour matching. Only findings of `kind: rule` or `recommendation` count toward the threshold; `aesthetic` and `intentional-exception` are listed but never gate.

### 10. REPORT

Header (platform, contract files, scanned/skipped counts), summary table per severity, findings by severity — each answering where (file:line, evidence), impact, which token/rule is violated, the fix, the files to change and how to verify — the inventory, the screenshot matrix with PASS / FAIL / BLOCKED / NOT RUN per cell, and limitations. State what was **derived** versus **assumed** (the profile's `unknowns`, the analysis's `not_derivable` and open conflicts), which references were viewed, described or not analysed, and the exact validate/scan/diff exit codes. Any BLOCKED cell makes the report INCOMPLETE; BLOCKED and NOT RUN are never folded into PASS.

## The four style-selection routes

| Route | Input | Command | Notes |
|---|---|---|---|
| **A — catalog** | a look, mood or style id | `vd.py styles "<query>"` → `vd.py profile --style <id> …` | unknown id → closest ids listed, exit 1, never a fabricated row |
| **B — genre** | a genre or app category | `vd.py genres "<query>"` → `vd.py profile --genre <id> [--style <id>] …` | the genre's first default style supplies the visual values unless `--style` names one |
| **C — single reference** | one image analysed by `reference-analysis` | `vd.py profile --reference reference-analysis.json …` | without `--style`, `style.id = reference-derived-custom` |
| **D — multi-reference with roles** | several images, each owning roles | `reference_analysis.py merge … --roles …` → `vd.py profile --reference merged.json [--style <id>] …` | references override only the roles they own; the catalog style fills the rest |

`--style`, `--genre` and `--reference` combine freely. Genre + style is the normal way to say "this game type in this look": `--genre` supplies product kind, genre, screens, HUD and touch rules, `--style` the visual values; `--genre` alone falls back to the genre's first default style. An unknown style or genre id exits 1 with the closest ids. `--seed-design-system ds-seed.json` (the orchestrator's `--design-system --json` output) can be added to any route and fills gaps only. Decision rules, what to ask the user and when, and the field mapping are in the `visual-direction` skill's `references/style-selection-workflow.md`; the confidence tests for reference claims are in the `reference-analysis` skill's `references/confidence-levels.md`.

## The design contract folder

```
design-system/<slug>/
├── MASTER.md                   # global contract: identity, visual direction, token summary, page-override logic,
│                               # intentional exceptions, anti-patterns, QA, unknowns (first line: generated-by: visual-direction)
├── MASTER.visual-direction.md  # only when a foreign MASTER.md already existed: the paste block (see below)
├── style-profile.json          # Visual Direction Profile, schema vdp/1
├── tokens.json                 # primitive -> semantic -> component, {"$value", "$type"} leaves, $extensions.vdp
├── component-catalog.md        # catalog rule first, then "Style modifier"
├── asset-guidelines.md         # with the ## Provenance skeleton (research tiers, licences, attribution records)
├── interaction-guidelines.md   # motion class, durations/easings, touch, feedback, reduced motion
├── visual-qa-checklist.md
├── CHANGELOG.md                # append-only; vd.py appends, manual entries allowed
└── pages/
    ├── README.md
    └── <page>.md               # overrides ONLY (vd.py page writes the skeleton; vd.py validate rejects copies of the master)
```

The slug follows the orchestrator's rule (lowercase, `[^a-z0-9_-]+` → `-`, stripped, fallback `default`), so `-p "Onet Garden"` in `search.py` and `--project "Onet Garden"` in `vd.py` land in the same `design-system/onet-garden/`.

**Coexistence with `search.py --design-system --persist`.** That command writes `MASTER.md` (Global Rules / Component Specs / Style Guidelines / Anti-Patterns / Pre-Delivery Checklist) and `pages/`. `vd.py init` applies this decision table:

| `MASTER.md` state | `vd.py init` does |
|---|---|
| absent | writes it from `templates/master-template.md`; the `vd.py init · [tool]` CHANGELOG entry records `- master: created` |
| present, first line contains `generated-by: visual-direction` | tool-owned: rewritten only with `--force`, otherwise kept and reported on stdout as `MASTER.md: kept-tool-owned` |
| present, anything else (`search.py` or hand-written) | left untouched; the ready-to-paste block is printed (and returned as `master_snippet` under `--json`) **and** written to `MASTER.visual-direction.md` next to it, so nothing is lost |

`init` never overwrites silently: existing files are listed as `skipped_files`; `--force` rewrites tool-owned files only, never a foreign `MASTER.md`, never `pages/*.md`, never `CHANGELOG.md`. `vd.py validate` then warns about Master colours that are not in `tokens.json`, which is the cue to merge the paste block into the persisted Master or to record the difference as an intentional exception.

## Applying the contract to another project

Copy **nothing but the generated `design-system/<slug>/` folder** into the target project (the skills themselves are installed there by the same install route, not copied with the contract). Then:

```bash
mkdir -p qa-logs
python3 $VD/vd.py validate --dir design-system/<slug>                                          # contract still coherent after the move
python3 $VA/audit.py scan . --contract design-system/<slug>/tokens.json --profile design-system/<slug>/style-profile.json --fail-on high --out qa-logs/findings.json --md qa-logs/findings.md
```

In CI, run that `scan` with `--fail-on high` (exit 1 fails the job; use `--exclude 'build/**' --exclude '**/node_modules/**'` for generated output) and keep `qa-logs/` — commit it or upload it as a build artifact — so `findings.json` and `findings.md` are reviewable per run and `audit.py compare before.json after.json` can fail only on **new** findings while a legacy backlog is worked off. Screenshot gating in CI needs a capture step produced by the project's own tooling followed by `visual_qa.py diff` per screen × device; without that step the matrix is NOT RUN, and the job must say so rather than pass.

## Exit codes at a glance

| Script | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| `vd.py` (all subcommands) | ok (zero search results included) | validation failed, unknown id (closest ids listed), malformed JSON | usage error, missing file | — |
| `reference_analysis.py` | ok | validation failed, merge rejected, malformed JSON | usage error, missing file | BLOCKED (Pillow missing) |
| `audit.py scan` | nothing at/above `--fail-on` | findings at/above threshold, malformed contract/profile | dir or contract missing, invalid `--platform` or `--fail-on` value (an undetectable platform exits 0 with a warning) | — |
| `audit.py compare` | no new findings at/above threshold | new findings at/above threshold | missing, unparsable or wrong-schema input | — |
| `visual_qa.py diff` | PASS | FAIL | usage error | BLOCKED (Pillow missing, unreadable image, size mismatch) |
| `visual_qa.py checklist` / `manifest` | ok | invalid profile | missing file, unsupported stack, usage | — |

## Limitations

- **Static heuristics, not a parser.** `audit.py` is a regex scanner: computed values (`radius * 2`), theme extensions, CSS-in-JS template literals with interpolation, multi-line `BoxShadow(` beyond one nesting level, Unity `.asset`/prefab YAML colours and sprite/texture UI are not inspected. Touch-target, duplicate-component and contrast rules are heuristics (`confidence: heuristic`) — confirm on device.
- **Platform coverage.** Swift and Kotlin patterns are experimental and untested against a fixture; Unity coverage is USS/UXML plus C# literals and is fixture-tested only; Flutter is fixture-tested (`scripts/tests/fixtures/drift-project/`, a static tree, not a runnable app).
- **Pixel diff is not art direction.** `visual_qa.py diff` is a regression gate: a wrong baseline passes forever, and it says where pixels changed, not whether the screen is on-brand or usable. The checklists and the human review carry that judgement.
- **No capture, no execution.** No script launches an app, drives a browser or takes screenshots; the manifest is instructions. Real Flutter/Unity captures are NOT RUN unless someone runs them.
- **No network, no downloads, no installs.** Research and asset sourcing are model/human activities governed by the `visual-direction` skill's `references/research-and-provenance.md`; reference images are never uploaded anywhere by the scripts.
- **No image generation.** The skills do not produce artwork or assets; the only image any script writes is the optional diff heat image (`visual_qa.py diff --out`).
- **Output directories (CC-14).** `audit.py` (`--out`, `--md`) and `visual_qa.py` (`--out` of `diff`, `checklist`, `manifest`) now create missing parent directories, so `qa-logs/` no longer has to exist first. `reference_analysis.py` does not yet: at the time of writing, `--out` into a missing directory (`extract-colors`, `template`, `to-profile`) still exits 1 with a traceback, so write those files at the project root or create the directory first. Shell redirects such as `> qa-logs/inventory.json` always need the directory, which is why the commands above start with `mkdir -p qa-logs`.
- **No invented values.** Non-derivable facts go to `unknowns` / `not_derivable` and are asked; an unknown style id exits 1 with the closest ids rather than a guess.

## Further reading

- Worked example (route B, profile → init → pages → validate → CSS, with the exact logs): `docs/examples/visual-design-pro-max/`
- Target architecture, integration contract (schemas `vdp/1`, `vdp-reference-analysis/1`, `visual-audit/1`, folder layout, `vd.py` command surface, contract changes CC-1…CC-12) and repository map: `docs/architecture/`
- Per-skill rules: `.claude/skills/visual-direction/references/`, `.claude/skills/reference-analysis/references/`, `.claude/skills/visual-audit/references/`
- Orchestrator routing: the "Visual Design Pro Max" section of `.claude/skills/ui-ux-pro-max/SKILL.md`
