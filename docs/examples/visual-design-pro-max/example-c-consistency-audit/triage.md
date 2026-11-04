# Triage — `drift-project` fixture audited against its `tokens.json` (hand-written)

Source of every number: `findings-before.json` (40 findings: critical 0 · high 16 · medium 19 · low 5 · info 0; platform `mixed`; 12 files scanned, 3 skipped), `findings-after.json` (9 findings after fixing only `lib/` and `web/`), `compare.txt`. Finding ids (`VA-nnnn`) are those of the **before** scan of the final regeneration (ids were renumbered when the heuristic findings moved from High to Medium). The "simulated project" is `.claude/skills/visual-audit/scripts/tests/fixtures/drift-project/` — a static, non-runnable, mixed Flutter / web / Unity text fixture; nothing was built or rendered.

Contract (fixture `tokens.json`): palette `primary #3B5BDB · onPrimary #FFFFFF · accent #FF8A4C · background #FFF8F0 · surface #FFFFFF · text #1A1A2E · textMuted #6B6B80 · reward #FFD43B · danger #E03E3E`; radius scale `4, 8, 16, 24, 9999`; spacing `4, 8, 12, 16, 24, 32`; fontSize `12, 14, 16, 20, 24, 32`; families `Fredoka, Nunito`; durations `120, 200, 350`; two shadows (`sm = 0 2px 8px rgba(0,0,0,.10)`, `md = 0 4px 4px rgba(0,0,0,.20)`).

## 1. Findings grouped by severity (before)

### High (16) — exact literal on a primary screen, or ≥ 3 occurrences project-wide

| Rule | Ids | Where | Evidence |
|---|---|---|---|
| `color.off-palette` ×3 | VA-0001, 0006, 0008 | `lib/screens/shop.dart:12`, `unity/Assets/Scripts/ShopPanel.cs:16`, `unity/Assets/UI/Shop.uss:3` | `#E91E63` (pink) in Flutter, C# (`TryParseHtmlString`) and USS (`rgb(233, 30, 99)`); nearest `semantic.color.danger #E03E3E` at 28.0 |
| `radius.off-scale` ×3 | VA-0002, 0009, 0010 | `shop.dart:19`, `Shop.uss:4`, `Shop.uss:5` | `13` on a `4, 8, 16, 24` scale; nearest 16 |
| `font-family.unlisted` | VA-0003 | `shop.dart:26` | `'Comic Sans MS'` — primary screen |
| `font-size.off-scale` ×4 | VA-0004, 0012, 0013, 0016 | `shop.dart:26`, `Shop.uss:11`, `CtaButton.tsx:8`, `shop.css:11` | `15` on `12, 14, 16, 20, 24, 32` |
| `duration.off-scale` ×5 | VA-0005, 0007, 0011, 0014, 0015 | `shop.dart:35`, `ShopPanel.cs:20` (`0.337f` s), `Shop.uss:7`, `CtaButton.tsx:9`, `shop.css:7` | `337 ms` on `120, 200, 350` |

### Medium (19) — secondary file or 1–2 occurrences, and **every heuristic finding** (capped at Medium by the scanner)

- Heuristic / recommendation, capped: `touch.target-too-small` VA-0022 (`shop.dart:30`, 32 × 32 `IconButton`, primary screen) and VA-0034 (`shop.css:15`, `.icon-btn` 28 × 28); `text.contrast-risk` VA-0035 (`shop.css:22`, `#FFD43B` on `#FFF8F0` → 1.35:1); `component.duplicate-implementation` VA-0017 (`MainButton` vs `PrimaryButton`), VA-0025 (`CtaButton` vs `Button`).
- Rule: `icon.mixed-libraries` VA-0018 (flutter: material + font_awesome_flutter, "preferred for flutter: material (declared in the contract)"), VA-0024 (web: reported at `web/components/Button.tsx:4`, the lucide import, "preferred for web: @heroicons/react (tie broken alphabetically)"); `spacing.off-scale` VA-0019, 0020, 0023, 0028, 0031, 0032 (`10` and `18`); `shadow.variant-explosion` VA-0021 (3 distinct, 2 allowed); `color.off-palette` VA-0026, 0029 (`#1E88E5`, count 2, web only); `radius.off-scale` VA-0027, 0030 (`7`); `font-family.unlisted` VA-0033 (`Poppins`).

### Low (5) — cosmetic

`color.near-duplicate` VA-0036 (`#FF8B4D` vs accent, 0.8), VA-0038 (`#FA804F`, 8.2), VA-0039 (`rgb(255,139,77)`, 0.8); `shadow.unlisted` VA-0037 (`0 5px 13px rgba(0,0,0,.25)` in Dart), VA-0040 (same in CSS).

### Not reported — and correctly so (negative oracle)

`Color(0x66000000)` scrim (alpha → inventory only), `rgba(255,138,76,0.9)` (accent with alpha), `.hero-shadow` (equals `--shadow-card`), `Color32(59,91,219,255)` and `DOFade(1f, 0.2f)` (on contract), everything under `build/`, `web/node_modules/` and `lib/screens/shop.g.dart` (3 skipped files).

