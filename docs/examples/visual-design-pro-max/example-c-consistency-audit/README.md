# Example C — Consistency audit of a simulated mixed project

The `visual-audit` skill end to end on a **static, non-runnable, mixed Flutter / web / Unity fixture**: inventory → contract scan → triage → partial fix → re-scan → compare, plus the two `visual_qa.py` helpers (capture manifest, per-screen checklist). No screenshot was captured, no app was run.

> **Final regeneration.** All script outputs were regenerated after every fix round was merged. The scanner now caps heuristic touch/contrast findings at Medium, so the fixture's oracle is 40 findings = critical 0 · high 16 · medium 19 · low 5 · info 0, and finding ids were renumbered (`triage.md` uses the final ids). Earlier observations are kept at the end with FIXED / STILL PRESENT / NEW status. The QA-pass-2 regeneration (scanner now also reads fonts from Tailwind configs and Google Fonts links) produced the **same** 40 / 9 / 31-0-9-8 numbers and the same finding ids on this fixture, which has neither, so `triage.md` stands unchanged; all 10 commands below were re-run and their exit codes re-checked.

## Purpose

Show what the audit produces on a project with known drift: 40 graded findings with `file:line` evidence, an inventory, a triage that answers the seven questions, and a before/after `compare` that also exposes how count-based severity behaves when only part of a project is fixed.

## Inputs (and their provenance)

| Input | Provenance |
|---|---|
| `.claude/skills/visual-audit/scripts/tests/fixtures/drift-project/` — the "simulated project" | the skill's own **pytest fixture**: hand-written text files with planted defects (its `README.md` says so). **Not copied** for the before-scan; referenced by path. Contains `pubspec.yaml` + `lib/`, `web/package.json` + `web/`, `unity/Assets/` + `unity/ProjectSettings/`, decoys `build/` and `web/node_modules/`, and its own `tokens.json` (the contract) |
| `.claude/skills/visual-audit/scripts/tests/fixtures/expected-findings.md` | the fixture's oracle — read, not executed; its line 108 states the capped summary `{"critical": 0, "high": 16, "medium": 19, "low": 5, "info": 0}` with the same 40 rows, which the before-scan matches |
| `fixed/` | **a copy of the fixture made for this example** (`cp -R`), then `lib/` and `web/` corrected by hand; `unity/`, `build/`, `web/node_modules/`, `tokens.json` untouched. Re-checked this round: every untouched file is `cmp`-identical to the fixture; the only file-list difference is the deliberately deleted `web/components/CtaButton.tsx` |
| `../example-a-japanese-cute-animal-puzzle/style-profile.json` | the final Example A profile, used only for `visual_qa.py checklist` |
| `--stack flutter --screens home,shop,rewards` | this example's brief |

## Commands executed (from the repository root, in order; final regeneration)

```bash
EX=docs/examples/visual-design-pro-max/example-c-consistency-audit
FX=.claude/skills/visual-audit/scripts/tests/fixtures/drift-project

# 1. contract scan (before) — exit 1 = findings at/above --fail-on high
python3 .claude/skills/visual-audit/scripts/audit.py scan $FX --contract $FX/tokens.json --format md --out $EX/findings-before.md      # exit 1 → logs/01-scan-before-stdout.txt
python3 .claude/skills/visual-audit/scripts/audit.py scan $FX --contract $FX/tokens.json --json      --out $EX/findings-before.json    # exit 1

# 2. inventory mode (no contract) — exit 0 now: the heuristic findings are capped at Medium, below --fail-on high
python3 .claude/skills/visual-audit/scripts/audit.py scan $FX --format md --out $EX/inventory.md                                      # exit 0 → logs/02-inventory-stdout.txt

# 3. partial fix: fixed/ is the existing copy (cp -R + hand edits listed in fixed/README.md); untouched files re-checked with cmp

# 4. contract scan (after), against the copied contract
python3 .claude/skills/visual-audit/scripts/audit.py scan $EX/fixed --contract $EX/fixed/tokens.json --format md --out $EX/findings-after.md    # exit 0 → logs/03-scan-after-stdout.txt
python3 .claude/skills/visual-audit/scripts/audit.py scan $EX/fixed --contract $EX/fixed/tokens.json --json      --out $EX/findings-after.json  # exit 0

# 5. delta
python3 .claude/skills/visual-audit/scripts/audit.py compare $EX/findings-before.json $EX/findings-after.json        > $EX/compare.txt   # exit 0
python3 .claude/skills/visual-audit/scripts/audit.py compare $EX/findings-before.json $EX/findings-after.json --json > $EX/compare.json  # exit 0

# 6. QA helpers (instructions only — nothing is captured)
python3 .claude/skills/visual-audit/scripts/visual_qa.py manifest --stack flutter --screens home,shop,rewards --out $EX/screens-manifest.json   # exit 0
python3 .claude/skills/visual-audit/scripts/visual_qa.py checklist \
  --profile docs/examples/visual-design-pro-max/example-a-japanese-cute-animal-puzzle/style-profile.json --screen gameplay --format md \
  > $EX/qa-checklist-gameplay.md                                                                                                        # exit 0

# 7. probe of the new screen-id validation (output discarded, stderr kept)
python3 .claude/skills/visual-audit/scripts/visual_qa.py checklist \
  --profile docs/examples/visual-design-pro-max/example-a-japanese-cute-animal-puzzle/style-profile.json --screen gameplay-board --format md \
  > /dev/null                                                                                                                            # exit 2 → logs/06-checklist-unknown-screen.stderr
```

