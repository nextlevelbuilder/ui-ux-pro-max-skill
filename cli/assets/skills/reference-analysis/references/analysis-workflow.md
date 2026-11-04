# Reference Image Analysis Workflow

Step-by-step procedure for an agent that receives 1..N reference images of a game or app UI and must produce `reference-analysis.json` (schema `vdp-reference-analysis/1`, specified in `references/extraction-schema.md`) that later feeds a Visual Direction Profile built by the `visual-direction` skill. Follow the steps in order. Every claim you write must carry a confidence value chosen by the tests in `references/confidence-levels.md`. Never describe pixels you have not seen.

## Step 0 — Intake (ask only what is missing)

Collect, for each image, three facts. Ask **one** message containing only the questions whose answers are not already in the user's request or file names.

| Fact | Ask only if | Default when unanswered |
|---|---|---|
| Role of the image (which topics it should drive) | the user gave 2+ images and no roles | apply `references/multi-reference-reconciliation.md` §3 default precedence, mark unconfirmed |
| Screen type (`home, gameplay, popup, shop, other`) | not stated and not obvious from the label/filename | `other` |
| Ownership / licence (`provenance.owner`, `provenance.license`) | never stated | `owner: "unknown"`, `license: "unknown"`; add `unknowns` note "licence of ref-N unknown; confirm before copying assets verbatim" |

Do not ask about product kind, platform or stack here; those belong to `../visual-direction/scripts/vd.py profile`. Do not ask the user to describe the image if you can view it (Step 1 decides).

Assign ids in the order the user listed the images: `ref-1`, `ref-2`, … Write `label` from the user's words or the filename.

## Step 1 — Capability check (can the runtime show me the image?)

1. Attempt to view the file with the runtime's file-reading tool (in Claude Code, `Read` on a `.png/.jpg/.webp/.gif` returns the image to the model).
2. The attempt counts as success only if the tool result contains image content that you can describe without reference to the filename. A result that contains only bytes, base64 text, metadata, or an error is a failure.
3. On success: `viewed_by: "model-vision"`. Proceed to Step 2.
4. On failure: do **not** guess from the filename, the label, or the user's intent. Set `viewed_by: "human-description"` and ask the user for a structured description using the template below. Observations derived from the description are capped at `high` and must cite `"user description, paragraph N"` as evidence.
5. If the user cannot or will not describe it: `viewed_by: "none"`, the reference owns no roles, every observation that references it is `not-derivable`, and the summary to the user states that the image was not analysed.

Human description template (send verbatim, one per image; also shipped as `templates/human-description-template.md`):

```
Describe <label> in up to 8 short paragraphs, facts only, no style names:
1. Overall layout top-to-bottom (what bands/regions, approximate % of height each).
2. Background colour(s) and any gradient direction.
3. The 3-5 most used colours and where each appears; the single most vivid colour and what it is used on.
4. Corner shapes of panels, cards, buttons (sharp / slightly rounded / very rounded / full pill); outline present? colour? thick or thin relative to the element?
5. Shading: flat fill / gradient / glossy highlight / drop shadow / hard bottom edge; where.
6. Text: heavy or light, rounded or sharp, with or without outline, ALL CAPS / Title Case / lower; any font name only if you know it from the source files.
7. Components visible: list buttons (count, shapes, colours), HUD elements, popups, menus, icons (filled / outlined / two-tone).
8. Characters or illustrations: proportions, outline, shading; anything that moves (only if the source is a video/gif).
```

If the runtime viewed some images but not others, record `viewed_by` per reference; the workflow continues with mixed sources.

## Step 2 — Prepare the file

Start from `templates/reference-analysis.template.json` (or `python3 scripts/reference_analysis.py template --out reference-analysis.json`). Write the skeleton: `schema`, `project` (if given), `references[]` with ids, labels, roles (Step 0), `viewed_by` (Step 1), `screen_type`, `provenance`. Leave `observations`, `rules`, `conflicts`, `not_derivable`, `palette_observed` as empty arrays. Validate the skeleton before analysis:

```bash
python3 scripts/reference_analysis.py validate reference-analysis.json
```

A role-ownership error now is cheaper than later (an empty `observations` array only produces a warning at this stage).

