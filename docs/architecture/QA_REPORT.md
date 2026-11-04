# Independent QA Report: Visual Design Pro Max (W2-F, pass 2)

Author: W2-F (Agent 9, Testing & Visual QA). Read-only on the repository except this file. Pass 1 (2026-10-15) covered the three skills and the docs. Pass 2 (2026-10-16) re-checks every pass-1 finding after the fix rounds, re-runs the gates, samples real code, regenerates the three examples, and reviews the Example A contract as an art director.

Scratch evidence lives in `scratchpad/w2f2/` (replay rows `replay/rows.tsv`, per-command stdout and stderr in `replay/out/<ID>.{out,err}`, gate logs `logs/gate/`, regenerated examples `ex/{a,b,c}/`, real-code samples `real/`). That directory can be wiped by a session reset, so every row below carries its own command and result line and can be re-run without it.

## 0. Environment

```
repo   /Volumes/DATA/PROJECTS/ai-developer/ui-ux-master/ui-ux-pro-max-skill · branch feat/visual-design-pro-max · HEAD 56ea9cf (all work uncommitted)
git status --porcelain | wc -l : 18 at start and at end of pass 2 (this file sits in the already-untracked docs/architecture/, so it adds no line; no other repo file was written)
Python 3.14.8 · pytest 8.4.2 · Pillow 11.3.0 · node v26.10.0 · Flutter 3.47.7 (/Users/f12/Tools/flutter/bin/flutter)
Darwin 27.0.0 · GNU grep absent → CI greps run with a perl PCRE replica (positive control below)
```

## 1. Gate table

The wave-1 `local-gate.sh` was lost in the reset. I rebuilt the same gates in `scratchpad/w2f2/gate.sh` (pytest runs use `-p no:cacheprovider` and `PYTHONDONTWRITEBYTECODE=1`, so the gates write nothing into the repo).

| Gate | Command | Status | Evidence |
|---|---|---|---|
| pytest visual-direction | `python3 -m pytest .claude/skills/visual-direction -q` | PASS | `173 passed in 11.70s` |
| pytest reference-analysis | `python3 -m pytest .claude/skills/reference-analysis -q` | PASS | `104 passed in 5.25s` |
| pytest visual-audit | `python3 -m pytest .claude/skills/visual-audit -q` | PASS | `171 passed, 1 skipped`. The skip is `test_audit.py:911: set VISUAL_AUDIT_FLUTTER_PROBE to a flutter create app`; §3 covers that check by hand |
| pytest all (CI `tests.yml`) | `python3 -m pytest .claude/skills -q` | PASS | `748 passed, 1 skipped in 38.98s` (300 baseline + 448 new) |
| unittest core | `python3 -m unittest discover -s src/ui-ux-pro-max/scripts/tests` | PASS | `Ran 164 tests … OK` |
| path contract | `… -p test_skill_script_paths.py` | PASS | `OK` |
| asset sync | `node cli/scripts/sync-assets.mjs --check` | PASS | `Assets are in sync.` |
| agent guide | `python3 scripts/validate-agent-guide.py` | PASS | `23 platforms and 3 locked examples checked.` |
| CI grep: install paths (`check-asset-sync.yml` lines 76–88) | perl replica of the three patterns + the `CLAUDE_PLUGIN_ROOT` allowlist | PASS | `OK grep-paths (perl)`. Positive control: a planted `~/.claude/skills/foo/…` line gives exit 1 with a hit |
| CI grep: bundled skills (lines 125–152) | perl replica: `/ck:`, claudekit names, and the `` `name` skill`` lookahead against the `.claude/skills/*` set | PASS | `165 skill-name hits checked … OK`. Positive control: planted `/ck:plan`, `` `chrome-devtools` skill`` and `` `ghost-skill` skill`` are all reported, exit 1 |
| three skills shipped + mirrors | `.claude/skills/<s>` and `cli/assets/skills/<s>` exist, `subSkills` lists them, `diff -r` is clean | PASS | `OK 3 skills shipped + mirrors identical` |
| Python 3.8 syntax | `ast.parse(…, feature_version=(3,8))` on every new `.py` | PASS | all files parse |
| CLI install listing | `node cli/dist/index.js init --ai claude --dry-run` (run in an empty scratch dir) | PASS | `Would copy 9 sub-skills (… reference-analysis … visual-audit, visual-direction)`. Exit 0, nothing written |
| `--help` / no-argument behaviour | all 5 scripts × every subcommand | PASS | every `--help` exits 0; no arguments exits 2 with usage and no traceback |
| `npm --prefix cli run verify:data`, CLI e2e | NOT RUN by W2-F | NOT RUN | Principal reports verify:data exit 0 and e2e 40/41. The failed e2e test is `preview.spec.ts › xiaomaomi-app.html renders without console errors` (missing Playwright browser binary = BLOCKED, per `scratchpad/cli-e2e-2.log`) |

Tracebacks: **0** across the 82 logged replay rows (`rows.tsv`), the ~45 example-regeneration commands and the ~30 help/no-argument probes.

## 2. Pass-1 findings: re-verification

Each finding was re-run with its original command (inputs rebuilt in scratch).

