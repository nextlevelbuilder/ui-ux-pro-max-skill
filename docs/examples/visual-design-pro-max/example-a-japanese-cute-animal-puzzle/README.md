# Example A — Japanese cute animal puzzle (Flutter + Flame)

Routes B + A of the `visual-direction` skill end to end for **Onet Garden**, a portrait tile-matching (onet) game: genre + catalog search → style profile → design contract → page overrides → web token CSS → hand-written screen specs → a drift demo with `visual-audit`.

> **Final regeneration (last round: focus ring, `hud.chipInteractive`).** Every script output here was regenerated from scratch after the last generator round: per-state button labels, `semantic.color.borderInteractive` for interactive outlines (panels keep `#FFDDAC`), `pressDuration` ≤ 90 ms, reward gold `#FFC83D` split from warning `#F5A524`, a `brand.700` selection outline, `neutral.900`-tinted shadows, a focus ring on a distinct brand step (`#740420`), a tappable HUD capsule variant `component.hud.chipInteractive`, and a `vd.py validate` that checks component-state contrast and focus rings (`0 error(s), 0 warning(s)` here). Hand-written content was corrected for the QA items about example content — **AD-1** (board arithmetic), **AD-5** (touch targets), **AD-10** (spin-wheel dividers and map success node, arithmetic in `screens.md`) and **N-2** (run count). Earlier observations are kept at the end with FIXED / STILL PRESENT / NEW status, each confirmed against the final `tokens.json`.

## Purpose

Show what an art director gets from the shipped scripts without any runtime: a `style-profile.json` (schema `vdp/1`) carrying both genre and style, the `design-system/onet-garden/` contract folder, three page-override files that pass `vd.py validate`, generated CSS variables, screen specs that cite token paths, and a before/after audit of a synthetic drift fixture.

## Inputs (and their provenance)

| Input | Provenance |
|---|---|
| Queries `"onet animal puzzle"`, `"japanese cute puzzle"`, flags `--genre onet-animal-puzzle --style japanese-cute-puzzle --platform mobile-ios,mobile-android --stack flutter-flame --audience casual-all-ages --project "Onet Garden"` | this example's brief |
| `.claude/skills/visual-direction/data/{genre-profiles,visual-styles,component-catalog}.csv` | repository catalog, read by `vd.py` |
| `drift-fixture/` (4 Dart files + `pubspec.yaml`) | **hand-written synthetic fixture, not runnable**; `lib/theme/app_tokens.dart` mirrors the generated token values (updated by hand in the last two rounds: CTA outline `#FF0443` → `#972743`, reward `#F5A524` → `#FFC83D`) and `lib/screens/shop_screen.dart` plants three defects |
| `drift-fixture-fixed/` | copy of the above with `shop_screen.dart` corrected by hand |
| Page tables | shop and rewards: the accepted hand-written tables, re-applied to fresh skeletons; gameplay: **rewritten** for AD-1 |
| Device frames used in the board arithmetic | phone-s 375 × 667, phone-m 390 × 844, phone-l 430 × 932 with status bars 20 / 47 / 59 — from `visual_qa.py manifest` (Example C `screens-manifest.json`); bottom safe areas 0 / 34 / 34 are an **assumption** |

No image, no user data, no network.

## Commands executed (from the repository root, in order; final regeneration)

