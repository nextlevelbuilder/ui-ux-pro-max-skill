# Integration Contract (locked for Wave 2)

All agents implement against this document. Deviations require a note in `AGENT_WORK_PLAN.md` → "Contract changes".

## 1. File ownership

| Path | Owner | Others may |
|---|---|---|
| `docs/architecture/*` | Principal | read |
| `.claude/skills/visual-direction/SKILL.md`, `scripts/vd.py`, `scripts/vd_core.py`, `scripts/tests/`, `references/*.md` (except `platforms/`) | W2-A | read |
| `.claude/skills/visual-direction/data/*.csv` | W1-2 (content) then W2-A (schema fixes only) | read |
| `.claude/skills/visual-direction/references/platforms/*.md` | W2-D | read |
| `.claude/skills/reference-analysis/**` | W2-B | read |
| `.claude/skills/visual-audit/**` | W2-C | read |
| `docs/examples/visual-design-pro-max/**` | W2-E | read |
| `.claude/skills/ui-ux-pro-max/SKILL.md` (routing section), `README.md` (one section), `cli/scripts/sync-assets.mjs` (`subSkills`), `docs/VISUAL_DESIGN_PRO_MAX.md`, `CHANGELOG`-style journal | W2-G | read |
| `cli/assets/skills/*` | nobody by hand — produced by `npm run sync:assets` (Principal runs it) | — |
| `src/ui-ux-pro-max/**`, gallery, stack, other sub-skills | **frozen** | read |

## 2. Skill layout (mandatory)

```
.claude/skills/<skill>/
├── SKILL.md                      # frontmatter: name, description, argument-hint, license: MIT, metadata{author: "ui-ux-pro-max", version: "1.0.0"}
├── references/*.md
├── data/*.csv                    # only visual-direction
├── templates/*                   # optional
└── scripts/
    ├── <entry>.py                # argparse CLI, stdlib only, `--json` output supported
    └── tests/test_*.py           # pytest, offline, uses fixtures under scripts/tests/fixtures/
```
Rules every markdown file must satisfy (CI): script invocations written as `scripts/<file>` or `../<sibling>/scripts/<file>` and the file must exist; no `~/.claude/skills`, no `.claude/skills/<x>`, no `CLAUDE_PLUGIN_ROOT`; the only skill names that may appear as `` `name` `` + "skill" are: `ui-ux-pro-max design design-system brand ui-styling slides banner-design visual-direction reference-analysis visual-audit`. Never mention claudekit-only skills (`frontend-design`, `chrome-devtools`, `ai-multimodal`, `ai-artist`, `assets-organizing`, `project-management`).
Each SKILL.md includes the standard "Script Paths" paragraph (copy from `design-system/SKILL.md`).

## 3. Design contract folder (project side)

```
design-system/<project-slug>/
├── MASTER.md                 # global contract. If absent, vd.py init writes it; if present, untouched (prints snippet)
├── style-profile.json        # Visual Direction Profile (schema vdp/1)
├── tokens.json               # three-layer tokens (compatible with ../design-system/scripts/generate-tokens.cjs)
├── component-catalog.md      # component rules filtered for product kind + style
├── asset-guidelines.md
├── interaction-guidelines.md # motion + touch + feedback
├── visual-qa-checklist.md
├── CHANGELOG.md              # vd.py appends entries; manual edits allowed
└── pages/<page>.md           # overrides ONLY (vd.py page creates the skeleton; vd.py validate flags copies of MASTER)
```
Slugging uses the same rule as `design_system.safe_slug`: lowercase, `[^a-z0-9_-]+` → `-`, strip `-`, fallback `default`.

## 4. Schemas