| ID | Pass-1 sev | Original command (abridged) | Status | Evidence (pass 2) |
|---|---|---|---|---|
| F-01 | High | from an empty cwd: `audit.py scan <fx> --contract … --out qa-logs/findings.json --md qa-logs/findings.md`; `visual_qa.py checklist … --out qa-logs/checklist-shop.md`; `visual_qa.py manifest … --out qa-logs/screens.json`; `visual_qa.py diff a b --out qa-logs/x.diff.png --json`; `reference_analysis.py extract-colors … --out qa-logs/p.json` | **FIXED** | All five create `qa-logs/` and write the file (exit codes 1/0/0/1/0 as designed, no traceback). `template --out qa-logs/deep/t.json` and `to-profile --out qa-logs/deep2/p.json` also create parents. An unwritable parent (a file in the path) gives exit 2 with one `error: FileExistsError …` line |
| F-02 | High (doc) | `vd.py profile --style japanese-cute-puzzle --genre match-3 --platform web --out sg.json` vs the docs' "mutually exclusive" sentence | **FIXED** | exit 0. `docs/VISUAL_DESIGN_PRO_MAX.md:184` now says "`--style`, `--genre` and `--reference` combine freely"; the false sentence is gone |
| F-03 | Medium | `to-profile <two-refs> --out frag.json` → `vd.py profile --reference frag.json …` vs `vd.py profile --reference <two-refs> …` | **FIXED** (residual Info) | Both routes now give the same `palette.surfaces` (`#C9F2DF / #FFF6E3 / #4A2E22`), seeds, principles and illustration. Only the `unknowns` list differs: the fragment route lists 4 more entries ("product.kind 'game' inferred …", "palette.seeds are role guesses …"). That is more conservative, which is acceptable |
| F-04 | Medium | `audit.py scan <xiaomaomi web dir> --json` | **FIXED** | The `.icon-btn svg {22×22}` finding is gone. Inventory mode: 0 touch findings, `{'critical': 0}`. Contract mode: one touch finding, `.icon-btn { width: 44; height: 44 }` at **medium** (44 < 48). `severity.md:37`: "medium, always (heuristic cap, CC-10h)" |
| F-05 | Medium | `audit.py scan <stock flutter create app> --json` | **FIXED** | `platform flutter {'flutter': 2} scanned 2 skipped 8`, with the note "flutter scaffold folders skipped (platform glue, not UI): android, ios, linux, macos, web, windows; pass --platform native to scan them". `--platform native` scans 7 files and labels the run experimental, as CC-14 says |
| F-06 | Medium (contract) | `audit.py scan <fx> --contract <fx>/tokens.json --format md` (337 ms vs 350) | **FIXED** (contract) | CC-13 withdraws CC-8's ±10 % band, and `drift-rules.md:15` now states the exact rule. The CC-8 bullet still contains the original "tolerates ±10 %" text. It is superseded by CC-13, but a reader of CC-8 alone is misled (Info) |
| F-07 | Low | append a line to tool-owned MASTER.md, then `vd.py init … --force` | **STILL PRESENT** | `HUMAN EDIT kept: 0`. Neither `init --help`, SKILL.md nor the docs warn that hand edits to a tool-owned `MASTER.md` are lost under `--force` |
| F-08 | Low | `vd.py profile --style … --platform web,web,mobile-ios` | **FIXED** | `['web', 'mobile-ios']` |
| F-09 | Low | `visual_qa.py checklist --profile p.json --screen cobol` | **FIXED** | exit 2, `error: unknown screen 'cobol'; valid ids: home, gameplay, …`; documented in visual-audit SKILL.md:34 and :50 |
| F-10 | Low | `--help` vs SKILL tables | **PARTIAL** | Fixed: the literal `%%` is gone; `--max-files` has help text; `to-profile --out` is shown as optional. Still undocumented in SKILL tables: `audit.py scan --max-files`, `vd.py profile --json`, `vd.py page --json`, `visual_qa.py checklist --json`, and the `extract-colors --colors/--ref` aliases |
| F-11 | Low | `audit.py scan <csv-only dir>`; second `vd.py init` | **FIXED** | The exit table now reads "invalid `--platform` or `--fail-on` value (an undetectable platform exits 0 with a warning)". The coexistence table says `kept and reported on stdout as MASTER.md: kept-tool-owned`, and the CHANGELOG wording matches (`- master: created`) |
| F-12 | Low | `vd_tokens.py --profile kawaii.json --seeds seeds.json` | **PARTIAL** | The docs (`VISUAL_DESIGN_PRO_MAX.md:117`) now say `--seeds` only fills slots the profile leaves empty. `vd_tokens.py --help` still says just "optional JSON object {…}", and the run still gives `brand.500 = #FF9FCB` (the profile seed wins) |
| F-13 | Low | component-catalog.csv id check | **STILL PRESENT** | 55 rows; `tooltip` and `toast` still have no `group.` prefix |
| F-14 | Low | visual-audit SKILL hand-off row for `validate-tokens.cjs` | **FIXED** | SKILL.md:66 and docs :137 now say it does not read `.html` and lists the extensions it does read |
| F-15 | Low | grep of the 17 semantic colours in `references/platforms/*.md` | **STILL PRESENT** | flutter-flame.md lacks `onSecondary, accent, onAccent, background, textMuted`; unity.md lacks `onPrimary, onSecondary, accent, onAccent, surface, textMuted`. All 13 primitive groups are present in all four files |
| F-16 | Low | `validate` on a profile with `shape.outline.width: -3` | **STILL PRESENT** | exit 0 (only stale-hash warnings) |
| F-17 | Info | inventory-mode rule ids | **PARTIAL** | The docs (`:80`) are correct now. visual-audit SKILL.md:58 still says "(+ `shadow.unlisted`, `<category>.variant-explosion` in inventory mode)". Inventory mode emits no `shadow.unlisted` (6 rule ids on the fixture, none of them `shadow.unlisted`); that rule needs a contract |

Summary: both pass-1 Highs and all five Mediums are fixed. Of the Lows, 6 are fixed, 4 are still present and 3 are partial (counting F-17).

Pass-1 negative cases re-checked, no regressions: unknown style id (typo) → exit 1 with closest ids; `--platform watch` → exit 2; not-JSON profile → 1; missing profile → 2; second `init` → MASTER.md hash unchanged; foreign MASTER.md → kept, `MASTER.visual-direction.md` written; page copying the master → 1; two owners of a role → 1 `R-ROLE-1`; merge id collision → 1, no output file; empty dir scan → 0 with warning; `--platform cobol` → 2; diff on README.md → 3 `BLOCKED: unreadable image`; manifest `--stack cobol` → 2. With a poisoned PIL on PYTHONPATH, `extract-colors` exits 3 with `BLOCKED: Pillow (PIL) is not installed (pip install Pillow); palette extraction unavailable`, and `diff --json` exits 3 with `"status": "BLOCKED"`.

Smoke replay: the core SKILL.md commands (20 per working directory, 40 runs) were run with cwd = the skill dir and with cwd = repo root. Exit codes match the docs: 1 for `validate --strict` with an open conflict, a contract scan with findings, and a 17 % pixel diff; 0 for everything else, inventory scan included. The written profiles and tokens are byte-identical across the two working directories.

## 3. Real-code samples

### 3a. Fresh Flutter app

`flutter create --offline --project-name qa_onet qa_onet` exited 0. I then added one realistic screen, `lib/screens/shop_screen.dart`, with a written ground truth: 11 planted off-contract values plus the stock `Colors.deepPurple`, 7 on-contract controls, 1 commented-out colour and 1 computed radius. Contract: the `japanese-cute-puzzle` / Onet Garden `tokens.json` generated by `vd.py init`.

| Mode | Command | Result |
|---|---|---|
| inventory | `audit.py scan qa_onet --json` | exit 0, `platform flutter`, scanned 3, skipped 18 (scaffold folders), 1 finding (`touch.target-too-small` medium, line 23). Inventory: colours 6, radii 13/16, sizes 14.5/15/18, durations 200/337/1000, families Comic Sans MS/Fredoka |
| contract | `audit.py scan qa_onet --contract …/tokens.json --profile …/style-profile.json --out … --md …` | exit 1, **12 findings** (high 6, medium 4, low 2) |

