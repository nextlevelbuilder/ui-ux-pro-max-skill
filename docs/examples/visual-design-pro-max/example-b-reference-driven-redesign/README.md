# Example B — Reference-driven redesign (route C) with a ground-truth check

The `reference-analysis` → `visual-direction` hand-off end to end for **Pet Diary Redesign** (Flutter, iOS + Android): one reference image → graded `reference-analysis.json` → `vd.py profile --reference` → `vd.py init` → page overrides → screen specs. The twist: the "reference" is a render of a file this repository owns, so every image-derived claim can be checked against the real CSS. That check is the deliverable.

> **Provenance of the reference image — read this first.** `inputs/xiaomaomi-390x844.png` is a Playwright render of the repository's own `preview/xiaomaomi-app.html` at 390 × 844, made by the Principal agent for this example. It is **repository-owned (MIT), not a user-provided reference**, and it is the one artifact in these examples allowed over 60 KB (77,413 bytes). Nothing about it should be read as "a user asked us to copy this app".

> **Final regeneration.** All script outputs here were regenerated from scratch after every fix round was merged (including the last generator rounds: focus ring on a distinct brand step, `hud.chipInteractive`, per-state button labels, `borderInteractive`, `pressDuration` 90 ms, reward split from warning, tinted shadows, and component-state contrast checks in `vd.py validate`), using only the inputs already committed in `inputs/` (unchanged since the first round). `ground-truth-check.md` shows all three rounds side by side; the script observations at the end carry FIXED / STILL PRESENT / NEW status.

## Purpose

1. Exercise route C exactly as a user would (validate → summary → profile → init → page → validate).
2. Grade the analysis against ground truth: which `observed / high / assumption / not-derivable` claims held up (`ground-truth-check.md`).
3. Show what a derived contract looks like when the image analysis is good but imperfect, and where the remaining fixes belong (profile vs page).

## Inputs (and their provenance)

| Input | Provenance |
|---|---|
| `inputs/xiaomaomi-390x844.png` (77 KB) | Playwright render of `preview/xiaomaomi-app.html` (repository file, MIT) — see the note above |
| `inputs/reference-analysis.json` (9.7 KB) | written by the Principal agent after viewing the image with the model's image reader (`viewed_by: model-vision`); schema `vdp-reference-analysis/1`; validated by W2-B; unchanged across rounds |
| `inputs/palette-extracted.json` (560 B) | output of `reference_analysis.py extract-colors` (76 × 200 downsample, k = 10, 3 colours kept, confidence `assumption`), produced by the Principal before this example; copied as evidence, not re-run |
| `preview/xiaomaomi-app.html` lines 13–31 and the rules cited in `ground-truth-check.md` | repository file, read with `sed`/`grep` |
| Flags `--platform mobile-ios,mobile-android --stack flutter --project "Pet Diary Redesign"` | this example's brief |
| Page tables | the accepted hand-written tables from the previous round, re-applied to freshly generated skeletons |

## Commands executed (from the repository root, in order; final regeneration)

