# Visual audit — .claude/skills/visual-audit/scripts/tests/fixtures/drift-project
platform: mixed · contract: none (inventory mode) · scanned 12 files · skipped 3 · generated 2026-10-16T11:55:48Z

| critical | high | medium | low | info |
|---|---|---|---|---|
| 0 | 0 | 9 | 0 | 0 |

## Findings (by severity)

### MEDIUM
- **VA-0001** `component.duplicate-implementation` [recommendation] — lib/screens/rewards.dart:6 — `class MainButton extends StatelessWidget`
  divergent re-implementation of Button: `MainButton` in lib/screens/rewards.dart:6 vs `PrimaryButton` in lib/widgets/primary_button.dart:6 Nearest: canonical: lib/widgets/primary_button.dart (PrimaryButton)
  Fix: Reuse `PrimaryButton` from lib/widgets/primary_button.dart and delete `MainButton`; if the variant is intentional, make it a prop/variant of the canonical component · Verify: re-run `audit.py scan`; VA-0001 must be absent (`audit.py compare` lists it under resolved)
- **VA-0002** `icon.mixed-libraries` [rule] — lib/screens/shop.dart:3 — `import 'package:font_awesome_flutter/...'`
  flutter group uses 2 icon libraries: font_awesome_flutter (1 file, 2 uses), material (2 files, 2 uses); keep material, replace font_awesome_flutter Nearest: preferred for flutter: material (most used in the flutter group)
  Fix: Keep material and replace the font_awesome_flutter icons with material equivalents; if a second library is required, declare it in the profile · Verify: re-run `audit.py scan`; VA-0002 must be absent (`audit.py compare` lists it under resolved)
- **VA-0003** `font-family.variant-explosion` [recommendation] — lib/screens/shop.dart:26 — `fontFamily: 'Comic Sans MS'`
  4 distinct fontFamily values project-wide (> 3): Nunito x3, Fredoka x2, Comic Sans MS x1, Poppins x1
  Fix: Define a scale in tokens.json (`vd.py init` from the visual-direction skill) and re-run with --contract · Verify: re-run `audit.py scan`; VA-0003 must be absent (`audit.py compare` lists it under resolved)
- **VA-0004** `touch.target-too-small` [recommendation] — lib/screens/shop.dart:30 — `SizedBox( width: 32, height: 32, child: IconButton`
  [heuristic] Tappable control 32x32 is below the minimum touch target 44 (IconButton) Nearest: minimum 44
  Fix: Grow the control (or its padding / hit-test area) to at least 44x44; confirm the rendered hit area on device · Verify: re-run `audit.py scan`; VA-0004 must be absent (`audit.py compare` lists it under resolved)
- **VA-0005** `radius.variant-explosion` [recommendation] — lib/theme/app_theme.dart:17 — `BorderRadius.circular(4)`
  5 distinct radius values project-wide (> 4): 16 x4, 8 x4, 13 x3, 7 x2, 4 x1
  Fix: Define a scale in tokens.json (`vd.py init` from the visual-direction skill) and re-run with --contract · Verify: re-run `audit.py scan`; VA-0005 must be absent (`audit.py compare` lists it under resolved)
- **VA-0006** `icon.mixed-libraries` [rule] — web/components/Button.tsx:4 — `from 'lucide-react`
  web group uses 2 icon libraries: @heroicons/react (1 file, 1 use), lucide-react (1 file, 1 use); keep @heroicons/react, replace lucide-react Nearest: preferred for web: @heroicons/react (tie broken alphabetically)
  Fix: Keep @heroicons/react and replace the lucide-react icons with @heroicons/react equivalents; if a second library is required, declare it in the profile · Verify: re-run `audit.py scan`; VA-0006 must be absent (`audit.py compare` lists it under resolved)
- **VA-0007** `component.duplicate-implementation` [recommendation] — web/components/CtaButton.tsx:5 — `export const CtaButton`
  divergent re-implementation of Button: `CtaButton` in web/components/CtaButton.tsx:5 vs `Button` in web/components/Button.tsx:8 Nearest: canonical: web/components/Button.tsx (Button)
  Fix: Reuse `Button` from web/components/Button.tsx and delete `CtaButton`; if the variant is intentional, make it a prop/variant of the canonical component · Verify: re-run `audit.py scan`; VA-0007 must be absent (`audit.py compare` lists it under resolved)
- **VA-0008** `touch.target-too-small` [recommendation] — web/shop.css:15 — `.icon-btn { width: 28; height: 28 }`
  [heuristic] Tappable control 28x28 is below the minimum touch target 44 (.icon-btn) Nearest: minimum 44
  Fix: Grow the control (or its padding / hit-test area) to at least 44x44; confirm the rendered hit area on device · Verify: re-run `audit.py scan`; VA-0008 must be absent (`audit.py compare` lists it under resolved)
- **VA-0009** `text.contrast-risk` [recommendation] — web/shop.css:22 — `.promo { color: #FFD43B; background: #FFF8F0 }`
  [heuristic] Text #FFD43B on #FFF8F0 has contrast 1.35:1 (< 4.5:1) in `.promo` Nearest: needs >= 4.5:1 (3:1 for large text)
  Fix: Pair the text with a darker/lighter semantic colour (text / onPrimary / onAccent) or add a plate behind it; verify on the rendered background · Verify: re-run `audit.py scan`; VA-0009 must be absent (`audit.py compare` lists it under resolved)

## Inventory
colours (opaque, distinct 12): #FFFFFF×5 #1A1A2E×4 #3B5BDB×4 #FFF8F0×4 #E91E63×3 #FF8A4C×3 #1E88E5×2 #6B6B80×2 #FF8B4D×2 #FFD43B×2 #E03E3E×1 #FA804F×1
colours with alpha: #000000@0.40×1 #FF8A4C@0.90×1
radii: 16×4 8×4 13×3 7×2 9999×2 4×1 | font sizes: 15×4 16×3 12×1 14×1 24×1 | spacing: 10×3 12×3 18×3 24×3 16×2
families: Comic Sans MS, Fredoka, Nunito, Poppins | shadows: 3 distinct | durations: 200×5 337×5 350×2 120×1
icon libraries: flutter {font_awesome_flutter, material}, web {@heroicons/react, lucide-react}
components: Button (web/components/Button.tsx), CtaButton (web/components/CtaButton.tsx), MainButton (lib/screens/rewards.dart), PrimaryButton (lib/widgets/primary_button.dart)

## Notes
- inventory-only rules: no --contract given, only variant-explosion / icon / duplicate / touch / contrast rules evaluated