Against the ground truth:
- **Planted defects: 12/12 found.** Coral `Color(0xFFFF7F50)`, near-duplicate `0xFFFF8FAC` (Low, distance 0.3), `circular(13)`, `fontSize: 15`, `EdgeInsets.all(18)`, 337 ms, `Duration(seconds: 1)`, `'Comic Sans MS'`, 32×32 `IconButton`, `Color.fromARGB(255,18,52,86)`, `Color.fromRGBO(255,127,80,1)` and `Colors.deepPurple` in `main.dart`.
- **False positives: 0.** Not flagged: the on-contract `0xFFFF8FAB`, `circular(16)`, `fontSize: 18`, `'Fredoka'`, `EdgeInsets.all(16)`, 200 ms, `Colors.white`, `fontSize: 14.5` (within ±1 of 14) and the commented-out `// … Color(0xFF123456)`. The inventory's single `#123456` comes from `fromARGB`.
- **False negatives: 1, documented.** `BorderRadius.circular(radius * 2)` is not inspected (SKILL limitation "computed values").
- **Spot check:** the evidence text appears on the cited line for 12/12 findings. Severities follow `severity.md`: `lib/screens/` is a primary segment, so single occurrences there are High; `main.dart` is Medium; durations are never raised for being on a primary screen.

### 3b. Web pages

Inputs: `projects/{healthcare-dashboard,portfolio-dark,saas-landing}/index.html` and `preview/xiaomaomi-app.html`, copied into a scratch dir with a `package.json` (1,623 lines).

| Mode | Command | Result |
|---|---|---|
| inventory | `audit.py scan web --json` | exit 0, `platform web`, 4 files, 3 medium variant-explosion findings (colour, shadow, radius). Inventory: 26 colours, 5 radii, 8 font sizes, 10 shadows, **font families `['Fredoka','Nunito']` only** |
| contract | `audit.py scan web --contract onet tokens.json --profile … --out findings.json` | exit 1, 76 findings (high 19, medium 29, low 28): `color.off-palette` 40, `color.near-duplicate` 15, `shadow.unlisted` 10, radius/font-size/spacing off-scale 3 each, `shadow.variant-explosion` 1, `touch.target-too-small` 1 |

- Spot check of 5 seeded-random findings at the cited line: 5/5 match. VA-0058 `--background: #FFF7ED;` · VA-0072 `linear-gradient(135deg, #FED7AA, #FDBA74)` · VA-0060 `--border: #FED7AA;` · VA-0066 `linear-gradient(145deg, #FED7AA 0%…)` · VA-0076 `box-shadow: 0 -4px 24px rgba(0,0,0,0.06);`.
- Across all 76 findings the evidence matches the cited line in 74. The other two are by design: a shadow-signature evidence string, and a multi-line CSS rule cited at its selector line (`.icon-btn {`, line 84; the width is on line 85).
- **Proven false negative (new, N-1):** three of the four pages declare their faces only through the Tailwind CDN config, for example `fontFamily: { heading: ['Fira Sans', …], body: ['Fira Sans', …], mono: ['Fira Code', …] }` (`healthcare-dashboard.html:26-29`), `['Space Grotesk'] / ['Archivo']` (`portfolio-dark.html:24-27`) and `['Poppins'] / ['Open Sans']` (`saas-landing.html:22-25`), and load them with Google Fonts `<link …family=…>`. None of the six families appears in the inventory, and against a Fredoka/Nunito contract `font-family.unlisted` reports nothing. Colours in the same config objects *are* caught (e.g. `danger: '#EF4444'`, healthcare line 24). `drift-rules.md:13` lists the font-family sources (Dart, GoogleFonts, CSS `font-family:`, `--*font*` vars) but does not name Tailwind/JS config arrays or `<link>` font loads as a limitation.
- Not a false positive: `.icon-btn` 44×44 against a 48 logical-unit contract is a correct Medium.

## 4. Examples: reproducibility

Each README's commands were re-run verbatim from the repo root with only `$A`/`$EX` pointed at a scratch dir. Hand-written inputs (drift fixtures, `fixed/`, page tables, `inputs/*`) were copied. Diffs ignore ISO timestamps and the example-root path.

| Example | Commands re-run (exit codes) | Artifacts diffed | Result |
|---|---|---|---|
| A — Onet Garden | genres, styles, profile `--genre --style`, init `--json`, page ×3, validate, generate-tokens, validate (committed hand-filled pages), scan ×4, compare. Exit 0, except the two before-scans = 1 | `style-profile.json` (both copies), `tokens.json`, `MASTER.md`, `component-catalog.md`, asset/interaction guidelines, `visual-qa-checklist.md`, `pages/README.md`, `tokens.css`, `audit-{before,after}.{json,md}`, `audit-compare.txt`, logs 01–07, 09–11 | **26/26 identical.** `CHANGELOG.md` differs only by the three `page --force` entries, which I deliberately did not re-run. Committed pages validate `OK — 0 error(s), 0 warning(s)` against the regenerated contract |
| B — Pet Diary Redesign | validate, validate `--json`, summary, profile `--reference`, init `--json`, page ×3, validate ×2 (all 0). I also re-ran the "COPIED, not re-run" `extract-colors` on `inputs/xiaomaomi-390x844.png` | 10 contract files + 8 logs | **18/18 identical.** The extra `extract-colors` run reproduces `palette-extracted.json` exactly (`#FFFFFF 0.7106 · #FEF5E9 0.2074 · #EACCB4 0.0819`, 76×200, 3 kept) |
| C — Consistency audit | scan ×2 (1), inventory (0), scan ×2 on `fixed/` (0), compare ×2 (0), manifest (0), checklist (0), unknown-screen probe (2) | `findings-{before,after}.{json,md}`, `inventory.md`, `compare.{txt,json}`, `screens-manifest.json`, `qa-checklist-gameplay.md`, 6 logs | **15/15 identical.** `fixed/` vs fixture: edited files are exactly README, `rewards.dart`, `shop.dart`, `web/package.json`, `web/shop.css`; `CtaButton.tsx` was deleted; all other files are `cmp`-identical, as the README says |

### Numbers checked against artifacts

**Example A: all confirmed except the run count.**
- Genre score 8.08 (next 1.08) ✓; style first, `xl/soft-cel/bouncy` ✓.
- Seeds and surfaces ✓; 11 anti-patterns, 6 QA criteria, 1 unknown ✓.
- Contrasts 6.54 / 9.74 / 9.47 / 5.41 / 5.67 / 6.89 / 6.27 ✓.
- Radius picks 16/24/32/12/9999 ✓; drift budget ✓; touch 48 ✓.
- `tokens.css` 325 lines / 11,607 B ✓; catalog 52,488 B ✓.
- Before-scan: 5 findings, distance 48.9, nearest 12 ✓. Compare `5/0/0/0` ✓.
- **"21 script runs" (README and index): the listed commands total 19** (N-2).
- The README's 8.4 KB for `style-profile.json` is 8,702 B (rounding).