## 2. The seven questions for the top five

Ranking: user impact first (accessibility beats brand), then breadth (platforms), then count. **This ranking deliberately disagrees with the scanner's severity for T2 and T3**: the scanner caps heuristic findings at Medium because it cannot see padding or rendered backgrounds; an art director ranks them first *pending device confirmation*, because if they are real they block users, not just brand consistency.

### T1 — Pink `#E91E63` on the shop surface on all three platforms (VA-0001 / 0006 / 0008, high)

1. **Where / evidence** — `lib/screens/shop.dart:12` `Color(0xFFE91E63)`; `unity/Assets/Scripts/ShopPanel.cs:16` `ColorUtility.TryParseHtmlString("#E91E63", …)`; `unity/Assets/UI/Shop.uss:3` `rgb(233, 30, 99)`.
2. **Evidence quality** — exact literal match (`confidence: exact`), three files, same normalised hex.
3. **Severity + impact** — High: a hue that exists nowhere in the palette, on a primary (`screens/`) file, three occurrences. The shop reads as a different product than Home on every platform.
4. **Violated rule** — `tokens.semantic.color / primitive.color (allowed set)`; colour drift budget 0.
5. **Fix** — Do **not** take "nearest" literally (`danger #E03E3E` is an error red). Decide the role: shop background → `semantic.color.background #FFF8F0` or `surface`; if the product wants a promo tint, add it to `tokens.json` once and reference it from all three stacks. Order: tokens → shared theme (`app_theme.dart`, `styles.css`, `Theme.uss`) → screens.
6. **Files** — `lib/screens/shop.dart`, `unity/Assets/Scripts/ShopPanel.cs`, `unity/Assets/UI/Shop.uss` (+ `tokens.json` if a role is added).
7. **Verification** — re-scan: no `color.off-palette` with `#E91E63`; `compare` lists all three under *Resolved*. **Result here:** Flutter resolved; the two Unity ones remain (after-ids VA-0001, VA-0003) and were **downgraded high → medium only because the project-wide count fell from 3 to 2** — the Unity screens did not improve (`compare.txt` note).

### T2 — 32 × 32 close button on the shop (VA-0022, medium per scanner, heuristic)

1. **Where / evidence** — `lib/screens/shop.dart:30` `SizedBox(width: 32, height: 32, child: IconButton(…))`.
2. **Evidence quality** — heuristic (`[heuristic]`): padding and hit-test slop are invisible statically.
3. **Severity + impact** — scanner: Medium (heuristic cap). Triage: first priority to confirm on device — a 32 dp target on the close control of a purchase surface is below the 48 dp Android / 44 pt iOS minimum; mis-taps here are a trust and accessibility problem.
4. **Violated rule** — `touch.target-too-small` (contract `touchTarget.min 44`); `ux-audit-checklist.md` D1.
5. **Fix** — grow the box to 48 (as in `fixed/`) or give the `IconButton` 48 constraints while keeping a 24 glyph.
6. **Files** — `lib/screens/shop.dart`.
7. **Verification** — static: VA-0022 absent after re-scan (**resolved**); runtime: `integration_test` `tester.getSize(find.byType(IconButton))` ≥ 48 — **NOT RUN**.

### T3 — Reward yellow text on cream (VA-0035, medium per scanner, heuristic)

1. **Where / evidence** — `web/shop.css:22` `.promo { color: #FFD43B; background: #FFF8F0 }`.
2. **Evidence quality** — computed from two in-palette literals in one rule block; ratio 1.35:1. The rendered background could differ — confirm on a screenshot.
3. **Severity + impact** — scanner: Medium (heuristic cap). Triage: if the rendered pair is as declared, 1.35:1 fails every WCAG threshold; promo copy is unreadable.
4. **Violated rule** — `text.contrast-risk`; contract QA "contrast ≥ 4.5:1". Both colours are *in* the palette — a pairing rule, not a palette rule.
5. **Fix** — text in `--color-text #1A1A2E` (or `onPrimary` on a `primary` plate); keep `#FFD43B` for reward icons/badges, never for text on light surfaces.
6. **Files** — `web/shop.css` (+ any inline `.promo` colour).
7. **Verification** — re-scan: VA-0035 absent (**resolved**); rendered contrast measurement — **NOT RUN**.

### T4 — 337 ms transitions on five surfaces (VA-0005 / 0007 / 0011 / 0014 / 0015, high)

