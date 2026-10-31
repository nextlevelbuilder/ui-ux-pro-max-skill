# Visual audit — .claude/skills/visual-audit/scripts/tests/fixtures/drift-project
platform: mixed · contract: .claude/skills/visual-audit/scripts/tests/fixtures/drift-project/tokens.json · scanned 12 files · skipped 3 · generated 2026-10-16T11:55:48Z

| critical | high | medium | low | info |
|---|---|---|---|---|
| 0 | 16 | 19 | 5 | 0 |

## Findings (by severity)

### HIGH
- **VA-0001** `color.off-palette` [rule] — lib/screens/shop.dart:12 — `Color(0xFFE91E63)`
  Hard-coded colour #E91E63 not in tokens.json palette Nearest: semantic.color.danger #E03E3E (distance 28.0)
  Fix: Replace with the nearest token semantic.color.danger (#E03E3E) or a semantic colour that fits the role; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0001 must be absent (`audit.py compare` lists it under resolved)
- **VA-0002** `radius.off-scale` [rule] — lib/screens/shop.dart:19 — `BorderRadius.circular(13)`
  Corner radius 13 is not on the contract scale (4, 8, 16, 24, 9999); nearest step 16 (3 occurrences project-wide) Nearest: primitive.radius.step 16 (scale 4, 8, 16, 24, 9999)
  Fix: Use the corner radius step 16; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0002 must be absent (`audit.py compare` lists it under resolved)
- **VA-0003** `font-family.unlisted` [rule] — lib/screens/shop.dart:26 — `fontFamily: 'Comic Sans MS'`
  Font family 'Comic Sans MS' is not a contract family (Fredoka, Nunito) Nearest: contract families: Fredoka, Nunito
  Fix: Use the display or body family (Fredoka, Nunito); if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0003 must be absent (`audit.py compare` lists it under resolved)
- **VA-0004** `font-size.off-scale` [rule] — lib/screens/shop.dart:26 — `fontSize: 15`
  Font size 15 is not on the contract scale (12, 14, 16, 20, 24, 32); nearest step 14 (4 occurrences project-wide) Nearest: primitive.fontSize.step 14 (scale 12, 14, 16, 20, 24, 32)
  Fix: Use the font size step 14; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0004 must be absent (`audit.py compare` lists it under resolved)
- **VA-0005** `duration.off-scale` [rule] — lib/screens/shop.dart:35 — `Duration(milliseconds: 337)`
  Duration (ms) 337 is not on the contract scale (120, 200, 350); nearest step 350 (5 occurrences project-wide) Nearest: primitive.duration.step 350 (scale 120, 200, 350)
  Fix: Use the duration (ms) step 350; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0005 must be absent (`audit.py compare` lists it under resolved)
- **VA-0006** `color.off-palette` [rule] — unity/Assets/Scripts/ShopPanel.cs:16 — `ColorUtility.TryParseHtmlString("#E91E63")`
  Hard-coded colour #E91E63 not in tokens.json palette Nearest: semantic.color.danger #E03E3E (distance 28.0)
  Fix: Replace with the nearest token semantic.color.danger (#E03E3E) or a semantic colour that fits the role; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0006 must be absent (`audit.py compare` lists it under resolved)
- **VA-0007** `duration.off-scale` [rule] — unity/Assets/Scripts/ShopPanel.cs:20 — `.DOScale(1.1f, 0.337f)`
  Duration (ms) 337 is not on the contract scale (120, 200, 350); nearest step 350 (5 occurrences project-wide) Nearest: primitive.duration.step 350 (scale 120, 200, 350)
  Fix: Use the duration (ms) step 350; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0007 must be absent (`audit.py compare` lists it under resolved)
- **VA-0008** `color.off-palette` [rule] — unity/Assets/UI/Shop.uss:3 — `rgb(233, 30, 99)`
  Hard-coded colour #E91E63 not in tokens.json palette Nearest: semantic.color.danger #E03E3E (distance 28.0)
  Fix: Replace with the nearest token semantic.color.danger (#E03E3E) or a semantic colour that fits the role; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0008 must be absent (`audit.py compare` lists it under resolved)
- **VA-0009** `radius.off-scale` [rule] — unity/Assets/UI/Shop.uss:4 — `border-top-left-radius: 13px`
  Corner radius 13 is not on the contract scale (4, 8, 16, 24, 9999); nearest step 16 (3 occurrences project-wide) Nearest: primitive.radius.step 16 (scale 4, 8, 16, 24, 9999)
  Fix: Use the corner radius step 16; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0009 must be absent (`audit.py compare` lists it under resolved)
- **VA-0010** `radius.off-scale` [rule] — unity/Assets/UI/Shop.uss:5 — `border-top-right-radius: 13px`
  Corner radius 13 is not on the contract scale (4, 8, 16, 24, 9999); nearest step 16 (3 occurrences project-wide) Nearest: primitive.radius.step 16 (scale 4, 8, 16, 24, 9999)
  Fix: Use the corner radius step 16; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0010 must be absent (`audit.py compare` lists it under resolved)
- **VA-0011** `duration.off-scale` [rule] — unity/Assets/UI/Shop.uss:7 — `transition-duration: 337ms`
  Duration (ms) 337 is not on the contract scale (120, 200, 350); nearest step 350 (5 occurrences project-wide) Nearest: primitive.duration.step 350 (scale 120, 200, 350)
  Fix: Use the duration (ms) step 350; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0011 must be absent (`audit.py compare` lists it under resolved)
- **VA-0012** `font-size.off-scale` [rule] — unity/Assets/UI/Shop.uss:11 — `font-size: 15px`
  Font size 15 is not on the contract scale (12, 14, 16, 20, 24, 32); nearest step 14 (4 occurrences project-wide) Nearest: primitive.fontSize.step 14 (scale 12, 14, 16, 20, 24, 32)
  Fix: Use the font size step 14; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0012 must be absent (`audit.py compare` lists it under resolved)
- **VA-0013** `font-size.off-scale` [rule] — web/components/CtaButton.tsx:8 — `text-[15px]`
  Font size 15 is not on the contract scale (12, 14, 16, 20, 24, 32); nearest step 14 (4 occurrences project-wide) Nearest: primitive.fontSize.step 14 (scale 12, 14, 16, 20, 24, 32)
  Fix: Use the font size step 14; if intentional, add to `pages/cta-button.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0013 must be absent (`audit.py compare` lists it under resolved)
- **VA-0014** `duration.off-scale` [rule] — web/components/CtaButton.tsx:9 — `transitionDuration: '337ms'`
  Duration (ms) 337 is not on the contract scale (120, 200, 350); nearest step 350 (5 occurrences project-wide) Nearest: primitive.duration.step 350 (scale 120, 200, 350)
  Fix: Use the duration (ms) step 350; if intentional, add to `pages/cta-button.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0014 must be absent (`audit.py compare` lists it under resolved)
- **VA-0015** `duration.off-scale` [rule] — web/shop.css:7 — `transition: all 337ms ease-in`
  Duration (ms) 337 is not on the contract scale (120, 200, 350); nearest step 350 (5 occurrences project-wide) Nearest: primitive.duration.step 350 (scale 120, 200, 350)
  Fix: Use the duration (ms) step 350; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0015 must be absent (`audit.py compare` lists it under resolved)
- **VA-0016** `font-size.off-scale` [rule] — web/shop.css:11 — `font-size: 15px`
  Font size 15 is not on the contract scale (12, 14, 16, 20, 24, 32); nearest step 14 (4 occurrences project-wide) Nearest: primitive.fontSize.step 14 (scale 12, 14, 16, 20, 24, 32)
  Fix: Use the font size step 14; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0016 must be absent (`audit.py compare` lists it under resolved)

### MEDIUM
- **VA-0017** `component.duplicate-implementation` [recommendation] — lib/screens/rewards.dart:6 — `class MainButton extends StatelessWidget`
  divergent re-implementation of Button: `MainButton` in lib/screens/rewards.dart:6 vs `PrimaryButton` in lib/widgets/primary_button.dart:6 Nearest: canonical: lib/widgets/primary_button.dart (PrimaryButton)
  Fix: Reuse `PrimaryButton` from lib/widgets/primary_button.dart and delete `MainButton`; if the variant is intentional, make it a prop/variant of the canonical component · Verify: re-run `audit.py scan`; VA-0017 must be absent (`audit.py compare` lists it under resolved)
- **VA-0018** `icon.mixed-libraries` [rule] — lib/screens/shop.dart:3 — `import 'package:font_awesome_flutter/...'`
  flutter group uses 2 icon libraries: font_awesome_flutter (1 file, 2 uses), material (2 files, 2 uses); keep material, replace font_awesome_flutter Nearest: preferred for flutter: material (declared in the contract)
  Fix: Keep material and replace the font_awesome_flutter icons with material equivalents; if a second library is required, declare it in the profile · Verify: re-run `audit.py scan`; VA-0018 must be absent (`audit.py compare` lists it under resolved)
- **VA-0019** `spacing.off-scale` [rule] — lib/screens/shop.dart:13 — `EdgeInsets.symmetric(horizontal: 18, vertical: 10) → 10`
  Spacing 10 is not on the contract scale (4, 8, 12, 16, 24, 32); nearest step 8 (3 occurrences project-wide) Nearest: primitive.spacing.step 8 (scale 4, 8, 12, 16, 24, 32)
  Fix: Use the spacing step 8; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0019 must be absent (`audit.py compare` lists it under resolved)
- **VA-0020** `spacing.off-scale` [rule] — lib/screens/shop.dart:13 — `EdgeInsets.symmetric(horizontal: 18, vertical: 10) → 18`
  Spacing 18 is not on the contract scale (4, 8, 12, 16, 24, 32); nearest step 16 (3 occurrences project-wide) Nearest: primitive.spacing.step 16 (scale 4, 8, 12, 16, 24, 32)
  Fix: Use the spacing step 16; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0020 must be absent (`audit.py compare` lists it under resolved)
- **VA-0021** `shadow.variant-explosion` [rule] — lib/screens/shop.dart:21 — `x=0 y=5 blur=13 spread=0 color=#000000 a=0.25`
  distinct=3 allowed=2 shadow signatures project-wide: x=0 y=2 blur=8 spread=0 color=#000000 a=0.1 x3; x=0 y=4 blur=4 spread=0 color=#000000 a=0.2 x1; x=0 y=5 blur=13 spread=0 color=#000000 a=0.25 x2 Nearest: allowed signatures: x=0 y=2 blur=8 spread=0 color=#000000 a=0.1; x=0 y=4 blur=4 spread=0 color=#000000 a=0.2
  Fix: Map every shadow to a primitive.shadow token; delete the extra signatures; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0021 must be absent (`audit.py compare` lists it under resolved)
- **VA-0022** `touch.target-too-small` [recommendation] — lib/screens/shop.dart:30 — `SizedBox( width: 32, height: 32, child: IconButton`
  [heuristic] Tappable control 32x32 is below the minimum touch target 44 (IconButton) Nearest: minimum 44
  Fix: Grow the control (or its padding / hit-test area) to at least 44x44; confirm the rendered hit area on device · Verify: re-run `audit.py scan`; VA-0022 must be absent (`audit.py compare` lists it under resolved)
- **VA-0023** `spacing.off-scale` [rule] — unity/Assets/UI/Shop.uss:6 — `padding: 10px`
  Spacing 10 is not on the contract scale (4, 8, 12, 16, 24, 32); nearest step 8 (3 occurrences project-wide) Nearest: primitive.spacing.step 8 (scale 4, 8, 12, 16, 24, 32)
  Fix: Use the spacing step 8; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0023 must be absent (`audit.py compare` lists it under resolved)
- **VA-0024** `icon.mixed-libraries` [rule] — web/components/Button.tsx:4 — `from 'lucide-react`
  web group uses 2 icon libraries: @heroicons/react (1 file, 1 use), lucide-react (1 file, 1 use); keep @heroicons/react, replace lucide-react Nearest: preferred for web: @heroicons/react (tie broken alphabetically)
  Fix: Keep @heroicons/react and replace the lucide-react icons with @heroicons/react equivalents; if a second library is required, declare it in the profile · Verify: re-run `audit.py scan`; VA-0024 must be absent (`audit.py compare` lists it under resolved)
- **VA-0025** `component.duplicate-implementation` [recommendation] — web/components/CtaButton.tsx:5 — `export const CtaButton`
  divergent re-implementation of Button: `CtaButton` in web/components/CtaButton.tsx:5 vs `Button` in web/components/Button.tsx:8 Nearest: canonical: web/components/Button.tsx (Button)
  Fix: Reuse `Button` from web/components/Button.tsx and delete `CtaButton`; if the variant is intentional, make it a prop/variant of the canonical component · Verify: re-run `audit.py scan`; VA-0025 must be absent (`audit.py compare` lists it under resolved)
- **VA-0026** `color.off-palette` [rule] — web/components/CtaButton.tsx:8 — `bg-[#1E88E5]`
  Hard-coded colour #1E88E5 not in tokens.json palette Nearest: semantic.color.primary #3B5BDB (distance 38.1)
  Fix: No close token (nearest semantic.color.primary #3B5BDB is 38.1 away) — pick the semantic role (primary/accent/surface/text/success/danger/reward) that matches the element's purpose and use its token; if intentional, add to `pages/cta-button.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0026 must be absent (`audit.py compare` lists it under resolved)
- **VA-0027** `radius.off-scale` [rule] — web/components/CtaButton.tsx:8 — `rounded-[7px]`
  Corner radius 7 is not on the contract scale (4, 8, 16, 24, 9999); nearest step 8 (2 occurrences project-wide) Nearest: primitive.radius.step 8 (scale 4, 8, 16, 24, 9999)
  Fix: Use the corner radius step 8; if intentional, add to `pages/cta-button.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0027 must be absent (`audit.py compare` lists it under resolved)
- **VA-0028** `spacing.off-scale` [rule] — web/components/CtaButton.tsx:8 — `px-[18px]`
  Spacing 18 is not on the contract scale (4, 8, 12, 16, 24, 32); nearest step 16 (3 occurrences project-wide) Nearest: primitive.spacing.step 16 (scale 4, 8, 12, 16, 24, 32)
  Fix: Use the spacing step 16; if intentional, add to `pages/cta-button.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0028 must be absent (`audit.py compare` lists it under resolved)
- **VA-0029** `color.off-palette` [rule] — web/shop.css:3 — `#1E88E5`
  Hard-coded colour #1E88E5 not in tokens.json palette Nearest: semantic.color.primary #3B5BDB (distance 38.1)
  Fix: No close token (nearest semantic.color.primary #3B5BDB is 38.1 away) — pick the semantic role (primary/accent/surface/text/success/danger/reward) that matches the element's purpose and use its token; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0029 must be absent (`audit.py compare` lists it under resolved)
- **VA-0030** `radius.off-scale` [rule] — web/shop.css:4 — `border-radius: 7px`
  Corner radius 7 is not on the contract scale (4, 8, 16, 24, 9999); nearest step 8 (2 occurrences project-wide) Nearest: primitive.radius.step 8 (scale 4, 8, 16, 24, 9999)
  Fix: Use the corner radius step 8; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0030 must be absent (`audit.py compare` lists it under resolved)
- **VA-0031** `spacing.off-scale` [rule] — web/shop.css:5 — `padding: 10px 18px → 10`
  Spacing 10 is not on the contract scale (4, 8, 12, 16, 24, 32); nearest step 8 (3 occurrences project-wide) Nearest: primitive.spacing.step 8 (scale 4, 8, 12, 16, 24, 32)
  Fix: Use the spacing step 8; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0031 must be absent (`audit.py compare` lists it under resolved)
- **VA-0032** `spacing.off-scale` [rule] — web/shop.css:5 — `padding: 10px 18px → 18`
  Spacing 18 is not on the contract scale (4, 8, 12, 16, 24, 32); nearest step 16 (3 occurrences project-wide) Nearest: primitive.spacing.step 16 (scale 4, 8, 12, 16, 24, 32)
  Fix: Use the spacing step 16; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0032 must be absent (`audit.py compare` lists it under resolved)
- **VA-0033** `font-family.unlisted` [rule] — web/shop.css:6 — `font-family: "Poppins", sans-serif`
  Font family 'Poppins' is not a contract family (Fredoka, Nunito) Nearest: contract families: Fredoka, Nunito
  Fix: Use the display or body family (Fredoka, Nunito); if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0033 must be absent (`audit.py compare` lists it under resolved)
- **VA-0034** `touch.target-too-small` [recommendation] — web/shop.css:15 — `.icon-btn { width: 28; height: 28 }`
  [heuristic] Tappable control 28x28 is below the minimum touch target 44 (.icon-btn) Nearest: minimum 44
  Fix: Grow the control (or its padding / hit-test area) to at least 44x44; confirm the rendered hit area on device · Verify: re-run `audit.py scan`; VA-0034 must be absent (`audit.py compare` lists it under resolved)
- **VA-0035** `text.contrast-risk` [recommendation] — web/shop.css:22 — `.promo { color: #FFD43B; background: #FFF8F0 }`
  [heuristic] Text #FFD43B on #FFF8F0 has contrast 1.35:1 (< 4.5:1) in `.promo` Nearest: needs >= 4.5:1 (3:1 for large text)
  Fix: Pair the text with a darker/lighter semantic colour (text / onPrimary / onAccent) or add a plate behind it; verify on the rendered background · Verify: re-run `audit.py scan`; VA-0035 must be absent (`audit.py compare` lists it under resolved)

### LOW
- **VA-0036** `color.near-duplicate` [rule] — lib/screens/shop.dart:18 — `Color(0xFFFF8B4D)`
  Colour #FF8B4D is a near-duplicate of a contract colour (distance 0.8 <= 12) Nearest: semantic.color.accent #FF8A4C (distance 0.8)
  Fix: Replace with the semantic.color.accent token (#FF8A4C); if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0036 must be absent (`audit.py compare` lists it under resolved)
- **VA-0037** `shadow.unlisted` [rule] — lib/screens/shop.dart:21 — `BoxShadow(color: Color(0x40000000), blurRadius: 13, offset: Offset(0, 5))`
  Shadow signature not in tokens.primitive.shadow: x=0 y=5 blur=13 spread=0 color=#000000 a=0.25 Nearest: allowed: shadow.md = x=0 y=4 blur=4 spread=0 color=#000000 a=0.2; shadow.sm = x=0 y=2 blur=8 spread=0 color=#000000 a=0.1
  Fix: Use one of the contract shadows (primitive.shadow.md, primitive.shadow.sm); if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0037 must be absent (`audit.py compare` lists it under resolved)
- **VA-0038** `color.near-duplicate` [rule] — unity/Assets/Scripts/ShopPanel.cs:9 — `new Color(0.98f, 0.5f, 0.31f)`
  Colour #FA804F is a near-duplicate of a contract colour (distance 8.2 <= 12) Nearest: semantic.color.accent #FF8A4C (distance 8.2)
  Fix: Replace with the semantic.color.accent token (#FF8A4C); if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0038 must be absent (`audit.py compare` lists it under resolved)
- **VA-0039** `color.near-duplicate` [rule] — web/shop.css:12 — `rgb(255, 139, 77)`
  Colour #FF8B4D is a near-duplicate of a contract colour (distance 0.8 <= 12) Nearest: semantic.color.accent #FF8A4C (distance 0.8)
  Fix: Replace with the semantic.color.accent token (#FF8A4C); if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0039 must be absent (`audit.py compare` lists it under resolved)
- **VA-0040** `shadow.unlisted` [rule] — web/shop.css:24 — `box-shadow: 0 5px 13px rgba(0, 0, 0, 0.25)`
  Shadow signature not in tokens.primitive.shadow: x=0 y=5 blur=13 spread=0 color=#000000 a=0.25 Nearest: allowed: shadow.md = x=0 y=4 blur=4 spread=0 color=#000000 a=0.2; shadow.sm = x=0 y=2 blur=8 spread=0 color=#000000 a=0.1
  Fix: Use one of the contract shadows (primitive.shadow.md, primitive.shadow.sm); if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0040 must be absent (`audit.py compare` lists it under resolved)

## Inventory
colours (opaque, distinct 12): #FFFFFF×5 #1A1A2E×4 #3B5BDB×4 #FFF8F0×4 #E91E63×3 #FF8A4C×3 #1E88E5×2 #6B6B80×2 #FF8B4D×2 #FFD43B×2 #E03E3E×1 #FA804F×1
colours with alpha: #000000@0.40×1 #FF8A4C@0.90×1
radii: 16×4 8×4 13×3 7×2 9999×2 4×1 | font sizes: 15×4 16×3 12×1 14×1 24×1 | spacing: 10×3 12×3 18×3 24×3 16×2
families: Comic Sans MS, Fredoka, Nunito, Poppins | shadows: 3 distinct | durations: 200×5 337×5 350×2 120×1
icon libraries: flutter {font_awesome_flutter, material}, web {@heroicons/react, lucide-react}
components: Button (web/components/Button.tsx), CtaButton (web/components/CtaButton.tsx), MainButton (lib/screens/rewards.dart), PrimaryButton (lib/widgets/primary_button.dart)

## Notes
- none