```bash
EX=docs/examples/visual-design-pro-max/example-b-reference-driven-redesign

python3 .claude/skills/reference-analysis/scripts/reference_analysis.py validate $EX/inputs/reference-analysis.json          # exit 0, 3 warnings → logs/01-validate.txt
python3 .claude/skills/reference-analysis/scripts/reference_analysis.py validate $EX/inputs/reference-analysis.json --json   # exit 0 → logs/01b-validate.json
python3 .claude/skills/reference-analysis/scripts/reference_analysis.py summary  $EX/inputs/reference-analysis.json          # exit 0 → logs/02-summary.txt

python3 .claude/skills/visual-direction/scripts/vd.py profile --reference $EX/inputs/reference-analysis.json \
  --platform mobile-ios,mobile-android --stack flutter --project "Pet Diary Redesign" --out $EX/style-profile.json           # exit 0 → logs/03-profile.txt
python3 .claude/skills/visual-direction/scripts/vd.py init --profile $EX/style-profile.json --output-dir $EX/project --json   # exit 0 → logs/04-init.json

DS=$EX/project/design-system/pet-diary-redesign
python3 .claude/skills/visual-direction/scripts/vd.py page --dir $DS --name home    --reason "quick-action tiles use the two secondary tints (blue, mint) that the global palette rule reserves for category tiles only (reference rule-8, context:home)"   # exit 0
python3 .claude/skills/visual-direction/scripts/vd.py page --dir $DS --name diary   --reason "the log is a dense chronological list: rows drop the card elevation and use a 1 px border divider so eight entries fit above the fold"                      # exit 0
python3 .claude/skills/visual-direction/scripts/vd.py page --dir $DS --name profile --reason "settings rows are grouped lists: the destructive sign-out row uses semantic.color.danger instead of the brand orange that carries every other emphasis"   # exit 0
python3 .claude/skills/visual-direction/scripts/vd.py validate --dir $DS                                                      # exit 0 → logs/06-validate.txt

# page tables filled by hand, then:
python3 .claude/skills/visual-direction/scripts/vd.py validate --dir $DS                                                      # exit 0 → logs/07-validate-final.txt
```

10 script runs, all exit 0. Ground-truth facts were read with `sed -n 13,31p preview/xiaomaomi-app.html` and `grep -n "box-shadow\|font-family\|border-radius\|border: \|gradient\|var(--accent)" preview/xiaomaomi-app.html` (read-only).

## Generated artifacts (committed next to this README)

| Path | Produced by | Size | Note |
|---|---|---|---|
| `inputs/*` | copied inputs | 77 KB + 9.7 KB + 0.6 KB | unchanged |
| `style-profile.json` | `vd.py profile --reference` | 8,663 B | **unmodified** script output |
| `project/design-system/pet-diary-redesign/{MASTER.md, tokens.json, component-catalog.md, asset-guidelines.md, interaction-guidelines.md, visual-qa-checklist.md, CHANGELOG.md, pages/README.md, style-profile.json}` | `vd.py init` | 10,133 / 34,453 / 22,707 B, rest < 3 KB | unmodified; all under 60 KB |
| `project/design-system/pet-diary-redesign/pages/{home,diary,profile}.md` | skeleton `vd.py page`, tables **hand-filled** | ~2 KB each | validate exit 0 |
| `ground-truth-check.md` | hand-written | — | observation verdicts, palette discrepancy, contract consequences with **Derived (final) / Second round / First round** columns |
| `screens.md` | hand-written | — | home / diary / profile under the final contract, one exception each |
| `logs/` | stdout/stderr of each command | — | numbered |

## Walkthrough — what an art director reads out of the artifacts

