# Screenshot and visual-regression QA (`scripts/visual_qa.py diff / checklist / manifest`)

## 1. What a pixel diff proves — and what it does not

| Proves | Does not prove |
|---|---|
| Two renders of the same screen on the same device/scale differ (or not) beyond a threshold | That the UI is correct, on-brand, or usable (a wrong baseline passes forever) |
| Where they differ (bbox) — enough to route to a screen/component | Why they differ (font fallback, timing, data, locale, anti-aliasing all look alike) |
| A change touched a region it should not have (ignore regions make this testable) | Drift that the baseline already contained |
| Cross-device consistency of **layout** when the same screen is captured on the matrix (compare against per-device baselines, never across devices) | Interaction quality, motion, feel |

Therefore: pixel diff = regression gate, not an audit. The audit is `scripts/audit.py` + `references/ux-audit-checklist.md`; the diff
only guards against *unintended* change after a fix plan is applied. Baselines are reviewed by a human once,
then frozen with their capture conditions recorded (section 4).

## 2. Diff method (stdlib + optional Pillow)

```bash
python3 scripts/visual_qa.py diff a.png b.png [--threshold 0.5] [--tolerance 16] [--ignore x0,y0,x1,y1]... [--out diff.png] [--json]
```
- Load with Pillow (`PIL.Image`). Pillow missing or image unreadable → `{"status": "BLOCKED", "reason": …}`, exit 3.
  Different dimensions → `BLOCKED` with `reason: size mismatch 390x844 vs 430x932` (never resize silently).
- Convert both to RGB. Per pixel: `changed = max(|ΔR|,|ΔG|,|ΔB|) > tolerance` (default 16 of 255, absorbs
  anti-aliasing and JPEG-ish noise; `0` for exact mode).
- `--ignore` rectangles (pixel coords, inclusive-exclusive) are masked **before** counting; typical uses:
  status bar (`0,0,W,47` on 390×844 iOS), clock/battery, FPS counter, live score, ad slots, animated
  particles. Masked pixels are excluded from the denominator too.
- `diff_ratio = changed / (W·H − masked)`; `status = FAIL if diff_ratio*100 > threshold (percent) else PASS`.
  Default threshold 0.5 % (≈ 1 650 px on 390×844): catches a moved button or colour change, tolerates
  sub-pixel text shimmer. Game screens with particles: raise to 2 % **and** mask the effect layer rather
  than raising further.
- `bbox` = `[x0,y0,x1,y1]` of all changed pixels (`None` when PASS with 0 changes). Also report
  `clusters`: connected components of changed pixels on a 8-px grid, top 5 by area — points the human at
  the component, not just the extent.
- `--out diff.png`: side-by-side a | b | heat overlay (changed = red at 70 % over greyscale b); written
  only with Pillow.
- Exit: `0` PASS, `1` FAIL, `3` BLOCKED, `2` usage error. JSON shape: `status`, `diff_ratio` (fraction), `diff_percent`, `bbox`, plus `clusters`,
  `changed_pixels`, `masked_pixels`, `masked_ratio`, `tolerance`, `threshold`, `size`, `diff_image`.

Implementation note: pure-Python per-pixel loops are fine up to ~2 MP (430×932×3 ≈ 1.2 M channel reads
< 1 s). For 1440-wide desktop captures use `Image.getdata()` and `zip` or `ImageChops.difference` +
`point` + `getbbox` (all Pillow, no numpy).

## 3. Device matrix (`python3 scripts/visual_qa.py devices`) (logical px; capture at 2× or 3× DPR but compare at the same DPR as the baseline)

| Name | Logical size | DPR | Represents | Mandatory for |
|---|---|---|---|---|
| `phone-s` | 375×667 | 2 | iPhone SE / small Android | all mobile games (smallest safe area) |
| `phone-m` | 390×844 | 3 | iPhone 14/15, most Android | all mobile |
| `phone-l` | 430×932 | 3 | iPhone Pro Max, large Android | all mobile |
| `tablet` | 768×1024 | 2 | iPad / Android tablet, portrait | if `product.platforms` includes `tablet` |
| `desktop` | 1440×900 | 1 (and 2 if Retina baselines exist) | web / desktop | if `web` or `desktop` |

Default rows per stack: mobile stacks `phone-s phone-m phone-l`; `web` `desktop phone-m`; `--devices` overrides, `--profile` adds `tablet`/`desktop` from `product.platforms`.

Orientation follows `product.orientation`; landscape games capture the matrix transposed.
Baseline file naming: `baselines/<screen>/<device>@<dpr>x[-<state>][-dark].png`. One baseline per
device — never compare phone-m against phone-l.

## 4. Capture guidance per platform (mechanism names only; `python3 scripts/visual_qa.py manifest --stack <stack> --screens …` emits these as instructions, never executes)