Optional, when Pillow is available and the image file is on disk, run per image and keep the output for Pass B:

```bash
python3 scripts/reference_analysis.py extract-colors refs/home.png --ref-id ref-1 --json
```

On `BLOCKED` (exit 3) continue without it and add `"pixel-share palette (extract-colors blocked)"` to `not_derivable`.

## Step 3 — Analysis passes (per image, in this order)

Rules for every pass:

- One observation = one claim, prefixed with its topic key (`"Panel corner radius: …"`), with `evidence` naming the region.
- Grade each claim with the decision tests in `references/confidence-levels.md`. The four labels below (OBSERVED / HIGH / ASSUMPTION / NOT DERIVABLE) show what each grade typically looks like in that pass; the examples are illustrative, not templates to copy.
- Relative measurements only (percent of frame, ratio to element height). Absolute units are ASSUMPTION.
- Do not name a style (`"glassmorphism"`, `"Japanese cute"`) in observations; style naming happens in `vd.py profile`, from rules.
- If a pass has nothing to say for an image (no HUD on a popup screenshot), write nothing; do not pad.

### Pass A — Layout hierarchy and visual density

Look at: reading order, bands/regions and their share of height, alignment axis, grid vs free placement, safe areas, number of distinct elements per region, whitespace.

- OBSERVED: "Layout: three bands — HUD strip ~8% height, central content ~70%, bottom bar ~12%." / "Density: 9 level cards in a 3×3 grid with gaps ≈ 15% of card width."
- HIGH: "Hierarchy: the primary button is the largest single element below the hero and is the only element using the accent colour → it is the intended first action."
- ASSUMPTION: "Safe area: the top strip sits ~6% below the frame edge, likely a notch/status-bar inset." (depends on device)
- NOT DERIVABLE: scroll extent, content beyond the frame, responsive behaviour at other aspect ratios.

### Pass B — Palette

Look at: dominant (largest area), secondary, accent (most saturated, smallest area), neutral/text colours, saturation range, light/dark base, where each colour sits (background, panels, CTAs, rewards, HUD), warm/cool bias. Use `extract-colors` output when present; the hex/share values are OBSERVED, the `role_guess` is ASSUMPTION.

- OBSERVED: "Dominant colour: light pastel pink filling ~40% of the frame; secondary: cream behind the hero; accent: saturated orange on the primary button and coin icon only."
- HIGH: "Accent discipline: the most saturated colour appears on exactly two elements, both action/reward related → accent is reserved for action and reward."
- ASSUMPTION: "Contrast: white label on the orange fill ≈ 3:1." (sampled, anti-aliased) / "Primary brand colour is the teal rather than the pink." (role guess)
- NOT DERIVABLE: colour-managed exact values, dark-mode variant, colours of states not shown.

Write `palette_observed[]` here (from `extract-colors` or, without Pillow, from visual estimate with shares rounded to 0.05 and a `not_derivable` entry "pixel-share palette estimated by eye").

### Pass C — Geometry