1. **`validate` and `summary`**. Status OK; 1 reference owning `color, shapes, buttons, icons, typography, layout` (unowned: `characters, hud, popup, motion`); 15 observations (`observed 7, high 5, assumption 1, not-derivable 2`); 8 rules, all `high`; 0 conflicts; 7 `not_derivable`. Warnings: `W-TARGET` (rule-7 target `nav`), `R-PAL-3` (`#FFF7ED` vs `#FFFFFF`, distance 19.7), `W-ND-STD`. Nothing blocks the hand-off.
2. **The profile** (`style-profile.json`). `product.kind app`, `style.id reference-derived-custom`, `confidence high`, roles kept in `sources[0]`. `palette.surfaces {background #FFF7ED, surface #FFFFFF, outline #FED7AA, text #9A3412}` straight from `palette_observed`; seeds `brand #F97316 · secondary #BFDBFE · accent #B24C05 · neutral #8A7A75` (accent = brand.700, flagged in `unknowns`); shape `xl / pill silhouette / 2 px lighter-tint-of-fill`; **typography split per obs-7: display `"bold rounded geometric sans"`, body `"humanist sans"`** (CC-4 classifications, both correct for Fredoka / Nunito); rendering `soft / none / none`; motion `soft 150/250/400`; anti-patterns: the 5 generic reference-workflow entries only (rule fragments dropped); one generated exception (home tiles, rule-8); twelve `unknowns`: ten from the analysis plus two disclosed colour walks — success "darkened from #138B3F to #107435 for contrast (5.88:1 …)" and "button.secondary.fg: primary-family label stepped from #F97316 to brand.700 (#B24C05) to reach 4.5:1".
3. **The contract** (`MASTER.md`, `tokens.json`). `primary #F97316` on `#322C2A` (4.90:1); `background #FFF7ED`, `text #9A3412` (6.88:1), `border #FED7AA` — all exact; `textMuted #746662` (5.18:1); `accent #B24C05` on white (5.34:1); `success #107435` on white (5.88:1), `danger #BB1E1E` (6.33:1), **`warning #F5A524` (6.73:1) and a separate `reward #FFC83D` (8.88:1)**, both with `#322C2A` text. CTA per state: hover `brand.400 #F3AB79` + `#322C2A` (7.14:1), pressed `#B24C05` + `fgPressed #FFFFFF` (5.34:1, B-11 fixed), `pressDuration 90ms`. Secondary button: label `brand.700 #B24C05` (5.34:1 on white, B-12 fixed), outline `semantic.color.borderInteractive #AC8558`. Tiles also use `#AC8558` (3.36:1 on white, 3.16:1 on the cream); cards, chips and progress keep the observed peach `#FED7AA`; the primary button outline stays `brand.200 #F8E4D6`. Radius picks `control 16 · container 24 · popup 32 · tile 12 · chip 9999`; outline `2`; all shadows `none` (consequence of the misgraded obs-6, correct given the input). Focus ring `#DD5E06` (`brand.600`): 3.48:1 on the background, 3.70:1 on white — above the 3:1 floor, though only 1.32:1 against the orange CTA fill (the 2 px offset puts the ring over the background). Tappable chips use `component.hud.chipInteractive` (outline 1 `#AC8558`). `vd.py validate` (now checking component-state contrast and focus rings): `OK — 0 error(s), 0 warning(s)`. What remains for the user is the `not-derivable` list (font names, shadows, motion base 200 ms, states) plus the placeholder accent.
4. **Ground truth** (`ground-truth-check.md`). Observation verdicts are input-bound and unchanged (5 confirmed, 6 partially, 2 wrong, 2 correct `not-derivable`). The consequences table has **10 of 16** rows exact or correct (first round: 2–3) — the earlier "8 of 15" in this README was a counting error (QA N-3).
5. **Pages** (`pages/*.md`, `screens.md`). Each screen keeps one functional exception: home keeps the blue/mint icon tiles (rule-8), diary flattens rows into a divider list, profile remaps destructive actions to `button.destructive` and uses 44-high rows. The accepted tables validate clean on the first try.

## Verification level

| Claim | Level | Evidence |
|---|---|---|
| `reference_analysis.py validate` ×2 and `summary`, `vd.py profile`, `init`, `page` ×3, `validate` ×2 — 10 runs, all exit 0 | **EXECUTED** | `logs/*`, committed outputs |
| `style-profile.json` and every file `vd.py init` wrote are unmodified | **EXECUTED** | byte-for-byte |
| `inputs/reference-analysis.json` was produced by viewing the image with the model's image reader | **as stated by the Principal agent**; this example only validated it (exit 0) | `viewed_by: model-vision` |
| `inputs/palette-extracted.json` is `extract-colors` output | **EXECUTED earlier by the Principal**, copied; **NOT re-run** | file header `status: OK` |
| Ground-truth facts (variables, radii, shadows, fonts, gradients, nav) | **HAND-WRITTEN from reading the CSS** (`sed`/`grep`) | line numbers in `ground-truth-check.md` |
| Contrast figures for `#64748B` (≈ 4.5:1 / 4.8:1) | **HAND-COMPUTED** from hex | not measured on a render |
| `pages/*.md` tables, `screens.md`, `ground-truth-check.md` | **HAND-WRITTEN** | validate exit 0 for the pages |
| Any rendering of the redesign, device screenshot, Flutter build, visual diff | **NOT RUN** | no app exists |
| That the PNG matches the HTML pixel-perfectly | **NOT RUN** (not re-rendered) | the PNG is taken as given |

