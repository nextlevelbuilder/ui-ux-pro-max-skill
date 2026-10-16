# Visual audit — docs/examples/visual-design-pro-max/example-c-consistency-audit/fixed
platform: mixed · contract: docs/examples/visual-design-pro-max/example-c-consistency-audit/fixed/tokens.json · scanned 11 files · skipped 3 · generated 2026-10-16T11:55:48Z

| critical | high | medium | low | info |
|---|---|---|---|---|
| 0 | 0 | 7 | 2 | 0 |

## Findings (by severity)

### MEDIUM
- **VA-0001** `color.off-palette` [rule] — unity/Assets/Scripts/ShopPanel.cs:16 — `ColorUtility.TryParseHtmlString("#E91E63")`
  Hard-coded colour #E91E63 not in tokens.json palette Nearest: semantic.color.danger #E03E3E (distance 28.0)
  Fix: Replace with the nearest token semantic.color.danger (#E03E3E) or a semantic colour that fits the role; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0001 must be absent (`audit.py compare` lists it under resolved)
- **VA-0002** `duration.off-scale` [rule] — unity/Assets/Scripts/ShopPanel.cs:20 — `.DOScale(1.1f, 0.337f)`
  Duration (ms) 337 is not on the contract scale (120, 200, 350); nearest step 350 (2 occurrences project-wide) Nearest: primitive.duration.step 350 (scale 120, 200, 350)
  Fix: Use the duration (ms) step 350; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0002 must be absent (`audit.py compare` lists it under resolved)
- **VA-0003** `color.off-palette` [rule] — unity/Assets/UI/Shop.uss:3 — `rgb(233, 30, 99)`
  Hard-coded colour #E91E63 not in tokens.json palette Nearest: semantic.color.danger #E03E3E (distance 28.0)
  Fix: Replace with the nearest token semantic.color.danger (#E03E3E) or a semantic colour that fits the role; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0003 must be absent (`audit.py compare` lists it under resolved)
- **VA-0004** `radius.off-scale` [rule] — unity/Assets/UI/Shop.uss:4 — `border-top-left-radius: 13px`
  Corner radius 13 is not on the contract scale (4, 8, 16, 24, 9999); nearest step 16 (2 occurrences project-wide) Nearest: primitive.radius.step 16 (scale 4, 8, 16, 24, 9999)
  Fix: Use the corner radius step 16; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0004 must be absent (`audit.py compare` lists it under resolved)
- **VA-0005** `radius.off-scale` [rule] — unity/Assets/UI/Shop.uss:5 — `border-top-right-radius: 13px`
  Corner radius 13 is not on the contract scale (4, 8, 16, 24, 9999); nearest step 16 (2 occurrences project-wide) Nearest: primitive.radius.step 16 (scale 4, 8, 16, 24, 9999)
  Fix: Use the corner radius step 16; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0005 must be absent (`audit.py compare` lists it under resolved)
- **VA-0006** `duration.off-scale` [rule] — unity/Assets/UI/Shop.uss:7 — `transition-duration: 337ms`
  Duration (ms) 337 is not on the contract scale (120, 200, 350); nearest step 350 (2 occurrences project-wide) Nearest: primitive.duration.step 350 (scale 120, 200, 350)
  Fix: Use the duration (ms) step 350; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0006 must be absent (`audit.py compare` lists it under resolved)
- **VA-0007** `font-size.off-scale` [rule] — unity/Assets/UI/Shop.uss:11 — `font-size: 15px`
  Font size 15 is not on the contract scale (12, 14, 16, 20, 24, 32); nearest step 14 (1 occurrence project-wide) Nearest: primitive.fontSize.step 14 (scale 12, 14, 16, 20, 24, 32)
  Fix: Use the font size step 14; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0007 must be absent (`audit.py compare` lists it under resolved)

### LOW
- **VA-0008** `color.near-duplicate` [rule] — unity/Assets/Scripts/ShopPanel.cs:9 — `new Color(0.98f, 0.5f, 0.31f)`
  Colour #FA804F is a near-duplicate of a contract colour (distance 8.2 <= 12) Nearest: semantic.color.accent #FF8A4C (distance 8.2)
  Fix: Replace with the semantic.color.accent token (#FF8A4C); if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0008 must be absent (`audit.py compare` lists it under resolved)
- **VA-0009** `spacing.off-scale` [rule] — unity/Assets/UI/Shop.uss:6 — `padding: 10px`
  Spacing 10 is not on the contract scale (4, 8, 12, 16, 24, 32); nearest step 8 (1 occurrence project-wide) Nearest: primitive.spacing.step 8 (scale 4, 8, 12, 16, 24, 32)
  Fix: Use the spacing step 8; if intentional, add to `pages/shop.md` intentional_exceptions · Verify: re-run `audit.py scan`; VA-0009 must be absent (`audit.py compare` lists it under resolved)

## Inventory
colours (opaque, distinct 10): #1A1A2E×4 #3B5BDB×4 #FFFFFF×4 #FF8A4C×3 #FFF8F0×3 #6B6B80×2 #E91E63×2 #E03E3E×1 #FA804F×1 #FFD43B×1
colours with alpha: #000000@0.40×1 #FF8A4C@0.90×1
radii: 16×4 8×3 13×2 9999×2 4×1 | font sizes: 16×4 12×1 14×1 15×1 24×1 | spacing: 12×3 16×3 24×3 8×2 10×1
families: Fredoka, Nunito | shadows: 2 distinct | durations: 200×5 337×2 350×2 120×1
icon libraries: flutter {material}, web {lucide-react}
components: Button (web/components/Button.tsx), PrimaryButton (lib/widgets/primary_button.dart)

## Notes
- none
