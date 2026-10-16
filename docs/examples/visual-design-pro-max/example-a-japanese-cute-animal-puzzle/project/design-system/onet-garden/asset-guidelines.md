<!-- generated-by: visual-direction vd.py 1.0.0; profile-hash: d350c253757e -->
# Asset Guidelines — Onet Garden

Style `japanese-cute-puzzle` (cute-cartoon). Every asset produced or sourced for this project must follow the rules below and be recorded in the Provenance section.

## Illustration

- Character style: `chibi`
- Asset rendering: vector flat with one soft shade band in a hue-shifted (toward purple) darker tone
- Shading: `soft-cel` · highlight `top-left-gloss` · shadow `double-clay` · texture `none`
- Outline: 3px (darker-shade-of-fill)
- Catalog rule: Chibi animals with 2:1 head-to-body ratio, dot eyes with single white highlight, blush circles, smiles only; vector flat with one soft shade band in a hue-shifted (toward purple) darker tone

## Iconography

- Style: `filled-rounded` · stroke: none · library hint: `custom`
- Sizes: sm=20 · md=28 · lg=40 · xl=64
- One icon library per project; mixing libraries is a `visual-audit` finding (`icon.mixed-libraries`).
- Catalog rule: Filled rounded glyphs with 2px darker-shade outline matching the button rule; two-tone max; never thin-stroke icons

## Typography

- Display: **Fredoka** · Body: **Nunito** · case: title · display 700 / body 500
- Sizes: xs=12 · sm=14 · base=16 · lg=18 · xl=22 · 2xl=28 · 3xl=36 · 4xl=48 · display=64
- Bundle font files with their licence text; record each family under Provenance.
- Catalog rule: Rounded sans display (Fredoka / M PLUS Rounded 1c / Zen Maru Gothic for JP) 700 for titles; body Nunito or Noto Sans JP 500; title case; tabular numerals; letter-spacing +1% on display only

## Palette seeds

| Slot | Hex |
|---|---|
| brand | `#FF8FAB` |
| secondary | `#7ED6C4` |
| accent | `#FFD23F` |
| neutral | `#7F758A` |
| success | `#16A34A` |
| danger | `#DC2626` |
| warning | `#F5A524` |
| reward | `#FFC83D` |

Strategy: Pastel base (tints at 85-92% lightness) for backgrounds and panels; exactly 3 saturated accents reserved for CTA, reward and selection states; never more than 2 saturated hues on one screen outside reward moments

## Provenance

Every externally sourced rule, font, icon set or reference gets one record (JSON object) plus one markdown line. `status` is `checked` only for pages actually opened in the session; otherwise `NOT RUN`. URLs are copied, never typed from memory.

```json
[]
```

- (no records yet — format: `- [use] **asset** — source, licence, tier, status date — note`)

Field rules: `licence_class` ∈ CC0 · OFL · MIT · Apache-2.0 · BSD · CC-BY · CC-BY-SA · CC-BY-NC · CC-BY-ND · marketplace · proprietary/unknown · trademark · ai-generated; `use` ∈ inspiration · rule · embedded; `tier` T1–T7. A `sources[]` entry of type `research` in `style-profile.json` points here as `asset-guidelines.md#provenance:<asset>`.
