# Extraction Schema — `reference-analysis.json`

Field-by-field specification of the analysis document (`"schema": "vdp-reference-analysis/1"`), the validation rules `scripts/reference_analysis.py validate` enforces, a worked two-image example, and the `extract-colors` algorithm.

Terminology: MUST = validation error (exit 1). SHOULD = validation warning (printed on stderr, exit 0). All ids are case-sensitive strings.

## 1. Top level

| Field | Type | Required | Rules |
|---|---|---|---|
| `schema` | string | yes | MUST equal `"vdp-reference-analysis/1"`. |
| `project` | string | no | Free text. Fixtures and synthetic data MUST say so here (`"synthetic fixture — not a user-provided reference"`). |
| `references` | array | yes | MUST have ≥ 1 entry. |
| `observations` | array | yes | SHOULD be non-empty once a reference was viewed or described (an empty skeleton only warns, so the file can be validated before analysis). |
| `rules` | array | yes | MAY be empty. |
| `conflicts` | array | yes | MAY be empty. |
| `not_derivable` | array of string | yes | MAY be empty; entries MUST be unique after trimming and lower-casing. |
| `palette_observed` | array | yes | MAY be empty. |

Unknown top-level keys: SHOULD warn (forward compatibility), never error. Keys starting with `_` (such as the `_help` fields of `templates/reference-analysis.template.json`) are comments and are ignored.

## 2. `references[]`

