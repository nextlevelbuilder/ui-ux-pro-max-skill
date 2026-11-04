<!-- generated-by: visual-direction vd.py 1.0.0; profile-hash: d350c253757e; body-hash: 58e21c445212 -->
# Design System Master File

> **LOGIC:** When building a specific page, first check `design-system/onet-garden/pages/[page-name].md`.
> If that file exists, its rules **override** this Master file for that page only.
> If not, strictly follow the rules below. Every override must carry a `reason`.

---

**Project:** Onet Garden
**Generated:** 2026-10-16T12:33:58Z by `visual-direction` (`vd.py init`, derivation `token-derivation.md v1`)
**Product:** game · onet-animal-puzzle · mobile-ios, mobile-android · stack `flutter-flame` · unit `logical`
**Contract files:** `style-profile.json` · `tokens.json` · `component-catalog.md` · `asset-guidelines.md` · `interaction-guidelines.md` · `visual-qa-checklist.md` · `CHANGELOG.md`

---

## Identity

- **Style:** Japanese Cute Puzzle (`japanese-cute-puzzle`, family `cute-cartoon`, confidence `high`)
- **Mood:** cheerful, soft, rounded, friendly, calm-energetic
- **Audience:** casual-all-ages · **Orientation:** portrait
- **Principles:**
  - Pastel base (tints at 85-92% lightness) for backgrounds and panels
  - Rounded-blob silhouettes
  - 3px outline on all gameplay pieces and buttons in a 25% darker shade of the fill (HSL L -25), never pure black
  - Rounded sans display (Fredoka / M PLUS Rounded 1c / Zen Maru Gothic for JP) 700 for titles
- **Sources:** genre:genre-profiles.csv#onet-animal-puzzle; catalog:visual-styles.csv#japanese-cute-puzzle

## Visual Direction

| Axis | Value |
|---|---|
| Shape | radius class `xl` · silhouette `rounded-blob` · outline 3 (darker-shade-of-fill) |
| Rendering | shading `soft-cel` · highlight `top-left-gloss` · shadow `double-clay` · texture `none` |
| Typography | display **Fredoka** / body **Nunito** · case title · display 700 / body 500 |
| Palette strategy | Pastel base (tints at 85-92% lightness) for backgrounds and panels; exactly 3 saturated accents reserved for CTA, reward and selection states; never more than 2 saturated hues on one screen outside reward moments |
| Iconography | filled-rounded · stroke none · library `custom` |
| Illustration | chibi · vector flat with one soft shade band in a hue-shifted (toward purple) darker tone |
| Motion | class `bouncy` · fast/base/slow 120/200/350 ms · reward/ambient 750/2500 ms · easing `spring-soft` · reduced motion: respect |

## Token Summary

Full source of truth: `tokens.json` (`$extensions.vdp.generatedFrom = japanese-cute-puzzle`). Values below are resolved; do not retype them in code — reference the token.

### Colour (semantic)

| Role | Token | Resolved | On-colour | Contrast |
|---|---|---|---|---|
| primary | `semantic.color.primary` | `#FF8FAB` | `#2E2A32` | 6.54:1 |
| secondary | `semantic.color.secondary` | `#7ED6C4` | `#2E2A32` | 8.24:1 |
| accent | `semantic.color.accent` | `#FFD23F` | `#2E2A32` | 9.74:1 |
| success | `semantic.color.success` | `#107435` | `#FFFFFF` | 5.88:1 |
| warning | `semantic.color.warning` | `#F5A524` | `#2E2A32` | 6.89:1 |
| danger | `semantic.color.danger` | `#BB1E1E` | `#FFFFFF` | 6.33:1 |
| reward | `semantic.color.reward` | `#FFC83D` | `#2E2A32` | 9.09:1 |
| background | `semantic.color.background` | `#FFF6E9` | `#4A3B5C` | 9.47:1 |
| surface | `semantic.color.surface` | `#FFFFFF` | `#4A3B5C` | 10.14:1 |
| surfaceElevated | `semantic.color.surfaceElevated` | `#FFFFFF` | `#4A3B5C` | 10.14:1 |
| border | `semantic.color.border` | `#FFDDAC` | `—` | — |
| text | `semantic.color.text` | `#4A3B5C` | `#FFF6E9` | 9.47:1 |
| textMuted | `semantic.color.textMuted` | `#6B6274` | `#FFF6E9` | 5.41:1 |
| overlay | `semantic.color.overlay` | `rgba(46, 42, 50, 0.5)` | `—` | — |

### Scales

