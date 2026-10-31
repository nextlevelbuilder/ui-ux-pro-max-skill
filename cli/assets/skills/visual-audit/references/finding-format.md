# Finding format (`visual-audit/1`)

`scripts/audit.py scan` emits this document; checklist and screenshot findings written by hand use the same shape so one report can hold all of them. The schema is the integration contract's section 4.4; the additive fields below never change existing ones.

## Document

```json
{
  "schema": "visual-audit/1", "generated_at": "2026-10-15T09:00:00Z", "root": "app/",
  "platform": "flutter|unity|web|native|mixed|unknown",
  "contract": {"tokens": "design-system/onet/tokens.json", "profile": "design-system/onet/style-profile.json"},
  "scanned_files": 42, "skipped_files": 3,
  "summary": {"critical": 0, "high": 2, "medium": 5, "low": 1, "info": 0},
  "inventory": {"colors": {"#FF7F50": 3}, "colors_with_alpha": {"#000000@0.40": 1}, "named_colors": {"blue": 1},
                "radii": {"8": 10, "13": 1}, "font_sizes": {"14": 20}, "spacing": {"16": 9}, "shadows": 4,
                "durations": {"200": 5, "337": 1}, "icon_libraries": ["material", "font_awesome_flutter"],
                "icon_libraries_by_platform": {"flutter": ["font_awesome_flutter", "material"]},
                "font_families": ["Nunito"], "components": {"PrimaryButton": ["lib/widgets/primary_button.dart"]}},
  "findings": [ ... ],
  "platforms": {"flutter": 5, "web": 4, "unity": 3},
  "notes": ["inventory-only rules: ...", "skipped (binary/minified/too large): web/vendor.min.css"]
}
```

`platform` is the detected (or forced) platform group; a stock Flutter app is `flutter`, because its `android/ ios/ macos/ linux/ windows/` glue folders and the Flutter `web/` shell are skipped unless `--platform native` is given. `contract.tokens`/`profile` are `null` in inventory mode. `summary` counts every finding including intentional exceptions (under `info`). `platform_detected` records auto-detection even when `--platform` forces another label.

## Finding

```json
{"id": "VA-0001", "rule": "color.off-palette", "severity": "high", "category": "color",
 "file": "lib/screens/shop.dart", "line": 12, "evidence": "Color(0xFFE91E63)",
 "message": "Hard-coded colour #E91E63 not in tokens.json palette",
 "violates": "tokens colour values, all layers (allowed set); profile anti_patterns: ad-hoc colours outside the palette",
 "nearest": "semantic.color.danger #E03E3E (distance 28.0)",
 "impact": "`shop` renders #E91E63 where the contract expects semantic.color.danger; adjacent screens will not match",
 "fix": "Replace with the nearest token semantic.color.danger (#E03E3E) or a semantic colour that fits the role; if intentional, add to `pages/shop.md` intentional_exceptions",
 "files_to_change": ["lib/screens/shop.dart"],
 "verify": "re-run `audit.py scan`; VA-0001 must be absent (`audit.py compare` lists it under resolved)",
 "kind": "rule", "confidence": "exact"}
```

| Field | Rule |
|---|---|
| `id` | `VA-` + 4-digit sequence in output order (severity desc, then file, line, rule, evidence). Ids are **not** stable across runs; `compare` matches on `(rule, file, evidence)`. |
| `rule` | One of the ids in `references/drift-rules.md`. |
| `severity` | `critical`, `high`, `medium`, `low`, `info` — see `references/severity.md`. |
| `category` | The rule prefix: `color`, `radius`, `font-size`, `font-family`, `spacing`, `shadow`, `duration`, `icon`, `component`, `touch`, `text`. |
| `file`, `line` | Relative to the scanned root, `/`-separated; line of the literal (CSS rule-level findings use the selector line). Hand-written screenshot findings use the image path and `line: 0`. |
| `evidence` | The matched source text, whitespace collapsed, ≤ 120 chars. Shorthand declarations that yield several values append ` → <value>` so each finding is distinct. Aggregates: shadow signature, import statement, class/export line. |
| `message` | One sentence, human readable; heuristic rules prefix `[heuristic]`; intentional exceptions prefix `[intentional: <reason>]`. |
| `violates` | Token path of the allowed set, or guideline / WCAG criterion; profile `anti_patterns` text sharing the category keyword is appended. Required for `kind: rule`. |
| `nearest` | Nearest allowed value with distance (colours: luma-weighted RGB; scales: nearest step, ties to the lower step). `null` when not applicable. |
| `impact` | What the user or the brand experiences, in one sentence, naming the screen. |
| `fix` | The replacement token or structural change plus the exception route (`pages/<slug>.md`, slug = file stem without `Screen/Panel/Page/View/Widget` suffixes, kebab-case). Colours farther than 30 from any token get "no close token — pick the semantic role …" instead of the far token. Never "remove the finding". |
| `files_to_change` | Every file the fix touches: the finding's file, plus the canonical file for duplicates, plus all shadow files for a variant explosion. |
| `verify` | How to prove the fix landed. |
| `kind` | See below. |
| `confidence` *(additive)* | `exact` for regex-extracted literals compared with the contract; `heuristic` for touch, contrast and duplicate rules. |

## `kind` tagging

| kind | Use when | Severity allowed | Counts toward `--fail-on` |
|---|---|---|---|
| `rule` | The item maps to a contract value (tokens.json, profile enum, component-catalog rule) or a WCAG success criterion **and** there is measurable evidence | any | yes |
| `recommendation` | Best-practice guideline not encoded in the contract, or a rule-level item whose evidence is heuristic (estimated size, sampled contrast, name-based duplicate) | scanner: ≤ medium (heuristic cap); human-written with a measurement: ≤ high | yes |
| `aesthetic` | Taste or judgement with no contract rule and no measurement; always state what measurement would turn it into a rule | ≤ low | no |
| `intentional-exception` | Matches a `style-profile.json` / `pages/<page>.md` `intentional_exceptions` entry (`scope` substring of the path, `rule` naming the rule or category); `violates` records the exception | info | no |

The scanner assigns `rule` to contract comparisons, `recommendation` to the heuristic rules and to inventory-mode variant explosions, and `intentional-exception` when `--profile` matches; `aesthetic` is reserved for human-written items. The auditor never creates exceptions: propose one in `fix` and leave the real severity until the contract changes.

## Markdown rendering

One finding = one bullet and two indented lines (grep- and diff-friendly, no tables):

```
### HIGH
- **VA-0001** `color.off-palette` [rule] — lib/screens/shop.dart:12 — `Color(0xFFE91E63)`
  Hard-coded colour #E91E63 not in tokens.json palette Nearest: semantic.color.danger #E03E3E (distance 28.0)
  Fix: … · Verify: …
```

## Compare output (`visual-audit-compare/1`)

```
resolved: 1  new: 0  unchanged: 39  changed_severity: 2
```

Key = `(rule, file, evidence lower-cased + whitespace-collapsed)`, matched as a multiset so two identical literals on one line are two findings. Line numbers are ignored (moved code is unchanged). `changed_severity` lists unchanged keys whose severity moved (a count dropping below 3 turns high into medium); the text output adds the line "note: severity recomputed from project-wide occurrence counts after fixes; changed_severity entries are unchanged findings, not regressions" so a partial fix is not read as a regression. Exit 1 only when a `new` finding is at/above `--fail-on`.