| Stack | Mechanism | Determinism notes |
|---|---|---|
| Flutter / Flame | `integration_test` + `IntegrationTestWidgetsFlutterBinding.takeScreenshot('<name>')`; golden tests (`matchesGoldenFile`) for widget-level; `flutter drive --driver … --target …` | Pin `window.physicalSize`/`devicePixelRatio` via `tester.view`; disable animations with `tester.binding.transitionDuration`/`timeDilation`; use fixed seed data; `pumpAndSettle` before capture; fonts must be bundled (no network) |
| Unity (uGUI / UI Toolkit) | `ScreenCapture.CaptureScreenshot(path, superSize)` or `Camera.Render` to `RenderTexture` + `Texture2D.ReadPixels`; Play Mode tests via Unity Test Framework; Device Simulator package for the matrix | Set `Screen.SetResolution`, fixed `Time.timeScale`/`Application.targetFrameRate`, disable particle systems or mask them, `DOTween.timeScale = 0` after reaching end state, deterministic seeds |
| Web (React/Next/Vue/Svelte/Tailwind) | Playwright `page.screenshot({fullPage:false})` with `page.setViewportSize`, `deviceScaleFactor`, `colorScheme`, `reducedMotion: 'reduce'`; `page.addStyleTag` to kill transitions (`*{transition:none!important;animation:none!important}`) | Wait for `document.fonts.ready` and network idle; mock clock (`page.clock`) for timers; freeze data via route mocks; mask with Playwright's `mask:` option or `--ignore` |
| SwiftUI / Compose (native) | XCTest `XCUIScreen.main.screenshot()` / Compose `captureToImage()` + Roborazzi/Paparazzi | Named simulators/emulators per matrix row, fixed locale, "Reduce Motion" on |

All four: capture after the screen's "settled" state (no in-flight animation), same locale, same seed,
same OS theme; record these in the baseline sidecar `baselines/<screen>/<device>.json`
(`{captured_with, app_version, locale, theme, dpr, ignore_regions, notes}`), because a diff without the
sidecar cannot be reproduced and is reported as BLOCKED by `checklist`.

## 5. Reporting rules (PASS / FAIL / BLOCKED / NOT RUN)

| Status | Meaning | Required fields |
|---|---|---|
| **PASS** | Compared, `diff_ratio` ≤ threshold | both paths, ratio, threshold, tolerance, masks |
| **FAIL** | Compared, above threshold | + bbox, clusters, diff image path, suspected screen/component, link to the finding (`VA-…`) if the change is drift |
| **BLOCKED** | Could not compare: Pillow missing, unreadable/missing image, size mismatch, missing baseline sidecar, capture tool unavailable in this environment | `reason` string naming the exact blocker and what would unblock it |
| **NOT RUN** | Nobody attempted it (no capture produced for this screen/device, or the matrix row is not mandatory for this product) | the reason it was not attempted; never left blank |

Rules:
1. Every (screen × device) cell of the mandatory matrix appears in the report with one of the four statuses.
2. BLOCKED is never summarised as PASS; a report with any BLOCKED cell carries the top-line status
   "INCOMPLETE" and lists the blockers.
3. A FAIL that the human then accepts becomes the **new baseline** with the sidecar updated and a journal
   line (`CHANGELOG.md` in `design-system/<slug>/`) — it is never relabelled PASS in place.
4. Thresholds and masks are part of the result; changing them after seeing a FAIL requires a note.
5. `visual_qa.py` cannot capture; captures are produced by the project's own test tooling or by hand.
   The final report must say which: "captured by Playwright in CI" vs "captured manually by <who>" vs NOT RUN.
6. Real Flutter/Unity app capture is expected to be **NOT RUN** in this repository's own verification (no
   app here); the fixture-generated synthetic images (Pillow, in-test) cover `diff` logic only — state this
   limitation verbatim in the report's "Known limitations" row.

## 6. `checklist` and `manifest` (brief)

- `python3 scripts/visual_qa.py checklist --profile style-profile.json [--screen gameplay] [--format md|json]`: emits
  `qa_criteria[]` from the profile + generic per-screen items from `references/ux-audit-checklist.md` sections A–G
  filtered by `product.kind` and screen. `--screen` accepts only the ids `home gameplay level-select pause win lose settings shop rewards profile tutorial` or the name of a
  `pages/<name>.md` next to the profile; anything else exits 2 with the valid list. Each id maps to an item group
  (`level-select` → menu, `pause`/`tutorial` → popup, `win`/`lose` → result, `rewards` → reward, `profile` → settings). Each item has `status: NOT RUN` by
  default so the auditor flips them.
- `python3 scripts/visual_qa.py manifest --stack <stack> --screens home,gameplay,shop --out screens.json`: for each screen × matrix row,
  the mechanism row from section 4, target filename, settle condition, suggested masks, and
  `"executed": false, "note": "manual/automation hint, not executed"`. Unsupported stack → exit 2 with the
  supported list (never a fabricated mechanism). Supported: `flutter`, `flutter-flame`, `unity-ugui`, `unity-ui-toolkit`, `web`
  (aliases `react nextjs vue svelte html-tailwind astro nuxtjs`), `swiftui`, `jetpack-compose`. Files are named `<screen>_<device>.png`.