```bash
A=docs/examples/visual-design-pro-max/example-a-japanese-cute-animal-puzzle
# 1. discover
python3 .claude/skills/visual-direction/scripts/vd.py genres "onet animal puzzle"                       # (1)  exit 0 → logs/01-genres.txt
python3 .claude/skills/visual-direction/scripts/vd.py styles "japanese cute puzzle"                     # (2)  exit 0 → logs/02-styles.txt

# 2. profile — the brief's combined form
python3 .claude/skills/visual-direction/scripts/vd.py profile --genre onet-animal-puzzle --style japanese-cute-puzzle \
  --platform mobile-ios,mobile-android --stack flutter-flame --audience "casual-all-ages" --project "Onet Garden" \
  --out $A/style-profile.json                                                                             # (3)  exit 0 → logs/03-profile.txt

# 3. contract (init creates --output-dir)
python3 .claude/skills/visual-direction/scripts/vd.py init --profile $A/style-profile.json --output-dir $A/project --json   # (4)  exit 0 → logs/04-init.json

# 4. page overrides
DS=$A/project/design-system/onet-garden
python3 .claude/skills/visual-direction/scripts/vd.py page --dir $DS --name gameplay --reason "board tiles need a tighter radius than menu cards"   # (5)  exit 0
python3 .claude/skills/visual-direction/scripts/vd.py page --dir $DS --name shop     --reason "limited-time offer cards need a saturated promo accent and a countdown chip that the menu never shows"   # (6)  exit 0
python3 .claude/skills/visual-direction/scripts/vd.py page --dir $DS --name rewards  --reason "reward reveal uses the slow motion tier and a full-screen celebratory overlay instead of the standard popup"   # (7)  exit 0
python3 .claude/skills/visual-direction/scripts/vd.py validate --dir $DS                                   # (8)  exit 0 → logs/06-validate.txt

# 5. web CSS variables from the same tokens.json
node .claude/skills/design-system/scripts/generate-tokens.cjs --config $DS/tokens.json -o $A/project/tokens.css   # (9)  exit 0 (352 lines, 12,781 B)

# 6. page tables: re-test of the first round's rejected fill, then the accepted fill on --force skeletons
python3 .claude/skills/visual-direction/scripts/vd.py validate --dir $DS   # (10) exit 0, 2 warnings (deliberately non-ISO Expires) → logs/08-validate-first-fill-retest.txt
python3 .claude/skills/visual-direction/scripts/vd.py page --dir $DS --name gameplay --force --reason "board tiles need a tighter radius than menu cards"   # (11) exit 0
python3 .claude/skills/visual-direction/scripts/vd.py page --dir $DS --name shop     --force --reason "limited-time offer cards need a saturated promo accent and a countdown chip that the menu never shows"   # (12) exit 0
python3 .claude/skills/visual-direction/scripts/vd.py page --dir $DS --name rewards  --force --reason "reward reveal uses the slow motion tier and a full-screen celebratory overlay instead of the standard popup"   # (13) exit 0
python3 .claude/skills/visual-direction/scripts/vd.py validate --dir $DS                                   # (14) exit 0 → logs/09-validate-final.txt

# 7. drift demo
python3 .claude/skills/visual-audit/scripts/audit.py scan $A/drift-fixture       --contract $DS/tokens.json --format md --out $A/audit-before.md    # (15) exit 1 → logs/10-…
python3 .claude/skills/visual-audit/scripts/audit.py scan $A/drift-fixture       --contract $DS/tokens.json --json      --out $A/audit-before.json  # (16) exit 1
python3 .claude/skills/visual-audit/scripts/audit.py scan $A/drift-fixture-fixed --contract $DS/tokens.json --format md --out $A/audit-after.md     # (17) exit 0 → logs/11-…
python3 .claude/skills/visual-audit/scripts/audit.py scan $A/drift-fixture-fixed --contract $DS/tokens.json --json      --out $A/audit-after.json   # (18) exit 0
python3 .claude/skills/visual-audit/scripts/audit.py compare $A/audit-before.json $A/audit-after.json > $A/audit-compare.txt                        # (19) exit 0
```

Environment: macOS, Python 3.14.8, Node v26.10.0; plain `python3` / `node`, as a user would type them. **19 script runs** — the numbered list above (earlier READMEs said 21, a counting error QA reported as N-2). All exit 0 except (15) and (16): exit 1 means findings at/above `--fail-on high`, which is the point of a before-scan.

## Generated artifacts (committed next to this README)

| Path | Produced by | Size | Note |
|---|---|---|---|
| `style-profile.json` | `vd.py profile --genre --style` | 8,901 B | `vdp/1`; `product.genre`, two `sources`, `genre_profile`, `palette.seeds` + `palette.surfaces`; unmodified |
| `project/design-system/onet-garden/MASTER.md` | `vd.py init` | 9,445 B | resolved token summary, drift budget, QA, Unknowns |
| `project/design-system/onet-garden/tokens.json` | `vd.py init` | 34,837 B | primitive → semantic → component, `$extensions.vdp` |
| `project/design-system/onet-garden/component-catalog.md` | `vd.py init` | 52,692 B | complete; each component opens with "Tokens (authoritative)" |
| `project/design-system/onet-garden/{asset,interaction}-guidelines.md`, `visual-qa-checklist.md`, `CHANGELOG.md`, `pages/README.md`, `style-profile.json` | `vd.py init` (+ `page` entries in `CHANGELOG.md`) | < 4 KB each | `interaction-guidelines.md` includes the genre touch rules |
| `project/design-system/onet-garden/pages/{gameplay,shop,rewards}.md` | skeleton by `vd.py page`, tables **hand-filled** | ~2 KB each | validate exit 0 |
| `project/tokens.css` | `generate-tokens.cjs` | 12,781 B (352 lines) | CSS custom properties |
| `screens.md` | hand-written | — | seven screen specs citing token paths and catalog rules; board arithmetic table (AD-1); hit areas (AD-5) |
| `drift-fixture/`, `drift-fixture-fixed/` | hand-written | 5 files each | synthetic, non-runnable Dart |
| `audit-before.{md,json}`, `audit-after.{md,json}`, `audit-compare.txt` | `audit.py scan` / `compare` | 0.5–7 KB | unmodified |
| `logs/` | stdout/stderr of the commands above | — | numbered |

