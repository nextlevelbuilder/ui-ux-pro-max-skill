# Visual Direction Profile — `style-profile.json` (schema `vdp/1`)

The single document every other artefact derives from: `tokens.json` (`token-derivation.md`), `MASTER.md` and its companions (`design-contract.md`), the audit's allowed sets, the QA checklist. Produced by `python3 scripts/vd.py profile …`, checked by `python3 scripts/vd.py validate --dir design-system/<slug>` (and by `vd.py init`, which refuses an invalid profile with exit 1 before writing anything).

Conventions: **required** keys are listed in §1; everything else is optional and may be omitted or `null`. Unknown extra keys are allowed (the validator ignores them) so projects can annotate. Enum values are exact, lower-case strings.

## 1. Required keys and exit behaviour

`schema, project, product.kind, product.platforms, style.id, sources, shape, rendering, typography, motion, anti_patterns, qa_criteria`

Missing key or wrong enum → `vd.py validate` finding of level `error` (rule `profile.<field>`), exit 1. Malformed JSON → exit 1 (`profile.malformed`). Missing file → exit 2.

## 2. Field by field

### `schema` (required)
`"vdp/1"`. Anything else is an error. A fragment with `"_partial": true` (from `reference_analysis.py to-profile`) is **not** a valid profile; `vd.py profile --reference` completes it (CC-3).

### `project` (required)
```json
{"name": "Onet Garden", "slug": "onet-garden"}
```
`name` required. `slug` is normalised by `safe_slug` (lower-case, `[^a-z0-9_-]+ → -`, stripped, fallback `default`) and names `design-system/<slug>/`; traversal is impossible by construction.

### `product` (required: `kind`, `platforms`)
| Key | Enum / type | Notes |
|---|---|---|
| `kind` | `game` · `app` | selects font/icon scales, component rows (`Applies To`), QA screens |
| `genre` | string or null | genre id from `data/genre-profiles.csv` when route B was used |
| `platforms` | non-empty subset of `mobile-ios, mobile-android, web, desktop, tablet` | touch-target tokens take the maximum across the list |
| `stack` | `flutter, flutter-flame, unity-ugui, unity-ui-toolkit, react, nextjs, vue, svelte, html-tailwind, swiftui, jetpack-compose, react-native, other` | decides `$extensions.vdp.platformUnit`; absent = `other` |
| `audience` | free string (CC-11) | e.g. `casual-all-ages`; defaults to the catalog `Audience` text |
| `orientation` | free string | `portrait` for mobile-only platform lists, else `responsive` |

### `style` (required: `id`)
| Key | Value |
|---|---|
| `id` | a `Style ID` from `data/visual-styles.csv`, or `reference-derived-custom` (CC-3) |
| `name`, `family` | copied from the row; family ids are documented in `visual-families.md` |
| `mood` | list of strings (catalog `Mood`, `;`-split) |
| `confidence` | `observed` · `high` · `assumption` · `not-derivable` — catalog rows are `high`; the reference route writes `high` only with ≥ 5 global observed/high rules and no open conflict |

### `sources` (required, list)
Each entry `{"type", "ref", …}`; `type ∈ {catalog, genre, reference-analysis, design-system-seed, research}` (CC-1).

| type | ref | extras |
|---|---|---|
| `catalog` | `visual-styles.csv#<style id>` | |
| `genre` | `genre-profiles.csv#<genre id>` | |
| `reference-analysis` | file name of the analysis | `roles`: subset of `color, shapes, characters, buttons, hud, popup, icons, typography, layout, motion` (union of owned roles) |
| `design-system-seed` | `search.py --design-system --json` | |
| `research` | `asset-guidelines.md#provenance:<asset>` | `tier` (T1–T7), see `research-and-provenance.md` |

### `principles` (optional, list of strings)
3–5 imperative sentences. Route A derives them from the row's palette / shape / outline / typography clauses; route C from the strongest global rules.

