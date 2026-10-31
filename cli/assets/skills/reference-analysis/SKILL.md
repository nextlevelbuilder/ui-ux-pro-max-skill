---
name: reference-analysis
description: Extract the visual language of a game or app from reference screenshots, mockups or images into an evidence-graded reference-analysis.json (observed / high / assumption / not-derivable) and hand it to the visual-direction skill. Use when the user supplies screenshots or images and wants the look extracted, copied, matched or compared, when several references must be combined with roles (this one for colours, that one for buttons), or when a design language must be described before a style profile exists.
argument-hint: "[image paths or analysis.json] [--roles ref-1:color,shapes ...]"
license: MIT
metadata:
  author: ui-ux-pro-max
  version: "1.0.0"
---

# Reference Analysis

Turn 1..N reference images into `reference-analysis.json` (schema `vdp-reference-analysis/1`): references with roles, one-claim observations with evidence and confidence, implementable rules, conflicts, what is not derivable, and a pixel-share palette. The file feeds `../visual-direction/scripts/vd.py profile --reference`, which turns it into a Visual Direction Profile and design contract.

## When to Use

- "Make it look like this screenshot" / "copy the style of these two games"
- Several references with different jobs ("colours from A, buttons from B")
- Describe a design language before choosing a catalog style
- Compare what two references share and where they disagree

Hand-off: style profile, tokens, design contract → `visual-direction` skill. Code audit → `visual-audit` skill. Web tokens from `tokens.json` → `design-system` skill.

## Step 0 — Capability check (do this first, every time)

1. Try to view each image with the runtime's file-reading tool (`Read` on a `.png/.jpg/.webp/.gif` in Claude Code).
2. Success means the tool returned image content you can describe without the filename. Bytes, base64, metadata or an error are failures.
3. Success → `viewed_by: "model-vision"`. Failure → `viewed_by: "human-description"`: send `templates/human-description-template.md` verbatim, once per image, and cap every derived observation at `high` with evidence `"user description, paragraph N"`. No description → `viewed_by: "none"`: the reference owns no roles and contributes only `not-derivable` observations.
4. **Never claim to have seen an image you did not view.** Write "per your description", never "I saw", for described references. Never guess from a filename or label.

## Intake (ask only what is missing, in one message)

| Need | Ask only if |
|---|---|
| Roles per image (`color, shapes, characters, buttons, hud, popup, icons, typography, layout, motion`) | 2+ images and no roles given → offer the default precedence from `references/multi-reference-reconciliation.md` §3 and let the user say "ok" |
| `screen_type` (`home, gameplay, popup, shop, other`) | not obvious from the label or filename |
| `provenance.owner` / `provenance.license` | never stated → default `unknown`, note it in the summary |

Do not ask about product kind, platform or stack; `vd.py profile` collects those.

## Analysis passes (per image, in order)

Full procedure: `references/analysis-workflow.md`. Every claim gets a confidence from the tests in `references/confidence-levels.md`:

- **OBSERVED** — re-checkable by pointing at a region: counts, relative sizes, visible colour families, silhouettes.
- **HIGH** — one conventional inference step from observed facts (outline is a darker shade of the fill; font is a rounded geometric sans).
- **ASSUMPTION** — plausible but not the only reading, or depends on device scale/intent (px values, contrast ratios, "the grey button is disabled").
- **NOT-DERIVABLE** — absent from a static frame: timing, pressed states, font family names, screens not shown. Record it; never fabricate it.

| Pass | Looks at | Typical rule target |
|---|---|---|
| A Layout | bands and their % of height, grid vs free, density, safe areas | `layout` |
| B Palette | dominant / secondary / accent, where each sits; `extract-colors` shares | `palette` |
| C Geometry | silhouette, radius class as % of element height (none 0, sm ≤5, md 5–12, lg 12–20, xl 20–40, pill ≥50), outline width and colour rule | `radius`, `outline` |
| D Shading | flat / gradient / gloss band, shadow type, elevation steps | `shading`, `shadow` |
| E Typography | classification only (never a family name from a raster), weights, case | `typography` |
| F Components | buttons, cards, popups, tab bars, HUD chips: silhouette, fill, outline, label, states visible | `button.*`, `hud`, `popup`, `card`, `tab-bar` |
| G Characters | proportion class, outline, shading, shared language with UI | `character` |
| H Motion | only for gif/video/frame sequences; otherwise one `not-derivable` observation | `motion` |
| I Readability | contrast and touch-target estimates as risk flags (assumption at best) | — |
| J / K Cross-image | agreement → rules; disagreement → conflicts or `context:<screen>` rules | any |

Rules: one observation = one claim prefixed with its topic key ("Panel corner radius: …"); relative measurements only; no style names in observations; a rule's confidence is the minimum of its observations; `not-derivable` observations never produce rules.

## Multiple references

Roles are topic leases: exactly one owner per role, a role may be unowned. Same topic, different class across images → a conflict: `resolved` when the topic's role has an owner (`"ref-1 wins (role shapes)"`), `open` otherwise (the resolution text states the question for the user). Different `screen_type` and user-confirmed intent → a `context:<screen>` rule instead of a conflict. Never convert a conflict into a context rule on your own judgement. Details and the topic → role map: `references/multi-reference-reconciliation.md`.