## Walkthrough — what an art director reads out of the artifacts

1. **Search results** (`logs/01-…`, `logs/02-…`). Genre `onet-animal-puzzle` (score 8.08; next 1.08), default styles `cute-animal-onet, japanese-cute-puzzle, kawaii-sticker, soft-2d-cartoon`; style search returns `japanese-cute-puzzle` first (family `cute-cartoon`, radius `xl`, shading `soft-cel`, motion `bouncy`).
2. **The profile** (`style-profile.json`). `product.genre onet-animal-puzzle`, confidence `high`, sources genre + catalog, seeds `brand #FF8FAB · secondary #7ED6C4 · accent #FFD23F · neutral #7F758A`, surfaces `background #FFF6E9 · surface #FFFFFF · text #4A3B5C`, shape `xl / rounded-blob / 3 px outline`, rendering `soft-cel / top-left-gloss / double-clay`, typography `Fredoka 700 / Nunito 500`, motion `bouncy 120/200/350 ms`, 11 anti-patterns (6 style + 5 genre), 6 QA criteria, **2 unknowns** — both colour walks the generator made and now discloses: "success: built-in status fill darkened from #138B3F to #107435 for contrast (5.88:1 …)" and "button.secondary.fg: primary-family label stepped from #FF8FAB to brand.700 (#BA4A66) to reach 4.5:1 on the secondary states".
3. **The resolved contract** (`MASTER.md`, `tokens.json`; contrast for component states computed from hex, the rest from the `MASTER.md` table).
   - Colour pairs: `primary #FF8FAB` / `#2E2A32` 6.54:1 · `accent #FFD23F` / `#2E2A32` 9.74:1 · `background #FFF6E9` with `text #4A3B5C` 9.47:1 · `textMuted #6B6274` 5.41:1 · `success #107435` / white 5.88:1 · `warning #F5A524` / `#2E2A32` 6.89:1 · **`reward #FFC83D` / `#2E2A32` 9.09:1** · `danger #BB1E1E` / white 6.33:1 · `border #FFDDAC` · **`borderInteractive #A88655`**.
   - CTA per state: default `#FF8FAB` + label `#2E2A32` 6.54:1 · hover `brand.400 #FBBECD` + `#2E2A32` 8.94:1 · pressed `brand.700 #BA4A66` + `fgPressed #FFFFFF` 4.93:1 · outline and hard shadow `brand.800 #972743` · `pressDuration 90ms`.
   - Secondary button: label and outline `brand.700 #BA4A66` (4.93:1 on white, 4.54:1 on its pressed fill `#FDF3F6`).
   - Outlines: panels (card, popup, HUD chip, progress) `semantic.color.border #FFDDAC`; interactive parts (tile, icon button) `semantic.color.borderInteractive #A88655` — 3.38:1 on white, 3.16:1 on the cream background; selected tile `brand.700 #BA4A66` (4.93:1 on white, 2.29:1 against the CTA fill).
   - Shadows: elevation `rgba(46, 42, 50, …)` (neutral.900 tint), component hard shadows `#56505E` / `#972743`; `grep "rgba(0, 0, 0"` on `tokens.json` returns 0.
   - Focus ring `semantic.state.focus.ringColor = #740420` (`brand.900`, width 3, offset 2): 11.01:1 on the background, 11.79:1 on white. Tappable HUD capsules use `component.hud.chipInteractive` (outline `#A88655`); decorative plates keep `component.hud.chip` (`#FFDDAC`).
   - Easing: `standard = cubic-bezier(0.22, 1, 0.36, 1)` (no overshoot) on progress/timer fills; `enter` keeps the bouncy overshoot for entrances.
   - Unchanged: radius picks `control 16 · container 24 · popup 32 · tile 12 · chip 9999`; outline 3; durations `120/200/350 (+600/750/2500)`; touch 48; per-page drift budget colour 0 · family 0 · radius 1 · spacing 2 · fontSize 2 · shadow 0 · duration 1.
   - `vd.py validate` (now also checking component-state contrast: error < 4.5:1, warning < 3:1 at boundaries): `OK — 0 error(s), 0 warning(s)` before and after the page fills (`logs/06-validate.txt`, `logs/09-validate-final.txt`).