1. **Where / evidence** — `shop.dart:35` `Duration(milliseconds: 337)`, `ShopPanel.cs:20` `.DOScale(1.1f, 0.337f)`, `Shop.uss:7` `transition-duration: 337ms`, `CtaButton.tsx:9` `transitionDuration: '337ms'`, `shop.css:7` `transition: all 337ms ease-in`.
2. **Evidence quality** — exact; the C# seconds value is normalised to ms.
3. **Severity + impact** — High by count (5). 337 vs 350 is invisible alone and visible as jitter when two surfaces animate together.
4. **Violated rule** — `tokens.primitive.duration (allowed set 120, 200, 350)`; duration budget ≤ 1 per page with reason.
5. **Fix** — reference the token (`AppMotion.slow`, a CSS duration variable, a C# constant). Subjective: 337 → 350 (`slow`); the fixed copy used `--duration-base` (200) for the shop hero, a design choice.
6. **Files** — the five above.
7. **Verification** — re-scan: three resolved (Flutter, two web); two Unity remain, downgraded to medium (count 2). Runtime timing — **NOT RUN**.

### T5 — Comic Sans and Poppins (VA-0003 high, VA-0033 medium)

1. **Where / evidence** — `lib/screens/shop.dart:26` `fontFamily: 'Comic Sans MS'`; `web/shop.css:6` `font-family: "Poppins", sans-serif`.
2. **Evidence quality** — exact family-name match against `Fredoka, Nunito`.
3. **Severity + impact** — High on the primary Flutter screen, Medium in the web stylesheet (count 1). Typography is the fastest brand tell after colour.
4. **Violated rule** — `font-family.unlisted`; font-family budget 0.
5. **Fix** — `AppText.title` / `AppText.body` in Dart, `var(--font-display)` / `var(--font-body)` in CSS; add a third family to `tokens.json` first if it is genuinely wanted.
6. **Files** — `lib/screens/shop.dart`, `web/shop.css`.
7. **Verification** — re-scan: both **resolved**; inventory `families` shrinks from `Comic Sans MS, Fredoka, Nunito, Poppins` to `Fredoka, Nunito`.

Honourable mentions, same shape: radius `13` ×3 / `7` ×2 (scanner: snap to 16 / 8; **subjective** — 12 if the contract gains that step), font size `15` ×4 (scanner says 14 by distance; body copy should be 16 — judgement), the two duplicate buttons (reuse the canonical one), the two icon-library mixes (one per platform — **subjective**; for web the scanner's alphabetical tie-break points at the canonical `Button.tsx`, so `fixed/` kept lucide and deleted heroicons — README C-8), `18`/`10` spacing (→ 16/8).

## 3. Classification

| Class | Findings | Why |
|---|---|---|
| **Mandatory rule** (kind `rule`, exact) | `color.off-palette` (5), `radius.off-scale` (5), `font-size.off-scale` (4), `font-family.unlisted` (2), `spacing.off-scale` (6), `duration.off-scale` (5), `icon.mixed-libraries` (2), `shadow.variant-explosion` (1), `shadow.unlisted` (2), `color.near-duplicate` (3) | literal value not in the contract; the contract, not taste, decides. `#FF8B4D` is a typo of `#FF8A4C` |
| **Recommendation** (kind `recommendation`, heuristic, capped at Medium) | `touch.target-too-small` (2), `text.contrast-risk` (1), `component.duplicate-implementation` (2) | the scanner cannot see padding, rendered backgrounds or intent; confirm on device / in review. Two of them (T2, T3) still lead the triage on impact |
| **Subjective** (needs a designer) | snap direction for `13`, `7`, `15`, `18`, `10`; which icon library survives per platform; 337 → 350 or 200; whether the shop may own a promo tint | the scanner proposes the nearest step; the design-system owner chooses |
| **Intentional exception** (legal only if declared) | none declared — no `style-profile.json` was passed, so `--profile` exceptions could not match. Candidate a team might *declare*: a promo hue for the shop (then in `tokens.json` + `pages/shop.md`, not as a literal). **Not** an exception: the Unity leftovers in `fixed/` — unfinished work kept on purpose to show a partial fix |

## 4. Fix plan order (tokens → shared components → screens)

1. **Tokens** — none missing for the Flutter/web fixes; decide whether the web sheet needs a 350 ms variable and whether a promo tint joins the palette.
2. **Shared components** — delete `MainButton` (`rewards.dart`) and `CtaButton.tsx`; route callers to `PrimaryButton` / `Button`; one icon library per platform (`package.json`, `pubspec.yaml`).
3. **Screens** — `shop.dart`, `shop.css`; then the Unity pair (`ShopPanel.cs`, `Shop.uss`), left open here.

## 5. What the re-scan and `compare` say

`compare.txt`: **resolved 31 · new 0 · unchanged 9 · changed_severity 8** (exit 0), with the tool's note: "severity recomputed from project-wide occurrence counts after fixes; changed_severity entries are unchanged findings, not regressions".

- Resolved: every Flutter and web finding (31 of 31 in those trees); `web/` is clean after the fix.
- Unchanged (9) and changed-severity (8): the Unity findings. Seven dropped high → medium and one medium → low **only because the project-wide count shrank** — "same defect, smaller crowd", not progress.
- New (0).

## 6. Screenshot / runtime matrix

| Screen × device | Status |
|---|---|
| home / shop / rewards × phone-s / phone-m / phone-l | **NOT RUN** — `screens-manifest.json` holds capture instructions; no app, no baseline, `visual_qa.py diff` not invoked |
| gameplay checklist (`qa-checklist-gameplay.md`, 37 items from the Example A profile: 6 criteria, 20 generic, 11 anti-patterns) | every item **NOT RUN** |

The report is therefore **INCOMPLETE** by the skill's own rule (any NOT RUN cell makes it so); it is complete as a *static* audit.