10 script runs. `audit.py scan --out` prints a one-line summary (kept in `logs/`), e.g. `visual audit: 40 findings (critical 0, high 16, medium 19, low 5, info 0) · platform mixed · scanned 12 · skipped 3 → …/findings-before.md`.

## Generated artifacts (committed next to this README)

| Path | Produced by | Size | Content |
|---|---|---|---|
| `findings-before.md` / `.json` | `audit.py scan --contract` on the fixture | 21.3 KB / 42.5 KB | `platform: mixed`, 12 scanned, 3 skipped, summary `high 16 · medium 19 · low 5`, 40 findings, inventory |
| `inventory.md` | `audit.py scan` without contract | 5.9 KB | 9 inventory-mode findings, all Medium (variant-explosion / icon / duplicate / touch / contrast) + inventory |
| `fixed/` | `cp -R` + hand edits | 18 files | partially corrected copy (see its `README.md`); decoys included |
| `findings-after.md` / `.json` | `audit.py scan --contract` on `fixed/` | 5.3 KB / 10.7 KB | 11 scanned, 3 skipped, summary `medium 7 · low 2`, 9 findings, all Unity |
| `compare.txt` / `compare.json` | `audit.py compare` | 3.7 KB / 10.0 KB | `resolved: 31 new: 0 unchanged: 9 changed_severity: 8` + note line |
| `screens-manifest.json` | `visual_qa.py manifest` | 17.6 KB | 3 screens × 3 phone devices, Flutter `integration_test` snippets, marked "not executed" |
| `qa-checklist-gameplay.md` | `visual_qa.py checklist` | 6.5 KB | 37 items (6 profile criteria + 20 generic + 11 anti-patterns), every status `NOT RUN` |
| `triage.md` | hand-written | — | severity groups (final ids), seven questions × 5, classification, fix order, what `compare` means |
| `logs/` | stdout/stderr of the scans, manifest, checklist, screen-id probe | — | |

All committed artifacts are under 60 KB; nothing was truncated.

## Walkthrough — what an art director (or tech lead) reads out of the artifacts

1. **Inventory first** (`inventory.md`). 12 opaque colours (`#E91E63 ×3`, `#1E88E5 ×2`, near-accents `#FF8B4D`, `#FA804F`), radii `16 ×4 · 8 ×4 · 13 ×3 · 7 ×2 · 9999 ×2 · 4 ×1`, a stray `15 ×4` font size, families `Comic Sans MS, Fredoka, Nunito, Poppins`, durations `200 ×5 · 337 ×5 · 350 ×2 · 120 ×1`, two icon libraries per platform ("keep material, replace font_awesome_flutter"; web: "keep @heroicons/react, replace lucide-react", an alphabetical tie-break — C-8), four button components. The step now exits 0: everything it reports is Medium.
2. **The contract scan** (`findings-before.md`). 40 findings, 12 of 12 minimum rule ids (+ `shadow.unlisted`), each with `file:line`, normalised evidence, violated set, nearest token, impact, fix (`pages/shop.md` for every shop surface), files and verification. **High (16)** are now exact literals only: pink `#E91E63` ×3, radius `13` ×3, `Comic Sans MS`, font size `15` ×4, `337 ms` ×5. The 32 × 32 close button (VA-0022), the 28 × 28 `.icon-btn` (VA-0034) and the 1.35:1 promo text (VA-0035) are **Medium** with `[heuristic]` in the message. Six clean files produce nothing; three decoys are skipped.
3. **Triage** (`triage.md`). The art-director ranking intentionally puts the two capped heuristics (T2, T3) ahead of brand findings *pending device confirmation*, and says so; `nearest` is treated as a distance, not a decision; subjective calls are separated from mandatory ones.
4. **Partial fix and compare** (`fixed/`, `findings-after.md`, `compare.txt`). Fixing `lib/` and `web/` resolves 31 findings and leaves `web/` clean. The 9 Unity findings stay; 8 change severity downward only because the project-wide counts fell, and `compare` says so in its note line. `new: 0`.
5. **QA helpers**. `screens-manifest.json`: nine capture entries with Flutter `integration_test` snippets, baseline/sidecar paths and status-bar masks, headed "not executed". `qa-checklist-gameplay.md`: 37 `NOT RUN` checkboxes from the Example A profile. An unknown screen id is now rejected: `error: unknown screen 'gameplay-board'; valid ids: home, gameplay, level-select, pause, win, lose, settings, shop, rewards, profile, tutorial (or add pages/<name>.md next to the profile)`, exit 2.