**Example B: confirmed except two.**
- Validate/summary counts (1 ref, 15 obs = 7/5/1/2, 8 rules all high, 0 conflicts, 7 not-derivable, 3 warnings, distance 19.7) ✓.
- Profile fields, surfaces, seeds, shape, typography split, motion 150/250/400, 5 anti-patterns, 1 exception, 11 unknowns ✓.
- Contrasts 4.90 / 6.88 / 5.18 / 5.22 / 5.67 / 6.73 ✓; `brand.200 #F8E4D6` ✓; all shadows `none` ✓.
- `#64748B` hand-computed 4.48 / 4.76 vs the stated ≈4.5 / 4.8 ✓.
- Ground-truth verdict tally 5 confirmed / 6 partial / 2 wrong / 2 correct-not-derivable = 15 ✓. CSS facts checked at `preview/xiaomaomi-app.html:13-31`, 84–100, 253, 276 ✓.
- **README walkthrough §4 says "8 of 15 rows exact or correct"; `ground-truth-check.md` says "10 of 16 rows", and its table has 16 rows** (N-3).
- README size for MASTER.md is "10.1 KB"; the file is 9,981 B (Info).

**Example C: all confirmed.**
- 40 findings = 0/16/19/5/0, scanned 12, skipped 3 ✓; "12 of 12 minimum rule ids (+ `shadow.unlisted`)" = 13 distinct ✓; after-scan 9 findings, all in `unity/` ✓; compare 31/0/9/8 with the note ✓.
- `triage.md`: all 22 cited VA ids exist; 16 id↔file:line pairs checked positionally, 0 mismatches; class-table counts match the JSON.
- The index README's "12 rule ids" understates the 13 distinct ids (Info).

**Token citations in hand-written specs:** every token path in A's `screens.md` and `pages/*.md` (177) and in B's (96) exists in that example's `tokens.json`. Cited values match; the only regex mismatches were two composite values (a shadow string and an rgba overlay), which are correct on inspection.

### Verification-level honesty

All three tables were checked against the runs above.
- Every EXECUTED row was reproduced.
- B's "COPIED, not re-run" palette is genuine extract-colors output.
- NOT RUN rows (renders, device runs, builds, pixel diffs) are not contradicted anywhere: a grep of the example markdown for rendered/measured/captured/compiled/"on device" claims, minus negated or hedged uses, finds no over-claim.
- C's manifest has 9 entries, all `status: NOT RUN` and `executed: false`; its checklist has 37 unchecked items, all NOT RUN.
- B's `inputs/reference-analysis.json` is labelled "as stated by the Principal agent", which is correct: its `viewed_by: model-vision` cannot be verified here.

## 5. Art-direction review: Example A (Onet Garden, japanese-cute-puzzle)

Scope: concrete contradictions inside `MASTER.md`, `tokens.json`, `component-catalog.md` and `screens.md` for a pastel, chibi, portrait onet game. A-4 (prose pill/28/2 px vs tokens 16/32/3) is already documented and not repeated.

| ID | Sev | Contradiction | Evidence |
|---|---|---|---|
| AD-1 | Medium | **Board arithmetic does not fit the screen it was written for.** screens.md §3 says an "8 × 6 board is 8 × 48 + 7 × 2 = 398 wide" and that only phone-s (375) needs the 44 pitch. 398 already exceeds phone-m's 390 before gutters, and the layout line says "portrait, phone-m 390 × 844". For a portrait 8×6 board the 6 tiles belong across (6×48 + 5×2 = 298 wide, 8×48 + 7×2 = 398 tall), so the `pages/gameplay.md` reason ("8 × 6 board on phone-s") and the 44-pitch exception are both unnecessary | `screens.md` §3 "Board tile — idle" |
| AD-2 | Medium | **Three outline colours on white-filled objects; the declared rule cannot produce any of them.** `semantic.outline.colorRule = fill.700` ("the 700 step of the fill's own ramp"; MASTER: "darker shade of the fill, never pure black"). Results: popup and secondary button outlines are `brand.700 #FF0443` (hot pink-red); tile, HUD chip, icon button and progress outlines are `neutral.700 #56505E`; the card border is `#FFDDAC`. The win popup therefore wears a saturated red-pink 3 px frame around plum-grey tiles and gold-framed reward cards. The style note says popup outline "secondary-darker" (mint), which matches none of them | `tokens.json#component.{popup,button.secondary}.outlineColor` vs `{tile,hud.chip,button.icon,progress}.outlineColor`; MASTER "Style-specific component notes · popup" |
| AD-3 | Medium | **The pressed state breaks the pastel strategy and erases the button outline.** `primaryPressed = brand.700 #FF0443` (HSL 345/100/51), down from the pastel fill `#FF8FAB` (L 78). Pressed fill = outline colour = hard-shadow colour (`0 4px 0 #FF0443`), so on press the CTA becomes a flat neon slab with no visible outline. Hover `brand.600 #FF4A77` is a hot pink as well. MASTER: "Pastel base … never more than 2 saturated hues on one screen" | `semantic.color.primaryPressed`, `component.button.primary.{outlineColor,shadow}`; screens.md §1 Play button "pressed: … bg #FF0443" |
| AD-4 | Medium | **Overshoot easing used as the default curve, including on progress fills.** `easing.standard` = `easing.enter` = `cubic-bezier(0.34, 1.56, 0.64, 1)` (easeOutBack). `component.progress.fillEasing = {primitive.easing.standard}`, so mission bars and the HUD timer overshoot their target value, momentarily showing more than 100 % or more time than is left. Progress/timer feedback needs a non-overshooting curve | `tokens.json#component.progress.fillEasing`; screens.md §3 Timer, §7 Mission row |
| AD-5 | Medium | **Touch targets below the contract's own minimum on interactive HUD/shop parts.** QA criterion: "All interactive targets ≥ 48 logical". The wallet `hud.chip` (height 36) is tappable ("tapping scrolls to the coin packs", screens.md §5); the price tag, the buy control on every pack card, is 44 high; the catalog's reward popup "close X 44dp" | screens.md §5 Wallet / Price tag; `component.hud.chip.height = 36`; component-catalog.md:465 |
| AD-6 | Low | **Press timing cannot meet the QA criterion it is tested against.** QA: "Pressed state visible within 100ms"; style note: "pressed … in 90ms". The shortest non-zero duration token is `fast` 120 ms, and screens.md resolves the conflict in prose ("120 ms total, first frame … on the next frame") instead of in the contract | MASTER QA + component notes; `primitive.duration` |
| AD-7 | Low | **One gold, three meanings on the gameplay screen.** `reward = warning = #F5A524`. On gameplay the hint highlight uses `warning`, the timer turns `warning` under 20 %, and stars/streak use `reward`. A hinted tile and a running-out timer look alike. Reward moments are meant to be "accent plus gold", but accent `#FFD23F` vs gold `#F5A524` is 1.41:1 (H 46° vs 37°) | `semantic.color.{reward,warning}`; screens.md §3 Hinted / Timer |
| AD-8 | Low | **Selection is specified two ways.** screens.md's shared vocabulary lists "Selection / reward accent = `semantic.color.accent #FFD23F`", but the selected tile uses `component.tile.outlineColorSelected = primary #FF8FAB`, the CTA colour, so a selected tile reads like a button. `bgSelected brand.100 #FDF3F6` on a white tile is 1.09:1, so the outline carries all of the selection signal | screens.md vocabulary table vs §3 "Selected"; `component.tile` |
| AD-9 | Low | **Two shadow languages.** Hard shadows on buttons, tiles and chips are hue-tinted (`0 2px 0 #56505E`, `0 4px 0 #FF0443`). Card and popup elevation (`semantic.elevation.*`) uses pure black `rgba(0,0,0,0.25)` hard offsets. The style asks for "hue-shifted (toward purple)" shading and forbids pure black outlines | `primitive.shadow.*` vs `component.tile.shadow` |
| AD-10 | Low | **Near-invisible distinctions in two specs.** Spin-wheel segments `brand.100 #FDF3F6` vs `secondary.100 #F2F9F8` are 1.02:1, so the segments only separate by outline. Completed level nodes fill with `success #0D7734` (L ≈ 26 %), making the most frequent map element the darkest saturated colour on a pastel map. That green is the contrast walk recorded as A-13 | screens.md §7 Spin wheel, §2 Level node |