## Script Paths

Script paths in this skill and its `references/` are relative to the directory that contains this SKILL.md, not to the project: `scripts/<file>` is this skill's own `scripts/` folder, and `../<skill>/scripts/<file>` is a sibling sub-skill installed alongside it. Build the full path from that directory (Claude Code reports it as the skill's base directory when the skill loads) and keep the working directory at the project root — the scripts read and write project files such as `reference-analysis.json`, `refs/*.png` or `design-system/<slug>/` relative to it.

## Commands

`scripts/reference_analysis.py` is standard-library Python 3.8+; only `extract-colors` needs Pillow and degrades to `BLOCKED` (exit 3) without it. Exit codes: `0` ok · `1` validation failed, merge rejected or malformed JSON · `2` usage, missing file or any other error (one `error:` line, never a traceback) · `3` BLOCKED. Every `--out` creates missing parent directories.

| Command | Purpose |
|---|---|
| `validate <analysis.json> [--strict] [--check-paths] [--json]` | Every rule in `references/extraction-schema.md` (ids, enums, role ownership, confidence caps, conflicts, palette). Lists every violation with its rule id; `--strict` makes open conflicts errors; target vocabulary is a warning. |
| `merge <a.json> <b.json> [...] --out merged.json [--roles ref-1:color,shapes ref-2:buttons] [--json]` | One document from per-image analyses: ids must be disjoint, one owner per role, conflict detection, rule confidence re-derived; writes only when the result validates. |
| `extract-colors <image> [--k 10] [--ref-id ref-1] [--json] [--out palette.json]` | Deterministic pixel-share palette (median cut, near-duplicate merge, role guesses marked `assumption`). Paste the entries into `palette_observed`. |
| `to-profile <analysis.json> [--style-id reference-derived-custom] [--project "Name"] [--out partial-profile.json] [--json]` | Partial Visual Direction Profile (`"_partial": true`, printed to stdout without `--out`) with the same derivation as `vd.py profile --reference`: observed/high rules → fields, `components`, `qa_criteria`, `principles`; separate display/body typography classifications; assumptions, open conflicts and `not_derivable` → `unknowns`; `palette_observed` → `palette.seeds`, `palette.surfaces`, `palette.observed`; a `sources[]` entry with the owned roles. |
| `summary <analysis.json>` | ≤ 12 lines: references and roles, counts per confidence, open conflicts with their questions, top rules, not derivable. |
| `template [--out file.json]` | Empty skeleton (same content as `templates/reference-analysis.template.json`). |

Typical sequence:

```bash
python3 scripts/reference_analysis.py template --out reference-analysis.json      # fill references, validate the skeleton
python3 scripts/reference_analysis.py extract-colors refs/home.png --ref-id ref-1 --json
python3 scripts/reference_analysis.py validate reference-analysis.json            # after writing observations and rules
python3 scripts/reference_analysis.py summary reference-analysis.json             # basis for the user-facing summary
python3 ../visual-direction/scripts/vd.py profile --reference reference-analysis.json --platform mobile-ios --out style-profile.json
```

With one file per image: `python3 scripts/reference_analysis.py merge ref-1.json ref-2.json --out reference-analysis.json --roles ref-1:color,shapes ref-2:buttons,popup`.

## Hand-off to `visual-direction`

`python3 ../visual-direction/scripts/vd.py profile --reference reference-analysis.json` (add `--style <id>` to let reference rules override a catalog style for the roles the references own; without it the profile uses `style.id = reference-derived-custom`). `to-profile` emits the same partial profile for inspection; `vd.py profile` completes `product.*`, catalog fallbacks and strips `_partial`. Only `observed`/`high` rules reach `MASTER.md` and `tokens.json`; everything else waits in `unknowns` until the user confirms it in writing.

## Report to the user (≤ 12 lines)

References and their roles · observation and rule counts per confidence · every open conflict with the decision needed · top rules · everything not derivable · licence caveats. State plainly which references were viewed, described, or not analysed.

## Privacy

Reference images stay on the user's machine. Never upload, post, or send them to any service, API or URL; never embed them in artifacts or share links; never copy them into the repository unless the user asks. `extract-colors` reads the file locally and writes only JSON. Record ownership and licence in `provenance` and remind the user before any asset is copied verbatim.

## References

| File | Content |
|---|---|
| `references/analysis-workflow.md` | Intake, capability check, passes A–K with graded examples, rule derivation, mapping into the Visual Direction Profile |
| `references/extraction-schema.md` | Every field and enum, validation rules R-*, `validate --json` shape, worked example, `extract-colors` algorithm |
| `references/multi-reference-reconciliation.md` | Roles, topic → role map, conflict detection and resolution, default precedence, context differences, `merge` behaviour |
| `references/confidence-levels.md` | Decision tests T0–T4, twelve classified statements, promotion table to MASTER |
| `templates/reference-analysis.template.json` | Empty skeleton with `_help` fields |
| `templates/human-description-template.md` | Questions to send when the runtime cannot view images |