### Limitations

- Single reference, single screen type (`home`): `characters, hud, popup, motion` roles are unowned; diary and profile are extrapolated by hand from the app catalog.
- The derived contract is committed as generated. Remaining mismatches are graded unknowns (fonts, shadows, motion, accent), analysis-side choices (secondary tint as seed); a real project would answer them in `style-profile.json` and re-run `vd.py init --force`.
- `provenance.owner` says `user` (schema enum) while the note says the repository owns the file; the enum has no `repository` value.
- `MASTER.md` carries a timestamp; everything else is deterministic.

### Script observations — status after the final regeneration

| # | Earlier observation | Status | Evidence (final run) |
|---|---|---|---|
| B-1 | px radius ladder → `radius_class: pill`, `control = 9999` | **FIXED** | `shape.radius_class: "xl"`, `silhouette: "pill"`; `semantic.radius.control` → 16 |
| B-2 | unknown family → literal `"display"`; then one classification for both roles | **FIXED** | `typography.display: "bold rounded geometric sans"`, `typography.body: "humanist sans"`; `primitive.fontFamily.*` match; `unknowns[0]` names the display classification |
| B-3 | "light tint of brand" → `contrast-dark` / `neutral.900`; later two peaches | **FIXED** | `lighter-tint-of-fill` → `fill.200`; non-interactive panels use the observed peach `#FED7AA`; interactive outlines (tile, secondary button) use `semantic.color.borderInteractive #AC8558` (≥ 3:1); the primary button keeps `brand.200 #F8E4D6` |
| B-4 | observed background/text/border replaced by neutral greys | **FIXED** | `palette.surfaces` → `semantic.color.background/text/border` = `#FFF7ED / #9A3412 / #FED7AA` |
| B-5 | accent `#F59E0B` from nowhere | **FIXED** | `#B24C05` = `brand.700` (the darker steps were re-derived this round), with an `unknowns` entry asking to confirm or seed |
| B-6 | rule texts as anti-patterns; then a clipped fragment | **FIXED** | `anti_patterns` holds 5 generic entries only. Side effect (minor): no product-specific anti-pattern remains (rule-3's "never grey/black outlines" is not restated) |
| B-7 | `style.confidence: high` counted, not weighed | **STILL PRESENT** | `style.confidence: "high"` |
| B-8 | page budget counted token→token remaps; no `Expires` hint | **FIXED** | skeleton notes; validate exit 0 on first fill |
| B-9 | no `palette_observed` vs `extract-colors` cross-check | **STILL PRESENT** | `validate` output unchanged (3 warnings, none about the 42 % / 71 % inversion) |
| B-10 | unseeded `warning`/`reward` stepped darker for white text → `#8F5800` (brown), not in `unknowns` (intermediate round) | **FIXED** | `semantic.color.warning = #F5A524` (6.73:1 with `#322C2A`); reward is now its own gold `#FFC83D` (8.88:1) |
| B-11 | pressed CTA label `#322C2A` on `#B24C05` = 2.57:1 | **FIXED** (generator) | `component.button.primary.fgPressed = #FFFFFF` → 5.34:1; checked by `vd.py validate` (0 errors) |
| B-12 | secondary label `#F97316` on white = 2.80:1 | **FIXED** (generator) | `component.button.secondary.fg = brand.700 #B24C05` → 5.34:1; walk disclosed in `unknowns` |
| QA leftover | focus ring `#F3AB79` (light peach) | **FIXED** (generator) | `semantic.color.focusRing = #DD5E06`: 3.48:1 vs background, 3.70:1 vs surface; residual: 1.32:1 against the primary fill, mitigated by the 2 px ring offset |
| — | `product.kind` / roles kept on the reference route | **confirmed** | `product.kind: "app"`, `sources[0].roles` = the six owned roles |
