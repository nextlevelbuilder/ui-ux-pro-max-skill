<!-- generated-by: visual-direction vd.py 1.0.0; profile-hash: 73c0e76468b6 -->
# Asset Guidelines — Pet Diary Redesign

Style `reference-derived-custom` (flat-modern). Every asset produced or sourced for this project must follow the rules below and be recorded in the Provenance section.

## Illustration

- Character style: `not-derivable`
- Asset rendering: not-derivable
- Shading: `soft` · highlight `none` · shadow `none` · texture `none`
- Outline: 2px (lighter-tint-of-fill)
- Catalog rule: derived from reference-analysis.json (observations with category character)

## Iconography

- Style: `filled-rounded` · stroke: none · library hint: `custom`
- Sizes: sm=16 · md=24 · lg=32 · xl=48
- One icon library per project; mixing libraries is a `visual-audit` finding (`icon.mixed-libraries`).
- Catalog rule: derived from reference-analysis.json (observations with category iconography)

## Typography

- Display: **bold rounded geometric sans** · Body: **humanist sans** · case: mixed · display bold / body medium
- Sizes: xs=12 · sm=14 · base=16 · lg=18 · xl=20 · 2xl=24 · 3xl=30 · 4xl=36 · display=48
- Bundle font files with their licence text; record each family under Provenance.
- Catalog rule: derived from reference-analysis.json (observations with category typography; font family is usually not-derivable from screenshots, record the classification instead)

## Palette seeds

| Slot | Hex |
|---|---|
| brand | `#F97316` |
| secondary | `#BFDBFE` |
| accent | `#B24C05` |
| neutral | `#8A7A75` |
| success | `#16A34A` |
| danger | `#DC2626` |
| warning | `#F5A524` |
| reward | `#FFC83D` |

Strategy: One brand orange carries all emphasis (brand mark, key numbers, active state, status dots); secondary tints are reserved for category tiles only.

## Provenance

Every externally sourced rule, font, icon set or reference gets one record (JSON object) plus one markdown line. `status` is `checked` only for pages actually opened in the session; otherwise `NOT RUN`. URLs are copied, never typed from memory.

```json
[]
```

- (no records yet — format: `- [use] **asset** — source, licence, tier, status date — note`)

Field rules: `licence_class` ∈ CC0 · OFL · MIT · Apache-2.0 · BSD · CC-BY · CC-BY-SA · CC-BY-NC · CC-BY-ND · marketplace · proprietary/unknown · trademark · ai-generated; `use` ∈ inspiration · rule · embedded; `tier` T1–T7. A `sources[]` entry of type `research` in `style-profile.json` points here as `asset-guidelines.md#provenance:<asset>`.