## Verification level

| Claim | Level | Evidence |
|---|---|---|
| `audit.py scan` ×5, `compare` ×2, `visual_qa.py manifest`, `checklist` ×2 ran with the exit codes above | **EXECUTED** | committed outputs, `logs/` |
| Committed `findings-*`, `inventory.md`, `compare.*`, `screens-manifest.json`, `qa-checklist-gameplay.md` are unmodified script output | **EXECUTED** | byte-for-byte |
| The before-scan summary is 40 = 0/16/19/5/0, 12 scanned, 3 skipped | **EXECUTED** | `findings-before.json#summary` vs `expected-findings.md` line 108 (read this round) |
| `fixed/` edits | **HAND-WRITTEN** | `fixed/README.md`; never compiled; untouched files `cmp`-identical to the fixture |
| `triage.md` | **HAND-WRITTEN** from the JSON | every `VA-` id in it exists in `findings-before.json` (checked by script) |
| Any screenshot, pixel diff, device run, Flutter/Unity/web build, checklist item status | **NOT RUN** | manifest and checklist say so; `visual_qa.py diff` never invoked |
| Touch-target and contrast findings are real on a rendered screen | **NOT RUN** (heuristic, static) | `confidence: heuristic` |

### Limitations

- The "project" is a text fixture built to be caught; real projects have computed values, theme extensions and interpolated template literals that the scanner does not inspect.
- No `style-profile.json` was passed (`--profile`), so no `intentional-exception` matching happened.
- `fixed/` keeps Unity broken on purpose; the compare demonstrates a partial fix.
- Severity is count-based across the whole tree; `--platform flutter|web|unity` per scan would avoid the cross-platform downgrades.

### Script observations — status after the final regeneration

| # | Earlier observation | Status | Evidence (final run) |
|---|---|---|---|
| C-1 | `box-shadow: var(--shadow-card)` parsed as a literal → 3 false findings | **FIXED** | after-scan: 9 findings, none on `web/`; `new: 0` |
| C-2 | web `icon.mixed-libraries` said `preferred: material` | **FIXED** | `preferred for web: @heroicons/react (tie broken alphabetically)`; flutter: `preferred for flutter: material (declared in the contract)` |
| C-3 | inventory-mode icon fix text self-contradictory | **FIXED** | "Keep material and replace the font_awesome_flutter icons …" |
| C-4 | count-based severity downgrades the untouched platform | **STILL PRESENT (by design), explained** | `compare.txt` line 2: "note: severity recomputed from project-wide occurrence counts after fixes; changed_severity entries are unchanged findings, not regressions" |
| C-5 | inventory mode exits 1 when heuristics fire at high | **FIXED (via the cap)** | heuristics capped at Medium → `inventory.md` summary `medium 9`, exit 0 |
| C-6 | `--out` echoes the full report | **FIXED** | one-line summaries in `logs/0[1-3]-*` |
| C-7 | page suggestions from source stems | **FIXED** | every shop finding says `pages/shop.md` (9 of 9 in `findings-after.md`) |
| C-8 | web icon tie-break alphabetical, points at the canonical `Button.tsx` | **STILL PRESENT** | `findings-before.json` VA-0024 at `web/components/Button.tsx:4` "keep @heroicons/react, replace lucide-react" — the library only the duplicate `CtaButton.tsx` used |
| C-9 | — | **NEW (design note)** | capping heuristics at Medium means a 32 × 32 close button on a primary screen (VA-0022) now ranks below a `15 px` font size (high). Defensible for an unconfirmed heuristic; `triage.md` re-ranks them by impact and says why |
| C-10 | — | **confirmed** | `visual_qa.py checklist` rejects unknown screen ids with the valid list, exit 2 (`logs/06-checklist-unknown-screen.stderr`) |