### 4.1 Visual Direction Profile — `style-profile.json` (`"schema": "vdp/1"`)
```json
{
  "schema": "vdp/1",
  "project": {"name": "Onet Garden", "slug": "onet-garden"},
  "product": {"kind": "game", "genre": "onet-animal-puzzle", "platforms": ["mobile-ios", "mobile-android"],
              "stack": "flutter-flame", "audience": "casual-all-ages", "orientation": "portrait"},
  "style": {"id": "japanese-cute-puzzle", "name": "Japanese Cute Puzzle", "family": "cute-cartoon",
            "mood": ["cheerful", "soft", "rounded"], "confidence": "high"},
  "sources": [
    {"type": "catalog", "ref": "visual-styles.csv#japanese-cute-puzzle"},
    {"type": "genre", "ref": "genre-profiles.csv#onet-animal-puzzle"},
    {"type": "reference-analysis", "ref": "reference-analysis.json", "roles": ["color", "buttons"]},
    {"type": "design-system-seed", "ref": "search.py --design-system --json"}
  ],
  "principles": ["string", "..."],
  "shape": {"radius_class": "xl", "silhouette": "rounded-blob", "outline": {"width": 3, "color_rule": "darker-shade-of-fill"}},
  "rendering": {"shading": "soft-cel", "highlight": "top-left-gloss", "shadow": "offset-soft", "texture": "none"},
  "typography": {"display": "Fredoka", "body": "Nunito", "case": "title", "weight_rule": "display bold / body medium"},
  "palette_strategy": "pastel-base + saturated accents for rewards",
  "iconography": {"style": "filled-rounded", "stroke": null, "library_hint": "custom|phosphor-fill"},
  "illustration": {"character_style": "chibi-animal", "asset_rendering": "vector-flat-with-soft-shade"},
  "motion": {"class": "bouncy", "duration_scale": {"fast": 120, "base": 200, "slow": 350}, "easing": "spring-soft", "reduced_motion": "respect"},
  "components": {"button.primary": "pill, 3px outline, double shadow, label uppercase off", "...": "..."},
  "anti_patterns": ["string"],
  "qa_criteria": ["string"],
  "intentional_exceptions": [{"scope": "gameplay-hud", "rule": "smaller radius for tiles", "reason": "grid density"}],
  "unknowns": ["string"]
}
```
Required: `schema, project, product.kind, product.platforms, style.id, sources, shape, rendering, typography, motion, anti_patterns, qa_criteria`. Everything else optional. `vd.py validate` enforces required keys and enum values below.

Enums: `product.kind ∈ {game, app}`; `platforms ⊆ {mobile-ios, mobile-android, web, desktop, tablet}`; `stack ∈ {flutter, flutter-flame, unity-ugui, unity-ui-toolkit, react, nextjs, vue, svelte, html-tailwind, swiftui, jetpack-compose, react-native, other}`; `shape.radius_class ∈ {none, sm, md, lg, xl, pill}`; `rendering.shading ∈ {flat, soft, soft-cel, cel, painterly, glossy, clay, pixel, realistic}`; `motion.class ∈ {static, snappy, soft, bouncy, dramatic}`; confidence ∈ `{observed, high, assumption, not-derivable}`.

### 4.2 `tokens.json` (compatible with `generate-tokens.cjs`)
Three top-level layers `primitive`, `semantic`, `component`; leaves are `{"$value": ..., "$type": ...}`; references use `"{primitive.color.brand.500}"`. Groups required in `primitive`: `color`, `spacing`, `radius`, `outline`, `shadow`, `fontSize`, `lineHeight`, `iconSize`, `touchTarget`, `duration`, `easing`, `zIndex`, `opacity`. `semantic.color` must define: `primary, onPrimary, secondary, onSecondary, accent, onAccent, background, surface, surfaceElevated, border, overlay, text, textMuted, success, warning, danger, reward`. `semantic.state` defines `hover, pressed, focus, disabled` opacity/offset rules. `$extensions.vdp` carries `{platformUnit: "px|dp|pt|logical", minTouchTarget, motionClass, generatedFrom: "<style id>"}`.

### 4.3 Reference analysis — `reference-analysis.json` (`"schema": "vdp-reference-analysis/1"`)
```json
{
  "schema": "vdp-reference-analysis/1",
  "project": "optional",
  "references": [{"id": "ref-1", "path": "refs/home.png", "label": "home screen", "roles": ["color", "shapes"],
                  "viewed_by": "model-vision|human-description|none", "screen_type": "home|gameplay|popup|shop|other",
                  "provenance": {"owner": "user", "license": "unknown", "note": "user-provided"}}],
  "observations": [{"id": "obs-1", "category": "layout|color|shape|shading|typography|component|character|motion|accessibility|iconography",
                    "statement": "...", "refs": ["ref-1"], "evidence": "where in the image", "confidence": "observed|high|assumption|not-derivable"}],
  "rules": [{"id": "rule-1", "target": "button.primary|palette|radius|hud|popup|icon|typography|...", "statement": "...",
             "derived_from": ["obs-1"], "confidence": "high", "scope": "global|context:<screen_type>"}],
  "conflicts": [{"topic": "corner radius", "between": ["ref-1", "ref-2"], "resolution": "ref-1 wins (role shapes)", "status": "resolved|open"}],
  "not_derivable": ["animation timing", "..."],
  "palette_observed": [{"hex": "#FFD5E5", "share": 0.31, "role_guess": "background", "ref": "ref-1"}]
}
```
Roles enum: `color, shapes, characters, buttons, hud, popup, icons, typography, layout, motion`. Exactly one reference may own a role; `merge` enforces it. Confidence values are the same four as 4.1.

