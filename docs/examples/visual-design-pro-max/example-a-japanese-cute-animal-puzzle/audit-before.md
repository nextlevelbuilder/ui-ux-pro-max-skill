# Visual audit — docs/examples/visual-design-pro-max/example-a-japanese-cute-animal-puzzle/drift-fixture
platform: flutter · contract: docs/examples/visual-design-pro-max/example-a-japanese-cute-animal-puzzle/project/design-system/onet-garden/tokens.json · scanned 4 files · skipped 0 · generated 2026-10-16T12:34:28Z

| critical | high | medium | low | info |
|---|---|---|---|---|
| 0 | 4 | 1 | 0 | 0 |

## Findings (by severity)

### HIGH
- **VA-0001** `color.off-palette` [rule] — lib/screens/shop_screen.dart:20 — `Color(0xFF8E24AA)`
  Hard-coded colour #8E24AA not in tokens.json palette Nearest: component.button.primary.outlineColor #972743 (distance 35.2)
  Fix: No close token (nearest component.button.primary.outlineColor #972743 is 35.2 away) — pick the semantic role (primary/accent/surface/text/success/danger/reward) that matches the element's purpose and use its token; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0001 must be absent (`audit.py compare` lists it under resolved)
- **VA-0002** `radius.off-scale` [rule] — lib/screens/shop_screen.dart:21 — `BorderRadius.circular(13)`
  Corner radius 13 is not on the contract scale (0, 2, 4, 8, 12, 16, 24, 32, 9999); nearest step 12 (2 occurrences project-wide) Nearest: semantic.radius.tile 12 (scale 0, 2, 4, 8, 12, 16, 24, 32, 9999)
  Fix: Use the corner radius step 12 (semantic.radius.tile); if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0002 must be absent (`audit.py compare` lists it under resolved)
- **VA-0003** `color.off-palette` [rule] — lib/screens/shop_screen.dart:44 — `Color(0xFF8E24AA)`
  Hard-coded colour #8E24AA not in tokens.json palette Nearest: component.button.primary.outlineColor #972743 (distance 35.2)
  Fix: No close token (nearest component.button.primary.outlineColor #972743 is 35.2 away) — pick the semantic role (primary/accent/surface/text/success/danger/reward) that matches the element's purpose and use its token; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0003 must be absent (`audit.py compare` lists it under resolved)
- **VA-0004** `radius.off-scale` [rule] — lib/screens/shop_screen.dart:45 — `BorderRadius.circular(13)`
  Corner radius 13 is not on the contract scale (0, 2, 4, 8, 12, 16, 24, 32, 9999); nearest step 12 (2 occurrences project-wide) Nearest: semantic.radius.tile 12 (scale 0, 2, 4, 8, 12, 16, 24, 32, 9999)
  Fix: Use the corner radius step 12 (semantic.radius.tile); if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0004 must be absent (`audit.py compare` lists it under resolved)

### MEDIUM
- **VA-0005** `component.duplicate-implementation` [recommendation] — lib/screens/shop_screen.dart:8 — `class CtaButton extends StatelessWidget`
  divergent re-implementation of Button: `CtaButton` in lib/screens/shop_screen.dart:8 vs `PrimaryButton` in lib/widgets/primary_button.dart:5 Nearest: canonical: lib/widgets/primary_button.dart (PrimaryButton)
  Fix: Reuse `PrimaryButton` from lib/widgets/primary_button.dart and delete `CtaButton`; if the variant is intentional, make it a prop/variant of the canonical component · Verify: re-run `audit.py scan`; VA-0005 must be absent (`audit.py compare` lists it under resolved)

## Inventory
colours (opaque, distinct 12): #8E24AA×2 #2E2A32×1 #4A3B5C×1 #56505E×1 #6B6274×1 #972743×1 #FF8FAB×1 #FFC83D×1 #FFD23F×1 #FFDDAC×1 #FFF6E9×1 #FFFFFF×1
colours with alpha: none
radii: 13×2 | font sizes: 12×1 14×1 16×1 28×1 | spacing: 16×2 20×1 24×1
families: Fredoka, Nunito | shadows: 0 distinct | durations: 120×1 200×1 350×1
icon libraries: none
components: CtaButton (lib/screens/shop_screen.dart), PrimaryButton (lib/widgets/primary_button.dart)

## Notes
- none