| Group | Keys → values (logical) |
|---|---|
| spacing | 0=0 · 1=4 · 2=8 · 3=12 · 4=16 · 5=20 · 6=24 · 8=32 · 10=40 · 12=48 · 16=64 · 20=80 · 24=96 |
| radius | none=0 · xs=2 · sm=4 · md=8 · lg=12 · xl=16 · 2xl=24 · 3xl=32 · full=9999 · picks: control `16`, container `24`, popup `32`, tile `12`, chip `9999` |
| outline | none=0 · thin=1 · regular=2 · strong=3 · heavy=4 · control = `3` |
| fontSize | xs=12 · sm=14 · base=16 · lg=18 · xl=22 · 2xl=28 · 3xl=36 · 4xl=48 · display=64 |
| lineHeight | tight=1.1 · snug=1.25 · normal=1.5 · relaxed=1.65 |
| iconSize | sm=20 · md=28 · lg=40 · xl=64 |
| touchTarget | min `48` · recommended `48` |
| duration | instant=0ms · fast=120ms · base=200ms · slow=350ms · reveal=600ms · reward=750ms · ambient=2500ms |
| easing | standard=cubic-bezier(0.22, 1, 0.36, 1) · enter=cubic-bezier(0.34, 1.56, 0.64, 1) · exit=cubic-bezier(0.36, 0, 0.66, -0.56) · emphasized=cubic-bezier(0.68, -0.6, 0.32, 1.6) |
| zIndex | base=0 · raised=10 · sticky=50 · hud=100 · overlay=200 · popup=300 · toast=400 · tutorial=500 · debug=1000 |
| opacity | disabled=0.4 · hover=0.92 · pressed=0.85 · loading=0.7 · scrim=0.5 · scrimHeavy=0.7 · muted=0.7 · ghost=0.12 · focusRing=0.35 |
| shadow set `double-clay` | none=none · sm=0 2px 0 rgba(46, 42, 50, 0.25), 0 4px 6px rgba(46, 42, 50, 0.12) · md=0 4px 0 rgba(46, 42, 50, 0.25), 0 8px 12px rgba(46, 42, 50, 0.14) · lg=0 6px 0 rgba(46, 42, 50, 0.25), 0 12px 20px rgba(46, 42, 50, 0.18) · inset=inset 0 3px 0 rgba(46, 42, 50, 0.18) |
| elevation | method `shadow` · raised `{primitive.shadow.sm}` · elevated `{primitive.shadow.md}` · floating `{primitive.shadow.lg}` |

### Typography roles

| Role | Family | Size | Line height | Weight |
|---|---|---|---|---|
| display | Fredoka | 64 | 1.1 | 700 |
| title | Fredoka | 28 | 1.25 | 700 |
| body | Nunito | 16 | 1.5 | 500 |
| label | Nunito | 14 | 1.25 | 600 |
| caption | Nunito | 12 | 1.25 | 500 |

## Component Rules

See `component-catalog.md` (filtered for `game` + `japanese-cute-puzzle`; 51 components).
Component defaults live in `tokens.json#component.*`; the catalog says how to use them, the tokens say what they are.
Style-specific component notes from the profile:
- `button.primary`: Pill primary 56px tall, fill = primary, 3px darker-shade outline, 4px hard bottom shadow, label 18px 700 centred with 1px darker text shadow; secondary = surface fill with primary outline; pressed = translate 3px down and drop shadow in 90ms
- `popup`: Rounded panel radius 28px, surface fill, 4px outline in secondary-darker, ribbon title plate overlapping the top edge by 50%; close button circular 44px top-right; entrance scale 0.85 to 1 with overshoot 1.04 in 260ms
- `hud`: Top bar 64px with coin/life/timer capsules (pill, surface fill, 2px outline); timer bar uses accent fill with rounded ends; never more than 3 capsules; gameplay grid gets at least 85% of vertical space in portrait
- `reward`: Reward popups go one saturation step higher (accent plus gold); confetti of 3 shapes max (circle, star, heart) in palette colours; mascot cheer pose; sparkle burst 6-8 rays; bounce to 1.1 scale synced to sound

## Page Override Logic

1. Read this file fully. Then read `pages/<page>.md` if it exists.
2. A page file may only contain **deviations**. Each deviation = `token path` + `page value` + `reason`.
3. A page file that restates ≥ 3 Master values unchanged is rejected by `vd.py validate` (copy, not override).
4. **Drift budget per screen:** colour and font family: 0 ad-hoc values; radius: ≤ 1 exception with reason; spacing/fontSize: ≤ 2 off-scale values with reason; shadows: 0 new variants; duration: ≤ 1 with reason. Anything above the budget is a `visual-audit` finding, not a style choice.
5. Pages never redefine `semantic.color.*` meanings; they may remap a component to a different existing token.

## Intentional Exceptions

| Scope | Rule | Reason | Status |
|---|---|---|---|
| — | none declared | — | — |

(Exceptions are the only place a value outside `tokens.json` is legal. `visual-audit` marks matching findings as `intentional-exception` instead of `rule`.)

## Anti-Patterns (Do NOT Use)

- ❌ Pure black outlines
- ❌ Thin stroke icons mixed with filled
- ❌ Sharp-corner tiles next to pill buttons
- ❌ More than 3 saturated hues on the gameplay screen
- ❌ Large-blur drop shadows on tiles
- ❌ Photoreal textures
- ❌ Timer bar that turns red and pulses for the whole level
- ❌ Tile faces with busy background patterns
- ❌ Boosters larger than tiles
- ❌ Ad overlay covering the board
- ❌ Mixed animal art styles across species

## QA Criteria

- [ ] All outlines are darker shades of their own fill, never #000
- [ ] Corner radius within the xl class on every panel and button
- [ ] Text contrast at least 4.5:1 on the cream background
- [ ] Tile silhouettes identical size and radius across the grid
- [ ] Reward screen uses the same character style as home
- [ ] Pressed state visible within 100ms
- [ ] Every `onX` text passes 4.5:1 on its `X` (see Colour table)
- [ ] All interactive targets ≥ `48` logical
- [ ] No colour, font family, radius or duration outside `tokens.json` without an entry above

## Unknowns

- success: built-in status fill darkened from #138B3F to #107435 for contrast (5.88:1 on {primitive.color.white})
- button.secondary.fg: primary-family label stepped from #FF8FAB to brand.700 (#BA4A66) to reach 4.5:1 on the secondary states

## Change Log

See `CHANGELOG.md` (append-only; `vd.py` writes `[tool]` entries, humans write `[manual]` entries). Last entry: 2026-10-16T12:33:58Z · vd.py init · [tool]
