<!-- generated-by: visual-direction vd.py 1.0.0; profile-hash: 73c0e76468b6; body-hash: 52bc915bb3d0 -->
# Design System Master File

> **LOGIC:** When building a specific page, first check `design-system/pet-diary-redesign/pages/[page-name].md`.
> If that file exists, its rules **override** this Master file for that page only.
> If not, strictly follow the rules below. Every override must carry a `reason`.

---

**Project:** Pet Diary Redesign
**Generated:** 2026-10-16T12:33:59Z by `visual-direction` (`vd.py init`, derivation `token-derivation.md v1`)
**Product:** app · — · mobile-ios, mobile-android · stack `flutter` · unit `logical`
**Contract files:** `style-profile.json` · `tokens.json` · `component-catalog.md` · `asset-guidelines.md` · `interaction-guidelines.md` · `visual-qa-checklist.md` · `CHANGELOG.md`

---

## Identity

- **Style:** Reference-Derived Custom (`reference-derived-custom`, family `flat-modern`, confidence `high`)
- **Mood:** —
- **Audience:** general · **Orientation:** portrait
- **Principles:**
  - One brand orange carries all emphasis (brand mark, key numbers, active state, status dots)
  - Radius ladder: cards 20–28px, tiles 12–14px, controls circular/pill
  - All surfaces use a 2px peach outline (light tint of brand), never grey/black
  - Two-family system: rounded display family for headings/numbers (bold), neutral sans for body
  - Filled rounded glyphs, single colour, same optical size across the app bar, tiles and nav
- **Sources:** reference-analysis:reference-analysis.json; catalog:visual-styles.csv#reference-derived-custom

## Visual Direction

| Axis | Value |
|---|---|
| Shape | radius class `xl` · silhouette `pill` · outline 2 (lighter-tint-of-fill) |
| Rendering | shading `soft` · highlight `none` · shadow `none` · texture `none` |
| Typography | display **bold rounded geometric sans** / body **humanist sans** · case mixed · display bold / body medium |
| Palette strategy | One brand orange carries all emphasis (brand mark, key numbers, active state, status dots); secondary tints are reserved for category tiles only. |
| Iconography | filled-rounded · stroke none · library `custom` |
| Illustration | not-derivable · not-derivable |
| Motion | class `soft` · fast/base/slow 150/250/400 ms · reward/ambient 650/3000 ms · easing `ease-in-out-soft` · reduced motion: respect |

## Token Summary

Full source of truth: `tokens.json` (`$extensions.vdp.generatedFrom = reference-derived-custom`). Values below are resolved; do not retype them in code — reference the token.

### Colour (semantic)

| Role | Token | Resolved | On-colour | Contrast |
|---|---|---|---|---|
| primary | `semantic.color.primary` | `#F97316` | `#322C2A` | 4.90:1 |
| secondary | `semantic.color.secondary` | `#BFDBFE` | `#322C2A` | 9.66:1 |
| accent | `semantic.color.accent` | `#B24C05` | `#FFFFFF` | 5.34:1 |
| success | `semantic.color.success` | `#107435` | `#FFFFFF` | 5.88:1 |
| warning | `semantic.color.warning` | `#F5A524` | `#322C2A` | 6.73:1 |
| danger | `semantic.color.danger` | `#BB1E1E` | `#FFFFFF` | 6.33:1 |
| reward | `semantic.color.reward` | `#FFC83D` | `#322C2A` | 8.88:1 |
| background | `semantic.color.background` | `#FFF7ED` | `#9A3412` | 6.88:1 |
| surface | `semantic.color.surface` | `#FFFFFF` | `#9A3412` | 7.31:1 |
| surfaceElevated | `semantic.color.surfaceElevated` | `#FFFFFF` | `#9A3412` | 7.31:1 |
| border | `semantic.color.border` | `#FED7AA` | `—` | — |
| text | `semantic.color.text` | `#9A3412` | `#FFF7ED` | 6.88:1 |
| textMuted | `semantic.color.textMuted` | `#746662` | `#FFF7ED` | 5.18:1 |
| overlay | `semantic.color.overlay` | `rgba(50, 44, 42, 0.5)` | `—` | — |

### Scales

| Group | Keys → values (logical) |
|---|---|
| spacing | 0=0 · 1=4 · 2=8 · 3=12 · 4=16 · 5=20 · 6=24 · 8=32 · 10=40 · 12=48 · 16=64 · 20=80 · 24=96 |
| radius | none=0 · xs=2 · sm=4 · md=8 · lg=12 · xl=16 · 2xl=24 · 3xl=32 · full=9999 · picks: control `16`, container `24`, popup `32`, tile `12`, chip `9999` |
| outline | none=0 · thin=1 · regular=2 · strong=3 · heavy=4 · control = `2` |
| fontSize | xs=12 · sm=14 · base=16 · lg=18 · xl=20 · 2xl=24 · 3xl=30 · 4xl=36 · display=48 |
| lineHeight | tight=1.1 · snug=1.25 · normal=1.5 · relaxed=1.65 |
| iconSize | sm=16 · md=24 · lg=32 · xl=48 |
| touchTarget | min `48` · recommended `48` |
| duration | instant=0ms · fast=150ms · base=250ms · slow=400ms · reveal=600ms · reward=650ms · ambient=3000ms |
| easing | standard=cubic-bezier(0.4, 0, 0.2, 1) · enter=cubic-bezier(0, 0, 0.2, 1) · exit=cubic-bezier(0.4, 0, 1, 1) · emphasized=cubic-bezier(0.25, 0.1, 0.25, 1) |
| zIndex | base=0 · raised=10 · sticky=50 · hud=100 · overlay=200 · popup=300 · toast=400 · tutorial=500 · debug=1000 |
| opacity | disabled=0.4 · hover=0.92 · pressed=0.85 · loading=0.7 · scrim=0.5 · scrimHeavy=0.7 · muted=0.7 · ghost=0.12 · focusRing=0.35 |
| shadow set `none` | none=none · sm=none · md=none · lg=none · inset=none |
| elevation | method `shadow` · raised `{primitive.shadow.sm}` · elevated `{primitive.shadow.md}` · floating `{primitive.shadow.lg}` |