Coherent and correct: the chibi/rounded identity (Fredoka 700 / Nunito 500, `xl` silhouettes, 3 px outlines on gameplay pieces); all `onX` pairs ≥ 4.5:1; HUD capped at 3 capsules with the board ≥ 85 %; reward motion tier (750 ms beat, 2500 ms ambient, reduced-motion fallbacks); and the page overrides, which really are deviations only (`validate` exit 0, budget respected). AD-2, AD-3 and AD-4 come from the token derivation (`vd.py` / `vd_tokens.py`), not from the hand-written example, so every pastel catalog style inherits them.

## 6. New findings (pass 2)

| ID | Sev | Area | Command | Expected | Actual | Evidence |
|---|---|---|---|---|---|---|
| N-1 | Medium | visual-audit font-family coverage | `audit.py scan <web dir with projects/*/index.html> --contract <Fredoka/Nunito tokens.json> --json` | `font-family.unlisted` for Fira Sans, Fira Code, Space Grotesk, Archivo, Poppins, Open Sans, or a documented limitation | 0 font findings; inventory families `['Fredoka','Nunito']` only. Tailwind `fontFamily: {…: ['X', …]}` config arrays and Google Fonts `<link>` loads are not read, and `drift-rules.md:13` does not list them as unread | §3b |
| N-2 | Low | Example A README + index | count the commands in "Commands executed" | 21 | 19 | §4 |
| N-3 | Low | Example B README §4 vs `ground-truth-check.md` | — | one figure | README "8 of 15 rows"; ground-truth-check.md "10 of 16 rows" (16-row table) | §4 |
| N-4 | Medium | AC row 14 journal | `sed -n 41,47p docs/journals/261015-1300-visual-design-pro-max.md` | test results and AC table filled | `TBD-FINAL` placeholders under "Test results (final)" and "Acceptance criteria" | journal lines 43, 47 |
| N-5 | Info | Contract CC-8 text | read CC-8 | superseded text marked | CC-8 still says "tolerates ±10 %"; only CC-13 below withdraws it | INTEGRATION_CONTRACT.md:172 vs :180 |
| AD-1…AD-10 | Medium ×5, Low ×5 | Example A contract / token derivation | see §5 | — | — | §5 |

No Critical or High findings in pass 2.

## 7. Limitation rows

| Row | Status | Note |
|---|---|---|
| Real Flutter app static audit | **PASS** | §3a: fresh `flutter create --offline` app + ground-truth screen, 12/12 detected, 0 FP |
| Real Flutter app screenshot diff | NOT RUN | app not built or captured; `visual_qa.py diff` exercised on synthetic PNGs and Example B's PNG only |
| Real Unity project audit | NOT RUN | fixture `unity/` only (Example C) |
| Web research / provenance fetch | NOT RUN (by design) | scripts never fetch; `research-and-provenance.md` §2 tiers, §3 licence classes, §4 record format present; both example contracts carry the `licence_class` field rule in `asset-guidelines.md` |
| Playwright capture from manifest | NOT RUN | manifests stay NOT RUN (C: 9/9) |
| CLI e2e / verify:data | NOT RUN by W2-F | Principal: verify:data exit 0; e2e 40/41, 1 BLOCKED (Playwright browser binary missing) |

## 8. Verdict on ACCEPTANCE_CRITERIA rows 1–14

| # | Criterion | Status | Basis |
|---|---|---|---|
| 1 | Architecture docs based on real code | PASS | six files exist; every cited path resolves (skill-relative shorthand under `.claude/skills/`) |
| 2 | Skills integrated | PASS | three dirs + identical `cli/assets` mirrors, `subSkills`, `check:assets` exit 0, CLI dry-run lists all three |
| 3 | Selection by catalog / genre / reference | PASS | style, genre, genre+style and reference routes produce valid profiles; tests pass |
| 4 | VDP schema + docs | PASS | enums and required keys enforced as documented (pass-1 probe, unchanged code paths); invalid profile → 1. F-16 (negative outline width) is a Low gap |
| 5 | Master + overrides | PASS | init keeps an existing MASTER.md; `page` skips existing files; `validate` flags copies and ≥ 3 restated values |
| 6 | UI/UX + drift audit | PASS | fixture: 13 rule ids with file:line; real Flutter 12/12; real web 5/5 spot-checked; `compare` deltas correct. N-1 is a coverage gap |
| 7 | Research & provenance | PASS | tiers, licence classes and attribution record format present; examples carry provenance and licence notes (B: repository file, MIT) |
| 8 | Per-stack guidance | PASS with gap | all 13 token groups mapped in all 4 adapters; F-15 semantic-colour names missing in flutter-flame.md and unity.md (Low) |
| 9 | Automated tests | PASS | 448 new tests pass (1 env-gated skip) |
| 10 | Three examples with verification level | PASS | all three regenerate byte-identically; verification tables are honest. N-2/N-3 are count typos |
| 11 | Tests executed, nothing hidden | PASS (W2-F part) | gate table above; verify:data and e2e taken from the Principal's run |
| 12 | No regression | PASS | 300 baseline pytest inside 748; 164 unittest; check:assets; validate-agent-guide |
| 13 | Usage + integration docs | PASS | prerequisites, runtimes and limitations present; pass-1 false statements (F-02, F-11, F-14) fixed |
| 14 | Final report (journal) | **NOT MET yet** | journal exists and lists BLOCKED/NOT RUN items, but "Test results (final)" and "Acceptance criteria" still read `TBD-FINAL` (N-4) |

