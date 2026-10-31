# Visual Design Pro Max — end-to-end examples

Three worked examples for the `visual-direction`, `reference-analysis` and `visual-audit` skills (`.claude/skills/*`). Every example directory has a `README.md` with the same sections — **Purpose · Inputs (provenance) · Commands executed · Generated artifacts · Walkthrough · Verification level** — and a `logs/` folder with the raw stdout/stderr of each command. All commands are plain `python3` / `node` invocations from the repository root, exactly as a user would type them; the scripts were used, never modified.

**Several rounds.** The examples were produced, the script defects they exposed were reported, W2-A and W2-C fixed them over several rounds, and every example was regenerated from scratch each time with the same commands (Example A with the brief's combined `--genre … --style …` form). The committed artifacts are the last round (after QA pass 2, `docs/architecture/QA_REPORT.md`, and the per-state-colour generator round); hand-written content was corrected for the Example A board arithmetic (AD-1), touch targets (AD-5), spin-wheel and map legibility (AD-10) and two README count errors (N-2, N-3). `vd.py validate` — which now also checks component-state contrast — reports `0 error(s), 0 warning(s)` on both contracts. Each README keeps the earlier observations with a **FIXED / STILL PRESENT / NEW** status and evidence from the final run; Example B's `ground-truth-check.md` shows the rounds side by side.

| Example | What it shows | Skills / scripts | Verification level (summary) |
|---|---|---|---|
| **A** — [`example-a-japanese-cute-animal-puzzle/`](example-a-japanese-cute-animal-puzzle/README.md) · *Onet Garden*, Flutter + Flame mobile onet game | routes B + A: `genres` → `styles` → `profile --genre --style` → `init` → `page` ×3 → `validate` → `generate-tokens.cjs`; hand-written specs for 7 screens citing token paths; a drift fixture scanned before/after with `compare` (5 → 0 findings) | `vd.py`, `generate-tokens.cjs`, `audit.py` | **EXECUTED:** 19 script runs (numbered in the README), all exit 0 except the two before-scans (exit 1, as designed). **HAND-WRITTEN:** `screens.md` (incl. the portrait 6 × 8 board arithmetic and 48 hit areas), page override tables, the two Dart fixtures (synthetic, non-runnable). **HAND-COMPUTED:** contrast ratios not in `MASTER.md`. **ASSUMPTION:** bottom safe areas. **NOT RUN:** any build, render, screenshot, device check. |
| **B** — [`example-b-reference-driven-redesign/`](example-b-reference-driven-redesign/README.md) · *Pet Diary Redesign*, Flutter mobile app | route C from one reference image → `reference_analysis.py validate/summary` → `vd.py profile --reference` → `init` → `page` ×3 → `validate`; **ground-truth check** of every image observation against the real CSS (the "reference" is a render of the repository's own `preview/xiaomaomi-app.html`, not a user file); 3 screen specs with one functional exception each | `reference_analysis.py`, `vd.py` | **EXECUTED:** 10 script runs, all exit 0; final contract matches the CSS for brand, background, text, border, radius class, outline rule and (as classifications) both type faces; reward/warning stay gold `#F5A524`. **COPIED, not re-run:** `palette-extracted.json`. **HAND-WRITTEN:** `ground-truth-check.md`, `screens.md`, page tables. **NOT RUN:** rendering, image re-capture, device check. The PNG (77 KB) is the one artifact over the 60 KB cap. |
| **C** — [`example-c-consistency-audit/`](example-c-consistency-audit/README.md) · the skill's own static mixed Flutter / web / Unity fixture | `audit.py scan` with and without a contract (40 findings = 0/16/19/5/0, 13 distinct rule ids: the 12 minimum ids + `shadow.unlisted`), hand-written triage (seven questions × top 5, mandatory / recommendation / subjective / exception), a partially fixed copy (`lib/` + `web/` corrected, `unity/` left), re-scan and `compare` (31 resolved · 0 new · 9 unchanged · 8 severity changes with the tool's note); `visual_qa.py manifest` and `checklist` | `audit.py`, `visual_qa.py` | **EXECUTED:** 10 script runs (exit 1 for the two before-scans, 2 for the deliberate unknown-screen probe, 0 otherwise); outputs unmodified. **HAND-WRITTEN:** `fixed/` edits, `triage.md`. **NOT RUN:** every screenshot/pixel-diff cell; the fixture never compiles. |

## Reading order

1. Example A for the vocabulary (profile → tokens → MASTER → pages → audit).
2. Example B for how confidence grading behaves against a known answer — and which contract fields still need the user after a single-reference analysis.
3. Example C for how to read and rank findings, and what `compare` does and does not tell you after a partial fix.

## Script and QA observations — consolidated status after the final regeneration

Numbered per example (A-n, B-n, C-n, and QA pass 2's AD-n / N-n; evidence with values from the final `tokens.json` in each README).

**FIXED**
- `vd.py profile`: `--style` + `--genre` combinable (A-1); catalog route keeps seed background/surface/text (A-11), border follows the outline rule (A-10); reference route: px radius ladder → class (B-1), display/body typography split (B-2), lighter-tint outline rule (B-3), `palette.surfaces` (B-4), traceable accent (B-5), no rule fragments in anti-patterns (B-6), `product.kind` and roles kept.
- Token derivation: on-colours chosen per fill (A-12, B-10); fill walks listed in `unknowns` (A-13); panel outlines `border`, interactive outlines `borderInteractive` (A `#A88655` 3.16–3.38:1, B `#AC8558`) (AD-2, A-16); pressed ≠ outline (AD-3); non-overshooting progress easing (AD-4); per-state labels — pressed `#FFFFFF` (A 4.93:1, B 5.34:1) and secondary `brand.700` (A 4.93:1, B 5.34:1) (A-14, A-15, B-11, B-12); `pressDuration` 90 ms (AD-6); `brand.700` selection outline (AD-8); neutral.900-tinted shadows, no pure black (AD-9). Last round: focus ring on a distinct brand step, ≥ 3:1 vs background and surface (A `#740420` 11.01 / 11.79:1, B `#DD5E06` 3.48 / 3.70:1), checked by `vd.py validate`; tappable HUD capsules get `component.hud.chipInteractive` with `borderInteractive` (closes the "wallet wears decorative border" leftover; used in Example A's specs).
- `vd.py init` creates `--output-dir` (A-2); complete catalog under 60 KB (A-3); `vd.py validate`: token→token remaps not drift (A-5, B-8), `Expires` rule documented (A-6), component-state contrast checked.
- `audit.py`: `var()`/`none` shadows (C-1); per-platform icon preference (C-2, C-3); heuristics capped at Medium (C-5); one-line `--out` summary (A-7, C-6); page slugs (A-8, C-7); role-based fix text for far tokens (A-9); `compare` explains `changed_severity` (C-4). `visual_qa.py checklist` rejects unknown screen ids (C-10).
- Example content: Example A board fits 375/390/430 portrait with ≥ 48 pitch (AD-1); ≥ 48 hit areas everywhere (AD-5); spin-wheel dividers 3.11–3.17:1 and completed map nodes ring 5.49:1 / number 8.38:1 (AD-10); run count 19 (N-2); Example B "10 of 16" (N-3); index rule-id count 13.

**FIXED with a residual**
- AD-7: reward `#FFC83D` is now separate from warning `#F5A524`, but the two golds are 1.32:1 apart (H 43° vs 37°) and reward vs accent `#FFD23F` is 1.07:1; Example A's specs add non-colour cues (hand glyph on hints, outlines on stars).
- AD-8: the selected outline `#BA4A66` is 4.60–4.93:1 against tile and board and 2.29:1 against the CTA fill, but only 1.46:1 against the idle outline `#A88655`; the spec pairs it with width (3 → 4) and scale.

**STILL PRESENT**
- Generated catalog text still says "close X 44dp" (Example A specs override it to 48).
- `style.confidence` counted, not weighed (B-7); no `palette_observed` vs `extract-colors` cross-check (B-9); catalog prose vs tokens (A-4, documented); count-based severity after partial fixes (C-4, labelled); alphabetical web icon tie-break (C-8).

**NEW / residual**
- B's focus ring `#DD5E06` passes 3:1 against background and surface but is 1.32:1 against the orange CTA fill; the 2 px offset keeps it over the background, so it is not a defect.
- None other found in the final round. All contrast figures above that are not in a `MASTER.md` table are hand-computed from hex values.

Nothing in these examples was built, rendered or run on a device. Statements about screens are specifications written against the generated contracts, and every README says so per claim.