### 4.4 Audit findings — `findings.json` (`"schema": "visual-audit/1"`)
```json
{
  "schema": "visual-audit/1", "generated_at": "ISO", "root": "<scanned dir>", "platform": "flutter|unity|web|mixed|unknown",
  "contract": {"tokens": "path or null", "profile": "path or null"},
  "scanned_files": 42, "skipped_files": 3,
  "summary": {"critical": 0, "high": 2, "medium": 5, "low": 1, "info": 0},
  "inventory": {"colors": {"#FF7F50": 3}, "radii": {"8": 10, "13": 1}, "font_sizes": {"14": 20}, "shadows": 4,
                "durations": {"200": 5, "337": 1}, "icon_libraries": ["material", "font_awesome"], "font_families": ["Nunito"]},
  "findings": [{"id": "VA-0001", "rule": "color.off-palette", "severity": "high", "category": "color",
                "file": "lib/screens/shop.dart", "line": 42, "evidence": "Color(0xFFFF7F50)",
                "message": "Hard-coded colour not in tokens.json palette",
                "violates": "tokens.semantic.color (allowed set) / visual-styles rule 'no ad-hoc colours'",
                "nearest": "semantic.color.accent #FF8A4C (distance 9.2)",
                "impact": "Shop CTA reads as a different brand than Home CTA",
                "fix": "Replace with the accent token; if intentional, add to pages/shop.md intentional_exceptions",
                "files_to_change": ["lib/screens/shop.dart"],
                "verify": "re-run `audit.py scan`; VA-0001 must be absent",
                "kind": "rule|recommendation|aesthetic|intentional-exception"}]
}
```
Rule ids (minimum set): `color.off-palette`, `color.near-duplicate`, `radius.off-scale`, `font-size.off-scale`, `font-family.unlisted`, `spacing.off-scale`, `shadow.variant-explosion`, `duration.off-scale`, `icon.mixed-libraries`, `component.duplicate-implementation`, `touch.target-too-small`, `text.contrast-risk`. Severity ladder: Critical (blocks usability/accessibility), High (visible brand/style break on a primary screen or ≥3 occurrences), Medium (secondary screen or 1–2 occurrences), Low (cosmetic), Info (inventory only).
Exit codes for `audit.py scan`: `0` no findings at/above `--fail-on` (default `high`), `1` findings at/above threshold, `2` usage/IO error. `audit.py compare before.json after.json` prints resolved/new/unchanged counts and exits 0 unless new findings at/above threshold.

### 4.5 Visual QA — `visual_qa.py`
- `diff <a.png> <b.png> [--threshold 0.5] [--out diff.png] [--json]` → `{"status": "PASS|FAIL|BLOCKED", "diff_ratio": 0.0123, "bbox": [x0,y0,x1,y1]}`; exit `0` PASS, `1` FAIL, `3` BLOCKED (Pillow missing or unreadable image).
- `checklist --profile style-profile.json [--screen gameplay] [--format md|json]` → checklist items from `qa_criteria` + generic per-screen items.
- `manifest --stack <stack> --screens home,gameplay,shop --out screens.json` → capture instructions per stack (Flutter integration_test, Unity screenshot API, Playwright), clearly marked "manual/automation hints, not executed".

## 5. `vd.py` command surface
```
vd.py styles "<query>" [-n 5] [--json]
vd.py genres "<query>" [-n 5] [--json]
vd.py components "<query>" [--kind game|app] [--json]
vd.py profile --style <id> | --genre <id> | --reference <analysis.json> [--seed-design-system <ds.json>]
              --platform <p>[,<p>] [--stack <s>] [--audience <a>] [--project "<Name>"] [--out style-profile.json]
vd.py init --profile style-profile.json --output-dir <project-root> [--force] [--json]
vd.py page --dir design-system/<slug> --name <page> [--reason "..."]
vd.py validate --dir design-system/<slug> [--json]
```
Exit: `0` ok, `1` validation failed / unknown style, `2` usage error. Unknown style id → list closest ids (difflib) and exit 1, never fabricate.