**Verdict.** Rows 1–13 are met on this machine with reproducible evidence; row 14 is not met until the Principal fills the journal's two `TBD-FINAL` sections. Every pass-1 High and Medium is fixed. The gate is green, the three examples regenerate byte-for-byte from their own README commands, and on real code the scanner found every planted Flutter defect with no false positives. The remaining defects are Medium or lower:
- the scanner cannot see fonts declared in Tailwind config or `<link>` tags (N-1);
- the Example A contract has five Medium art-direction contradictions (AD-1…AD-5). Three of them (outline colours on white surfaces, the neon pressed state, overshoot easing on progress) come from the token derivation and will appear in every pastel contract until `vd_tokens.py` is changed;
- seven Low leftovers from pass 1.

None blocks acceptance. AD-2, AD-3 and AD-4 should be scheduled before the skill is promoted for game art direction.

---

# Pass 3 (2026-10-16): deltas after the generator art-direction round and CC-15

Scope: re-check AD-1…AD-10, N-1 and the pass-2 Lows; compute component-state contrast independently for all 20 styles; regenerate Examples A and B; re-run N-1 on `projects/*.html`; re-read Example A as an art director. Example C was not touched this round and was not re-run. Scratch: `scratchpad/w2f3/` (my contrast checker is `contrast_check.py`; it imports nothing from the skills). The repo is unchanged apart from this section: `git status --porcelain | wc -l` = 18 before and after.

## P3-0. Gate (abridged)

| Gate | Status | Evidence |
|---|---|---|
| `python3 -m pytest .claude/skills -q -p no:cacheprovider` | PASS | `784 passed, 1 skipped in 37.98s` |
| `python3 -m unittest discover -s src/ui-ux-pro-max/scripts/tests` | PASS | `OK` (164) |
| `node cli/scripts/sync-assets.mjs --check` + `diff -r` of the three mirrors | PASS | `Assets are in sync.`; mirrors identical |
| CI grep replica (paths, bundled skills) | PASS | `OK grep-paths (perl)`, `OK grep-bundled (perl)` |
| Python 3.8 `ast.parse` on every new `.py` | PASS | no failures |

## P3-1. Status of pass-2 findings

| ID | Pass-2 sev | Status | Evidence (command → observed) |
|---|---|---|---|
| AD-1 board arithmetic | Medium | **FIXED** | `screens.md` §3 is now 6 across × 8 down with `tile = min(56, floor((W − 32 − 20)/6))`. I recomputed every cell: phone-s 53 / 338 × 452 / pitch 57 / 608 ≤ 667 / 88 %; phone-m 56 / 356 × 476 / 693 ≤ 844 / 75.9 %; phone-l 705 ≤ 932 / 67.7 %; 6 × 10 = 596 → 95 % / 85 %. All correct. The README admits the 85 % rule is missed on tall phones |
| AD-2 outline colours | Medium | **FIXED** | Example A `tokens.json`: decorative outlines (`popup`, `hud.chip`, `progress`, `card`) all `semantic.color.border #FFDDAC`; interactive (`tile`, `button.icon`) `borderInteractive #A88655`; CTA outlines are brand shades (`primary` `brand.800 #972743` on the pink fill, `secondary` `brand.700 #BA4A66` = its label). Residual: see P3-5 AD3-1 |
| AD-3 pressed state | Medium | **FIXED** | `bgPressed #BA4A66` (HSL 345/45/51) ≠ outline `#972743`; pressed label `fgPressed #FFFFFF` 4.93:1; hover lightens to `#FBBECD` so the dark default label still passes (8.94:1); brand ramp 600–900 no longer neon (`#DC6C88 #BA4A66 #972743 #740420`) |
| AD-4 overshoot on progress | Medium | **FIXED** | `easing.standard = cubic-bezier(0.22, 1, 0.36, 1)` (no overshoot), `component.progress.fillEasing` → standard; overshoot kept only for `easing.enter` |
| AD-5 touch targets | Medium | **FIXED** (spec) | Wallet and Home capsules specify a 48 × ≥ 48 hit area around the 36 plate; price tag 48; non-tappable plates labelled. `component.hud.chip.height` stays 36: the hit area is a spec rule, not a token |
| AD-6 press timing | Low | **FIXED in the contract, but see N3-1** | `component.button.{primary,secondary,icon}.pressDuration = 90ms`; screens.md §QA cites it. The audit tool rejects that value (N3-1, High) |
| AD-7 one gold, three meanings | Low | **PARTIAL** | `reward #FFC83D` is now distinct from `warning #F5A524` (1.32:1), and the hint carries a non-colour cue (hand glyph). But reward vs `accent #FFD23F` is **1.07:1** (hue 43° vs 46°), so the collision moved from warning to accent. Stars and streak (`reward`) are indistinguishable from the match path, current-node ring and badges (`accent`) |
| AD-8 selection specified twice | Low | **FIXED** | vocabulary and §3 both use `component.tile.outlineColorSelected = brand.700 #BA4A66` (2.29:1 vs the CTA fill; selection = rose vs tan + width 3 → 4 + scale) |
| AD-9 two shadow languages | Low | **FIXED** | every `primitive.shadow.*` is tinted `rgba(46, 42, 50, …)` (neutral.900); hard edges `#56505E` / `#972743` |
| AD-10 near-invisible distinctions | Low | **FIXED** | wheel segments keep 1.02:1 fills but get 3 px `borderInteractive` dividers (3.11 / 3.17:1, recomputed). Completed node = `success.200 #CEF2DB` fill + `success #107435` ring (5.49:1 vs map) |
| N-1 Tailwind/Google Fonts families | Medium | **FIXED** | `audit.py scan <projects/*/index.html + xiaomaomi> --contract <Example A tokens> --json`: 13 `font-family.unlisted` findings naming exactly `Archivo, Fira Code, Fira Sans, Open Sans, Poppins, Space Grotesk`, each at a correct line (`<link … family=…>` and the `fontFamily: {heading: [...]}` entries). Contract fonts (Fredoka/Nunito in xiaomaomi) are not flagged. Inventory `font_families` now lists all 8 |
| N-2 run count | Low | **FIXED** | Example A README "**19 script runs**"; index README "19 script runs" |
| N-3 8/15 vs 10/16 | Low | **FIXED** | B README:68 "10 of 16"; `ground-truth-check.md:76` "10 of 16"; table has 16 rows |
| N-4 journal TBD-FINAL | Medium | **STILL PRESENT** | `docs/journals/261015-1300-visual-design-pro-max.md` lines 6, 43, 47 still `TBD-FINAL` |
| N-5 CC-8 text | Info | **STILL PRESENT** | CC-8 still says "tolerates ±10 %"; only CC-13 below it withdraws that |
| F-07 `--force` drops hand edits | Low | **FIXED** | hand-edited tool MASTER.md + `init --force` → `MASTER.md: rewritten (hand-edited copy saved as MASTER.md.bak-20261016T122409Z)`; the backup holds the edit; an unedited MASTER gets no backup |
| F-10 undocumented flags | Low | **STILL PARTIAL** | visual-audit SKILL.md still omits `--max-files` (0 hits); `vd.py profile/page --json`, `checklist --json`, `extract-colors --colors/--ref` still not in the tables |
| F-12 `--seeds` precedence in help | Low | **STILL PARTIAL** | `vd_tokens.py --help` unchanged ("optional JSON object {…}"); the docs explain the precedence |
| F-13 unprefixed ids | Low | **FIXED** | 55 rows, 0 without a prefix (`overlay.tooltip`, `feedback.toast`, `feedback.toast-app`) |
| F-15 platform adapters | Low | **STILL PRESENT, widened** | flutter-flame.md still lacks `onSecondary, accent, onAccent, background, textMuted`; unity.md lacks `onPrimary, onSecondary, accent, onAccent, surface, textMuted`. **None of the four adapters mentions the new `borderInteractive`** that CC-15 makes contractual |
| F-16 negative outline width | Low | **FIXED** | `init` on a profile with `shape.outline.width: -3` → exit 1, `shape.outline.width: must be a finite number >= 0 (got -3)` |
| F-17 inventory `shadow.unlisted` | Info | **STILL PARTIAL** | visual-audit SKILL.md:58 still says "(+ `shadow.unlisted`, `<category>.variant-explosion` in inventory mode)" |