Look at: silhouette of containers (rectangle, rounded rectangle, pill, blob, bevelled), corner radius class per element family (`none, sm, md, lg, xl, pill` — express radius as % of the element's height: none 0, sm ≤5, md 5–12, lg 12–20, xl 20–40, pill ≥50), outline presence/width (% of element height) and colour rule (black / darker shade of fill / contrasting / none), stroke consistency, symmetry.

- OBSERVED: "Button silhouette: full pill (radius = half height)." / "Outline width: ≈ 2% of element height on every panel."
- HIGH: "Outline colour rule: darker shade of each element's own fill (hue retained on orange, green and pink elements)."
- ASSUMPTION: "Outline is 3 px at 1× scale." / "Panels with slightly uneven edges are hand-drawn rather than vector."
- NOT DERIVABLE: nine-slice boundaries, vector vs raster source, radius values in px/dp.

### Pass D — Shading, highlight, shadow, elevation

Look at: fill treatment (flat, linear gradient, radial, two-tone band), highlight (top gloss band, specular dot, rim light), shadow type (none, hard offset, soft blur, inner, bottom edge/"bevel"), elevation levels visible (how many distinct shadow strengths), consistency between UI and illustration.

- OBSERVED: "Button shading: flat fill, lighter horizontal band across the top third, solid darker bottom edge ~10% of height; no blur."
- HIGH: "Elevation: two levels only — flat panels and raised buttons (bottom edge) → two-step elevation scale."
- ASSUMPTION: "The soft shadow under the popup is a 40% black blur." (opacity/blur unmeasurable)
- NOT DERIVABLE: pressed-state depth change, shadow behaviour during motion, light direction consistency across screens not shown.

Map to the profile's `rendering.shading` enum only in Step 6, never in the observation.

### Pass E — Typography

Look at: classification only (rounded sans / geometric sans / humanist sans / slab / serif / display-decorative / pixel / handwritten), weight hierarchy (how many distinct weights, which is heaviest), case (Title / UPPER / lower / Sentence) per element family, outline/shadow on text, letter-spacing (tight/normal/wide), size hierarchy as ratios (title : label : caption), numeral style (lining/old-style, tabular). **Never name a family from a raster**; if the user supplies the name, record it as `high` with `evidence: "user statement"`.

- OBSERVED: "Label case: Title Case on the primary button; UPPER on HUD counters." / "Text outline: dark outline on all HUD numerals."
- HIGH: "Font classification: heavy rounded geometric sans (single-storey a, round terminals) for display and labels."
- ASSUMPTION: "Body text uses a second, lighter family." (only one body sample visible, could be the same family at low weight)
- NOT DERIVABLE: family name, exact sizes in sp/pt, line-height, available weights, licence of the font.

### Pass F — Components

For each visible component family — button (primary/secondary/icon), card/tile, popup/dialog, menu/tab bar, HUD elements (counters, lives, timer, progress), icon buttons, toggles — record: silhouette, fill, outline, shading, label style, icon placement, relative size (height as % of frame height), visible states (default only, or pressed/disabled/selected visible?).

- OBSERVED: "HUD chip: pill, cream fill, dark outline, coin icon overlapping the left edge by ~30% of its width, numeral right of it." / "Tab bar: 4 items, selected item has a raised pill background."
- HIGH: "Button hierarchy: green = advancing action, grey = secondary (two buttons, same silhouette, different fills)."
- ASSUMPTION: "The grey button is a disabled state rather than a secondary style." (cannot distinguish without interaction)
- NOT DERIVABLE: hover/pressed/focus/disabled visuals not shown, touch feedback, tap target padding beyond the visual bounds.

### Pass G — Character and illustration rendering

Look at: proportion class (realistic / stylised / chibi — head ≥ 40% of height), outline (present, colour, width vs UI outline), shading (flat / soft cel / hard cel / painterly / gradient), eye/face treatment, texture, whether illustration and UI share outline and shading language.

- OBSERVED: "Mascot proportions: head ≈ 50% of total height; flat colour fills; one shadow shape under the chin."
- HIGH: "Illustration and UI share the same dark-brown outline and flat-plus-one-shadow shading → one rendering language across assets."
- ASSUMPTION: "Characters are vector artwork." (edges look clean at this resolution)
- NOT DERIVABLE: rig/animation style, number of expressions, asset resolution, whether the illustration is a placeholder.

### Pass H — Motion cues

Only when the input is a video, gif, or a frame sequence (the reference `path` ends in `.gif/.mp4/.webm/.mov` or the label says frames/sequence/video). Otherwise write exactly one observation per analysis, `category: "motion"`, `confidence: "not-derivable"`, `evidence: "n/a — static image"`, and list the motion topics in `not_derivable`.

With a sequence: count frames per transition, note overshoot (bouncy), ease-in/out shape, anticipation/squash, stagger order, idle loops. Timing in frames (OBSERVED) or ms only if the frame rate is known (HIGH); otherwise ASSUMPTION.

- OBSERVED: "Popup entrance: scales from ~0.8 to ~1.05 then settles at 1.0 across 9 frames."
- HIGH: "Overshoot present → bouncy motion class." (one step from the observed overshoot)
- ASSUMPTION: "Duration ≈ 300 ms." (frame rate not given)
- NOT DERIVABLE (static): everything.

### Pass I — Contrast, readability, touch-target estimates

Look at: text/background pairs (estimate ratio from sampled colours, state the pair), text size relative to frame height (label height % of frame), smallest tappable element as % of frame width, spacing between adjacent targets, reliance on colour alone for meaning (lives as red hearts vs count).

- OBSERVED: "Smallest tappable element: settings gear ≈ 5% of frame width; adjacent HUD chips separated by ≈ 2% of frame width."
- HIGH: "Readability aid: every text over a coloured fill carries a dark outline → legibility does not depend on the fill contrast alone."
- ASSUMPTION: "White on orange ≈ 3:1 — below 4.5:1 without the outline." / "Gear is ~44 pt on a 390 pt-wide phone." (device assumed)
- NOT DERIVABLE: actual hit-test area, dynamic type behaviour, screen-reader labels, colour-blind safety of unseen states.

All contrast and size numbers in this pass are ASSUMPTION at best unless the user supplied device and scale. Flag risks; do not assert failures.

### Pass J — Recurring rules across images (multi-image only)

After Passes A–I for every image, compare observations across references, topic by topic. A topic agreeing across ≥ 2 references becomes a rule with `derived_from` listing one observation per reference and confidence = min of them; agreement raises nothing above `observed`. Disagreements go to `references/multi-reference-reconciliation.md` §2.

- OBSERVED: "Outline present on all interactive elements in ref-1 and ref-2."
- HIGH: "One outline colour (dark brown) across UI and characters in both references."
- ASSUMPTION: "Screens not provided follow the same rules." (do not write this as an observation; write the unseen screens into `not_derivable`)

### Pass K — Context-dependent differences

For differences between references of different `screen_type`: classify as intentional context difference or conflict per `references/multi-reference-reconciliation.md` §4. Record intentional ones as `context:<screen_type>` rules, the rest as conflicts. Also note within-image contextual variation (HUD during gameplay smaller than on home) as separate observations with explicit regions.

## Step 4 — Derive rules

For every topic with at least one `observed`/`high` observation, write a rule: `target` from the recommended vocabulary (`references/extraction-schema.md` §4), an implementable statement, `derived_from` ids, `confidence` = min of the derived observations, `scope` `global` unless the evidence is confined to one screen type. Observations graded `assumption` produce rules only with confidence `assumption` (they will be routed to `unknowns`); `not-derivable` observations produce no rules.

Ordering of rule targets in the file (for stable diffs): `palette, radius, outline, shading, shadow, typography, icon, layout, button.*, hud, popup, card, character, motion`.

## Step 5 — Reconcile, validate, report

1. Apply `references/multi-reference-reconciliation.md` (roles, conflicts, context differences). With one file per image, let the script do it:
   ```bash
   python3 scripts/reference_analysis.py merge ref-1.json ref-2.json --out reference-analysis.json --roles ref-1:color,shapes ref-2:buttons,popup
   ```
2. Fill `not_derivable` with every topic the user asked about or the profile needs that no input can answer. Standard entries for static input: `animation timing and easing`, `pressed and disabled states`, `font family names`, `exact pixel values at device scale`, `screens not provided: <list>`.
3. Run `python3 scripts/reference_analysis.py validate reference-analysis.json` (`references/extraction-schema.md` §8). Fix errors; keep warnings in the summary.
4. Summarise to the user in ≤ 12 lines (`python3 scripts/reference_analysis.py summary reference-analysis.json` prints a starting point): references and roles, counts by confidence, open conflicts (each with the question to answer), top rules, everything not derivable. Never write "I saw" for a `human-description` reference; write "per your description".

## Step 6 — From analysis to Visual Direction Profile

`python3 scripts/reference_analysis.py to-profile reference-analysis.json --out partial-profile.json` (or directly `python3 ../visual-direction/scripts/vd.py profile --reference reference-analysis.json`) maps rules to profile fields. Both routes use the same derivation, so continuing from the fragment gives the same profile as continuing from the raw analysis (the fragment additionally separates the body classification from display). Only `observed`/`high` rules populate contract fields; everything else goes to `unknowns`. Mapping:

| Profile field | Source in `reference-analysis.json` | Mapping rule |
|---|---|---|
| `sources[]` | `references[]` | one entry `{"type": "reference-analysis", "ref": "reference-analysis.json", "roles": [union of all owned roles]}` |
| `product.kind` | `references[]` | only without `--style-id`: `game` when any reference is `gameplay`/`shop` or the references own `hud`/`characters`, else `app`; an `unknowns` line asks to confirm |
| `style.confidence` | rules | `high` if ≥ 5 global rules are observed/high and no open conflicts; else `assumption` |
| `shape.radius_class` | rule `target: radius` | px values in the rule and its observations first (median: ≤2 none, ≤6 sm, ≤10 md, ≤16 lg, ≤32 xl, else pill); otherwise the class named for the dominant container family (the clause containing container/panel/card wins over the button clause); an `unknowns` line asks to verify |
| `shape.silhouette` | rule `radius` | `rounded-rect`, `pill`, `rounded-blob`, `bevelled`, `sharp` |
| `shape.outline.width` / `color_rule` | rule `target: outline` | width: `0` for none, else the first px value in the rule or its observations, else `3` for thick/heavy and `2` otherwise (flagged in `unknowns` as an assumption); `color_rule` ∈ `lighter-tint-of-fill, darker-shade-of-fill, contrast-dark, none` |
| `rendering.shading` | rule `target: shading` | map: flat → `flat`; flat + single soft shadow shape → `soft-cel`; hard shadow shapes → `cel`; gloss band/specular → `glossy`; blurred gradients → `soft`; brushy → `painterly`; pixel grid → `pixel`; clay-like volume → `clay` |
| `rendering.highlight` / `shadow` / `texture` | Pass D rules | free strings from the rule statement (`top-left-gloss`, `top-band`, `offset-soft`, `bottom-edge`, `none`) |
| `typography.display` / `body` | rule `target: typography` + its observations | **classification** strings (`heavy rounded sans`) when the family name is not known (CC-4). Clauses mentioning body / caption / sub-label / regular / humanist classify `body`; the rest classify `display`. Without a body clause, `body` is the display classification without its weight word and an `unknowns` line asks to confirm. When the user named the family, use the name for both. |
| `typography.case` / `weight_rule` | rule `typography` | `title / upper / lower / sentence / mixed`; weight rule as stated |
| `palette_strategy` | rule `target: palette` | the rule statement verbatim |
| `palette.seeds` / `palette.surfaces` / `palette.observed` | `palette_observed[]` | seeds: `primary → brand`, `secondary → secondary`, `accent`/`cta` → accent, `text`/`neutral` → neutral (largest share wins; `vd.py` tints the neutral); surfaces: highest-share `background`, `surface`, `text`, `outline` guesses; the full list is passed through as `palette.observed`, from which `vd.py` re-derives seeds and surfaces. Role guesses stay assumptions until the user confirms them |
| `iconography.style` | rule `target: icon` | `filled-rounded / filled / filled-two-tone / outline / pixel / mixed`; `stroke` null |
| `illustration.character_style` / `asset_rendering` | rule `target: character` | first clause of the statement (lower-case, ≤ 60 characters) / the statement (≤ 160 characters) |
| `motion.class` | rule `target: motion` | only from a sequence input; otherwise left empty with `unknowns`: "motion class not derivable from static references" |
| `components` | rules `button.*`, `hud`, `popup`, `card`, `tab-bar`, `chip`, other component targets | key = target, value = statement |
| `intentional_exceptions[]` | rules with `scope: context:<screen>` | `{"scope": "<screen>", "rule": statement, "reason": "observed in <ref-ids> (rule-N)"}` |
| `anti_patterns[]` | observed/high global rules | clauses starting with no / never / not become `Do not use …` (at least four words; clauses with except/unless are skipped) |
| `qa_criteria[]` | rules observed/high, global | one checkable line per rule: `"<target>: <statement>"` |
| `unknowns[]` | assumption rules, open conflicts, `not_derivable[]`, defaulted roles | per the `references/confidence-levels.md` promotion table |
| `principles[]` | first 5 global rules | first clause of the statement, ≤ 110 characters (longer ones end in `…`) |

Required profile fields that references cannot supply (`product.kind`, `product.platforms`, a catalog `style.id`) come from the user / catalog in `vd.py profile`; `to-profile` output is a **partial** profile and says so (`"_partial": true`, stripped by `vd.py profile` after merge). Without `--style-id`, the partial profile records `style.id = reference-derived-custom`; with a catalog style, reference rules override catalog values for the roles the references own.
