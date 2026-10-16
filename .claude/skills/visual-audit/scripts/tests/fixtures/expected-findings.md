# Expected findings — `fixtures/drift-project` audited against its `tokens.json`

Test oracle for `audit.py scan fixtures/drift-project --contract fixtures/drift-project/tokens.json`.
Line numbers and normalised values were produced by `regex-selftest.py` (all assertions pass).
Severity follows scanner-spec §6.1 (`primary` = path segment `screens/`; `count` = project-wide
occurrences of the same normalised value for the same rule).

Expected header: `platform: mixed`, `scanned_files: 12`, `skipped_files: 3`
(`build/generated_junk.css`, `web/node_modules/x/index.css`, `lib/screens/shop.g.dart`).
Clean files with **zero** findings: `lib/theme/app_theme.dart`, `lib/screens/home.dart`,
`lib/widgets/primary_button.dart`, `web/styles.css`, `web/components/Button.tsx`, `unity/Assets/UI/Theme.uss`
(the last two only participate as the "other half" of a duplicate / icon pair whose finding points elsewhere).

## Findings (40)

| # | rule | severity | file:line | evidence (normalised) | why this severity |
|---|---|---|---|---|---|
| 1 | color.off-palette | high | lib/screens/shop.dart:12 | `Color(0xFFE91E63)` → #E91E63, nearest red.500 #E03E3E (27.9) | count 3 + primary |
| 2 | color.off-palette | high | unity/Assets/UI/Shop.uss:3 | `rgb(233, 30, 99)` → #E91E63 | count 3 |
| 3 | color.off-palette | high | unity/Assets/Scripts/ShopPanel.cs:16 | `TryParseHtmlString("#E91E63")` | count 3 |
| 4 | color.off-palette | medium | web/shop.css:3 | `#1E88E5`, nearest brand.500 #3B5BDB (38.1) | count 2, not primary |
| 5 | color.off-palette | medium | web/components/CtaButton.tsx:8 | `bg-[#1E88E5]` | count 2 |
| 6 | color.near-duplicate | low | lib/screens/shop.dart:18 | `Color(0xFFFF8B4D)` → #FF8B4D, accent #FF8A4C (0.8) | always low |
| 7 | color.near-duplicate | low | web/shop.css:12 | `rgb(255, 139, 77)` → #FF8B4D (0.8) | always low |
| 8 | color.near-duplicate | low | unity/Assets/Scripts/ShopPanel.cs:9 | `new Color(0.98f, 0.5f, 0.31f)` → #FA804F, accent (8.2) | always low |
| 9 | radius.off-scale | high | lib/screens/shop.dart:19 | `BorderRadius.circular(13)` → 13, nearest 16 | count 3 + primary |
| 10 | radius.off-scale | high | unity/Assets/UI/Shop.uss:4 | `border-top-left-radius: 13px` | count 3 |
| 11 | radius.off-scale | high | unity/Assets/UI/Shop.uss:5 | `border-top-right-radius: 13px` | count 3 |
| 12 | radius.off-scale | medium | web/shop.css:4 | `border-radius: 7px`, nearest 8 | count 2 |
| 13 | radius.off-scale | medium | web/components/CtaButton.tsx:8 | `rounded-[7px]` | count 2 |
| 14 | font-size.off-scale | high | lib/screens/shop.dart:26 | `fontSize: 15`, nearest 14 | count 4 + primary |
| 15 | font-size.off-scale | high | web/shop.css:11 | `font-size: 15px` | count 4 |
| 16 | font-size.off-scale | high | web/components/CtaButton.tsx:8 | `text-[15px]` | count 4 |
| 17 | font-size.off-scale | high | unity/Assets/UI/Shop.uss:11 | `font-size: 15px` | count 4 |
| 18 | font-family.unlisted | high | lib/screens/shop.dart:26 | `fontFamily: 'Comic Sans MS'` | primary |
| 19 | font-family.unlisted | medium | web/shop.css:6 | `font-family: "Poppins", sans-serif` → Poppins | count 1 |
| 20 | spacing.off-scale | medium | lib/screens/shop.dart:13 | `EdgeInsets.symmetric(horizontal: 18, …)` → 18, nearest 16 | count 3 (cap medium) |
| 21 | spacing.off-scale | medium | lib/screens/shop.dart:13 | `… vertical: 10)` → 10, nearest 8 | count 3 |
| 22 | spacing.off-scale | medium | web/shop.css:5 | `padding: 10px 18px` → 10 | count 3 |
| 23 | spacing.off-scale | medium | web/shop.css:5 | `padding: 10px 18px` → 18 | count 3 |
| 24 | spacing.off-scale | medium | web/components/CtaButton.tsx:8 | `px-[18px]` | count 3 |
| 25 | spacing.off-scale | medium | unity/Assets/UI/Shop.uss:6 | `padding: 10px` | count 3 |
| 26 | shadow.variant-explosion | medium | lib/screens/shop.dart:21 | `x=0 y=5 blur=13 spread=0 color=#000000 a=0.25` — distinct 3, allowed 2 | one per project |
| 27 | shadow.unlisted *(ext.)* | low | lib/screens/shop.dart:21 | same signature | per occurrence |
| 28 | shadow.unlisted *(ext.)* | low | web/shop.css:28 | `0 5px 13px rgba(0,0,0,0.25)` → same signature | per occurrence |
| 29 | duration.off-scale | high | lib/screens/shop.dart:35 | `Duration(milliseconds: 337)`, nearest 350 | count 5 |
| 30 | duration.off-scale | high | web/shop.css:7 | `transition: all 337ms ease-in` | count 5 |
| 31 | duration.off-scale | high | web/components/CtaButton.tsx:9 | `transitionDuration: '337ms'` | count 5 |
| 32 | duration.off-scale | high | unity/Assets/UI/Shop.uss:7 | `transition-duration: 337ms` | count 5 |
| 33 | duration.off-scale | high | unity/Assets/Scripts/ShopPanel.cs:20 | `.DOScale(1.1f, 0.337f)` → 337 | count 5 |
| 34 | icon.mixed-libraries | medium | lib/screens/shop.dart:3 | `import 'package:font_awesome_flutter/…'` — flutter group {material, font_awesome_flutter} | 2 libs |
| 35 | icon.mixed-libraries | medium | web/components/CtaButton.tsx:3 | `from '@heroicons/react/24/solid'` — web group {lucide-react, @heroicons/react} | 2 libs |
| 36 | component.duplicate-implementation | medium | lib/screens/rewards.dart:6 | `class MainButton extends StatelessWidget` vs `PrimaryButton` in lib/widgets/primary_button.dart:6 (divergent bodies) | fixed |
| 37 | component.duplicate-implementation | medium | web/components/CtaButton.tsx:5 | `export const CtaButton` vs `Button` in web/components/Button.tsx:8 (divergent) | fixed |
| 38 | touch.target-too-small | high | lib/screens/shop.dart:30 | `SizedBox(width: 32, height: 32, child: IconButton` → 32×32 < 44 [heuristic] | primary |
| 39 | touch.target-too-small | medium | web/shop.css:15 | `.icon-btn { width: 28px; height: 28px }` → 28×28 [heuristic] | not primary, ≥ 24 |
| 40 | text.contrast-risk | high | web/shop.css:22 | `.promo` #FFD43B on #FFF8F0 → ratio 1.35 | < 3.0 |