## P3-2. Independent component-state contrast: all 20 catalog styles

Method: for each `Style ID` in `visual-styles.csv`, I generated `vd.py profile --style <id> --platform mobile-ios --project "S <id>"` and then `vd_tokens.py --profile … --out <id>-tokens.json`. My own resolver and WCAG 2.x luminance checked:
- **Labels (≥ 4.5:1):** `button.primary` and `button.secondary` label on `bg`, `bgHover` and `bgPressed`, using the per-state `fgHover`/`fgPressed` when present and `fg` otherwise; `card`, `popup`, `hud.chip` and `button.icon` fg/bg (a ghost icon button with a `transparent` bg is checked against the page); the seven `semantic.on*` pairs; and `text`/`textMuted` on background, surface and surfaceElevated.
- **Boundaries (≥ 3:1, WCAG 1.4.11):** the `outlineColor` / `outlineColorSelected` of `button.icon`, `tile` and `button.secondary` against the page background and against surface; the primary button's better edge (fill or outline) against the page; `borderInteractive` against background and surface; `focusRing` against background.

| Check | Pairs | Below threshold | Worst |
|---|---|---|---|
| Labels ≥ 4.5:1 | **457** | **0** | 4.52 (kawaii-sticker pressed CTA `#FFFFFF` on `#B65682`) |
| Ghost icon glyph vs page (3 styles with `transparent` icon bg) | 3 | 0 | 7.60 (cozy-pastel) |
| Interactive outlines + `borderInteractive` ≥ 3:1 (the CC-15 scope; ghost icon buttons with `transparent` outlines skipped) | 172 | **0** | 3.16 (japanese-cute-puzzle `#A88655` on `#FFF6E9`) |
| Primary CTA edge vs page (fill or outline, whichever is better; fill only where the outline is `transparent`) | 20 | **7** | **1.83** (cozy-pastel fill `#E8A5B8` on `#FBF4EE`, no outline). The others: kawaii-sticker 1.90, dark-fantasy-game-ui **2.16** (outline `#51111A` 1.34, i.e. darker than the fill on a dark page), paper-cutout 2.60, japanese-casual-game 2.65, colorful-toy-3d 2.76, hand-painted-storybook 2.86 → N3-3 |
| `focusRing` vs background | 20 | **14** | **1.37** (cozy-pastel `#EECAD4` on `#FBF4EE`) → N3-2 |

CC-15's claims hold. **Zero labels below 4.5:1 and zero CC-15 interactive boundaries below 3:1.** The 7 low-contrast CTA fills are outside CC-15 by design: seeded fills are never changed, and a text button is identified by its ≥ 4.5:1 label, which WCAG 1.4.11 accepts. Exactly 8 styles keep a near-black primary label (anime-inspired-game-ui, cel-shaded-adventure, glossy-candy-match3, hand-painted-storybook, minimal-modern-mobile, pixel-retro-arcade, premium-casual-game, soft-2d-cartoon), and MASTER → Unknowns surfaces it. For example, minimal-modern-mobile has "primary: on-colour is #000000 because it is the only candidate reaching 4.5:1 on #2F6BFF …".

`vd.py validate` rejection test (`scratchpad/w2f3/validate_test.sh`, Example A style, fresh `init`):
1. Baseline → `OK — 0 error(s), 0 warning(s)`, exit 0.
2. Hand-edit `component.button.primary.fgPressed` to `#A5A5A5` (2.00:1 on `#BA4A66`) → `ERROR: tokens.json: tokens.component.button.primary.fgPressed: label #A5A5A5 on bgPressed #BA4A66 is 2.00:1 (< 4.5)`, `FAILED — 1 error(s)`, **exit 1** ✓.
3. Set `borderInteractive` to `#EEEEEE` → 4 warnings (tile and icon outline vs bg 1.16:1 and vs background 1.08:1), exit 0 ✓ (CC-15: boundary = warning).
4. Set the secondary label to `#FFB0C4` → 3 errors (default 1.71, hover 1.63, pressed 1.58), exit 1 ✓.

`vd.py validate` is silent on N3-2 and N3-3: dark-fantasy-game-ui, cozy-pastel and minimal-modern-mobile contracts all validate `OK — 0 error(s), 0 warning(s)`.

## P3-3. Examples A and B regenerated (README commands verbatim, scratch output paths)

| Example | Runs (exit codes) | Compared | Result |
|---|---|---|---|
| A | (1)–(9) 0; (10) **not re-run**, because the first-round page fill it re-tests is not committed; (11)–(14) 0 with the three `page --force` and the committed hand tables copied in; (15)/(16) 1; (17)–(19) 0 | 31 committed files under `project/`, `style-profile.json`, `audit-*`, `logs/` | **30/30 regenerable files identical after timestamp normalisation** (`logs/08-validate-first-fill-retest.txt` not regenerable, see (10)). 17/31 byte-identical without any normalisation |
| B | 10 runs, all 0 | 23 committed files | **23/23 identical after timestamp normalisation**; 14/23 byte-identical raw |

The only non-timestamp line that differs is MASTER.md line 1 `body-hash`. `vd.py` computes it as sha256 of the MASTER body, which contains the `Generated:` timestamp, so it is timestamp-derived. With timestamps masked, the bodies are identical (`cmp` exit 0), and the committed `body-hash` (`8a8bae76a0e4` for A) equals the sha256 of its own body, which proves the committed MASTER.md was not hand-edited after generation (Info N3-7).

Spec citations re-checked: Example A `screens.md` + 3 pages cite 207 token paths, all exist, 0 value mismatches, and every hex in the specs exists in `tokens.json`. Example B cites 100 paths, 0 missing, 0 mismatches. Its one hex not in tokens, `#BBF7D0`, is the declared `home-quick-actions` page exception (the CSS mint), which is legal.

## P3-4. New findings