### `shape` (required)
```json
{"radius_class": "xl", "silhouette": "rounded-blob", "outline": {"width": 3, "color_rule": "darker-shade-of-fill"}}
```
- `radius_class` (enum, error if missing): `none, sm, md, lg, xl, pill`. Classes are **percent of element height** (CC-5): none 0 · sm ≤ 5 · md 5–12 · lg 12–20 · xl 20–40 · pill ≥ 50. Pixel values per class come from `token-derivation.md` §2.3 (control/container/popup/tile/chip picks), never from this file.
- `silhouette` (free string): `rounded-rect`, `rounded-blob`, `pill`, `chunky-rounded`, `angular-cut`, `chamfered`, `organic`, `pixel-grid`, `rectangular`, …
- `outline.width` (finite number ≥ 0, px at 1×; `0` = none — negative, NaN or infinite values are a validate error) and `outline.color_rule` ∈ `darker-shade-of-fill` (filled controls: the fill's edge step, fill + 3; surface elements: `semantic.color.border`), `lighter-tint-of-fill` (fill's 200 step), `contrast-dark` (neutral.900), `border-token` (`semantic.color.border`), `none` (transparent). Other strings are accepted but derive as `none`. Optional `outline.secondary_button` ∈ `primary` · `surface`: `primary` gives the secondary button a `semantic.color.primary` outline (set automatically when the style row says so); otherwise every surface element shares one outline colour (`token-derivation.md` §2.5).
- From references: the class comes from the median px value in the radius rule and its observations (≤2 none, ≤6 sm, ≤10 md, ≤16 lg, ≤32 xl, >32 pill); `pill`/`circular` words alone never override px evidence.

### `rendering` (required: `shading`)
| Key | Values |
|---|---|
| `shading` | `flat, soft, soft-cel, cel, painterly, glossy, clay, pixel, realistic` (enum) → elevation method (`tint` / `shadow` / `outline`) in `token-derivation.md` §2.4 |
| `highlight` | free tag: `none, top-left-gloss, top-gloss, glass-gloss, top-band, radial-specular, inner-stroke, inner-glow, bevel-light, glow, painted, …` |
| `shadow` | one of the six derivation kinds `none, offset-soft, soft-ambient, hard-offset, double-clay, glow` (free text is normalised by keyword, e.g. "hard … soft" → `double-clay`) |
| `texture` | `none, paper-grain, brush, grain, pixel-grid, …` |
| `shadow_tint` | optional `neutral` (default: shadows tinted with `neutral.900`) · `black` (the style row asks for black/uncoloured shadows on a dark or flat style) |

### `typography` (required: `display`)
```json
{"display": "Fredoka", "body": "Nunito", "case": "title", "weight_rule": "display 700 / body 500"}
```
`display` / `body` are font-family names **or a classification string** such as `bold rounded sans` / `regular humanist sans` when the family is not derivable (CC-4; hyphenated fragment forms like `heavy-rounded-sans` are normalised to spaces; body comes from body/caption/sub-label/regular/humanist clauses, else it is the display classification minus its weight word with an `unknowns` entry); the missing family is then listed in `unknowns` and the design-system seed may fill it. `case ∈ title, sentence, upper, lower, small-caps, mixed` (free). Families are copied verbatim into `primitive.fontFamily.*`.

### `palette_strategy` (optional string) and `palette` (optional, CC-9)
`palette_strategy` is prose; two substrings are **semantic**: `pastel-base` (background = `brand.50`), `dark` without `supports-dark` (dark-first semantic layer), `supports-dark` (adds the `dark` token layer).
```json
"palette": {"seeds": {"brand": "#FF8FAB", "secondary": "#7ED6C4", "accent": "#FFD23F", "neutral": "#7F758A",
                      "success": "#16A34A", "danger": "#DC2626", "warning": "#F5A524", "reward": "#FFC83D"},
            "observed": [{"hex": "#FFD5E5", "share": 0.42, "role_guess": "background", "ref": "ref-1"}]}
```
`seeds` slots are exactly `brand, secondary, accent, neutral, success, danger, warning, reward`, values `#RRGGBB` (validated). Resolution order: `palette.seeds` → design-system seed → reference `palette_observed` → catalog `Seed Colors` → constants (`token-derivation.md` §0.2). `reward` is only a ramp when seeded; otherwise `semantic.color.reward` aliases `warning`. When a reference yields a brand but no accent, `accent = brand.700` and `unknowns` says so. `observed` is provenance only.

`palette.surfaces` (optional) `{"background": "#FFD5E5", "surface": "#FFF3E0", "text": "#5B3A29", "outline": "#…"}` — surface colours, **authoritative** for the semantic layer. Route A/B fills them from the catalog `Seed Colors` positions 4–6 (`background;surface;text`) — no `outline`; the border token is derived from `shape.outline.color_rule` applied to the background (`token-derivation.md` §2.1a); route C/D from `palette_observed` (roles `background`, `surface`, `text`, `outline`, highest share each). `vd_tokens.py` writes them literally into `semantic.color.background / surface / border` and into `text` when it reaches 4.5:1 on the background; `textMuted` walks the neutral ramp darker until it passes; the neutral ramp itself is derived from the observed text colour. Values are validated as `#RRGGBB`.

### `iconography` (optional)
`{"style": "filled-rounded", "stroke": null, "library_hint": "custom|phosphor-fill"}` — `style` free tag (`filled-rounded, filled, filled-two-tone, outline, pixel, sticker, …`), `stroke` number or null, `library_hint` `|`-separated library slugs or `custom`. One library per product (`icon.mixed-libraries` audit rule).