Expected `summary`: `{"critical": 0, "high": 18, "medium": 17, "low": 5, "info": 0}`.
Rule ids present: 12 of the 12 minimum ids (+ `shadow.unlisted` extension). Acceptance criterion 6 (≥ 6 ids) satisfied.

## Must NOT be reported (negative oracle)

| location | value | reason |
|---|---|---|
| lib/screens/shop.dart:34 | `Color(0x66000000)` | translucent black scrim → inventory `colors_with_alpha` only |
| lib/screens/shop.dart:21 | `Color(0x40000000)` inside BoxShadow | part of shadow signature, not a colour |
| lib/screens/home.dart:16 | `https://example.com` after `//` in a string | string-aware comment stripper; also no colour there |
| lib/screens/rewards.dart:17 | `EdgeInsets.all(16)` | 16 is on the spacing scale |
| web/shop.css:18 | `border-radius: 8px` on `.icon-btn` | on scale |
| web/shop.css:23 | `background: #FFF8F0` | in palette (participates only in the contrast pair) |
| web/shop.css:28 and :32 | `rgba(0, 0, 0, 0.25)` / `(…0.10)` | masked shadow rgba; `.hero-shadow` equals token `sm` → not a new variant |
| web/components/CtaButton.tsx:9 | `color: '#FFFFFF'` | in palette |
| web/styles.css (all) | `:root` definitions, `transition: transform 200ms`, `min-width/height: 44px` | all on contract |
| unity/Assets/UI/Shop.uss:12 | `rgba(255, 138, 76, 0.9)` | accent with alpha → in palette; alpha to inventory |
| unity/Assets/Scripts/ShopPanel.cs:11, :21, :22 | `Color32(59, 91, 219, 255)`, `DOFade(1f, 0.2f)`, `DOTween.To(…, 0.35f)` | on contract |
| build/, web/node_modules/, lib/screens/shop.g.dart | anything | skipped (3 files) |