| ID | Sev | Area | Exact command | Expected | Actual | Evidence |
|---|---|---|---|---|---|---|
| **N3-1** | **High** | visual-direction ↔ visual-audit integration | (a) Dart: three widgets `lib/widgets/og_{,secondary_,icon_}button.dart` each with `AnimatedContainer(duration: const Duration(milliseconds: 90), …)`, i.e. the contract's own `component.button.*.pressDuration`; then `python3 .claude/skills/visual-audit/scripts/audit.py scan <dir> --contract docs/examples/visual-design-pro-max/example-a-japanese-cute-animal-puzzle/project/design-system/onet-garden/tokens.json --json`. (b) CSS copying `component.*` values verbatim (`transition: transform 90ms`; `box-shadow: 0 4px 0 #972743, 0 8px 12px rgba(46, 42, 50, 0.14)`; `box-shadow: 0 2px 0 #56505E, 0 4px 6px rgba(46, 42, 50, 0.12)`), same scan | code that implements the generated contract exactly scans clean | (a) **exit 1**, 3 × `duration.off-scale` **high** (`nearest primitive.duration.step 120`). (b) exit 0 but 5 findings: 2 × `duration.off-scale` medium (90 ms), 3 × `shadow.unlisted` low (the component hard shadows of `button.primary`, `button.secondary` and `tile`). Cause: the generator now emits literal component values (`pressDuration 90ms`, coloured hard-edge shadows) that are not in `primitive.duration.*` / `primitive.shadow.*`, and `drift-rules.md:38` builds the audit's allowed sets from `primitive.*` only. A team following the docs' CI recipe (`--fail-on high`) fails CI on conformant code. Fix either side: add `primitive.duration.press` and the hard-shadow signatures as primitives, or let the audit admit `component.*` leaf values | `scratchpad/w2f3/logs/ad6b.json`, `logs/conf-web.json` |
| N3-2 | Medium | token derivation, focus state | `vd_tokens.py` for each of the 20 styles, then my checker: `focusRing` (`brand.400`) vs `semantic.color.background` | ≥ 3:1 (WCAG 1.4.11 applies to focus indicators; relevant for the web/desktop/tablet platforms the profiles allow) | **14/20 below 3:1**, worst cozy-pastel 1.37, japanese-cute-puzzle 1.47; even app styles minimal-modern-mobile and playful-edtech-app 2.34. `vd.py validate` does not check it. In Example A, `focusRing #FBBECD` also equals the primary `bgHover #FBBECD`, so a focus ring on a hovered CTA is invisible | `scratchpad/w2f3/logs/contrast.txt` |
| N3-3 | Medium (dark-fantasy) / Info (6 pastel styles) | token derivation, CTA edge | `vd.py profile --style dark-fantasy-game-ui --platform mobile-ios --out p.json; vd_tokens.py --profile p.json --out t.json` | the primary CTA separates from the page (fill or outline ≥ 3:1) | fill `#8B1E2D` vs page `#0E0B14` = 2.16:1, and the outline steps **darker** (`brand.800 #51111A`, 1.34:1). On a dark page the "darker shade" outline rule makes the CTA edge vanish; a lighter step would give the edge without touching the seeded fill. The white label (≥ 4.5) keeps it WCAG-legal; `validate` is silent. Info: 6 pastel styles (cozy-pastel 1.83 … hand-painted-storybook 2.86) have fill-only CTAs below 3:1 vs page with a `transparent` outline, legal under CC-15 because they rely on label + hard shadow | `logs/contrast.txt`; `vv-dark-fantasy-game-ui` validate `OK` |
| N3-4 | Low | platform adapters | `grep -c borderInteractive .claude/skills/visual-direction/references/platforms/*.md` | each adapter maps the new CC-15 slot | 0 in all four (`flutter-flame.md`, `unity.md`, `web.md`, `mobile-native.md`) | P3-1 F-15 row |
| N3-7 | Info | `MASTER.md` header determinism | regenerate any example | — | `body-hash` covers the timestamped body, so the header line changes every run even when nothing else does. Harmless but noisy in diffs | P3-3 |

## P3-5. Art-direction re-read, Example A (contradictions only)

| ID | Sev | Contradiction | Evidence |
|---|---|---|---|
| AD3-1 | Low | **Reward gold ≈ accent yellow.** The reward colour was moved off the warning gold, but it now sits at 1.07:1 / Δhue 3° from `accent`. "Reward popups go one saturation step higher (accent plus gold)" reads as a single colour, and stars (`reward`) look like the match path and current-level ring (`accent`) | `semantic.color.reward #FFC83D`, `accent #FFD23F` |
| AD3-2 | Low | **Tappable capsule wears the decorative border.** Home and Shop wallet capsules are declared tappable (48 hit area), but their outline is `hud.chip.outlineColor = border #FFDDAC` (1.21:1 on the cream page), not `borderInteractive`. CC-15 reserves `border` for decorative panels | screens.md §1 "Currency capsule — tappable", §5 Wallet; `component.hud.chip.outlineColor` |
| AD3-3 | Low | **Outline and hard shadow disagree on interactive pieces.** Tile and icon button have a tan outline `#A88655` over a plum-grey hard shadow `#56505E`; the secondary button has a rose outline `#BA4A66` over the same grey. The style's "one darker shade" logic is split across two unrelated darks on the same object | `component.{tile,button.icon,button.secondary}.{outlineColor,shadow}` |
| AD3-4 | Low | **Focus ring = hover fill** (see N3-2): `focusRing #FBBECD` = `primaryHover #FBBECD`, and 1.47:1 on the page | `semantic.color.{focusRing,primaryHover}` |

Coherent now: one decorative outline colour; interactive edges ≥ 3:1; a non-neon pressed state with its own label; a non-overshooting standard curve; 90 ms press tokens matching the QA criterion; tinted shadows; correct board arithmetic; 48 hit areas everywhere a tap is specified.

## P3-6. Verdict update

Rows 1–13 stay met. CC-15's own claims verify independently: 0/457 labels below 4.5:1, 0/172 CC-15 boundaries below 3:1, 8 black-label styles surfaced, and `validate` rejects a 2:1 pressed label with exit 1. Examples A and B reproduce from their README commands (all differences are timestamps). All Medium art-direction defects AD-1…AD-5 and N-1 are fixed.

Row 14 is still **not met**: the journal keeps three `TBD-FINAL` placeholders.

One **new High (N3-1)** blocks a clean release of the skill set as an end-to-end workflow. The generator now emits component literals (`pressDuration 90ms`, coloured hard-edge component shadows) that `audit.py` does not accept, so code that implements the generated contract verbatim fails `audit.py scan --fail-on high` (exit 1). Rows 5 and 6 still pass their written criteria, but the two halves of the contract contradict each other until N3-1 is fixed.

Also open: N3-2 (focus rings < 3:1 in 14/20 styles), N3-3 (dark-style CTA edge 2.16:1, outline steps darker), and five Lows.