### `illustration` (optional)
`{"character_style": "chibi", "asset_rendering": "vector flat with one soft shade band…"}` — both free strings; `none` for products without illustration.

### `motion` (required: `class`)
```json
{"class": "bouncy", "duration_scale": {"fast": 120, "base": 200, "slow": 350}, "easing": "spring-soft", "reduced_motion": "respect"}
```
- `class` enum: `static, snappy, soft, bouncy, dramatic` → `primitive.duration.*` (seven keys incl. `reward`, `ambient`, CC-8) and `primitive.easing.*` rows in `token-derivation.md` §1.10–1.11 / `motion-direction.md` §2.
- `duration_scale`: object or `null`; any of the seven keys overrides the class row verbatim (non-negative numbers).
- `easing`: human name (`spring-soft`, `standard-decelerate`, …) — informational; the token stores the bezier.
- `reduced_motion`: `respect` (recommended), `ignore-decorative-only`, `ignore`.

### `components` (optional object)
Free-text visual notes keyed by component id or rule target: `button.primary`, `popup`, `hud`, `reward`, `card`, `chip`, `radius`, … Route A fills them from the style row's Button / Panel Popup / HUD / Reward rules; route C from reference rules. `vd.py init` prints them as "Style modifier" lines under the matching catalog components (CC-11: the catalog row is canonical for structure and states, the note is the visual layer) and in `MASTER.md` § Component Rules.

### `anti_patterns` (required, list of strings) · `qa_criteria` (required, list of strings)
One checkable statement each. Rendered as ❌ bullets and `- [ ]` boxes in `MASTER.md`; `qa_criteria` also feed `visual-qa-checklist.md` and the `visual-audit` skill's checklist command.

### `intentional_exceptions` (optional list)
`{"scope": "gameplay-hud", "rule": "smaller radius for tiles", "reason": "grid density", "status": "active|retired"}` — `scope`, `rule`, `reason` required per entry. Reference rules with `scope: context:<screen>` land here automatically. These are the only legal values outside `tokens.json`; the audit marks matching findings `intentional-exception`.

### `unknowns` (optional list of strings)
Everything not derivable or assumed: missing families, motion class from static references, assumption rules (`assumption (rule-N, …): …`), open conflicts, rules not applied because their role is not owned. Shrinks as the user answers; never silently emptied.

### Optional annotation blocks written by `vd.py profile`
- `catalog_rules`: the raw catalog clauses (shape language, outline/highlight/shadow rules, typography direction, icon/illustration style, button/panel/HUD/reward rules, best/avoid for, reference notes) so `asset-guidelines.md` can quote them.
- `genre_profile`: `name, default_styles, core_screens, hud_elements, key_interactions, reward_loop, touch_rules, performance_notes` from route B.

## 3. Minimal valid example

```json
{
  "schema": "vdp/1",
  "project": {"name": "Ledger Lite", "slug": "ledger-lite"},
  "product": {"kind": "app", "platforms": ["web"], "stack": "react"},
  "style": {"id": "minimal-modern-mobile", "confidence": "high"},
  "sources": [{"type": "catalog", "ref": "visual-styles.csv#minimal-modern-mobile"}],
  "shape": {"radius_class": "md", "outline": {"width": 1, "color_rule": "border-token"}},
  "rendering": {"shading": "flat", "shadow": "soft-ambient"},
  "typography": {"display": "Inter", "body": "Inter"},
  "motion": {"class": "snappy"},
  "anti_patterns": ["drop shadows on resting cards"],
  "qa_criteria": ["text contrast 4.5:1 in both themes"]
}
```

## 4. Validation summary (`vd.py validate`, profile part)

| Check | Level |
|---|---|
| required keys present; `schema == vdp/1`; `_partial` absent | error |
| `product.kind`, `product.platforms ⊆ enum`, `product.stack` enum | error |
| `style.id` non-empty; `style.confidence` enum | error |
| every `sources[].type` in the CC-1 enum, `ref` non-empty, `roles ⊆` role enum | error |
| `shape.radius_class`, `rendering.shading`, `motion.class` enums; `motion.duration_scale` numeric | error |
| `typography.display` non-empty (family or classification) | error |
| `anti_patterns`, `qa_criteria`, `principles`, `unknowns` lists of strings; `intentional_exceptions[]` have scope/rule/reason | error |
| `palette.seeds` slots and `#RRGGBB` values | error |

Tokens, MASTER.md, pages and CHANGELOG checks are listed in `design-contract.md` §8 and `token-derivation.md` §6.