| Field | Type | Required | Rules |
|---|---|---|---|
| `id` | string | yes | MUST be unique within `references`. MUST match `^ref-[0-9]+$`. |
| `path` | string | yes | Relative or absolute path as supplied; `validate` MUST NOT require the file to exist (the JSON may travel without the images). `validate --check-paths` adds an existence check as a warning (`W-PATH`). |
| `label` | string | yes | Human label; non-empty. |
| `roles` | array of enum | yes | Subset of `color, shapes, characters, buttons, hud, popup, icons, typography, layout, motion`. MAY be empty. No duplicates within one reference. |
| `viewed_by` | enum | yes | `model-vision` (the agent's runtime returned the image content to the model), `human-description` (a person described the image in writing; the agent did not see it), `none` (listed but neither viewed nor described). |
| `screen_type` | enum | yes | `home, gameplay, popup, shop, other`. |
| `provenance` | object | yes | See below. |
| `provenance.owner` | string | yes | `user`, `third-party`, `unknown`. |
| `provenance.license` | string | yes | `own-work`, `licensed`, `fair-use-reference`, `unknown`. Default when the user does not answer: `unknown`. |
| `provenance.note` | string | no | Free text (where it came from, what the user said). |

Cross-field rules:

- R-ROLE-1: each role value MUST appear in the `roles` of at most one reference ("exactly one owner" when owned; zero owners is allowed and produces open conflicts, see §5). Error text: `role 'color' owned by ref-1 and ref-2`.
- R-VIEW-1: a reference with `viewed_by: "none"` SHOULD have `roles: []`. If it owns roles, warn: "role reserved on an unviewed reference; no rules may derive from it".
- R-VIEW-2: every observation whose `refs` include a `viewed_by: "none"` reference MUST have `confidence: "not-derivable"`.
- R-VIEW-3: every observation whose `refs` include only `human-description` references MUST NOT have `confidence: "observed"` (cap at `high`).

## 3. `observations[]`

| Field | Type | Required | Rules |
|---|---|---|---|
| `id` | string | yes | Unique within `observations`; MUST match `^obs-[0-9]+$`. |
| `category` | enum | yes | `layout, color, shape, shading, typography, component, character, motion, accessibility, iconography`. |
| `statement` | string | yes | One claim per observation (see `references/confidence-levels.md`: split mixed statements). Non-empty. Begin with the topic key ("Panel corner radius: …") so `merge` can compare topics mechanically. |
| `refs` | array of string | yes | ≥ 1 entry; every entry MUST resolve to a `references[].id`. |
| `evidence` | string | yes | Where in the image (region, element) or where in the description (paragraph). For `not-derivable` it MUST start with `"n/a"` followed by the reason. |
| `confidence` | enum | yes | `observed, high, assumption, not-derivable`. |

Cross-field rules:

- R-OBS-1: `category: "motion"` observations MUST be `not-derivable` unless at least one ref `label` or `path` indicates a sequence (`.gif`, `.mp4`, `.webm`, `.mov`, or label containing `frames`/`sequence`/`video`). SHOULD warn when such a ref exists but the observation is still `not-derivable`.
- R-OBS-2: an observation with `refs` spanning ≥ 2 references and a statement that records a difference ("differs", "versus", "vs", "contradicts", "whereas", "rather than") SHOULD have a matching entry in `conflicts` (topic contained in the statement) or a `context:` scoped rule derived from it (warning only; the agent decides which).

## 4. `rules[]`

| Field | Type | Required | Rules |
|---|---|---|---|
| `id` | string | yes | Unique within `rules`; MUST match `^rule-[0-9]+$`. |
| `target` | string | yes | Non-empty. Recommended vocabulary: `palette, radius, outline, shading, shadow, typography, icon, hud, popup, card, character, layout, motion, button.primary, button.secondary, button.icon, chip, tab-bar, dialog, toast, progress, reward`. Values outside the list SHOULD warn (`W-TARGET`, never an error) so new component names can be introduced. |
| `statement` | string | yes | Imperative, implementable, one sentence or a short list. |
| `derived_from` | array of string | yes | ≥ 1 entry; every entry MUST resolve to an `observations[].id`. |
| `confidence` | enum | yes | `observed, high, assumption`. `not-derivable` is NOT allowed on a rule. |
| `scope` | string | yes | MUST be `global` or `context:<screen_type>` with `<screen_type>` ∈ `home, gameplay, popup, shop, other`. |

Cross-field rules:

- R-RULE-1: `confidence` MUST be ≤ the minimum confidence of its `derived_from` observations (ordering `observed > high > assumption > not-derivable`). If any derived observation is `not-derivable`, the rule is invalid.
- R-RULE-2: a rule whose `target` maps to a role (table in `references/multi-reference-reconciliation.md` §1.2) and whose `derived_from` observations all reference a single reference MUST have that reference as the role owner, or the role MUST be unowned. (Prevents "ref-2 says buttons are pills" becoming a rule when ref-1 owns `buttons`.) Error.
- R-RULE-3: `scope: global` rules with confidence `assumption` SHOULD warn: "assumption cannot enter MASTER; will be routed to unknowns".

## 5. `conflicts[]`

| Field | Type | Required | Rules |
|---|---|---|---|
| `topic` | string | yes | Short noun phrase, lower-case, unique within `conflicts` (case-insensitive). |
| `between` | array of string | yes | ≥ 2 entries, all MUST resolve to `references[].id`, no duplicates. |
| `resolution` | string | yes | For `resolved`: MUST name the winning ref and the reason (`"ref-1 wins (role shapes)"`). For `open`: MUST say what the user needs to decide. Non-empty in both cases. |
| `status` | enum | yes | `resolved, open`. |

Cross-field rules:

- R-CONF-1: `status: "resolved"` resolution MUST contain the string `ref-<n> wins` where `ref-<n>` ∈ `between`. Error otherwise.
- R-CONF-2: for every role owned by exactly one reference, no `open` conflict whose topic maps to that role may exist (it must have been resolved by ownership). Error.
- R-CONF-OPEN (`--strict` only): any `open` conflict is an error. Without `--strict`, open conflicts are reported in the summary and exit 0.

## 6. `not_derivable[]`

Array of strings; each a noun phrase naming what was asked for or expected but cannot be known from the inputs. SHOULD include the standard entries whenever only static images were given (`W-ND-STD`): `"animation timing and easing"`, `"pressed and disabled states"`, `"font family names"`, `"exact pixel values at device scale"`.

## 7. `palette_observed[]`

| Field | Type | Required | Rules |
|---|---|---|---|
| `hex` | string | yes | MUST match `^#[0-9A-F]{6}$` (upper-case; `validate` accepts lower-case with a warning `W-HEX-CASE`). |
| `share` | number | yes | `0 < share ≤ 1`, at most 4 decimals. |
| `role_guess` | enum | yes | `background, surface, primary, secondary, accent, text, outline, shadow, highlight, unknown`. |
| `ref` | string | yes | MUST resolve to `references[].id`. |

Cross-field rules:

- R-PAL-1: sum of `share` per `ref` MUST be ≤ 1.0 + 0.01.
- R-PAL-2: per `ref`, at most one entry each for `background` and `text`. Warning.
- R-PAL-3: per `ref`, any two entries with RGB Euclidean distance < 24 SHOULD warn as near-duplicates.
- R-PAL-4: `role_guess` is always treated as `assumption` by consumers; the file does not carry a confidence field for palette entries.

## 8. Validation summary (ordered, for `validate --json`)

Output shape: `{"status": "OK|FAIL", "file": "...", "errors": [{"code": "R-RULE-1", "path": "rules[2]", "message": "..."}], "warnings": [...], "counts": {...}}`. Exit `0` when no errors, `1` when ≥ 1 error **or the file is not valid JSON** (the error then has code `E-JSON` and names the line/column), `2` when the file is missing or unreadable (`E-IO`). Text mode prints `OK <file>: <counts>` or one `ERROR <code> <path>: <message>` line per error followed by `FAIL <file>: n error(s)`; warnings go to stderr as `WARN <code> <path>: <message>`.

Check order: schema string → required top-level keys → per-array id patterns and uniqueness → enums → reference resolution (`refs`, `derived_from`, `between`, `ref`) → role ownership (R-ROLE-1) → viewed_by constraints (R-VIEW-*) → motion/difference checks (R-OBS-*) → rule confidence and ownership (R-RULE-1..3) → conflicts (R-CONF-*) → palette (R-PAL-*) → advisory warnings. Report all errors, do not stop at the first.

## 9. Worked mini example (two images)

The user supplied `refs/home.png` ("use this for colours and shapes") and `refs/popup.png` ("use this for the buttons"). The runtime could view both.

```json
{
  "schema": "vdp-reference-analysis/1",
  "project": "mini example — synthetic",
  "references": [
    {"id": "ref-1", "path": "refs/home.png", "label": "home screen", "roles": ["color", "shapes"],
     "viewed_by": "model-vision", "screen_type": "home",
     "provenance": {"owner": "user", "license": "unknown", "note": "user-provided"}},
    {"id": "ref-2", "path": "refs/popup.png", "label": "settings popup", "roles": ["buttons"],
     "viewed_by": "model-vision", "screen_type": "popup",
     "provenance": {"owner": "user", "license": "unknown", "note": "user-provided"}}
  ],
  "observations": [
    {"id": "obs-1", "category": "color", "statement": "Background is a light lavender; the accent is a saturated yellow used on the play button only.",
     "refs": ["ref-1"], "evidence": "full-bleed background; centre button", "confidence": "observed"},
    {"id": "obs-2", "category": "shape", "statement": "Cards have corners rounded to about 20% of their height (lg class).",
     "refs": ["ref-1"], "evidence": "three stacked cards, centre of frame", "confidence": "observed"},
    {"id": "obs-3", "category": "component", "statement": "Popup buttons are pills with a 2-tone fill (lighter top half) and a dark outline.",
     "refs": ["ref-2"], "evidence": "two buttons at the bottom of the popup", "confidence": "observed"},
    {"id": "obs-4", "category": "shape", "statement": "The popup panel corners are rounded to about 10% of height (md class), smaller than home cards.",
     "refs": ["ref-1", "ref-2"], "evidence": "popup panel vs home cards", "confidence": "observed"},
    {"id": "obs-5", "category": "motion", "statement": "No motion information in static frames.",
     "refs": ["ref-1", "ref-2"], "evidence": "n/a — static images", "confidence": "not-derivable"}
  ],
  "rules": [
    {"id": "rule-1", "target": "palette", "statement": "Lavender base, yellow accent reserved for the primary action.",
     "derived_from": ["obs-1"], "confidence": "observed", "scope": "global"},
    {"id": "rule-2", "target": "radius", "statement": "Cards and panels use the lg radius class.",
     "derived_from": ["obs-2", "obs-4"], "confidence": "observed", "scope": "global"},
    {"id": "rule-3", "target": "button.primary", "statement": "Pill, 2-tone fill with lighter top half, dark outline.",
     "derived_from": ["obs-3"], "confidence": "observed", "scope": "global"}
  ],
  "conflicts": [
    {"topic": "panel corner radius", "between": ["ref-1", "ref-2"],
     "resolution": "ref-1 wins (role shapes): lg globally; ref-2 md noted, ask user if popups intentionally differ.",
     "status": "resolved"}
  ],
  "not_derivable": ["animation timing and easing", "pressed and disabled states", "font family names", "exact pixel values at device scale"],
  "palette_observed": [
    {"hex": "#E6E0FF", "share": 0.47, "role_guess": "background", "ref": "ref-1"},
    {"hex": "#FFFFFF", "share": 0.22, "role_guess": "surface", "ref": "ref-1"},
    {"hex": "#FFD23F", "share": 0.08, "role_guess": "accent", "ref": "ref-1"},
    {"hex": "#3B2F5C", "share": 0.09, "role_guess": "text", "ref": "ref-1"}
  ]
}
```

What makes this valid: ids unique and patterned; `refs`/`derived_from`/`between`/`ref` all resolve; `color` and `shapes` owned by ref-1 only, `buttons` by ref-2 only; rule-2 (target `radius` → role `shapes`) derives from observations that include ref-1, the owner; the radius conflict is `resolved` and names `ref-1 wins`; the motion observation is `not-derivable` because no sequence input exists; palette shares sum to 0.86 ≤ 1.01.

## 10. `extract-colors` algorithm (Pillow optional)

Command:

```bash
python3 scripts/reference_analysis.py extract-colors refs/home.png --ref-id ref-1 --k 10 --json --out palette-ref-1.json
```

(`--ref` and `--colors` are accepted as aliases of `--ref-id` and `--k`.)

Purpose: produce `palette_observed[]` entries for one reference. It does not classify style; it counts pixels. It never writes the image, never modifies an analysis file, and never contacts the network.

### 10.1 Preconditions and degradation

1. The image path must exist; otherwise usage error, exit 2.
2. `--k` MUST be in `[8, 12]`; outside → usage error, exit 2. Default 10.
3. `try: from PIL import Image` — on `ImportError` print `BLOCKED: Pillow (PIL) is not installed (pip install Pillow); palette extraction unavailable` to stderr, emit `{"status": "BLOCKED", "reason": "pillow-missing", "message": "..."}` on stdout when `--json`, exit **3**. The import happens inside the command, so every other subcommand works without Pillow.
4. Open the file; on any `OSError`/`UnidentifiedImageError` → `{"status": "BLOCKED", "reason": "unreadable-image"}`, exit 3.

### 10.2 Steps (deterministic; no randomness)

```
1. img = Image.open(path); img.load()
2. Downscale: img.thumbnail((200, 200), Image.Resampling.LANCZOS)
   → longest side ≤ 200 px, aspect preserved. (Thumbnail never upscales.)
3. Alpha handling:
   a. If img.mode in ("RGBA", "LA", "P" with transparency): convert to "RGBA",
      collect pixels with alpha ≥ 128 into a list; if fewer than 1% of pixels
      remain → BLOCKED reason "image-transparent", exit 3.
      Build a working image: Image.new("RGB", (len(pixels), 1)) and putdata(pixels)
      (a 1-row strip; max 40 000 px, trivially small).
   b. Else: work = img.convert("RGB").
4. Quantize: q = work.quantize(colors=K, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
   (Pillow < 9.1: method=0, dither=0.) K = --k.
5. Counts: for (count, index) in q.getcolors(): rgb = palette[index*3 : index*3+3]
   where palette = q.getpalette(). total = sum(counts).
   share = round(count / total, 4).
6. Sort entries by share descending, then by hex ascending (tie-break for determinism).
7. Near-duplicate merge: walk the sorted list; keep an output list.
   For each entry e: if any kept k has sqrt((Δr)²+(Δg)²+(Δb)²) < 24 → k.share += e.share
   (k keeps its own hex, i.e. the larger-share colour wins); else append e.
   Re-round shares to 4 decimals.
8. Role guess (ALL guesses are confidence "assumption"; the JSON result carries
   "confidence": "assumption" at the top level so callers cannot miss it):
   Define for each kept colour:
     Y = (0.299·R + 0.587·G + 0.114·B) / 255            # perceived luminance, 0..1
     S = 0 if max(R,G,B) == 0 else (max(R,G,B) - min(R,G,B)) / max(R,G,B)   # HSV saturation
   a. background: the largest-share colour with Y ≥ 0.55; if none, the largest-share colour.
   b. text: if background.Y ≥ 0.45 → the lowest-Y remaining colour with Y ≤ 0.25 and share ≥ 0.01;
            else → the highest-Y remaining colour with Y ≥ 0.75 and share ≥ 0.01. May be absent.
   c. outline: the remaining colour with Y ≤ 0.30, S ≤ 0.6, share ≥ 0.02, if different from text. May be absent.
   d. accent: among remaining with 0.03 ≤ share ≤ 0.35, the highest S if S ≥ 0.45. May be absent.
   e. surface: the remaining colour with |Y − background.Y| ≤ 0.15 and share ≥ 0.05, largest share. May be absent.
   f. primary: remaining colour with the highest share·S where S ≥ 0.30. May be absent.
   g. secondary: next remaining by the same measure, S ≥ 0.30. May be absent.
   h. everything else: "unknown".
   Each role is assigned at most once; a colour gets the first role it qualifies for in the order a→g.
9. Emit:
   {"status": "OK", "ref": "<--ref-id or null>", "image": "<path>", "size_analysed": [w, h],
    "colors_requested": K, "colors_kept": n, "confidence": "assumption",
    "palette_observed": [{"hex": "#RRGGBB", "share": 0.4213, "role_guess": "background", "ref": "ref-1"}, ...]}
   Exit 0. Text mode prints one line per colour: "#RRGGBB  42.13%  background (assumption)".
```

### 10.3 Notes

- `hex` is upper-case. `share` sums to ≤ 1.0 by construction (quantize covers every pixel; merging adds shares).
- The `role_guess` thresholds are heuristics; the docstring of `guess_roles` says "assumption — verify against the image". Tests assert `confidence == "assumption"` in the output.
- Median cut output can differ by one or two RGB units between Pillow versions. Tests use synthetic images made of flat rectangles with colours ≥ 60 units apart and assert shares within ±0.02 and hex within distance 8, not exact equality.
- The Pillow-free path is tested in-process (`sys.modules["PIL"] = None`) and in a subprocess with a fake `PIL` package that raises `ImportError`; both must yield the BLOCKED JSON and exit 3.
- Paste the `palette_observed` array into the analysis file (or let `merge` concatenate per-image files); the script itself never edits an analysis.