4. **Board (AD-1).** `screens.md` §3 now lays the board out 6 across × 8 down, tile = `min(56, floor((W − 32 − 20) / 6))`: 53 on phone-s (board 338 × 452, pitch 57), 56 on phone-m and phone-l (356 × 476, pitch 60). Every vertical budget fits (608 ≤ 667, 693 ≤ 844, 705 ≤ 932). No density exception from `game-ui-patterns.md` §1.2 is needed. The profile's "grid ≥ 85 % of vertical space" holds on phone-s (88 %) and not on taller phones at 6 × 8 (76 % / 68 %); the spec says so and points at 6 × 10 levels (95 % / 85 %) as a level-design option. `pages/gameplay.md` keeps the tile radius override (12 → 8), now justified at real tile sizes: 12 is 21–23 % of the tile height (xl), the catalog wants one step tighter (lg 12–20 %) → 8 = 14–15 %. The HUD-without-shadow rule moved from an exception row to a token override (`component.hud.chip.shadow` → `primitive.shadow.none`).
5. **Touch targets (AD-5) and AD-10.** Spin-wheel segments (1.02:1 to each other) are separated by 3 `#A88655` dividers: 3.11:1 / 3.17:1 against the two fills. Completed level nodes use a `success.200 #CEF2DB` fill with a 3 `#107435` ring — ring vs map 5.49:1, number `#4A3B5C` on the fill 8.38:1 — instead of a full dark-green fill. Touch targets: Wallet/currency capsules and filter chips keep the 36 visual inside a 48 hit area; the large price tag (the buy control) is 48 high, not the catalog's 44; popup close buttons are `component.button.icon` 48, not the catalog's "close X 44dp"; small price tags appear only inside larger tappable parents. The cross-screen QA list in `screens.md` enumerates every tappable element and its hit size.
6. **Pages** (`pages/*.md`). `gameplay.md`: two overrides + board arithmetic note; `shop.md`: hero card radius 24 → 32, offer outline remapped to `accent.700 #CA9D0A`, countdown-chip exception to 2026-12-31; `rewards.md`: popup enter 200 → 750 ms, full-screen overlay exception (`never`). The first round's rejected colour remaps re-validate as `OK — 0 error(s), 2 warning(s)` (`logs/08-…`).
7. **Drift demo.** The fixture plants an off-palette purple `Color(0xFF8E24AA)` (×2), `BorderRadius.circular(13)` (×2) and `CtaButton`, a second `PrimaryButton`. The scan reports exactly those five: `VA-0001/0003 color.off-palette` high (nearest `component.button.primary.outlineColor #972743` at 35.2 — the scanner now accepts any value defined in `tokens.json`, so it names the component token; fix text "No close token … pick the semantic role"), `VA-0002/0004 radius.off-scale` high (nearest 12), `VA-0005 component.duplicate-implementation` medium; the clean files produce nothing. After the fix the scan is empty and `compare` reports `resolved: 5 new: 0 unchanged: 0 changed_severity: 0`.

## Verification level