### Typography roles

| Role | Family | Size | Line height | Weight |
|---|---|---|---|---|
| display | bold rounded geometric sans | 48 | 1.1 | 700 |
| title | bold rounded geometric sans | 24 | 1.25 | 700 |
| body | humanist sans | 16 | 1.5 | 400 |
| label | humanist sans | 14 | 1.25 | 600 |
| caption | humanist sans | 12 | 1.25 | 500 |

## Component Rules

See `component-catalog.md` (filtered for `app` + `reference-derived-custom`; 33 components).
Component defaults live in `tokens.json#component.*`; the catalog says how to use them, the tokens say what they are.
Style-specific component notes from the profile:
- `radius`: Radius ladder: cards 20–28px, tiles 12–14px, controls circular/pill; nothing below 12px except text.
- `button.icon`: Circular 44px white button with 2px peach outline and orange glyph.
- `nav`: Bottom nav active state = peach pill + orange icon/label; max 4–5 items.

## Page Override Logic

1. Read this file fully. Then read `pages/<page>.md` if it exists.
2. A page file may only contain **deviations**. Each deviation = `token path` + `page value` + `reason`.
3. A page file that restates ≥ 3 Master values unchanged is rejected by `vd.py validate` (copy, not override).
4. **Drift budget per screen:** colour and font family: 0 ad-hoc values; radius: ≤ 1 exception with reason; spacing/fontSize: ≤ 2 off-scale values with reason; shadows: 0 new variants; duration: ≤ 1 with reason. Anything above the budget is a `visual-audit` finding, not a style choice.
5. Pages never redefine `semantic.color.*` meanings; they may remap a component to a different existing token.

## Intentional Exceptions

| Scope | Rule | Reason | Status |
|---|---|---|---|
| home | Category tiles may use the secondary tints (blue/mint) — an intentional context exception to rule-1. | observed in obs-3 (rule-8) | active |

(Exceptions are the only place a value outside `tokens.json` is legal. `visual-audit` marks matching findings as `intentional-exception` instead of `rule`.)

## Anti-Patterns (Do NOT Use)

- ❌ Mixing rules from two references that conflict without a resolved entry in conflicts
- ❌ Inventing values for not_derivable items
- ❌ Copying a reference pixel-for-pixel instead of extracting rules
- ❌ Dropping the closest catalog style as fallback for gaps
- ❌ Treating a single screenshot as proof of motion or typography

## QA Criteria

- [ ] palette: One brand orange carries all emphasis (brand mark, key numbers, active state, status dots); secondary tints are reserved for category tiles only.
- [ ] radius: Radius ladder: cards 20–28px, tiles 12–14px, controls circular/pill; nothing below 12px except text.
- [ ] outline: All surfaces use a 2px peach outline (light tint of brand), never grey/black; outline is the primary separation device, shadow is secondary.
- [ ] typography: Two-family system: rounded display family for headings/numbers (bold), neutral sans for body; captions one step smaller and muted.
- [ ] icon: Filled rounded glyphs, single colour, same optical size across the app bar, tiles and nav.
- [ ] button.icon: Circular 44px white button with 2px peach outline and orange glyph.
- [ ] nav: Bottom nav active state = peach pill + orange icon/label; max 4–5 items.
- [ ] Every rule in style-profile.json cites an observation id
- [ ] Fields with no observation are marked not-derivable or inherited from a named catalog style
- [ ] Palette seeds match palette_observed roles
- [ ] Text contrast at least 4.5:1 after extraction (adjust text, not background)
- [ ] Enum fields hold valid catalog values, never free text
- [ ] Every `onX` text passes 4.5:1 on its `X` (see Colour table)
- [ ] All interactive targets ≥ `48` logical
- [ ] No colour, font family, radius or duration outside `tokens.json` without an entry above

## Unknowns

- typography.display family not identified; classification 'bold rounded geometric sans' from obs-7 (CC-4)
- not derivable from references: font family names
- not derivable from references: motion timing and easing
- motion class not derivable from static references; catalog default 'soft' kept
- not derivable from references: hover/press/disabled states
- not derivable from references: exact shadow values
- not derivable from references: dark mode
- not derivable from references: exact contrast ratios
- not derivable from references: behaviour of the fixed nav on scroll
- accent colour not observed; derived from the brand ramp (brand.700 = #B24C05) — confirm or seed palette.seeds.accent
- success: built-in status fill darkened from #138B3F to #107435 for contrast (5.88:1 on {primitive.color.white})
- button.secondary.fg: primary-family label stepped from #F97316 to brand.700 (#B24C05) to reach 4.5:1 on the secondary states

## Change Log

See `CHANGELOG.md` (append-only; `vd.py` writes `[tool]` entries, humans write `[manual]` entries). Last entry: 2026-10-16T12:33:59Z · vd.py init · [tool]