## 6. Test conventions
- pytest, file `scripts/tests/test_<entry>.py`, every CLI command exercised through `subprocess.run([sys.executable, script, ...])` at least once plus unit tests on pure functions.
- Fixtures: `scripts/tests/fixtures/…`; synthetic images are generated in-test with Pillow **and skipped** (`pytest.importorskip`) when Pillow is missing — the BLOCKED path must have a test that runs without Pillow by monkeypatching the import.
- Invalid input, missing file, unknown style, missing Pillow, unsupported platform each have a test.

## 7. Orchestrator hand-offs (text to be added by W2-G)
| Trigger | Route |
|---|---|
| choose/define an art style, game HUD, style profile, design contract | `visual-direction` |
| user supplies screenshots/images to copy a look | `reference-analysis` → `visual-direction` |
| "audit", "inconsistent", "style drift", "screenshot compare" | `visual-audit` |
| web token CSS from tokens.json | `design-system` (`generate-tokens.cjs`) |

## 8. Contract changes
- CC-1 (from Agent 6): `sources[].type` enum extended to `{catalog, genre, reference-analysis, design-system-seed, research}`; a `research` source carries `ref` = the attribution record id in `asset-guidelines.md`.
- CC-2 (Principal): `visual-direction/scripts/vd_core.py` is pre-written by the Principal; W2-A must build `vd.py` on it (may extend, must keep `search/row_by_id/closest_ids/split_list`).
- CC-3 (from Agent 3, decided by Principal): `vd.py profile --reference <json>` without `--style` uses `style.id = reference-derived-custom`; with `--style`, reference rules override catalog values for the roles the reference owns. `reference_analysis.py to-profile` emits a partial profile marked `"_partial": true`; `vd.py profile` completes it.
- CC-4: `typography.display/body` may hold a classification string (e.g. "rounded geometric sans") when the family is not derivable; the family name then goes to `unknowns`.
- CC-5: radius classes are defined as percent of element height (none 0, sm ≤5, md 5–12, lg 12–20, xl 20–40, pill ≥50); px values per class come from the token derivation rules.
- CC-6: `rules[].target` vocabulary is a warning, not an error, in `reference_analysis.py validate`. Id patterns `ref-N`, `obs-N`, `rule-N` are mandatory. Pillow ≥ 9.1 assumed; older constants fall back to integers.
- CC-7 (from Agent 8, pending Agent 5): token **leaf names** are locked after Agent 5's derivation table lands; W2-A's `vd.py init` emits exactly those names and W2-D reconciles `references/platforms/*.md` to them. Generator quirk recorded: `generate-tokens.cjs` prefixes primitives with `--primitive-`, leaves semantic/component unprefixed, preserves camelCase.
- CC-8 (from Agent 4): `primitive.duration` carries `fast, base, slow, reward, ambient` (reward/ambient derived from motion.class); audit `duration.off-scale` tolerates ±10 % of any listed value. `progress.*` components belong to group `feedback`. Seven base components (HudPlate, BoosterSlot, PopupPanel, RewardCard, PriceTag, ProgressBar, EffectSequencer) are named in Code Reuse Hints; they are documentation names, not shipped code.
- CC-7 (resolved): token leaf names are those emitted by Agent 5's `derive_tokens_ref.py`: `primitive.color.{brand,secondary,accent,neutral,success,danger,warning,reward}.{50..900}` (+ `white`, `black`), `primitive.spacing.{0,1,2,3,4,5,6,8,10,12,16,20,24}`, `primitive.radius.{none,xs,sm,md,lg,xl,2xl,3xl,full}`, `primitive.outline.{none,thin,regular,strong,heavy}`, `primitive.shadow.{none,sm,md,lg,inset}`, `primitive.fontSize.{xs,sm,base,lg,xl,2xl,3xl,4xl,display}`, `primitive.lineHeight.{tight,snug,normal,relaxed}`, `primitive.iconSize.{sm,md,lg,xl}`, `primitive.touchTarget.{min,recommended}`, `primitive.duration.{instant,fast,base,slow,reveal,reward,ambient}` (reward/ambient added per CC-8), `primitive.easing.{standard,enter,exit,emphasized}`, `primitive.zIndex.{base,raised,sticky,hud,overlay,popup,toast,tutorial,debug}`, `primitive.opacity.{disabled,hover,pressed,loading,scrim,scrimHeavy,muted,ghost,focusRing}`, `primitive.fontFamily.{display,body}`; `semantic.{color,elevation,outline,radius,spacing,state,typography}`; `component.{button,card,hud,popup,progress,tile}` nested (never dotted keys). Every `$value` is a string (generator treats numeric 0 as falsy).
- CC-9 (from Agent 5): VDP gains optional `palette.seeds {brand,secondary,accent,neutral,success,danger,warning,reward}`; `vd.py profile` fills it from `visual-styles.csv` "Seed Colors" (primary;secondary;accent;background;surface;text → brand/secondary/accent + derived neutral) or from `palette_observed` of a reference analysis. When `MASTER.md` already exists, `vd.py init` writes `MASTER.visual-direction.md` and prints the paste block.
- CC-10 (from Agent 9, decided by Principal): (a) zero-result `styles/genres/components` search → exit 0, `count: 0`, `suggestions` listed; (b) missing input file → exit 2, malformed JSON / schema failure → exit 1; (c) `vd.py page` on an existing file → skipped with message, exit 0, unless `--force`; (d) page-copies-master: ≥3 restated master token values → validate error; (e) `reference_analysis.py merge` requires disjoint ids across inputs, collision → exit 1; (f) BLOCKED: stderr line `BLOCKED: <reason>`, stdout `{"status":"BLOCKED",...}` under `--json`, exit 3; (g) `visual_qa.py --threshold` is **percent** (default 0.5 = 0.5 %), output carries `diff_ratio` (fraction) and `diff_percent`; (h) audit thresholds: near-duplicate colour ≤12 weighted-RGB distance, shadow variant explosion >6 distinct, touch target heuristic <44 (web px/pt) or <48 (dp) → Medium; (i) `audit.py compare` matches findings on `(rule, file, evidence)`; (j) test files are named per skill (`test_contracts_<skill>.py`) to avoid pytest basename collisions.
- CC-11 (from Agent 2, decided by Principal): (1) the `reference-derived-custom` row keeps enum-valid fallbacks; (2) no per-family ranking cap, but `vd.py styles` prints `Family` and accepts `--family <id>` filter; (3) `Audience` stays free text; `product.audience` in the VDP is a free string; (4) `premium-casual-game` stays in family `candy-glossy`; (5) on conflict between a style row's Button/Panel/HUD/Reward rule and `component-catalog.csv`, the catalog is canonical for structure/states and the style row is the visual modifier — `vd.py init` renders both: catalog rule first, then "Style modifier: …".
- CC-12 (from Agent 7): scale tolerance = integers must hit a step exactly, non-integers ±1, `--tolerance` overrides; colour distance ≤12 → `color.near-duplicate` (Low), >12 → `color.off-palette` (the §4.4 example's "distance 9.2" is therefore a near-duplicate example); additive finding field `confidence: exact|heuristic`; extra rule ids `shadow.unlisted`, `<category>.variant-explosion` (inventory mode). Swift/Kotlin patterns and Unity C#/USS coverage are fixture-only → limitation rows.

**Contract locked 2026-10-15 after Wave 1.** Wave 2 implements against §1–§8 including CC-1..CC-12.
- CC-13 (from W2-F F-06, decided by Principal): the "±10 %" duration tolerance in CC-8 is withdrawn; `duration.off-scale` uses the same exact-integer / ±1-non-integer rule as every other scale (CC-12). Reward and ambient beats are explicit tokens (`primitive.duration.reward/ambient`), so no tolerance is needed.
- CC-14 (from W2-F F-01/F-04/F-05): every `--out`/`--md` writer creates parent directories; heuristic touch-target and contrast findings are capped at Medium (CC-10h) and `severity.md` says so; a tree with `pubspec.yaml` is `flutter` and its platform scaffold folders (`android/ ios/ macos/ linux/ windows/ web/`) are skipped unless `--platform native` is given.
- CC-15 (Principal, 2026-10-16): component-state contrast is part of the contract. Every component label ≥ 4.5:1 on each state background (default/hover/pressed); interactive boundaries ≥ 3:1 via `semantic.color.borderInteractive`; decorative panels use `semantic.color.border`. `vd.py validate` errors on a label below 4.5:1 and warns on a boundary below 3:1. Hover steps in the direction that keeps the default label passing. Seeded brand fills are never changed to avoid a black label: 8 of 20 catalog styles keep a black default primary label because their seed passes 4.5:1 only with black; this is surfaced in `contrastNotes` and MASTER Unknowns for the art director to re-seed if desired.