| Claim | Level | Evidence |
|---|---|---|
| The 19 numbered commands ran with the exit codes listed | **EXECUTED** | `logs/*`, committed outputs |
| `style-profile.json`, `tokens.json`, `MASTER.md`, `component-catalog.md`, guidelines, checklist, `CHANGELOG.md`, `tokens.css`, `audit-*`, `audit-compare.txt` are unmodified script output | **EXECUTED** | byte-for-byte; nothing truncated |
| `pages/{gameplay,shop,rewards}.md` override tables, remaps, exceptions, board note | **HAND-WRITTEN** (skeleton by `vd.py page`) | validate exit 0 (`logs/09-…`) |
| `screens.md`, including the board arithmetic and hit-area rules | **HAND-WRITTEN** | token paths/values from `tokens.json`; arithmetic shown inline |
| Contrast ratios in `screens.md` and this README that are not in the `MASTER.md` table (11.01, 11.79, 5.49, 8.94, 4.93, 4.54, 3.38, 3.16, 4.60, 2.29, 1.46, 3.64, 1.59, 1.32, 1.07, 1.44, 1.55, 3.11, 3.17, 5.49, 8.38, 1.13, 1.09, 1.02) | **HAND-COMPUTED** with the WCAG relative-luminance formula from hex values | not measured on a render; `vd.py validate` independently checks component-state pairs and reports 0 errors / 0 warnings |
| Bottom safe areas 0 / 34 / 34 | **ASSUMPTION** | not in the contract or the manifest |
| `drift-fixture/`, `drift-fixture-fixed/` | **HAND-WRITTEN synthetic** | never compiled; `pubspec.yaml` only for platform detection |
| Any screenshot, device run, Flutter build, measured contrast, pressed-state timing, board fit on a real device | **NOT RUN** | nothing was built or rendered |
| The genre/style search ranking is "correct" | not verifiable here | BM25 scores printed; relevance is a judgement |

### Limitations

- No Flutter/Flame project exists; every `screens.md` value is a specification, not a measurement.
- `MASTER.md` and `CHANGELOG.md` carry timestamps; `style-profile.json` / `tokens.json` are deterministic.
- The duplicate-component rule only recognises names like `(Primary|Main|Cta|Secondary|Action|Icon|Big|Small)?Button…` (and `*Popup/Dialog/Card/…`).
- The fixture's `app_tokens.dart` mirror is maintained by hand and changed again (`#FF0443` → `#972743`, reward → `#FFC83D`); in a real project it must be generated from `tokens.json`.

### Status — QA pass 2 art-direction items (`docs/architecture/QA_REPORT.md` §5) and count errors

| # | QA item | Status | Evidence (final run) |
|---|---|---|---|
| AD-1 | 8 × 6 board "398 wide" does not fit 390 | **FIXED** (example content) | `screens.md` §3: portrait 6 × 8, tile 53 / 56, board 338 / 356 wide, pitch 57 / 60 ≥ 48, vertical budgets shown; no density exception needed; 85 % share met on phone-s only, documented |
| AD-2 | three outline colours on white objects | **FIXED** (generator, refined) | panels `#FFDDAC`; interactive parts `semantic.color.borderInteractive #A88655` (≥ 3:1); secondary button `#BA4A66`; primary CTA `#972743` — four outline colours, each with one documented job |
| AD-3 | pressed = outline = shadow, neon pressed | **FIXED** (generator) | hover `#FBBECD`, pressed `#BA4A66`, outline/shadow `#972743` (pressed vs outline 1.59:1); pressed label `#FFFFFF` 4.93:1 |
| AD-4 | overshoot easing on progress fills | **FIXED** (generator) | `primitive.easing.standard = cubic-bezier(0.22, 1, 0.36, 1)`; `component.progress.fillEasing = {primitive.easing.standard}` |
| AD-5 | 36 wallet chip / 44 price tag tappable | **FIXED** (example content) | `screens.md` §1, §2, §4, §5, §7 and the cross-screen QA list: 48 hit areas, price tag 48. **STILL PRESENT in the generated catalog text**: `component-catalog.md` line 465 still says "close X 44dp" — the specs override it explicitly |
| AD-6 | press timing 100 ms vs `fast` 120 ms | **FIXED** (generator) | `component.button.{primary,secondary,icon}.pressDuration = 90ms` ≤ 100 ms; `screens.md` uses it for every press |
| AD-7 | one gold for reward, warning and hint | **FIXED at token level, residual noted** | `semantic.color.reward = #FFC83D` (`onReward` 9.09:1) is now separate from `semantic.color.warning = #F5A524`. Residual: the two golds are only 1.32:1 apart (H 43° vs 37°) and reward vs accent `#FFD23F` is 1.07:1, so the specs add non-colour cues (hand glyph on hints, outlines on stars) rather than relying on hue |
| AD-8 | selection = CTA colour, `bgSelected` 1.09:1 | **FIXED** (generator) | `component.tile.outlineColorSelected = brand.700 #BA4A66`: 4.93:1 on the white tile, 4.60:1 on the cream board, 2.29:1 against the CTA fill. Against the idle outline `#A88655` it is 1.46:1, so the spec pairs it with the 3 → 4 width and the scale-up; `bgSelected` stays 1.09:1 (decorative) |
| AD-9 | two shadow languages | **FIXED** (generator) | elevation shadows `rgba(46, 42, 50, …)` (neutral.900 tint); component hard shadows `#56505E` / `#972743`; 0 occurrences of `rgba(0, 0, 0` in `tokens.json` |
| AD-10 | spin-wheel segments 1.02:1; dark success on the map | **FIXED** (example content) | `screens.md` §7: 3 `borderInteractive #A88655` dividers, 3.11:1 / 3.17:1 against the segment fills; §2: completed node = `success.200 #CEF2DB` fill + 3 `#107435` ring (5.49:1 vs `#FFF6E9`) + number `#4A3B5C` (8.38:1) + check glyph |
| N-2 | README "21 script runs" vs 19 listed | **FIXED** | commands numbered (1)–(19); this README and the index say 19 |
| QA leftover | wallet capsule wears the decorative panel border | **FIXED** (generator + example content) | `component.hud.chipInteractive.outlineColor = semantic.color.borderInteractive #A88655` (3.38:1 on white); `screens.md` §1 and §5 use it for the currency capsule and the wallet |
| QA leftover | focus ring `#FBBECD` too close to the fills | **FIXED** (generator) | `semantic.color.focusRing = #740420` (`brand.900`): 11.01:1 vs background, 11.79:1 vs surface; `vd.py validate` now checks focus rings (0 warnings) |