## Expected inventory (subset, for assertion)

`radii`: `{"4":1,"8":4,"16":4,"9999":2,"13":3,"7":2}` (includes definitions);
`font_sizes`: `{"16":3,"12":1,"24":1,"14":1,"15":4}`; `durations`: `{"120":1,"200":5,"350":2,"337":5}`;
`shadows`: 3; `icon_libraries`: `["@heroicons/react","font_awesome_flutter","lucide-react","material"]`;
`font_families`: `["Comic Sans MS","Fredoka","Nunito","Poppins"]`; `colors["#E91E63"]`: 3.
(Exact counts of definitions may shift if W2-C decides to exclude `:root` sheets from inventory; the
findings table above is the binding part.)

## `compare` oracle

Scan the fixture → `before.json`. Edit a copy replacing `Color(0xFFE91E63)` in shop.dart with
`AppColors.danger` and moving the file's `Duration(milliseconds: 337)` line down by two lines →
`after.json`. Expected: `resolved: 1` (#1), `new: 0`, `unchanged: 39` (the moved duration finding is
unchanged because lines are ignored). Exit 0.

## Inventory-mode oracle (`--contract` omitted)

Only: `radius.variant-explosion` (5 distinct > 4), `font-family.variant-explosion` (4 > 3),
`icon.mixed-libraries` ×2, `component.duplicate-implementation` ×2, `touch.target-too-small` ×2,
`text.contrast-risk` ×1 → 10 findings, all medium except touch (high/medium as above) and contrast (high).

## Implementation notes (W2-C, after the fix round)

The table above is the Wave 1 oracle, kept verbatim. `test_audit.py` asserts it with two documented differences:

- Row 28: the second unlisted shadow (`0 5px 13px rgba(0,0,0,0.25)`) is on `web/shop.css:24` (`.promo`); the file has 29 lines, so line 24 is asserted.
- Row 35: the preferred icon library is now chosen **per platform** as the most-used library (tie → the contract's `$extensions.vdp.iconLibrary` when it is one of the tied libraries, else alphabetical). In the web group lucide-react and @heroicons/react tie 1–1 and the contract names `material`, so `@heroicons/react` is kept and the finding points at the library to replace: `web/components/Button.tsx:4` (`from 'lucide-react'`). Counts, severities and all other rows are unchanged (40 findings, 18/17/5/0).
- Inventory-mode oracle: the itemised list sums to 9 findings (the "10" is an arithmetic slip); 9 is asserted.
- Rows 38 and 40 (`touch.target-too-small` on `lib/screens/shop.dart:30`, `text.contrast-risk` on `web/shop.css:22`) are **medium**: heuristic rules are capped at medium (CC-10h, final fix round). Expected summary is therefore `{"critical": 0, "high": 16, "medium": 19, "low": 5, "info": 0}`; the 40 rows, files and lines are unchanged.
