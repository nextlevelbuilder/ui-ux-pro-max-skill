<!-- generated-by: visual-direction vd.py {{tool_version}}; profile-hash: {{profile_hash}} -->
# Design System Master File

> **LOGIC:** When building a specific page, first check `design-system/{{project_slug}}/pages/[page-name].md`.
> If that file exists, its rules **override** this Master file for that page only.
> If not, strictly follow the rules below. Every override must carry a `reason`.

---

**Project:** {{project_name}}
**Generated:** {{generated_at}} by `visual-direction` (`vd.py init`, derivation `{{derivation_version}}`)
**Product:** {{product_kind}} · {{product_genre}} · {{platforms_csv}} · stack `{{stack}}` · unit `{{platform_unit}}`
**Contract files:** `style-profile.json` · `tokens.json` · `component-catalog.md` · `asset-guidelines.md` · `interaction-guidelines.md` · `visual-qa-checklist.md` · `CHANGELOG.md`

---

## Identity

- **Style:** {{style_name}} (`{{style_id}}`, family `{{style_family}}`, confidence `{{style_confidence}}`)
- **Mood:** {{mood_csv}}
- **Audience:** {{audience}} · **Orientation:** {{orientation}}
- **Principles:**
{{#principles}}
  - {{.}}
{{/principles}}
- **Sources:** {{sources_csv}}

## Visual Direction

| Axis | Value |
|---|---|
| Shape | radius class `{{radius_class}}` · silhouette `{{silhouette}}` · outline {{outline_width}} ({{outline_color_rule}}) |
| Rendering | shading `{{shading}}` · highlight `{{highlight}}` · shadow `{{shadow}}` · texture `{{texture}}` |
| Typography | display **{{font_display}}** / body **{{font_body}}** · case {{type_case}} · {{weight_rule}} |
| Palette strategy | {{palette_strategy}} |
| Iconography | {{icon_style}} · stroke {{icon_stroke}} · library `{{icon_library_hint}}` |
| Illustration | {{character_style}} · {{asset_rendering}} |
| Motion | class `{{motion_class}}` · fast/base/slow {{duration_fast}}/{{duration_base}}/{{duration_slow}} ms · reward/ambient {{duration_reward}}/{{duration_ambient}} ms · easing `{{easing_name}}` · reduced motion: {{reduced_motion}} |

## Token Summary

Full source of truth: `tokens.json` (`$extensions.vdp.generatedFrom = {{style_id}}`). Values below are resolved; do not retype them in code — reference the token.

### Colour (semantic)

| Role | Token | Resolved | On-colour | Contrast |
|---|---|---|---|---|
{{#semantic_colors}}
| {{label}} | `semantic.color.{{key}}` | `{{hex}}` | `{{on_hex}}` | {{contrast}} |
{{/semantic_colors}}

### Scales

| Group | Keys → values ({{platform_unit}}) |
|---|---|
| spacing | {{spacing_row}} |
| radius | {{radius_row}} · picks: control `{{radius_control}}`, container `{{radius_container}}`, popup `{{radius_popup}}`, tile `{{radius_tile}}`, chip `{{radius_chip}}` |
| outline | {{outline_row}} · control = `{{outline_control}}` |
| fontSize | {{font_size_row}} |
| lineHeight | {{line_height_row}} |
| iconSize | {{icon_size_row}} |
| touchTarget | min `{{touch_min}}` · recommended `{{touch_recommended}}` |
| duration | {{duration_row}} |
| easing | {{easing_row}} |
| zIndex | {{z_index_row}} |
| opacity | {{opacity_row}} |
| shadow set `{{shadow}}` | {{shadow_row}} |
| elevation | method `{{elevation_method}}` · raised `{{elevation_raised}}` · elevated `{{elevation_elevated}}` · floating `{{elevation_floating}}` |

### Typography roles

| Role | Family | Size | Line height | Weight |
|---|---|---|---|---|
{{#typography_roles}}
| {{role}} | {{family}} | {{size}} | {{line_height}} | {{weight}} |
{{/typography_roles}}

## Component Rules

See `component-catalog.md` (filtered for `{{product_kind}}` + `{{style_id}}`; {{component_count}} components).
Component defaults live in `tokens.json#component.*`; the catalog says how to use them, the tokens say what they are.
Style-specific component notes from the profile:
{{#component_notes}}
- `{{id}}`: {{note}}
{{/component_notes}}

## Page Override Logic

1. Read this file fully. Then read `pages/<page>.md` if it exists.
2. A page file may only contain **deviations**. Each deviation = `token path` + `page value` + `reason`.
3. A page file that restates ≥ {{drift_restated_threshold}} Master values unchanged is rejected by `vd.py validate` (copy, not override).
4. **Drift budget per screen:** colour and font family: 0 ad-hoc values; radius: ≤ {{budget_radius}} exception with reason; spacing/fontSize: ≤ {{budget_spacing}} off-scale values with reason; shadows: 0 new variants; duration: ≤ {{budget_duration}} with reason. Anything above the budget is a `visual-audit` finding, not a style choice.
5. Pages never redefine `semantic.color.*` meanings; they may remap a component to a different existing token.

## Intentional Exceptions

| Scope | Rule | Reason | Status |
|---|---|---|---|
{{#intentional_exceptions}}
| {{scope}} | {{rule}} | {{reason}} | {{status}} |
{{/intentional_exceptions}}

(Exceptions are the only place a value outside `tokens.json` is legal. `visual-audit` marks matching findings as `intentional-exception` instead of `rule`.)

## Anti-Patterns (Do NOT Use)

{{#anti_patterns}}
- ❌ {{.}}
{{/anti_patterns}}

## QA Criteria

{{#qa_criteria}}
- [ ] {{.}}
{{/qa_criteria}}
- [ ] Every `onX` text passes 4.5:1 on its `X` (see Colour table)
- [ ] All interactive targets ≥ `{{touch_min}}` {{platform_unit}}
- [ ] No colour, font family, radius or duration outside `tokens.json` without an entry above

## Unknowns

{{#unknowns}}
- {{.}}
{{/unknowns}}

## Change Log

See `CHANGELOG.md` (append-only; `vd.py` writes `[tool]` entries, humans write `[manual]` entries). Last entry: {{last_changelog_entry}}