### Status — earlier script observations

| # | Earlier observation | Status | Evidence (final run) |
|---|---|---|---|
| A-1 | `--style` + `--genre` mutually exclusive | **FIXED** | combined command exit 0; `product.genre: onet-animal-puzzle`, `genre_profile` |
| A-2 | `init` exit 2 when `--output-dir` missing | **FIXED** | `init` created `project/` |
| A-3 | `component-catalog.md` 76 KB | **FIXED** | 52,530 B, complete |
| A-4 | catalog prose vs tokens (pill vs 16, 2 px vs 3 px, 28 vs 32) | **STILL PRESENT, documented** | prose unchanged; catalog header says the token wins |
| A-5 | token→token colour remap counted as drift | **FIXED** | `logs/08-validate-first-fill-retest.txt`: `OK — 0 error(s), 2 warning(s)` |
| A-6 | no hint that `Expires` must be ISO or `never` | **FIXED** | skeleton comment |
| A-7 | `scan --out` echoed the full report | **FIXED** | one-line stdout (`logs/10-…`, `logs/11-…`) |
| A-8 | page suggestion from the source stem | **FIXED** | fix text says `pages/shop.md` |
| A-9 | "nearest token" fix text at large distances | **FIXED** | "No close token (nearest primitive.color.brand.800 #972743 is 35.2 away) — pick the semantic role …" |
| A-10 | grey border seed, black `onSuccess` | **FIXED** | `border #FFDDAC`; `onSuccess #FFFFFF` |
| A-11 | catalog route ignored seed background/text, darkened accent | **FIXED** | `#FFF6E9`, `#4A3B5C`, accent `#FFD23F` |
| A-12 | `onWarning/onReward` 4.97:1 | **FIXED** | `#2E2A32` on `#F5A524` 6.89:1 |
| A-13 | fill walks listed in `unknowns` | **confirmed** | 2 entries: success `#138B3F` → `#107435` (5.88:1); secondary label `#FF8FAB` → `#BA4A66` |
| A-14 | pressed CTA label `#2E2A32` on `#BA4A66` = 2.85:1 | **FIXED** (generator) | `component.button.primary.fgPressed = #FFFFFF` → 4.93:1; `vd.py validate` now checks it (0 errors) |
| A-15 | secondary label `#FF8FAB` on white = 2.15:1 | **FIXED** (generator) | `component.button.secondary.fg = #BA4A66` → 4.93:1 on white, 4.54:1 on the pressed fill; walk disclosed in `MASTER.md` → Unknowns |
| A-16 | tile outline `#FFDDAC` 1.30:1 / 1.21:1 | **FIXED** (generator) | `component.tile.outlineColor = semantic.color.borderInteractive #A88655` → 3.38:1 on the white tile, 3.16:1 on the cream board |
