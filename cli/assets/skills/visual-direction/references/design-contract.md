# Design contract — reference for the `visual-direction` skill

Defines what `vd.py init / page / validate` read and write under `design-system/<project-slug>/`.
Everything here is checkable by a script; nothing requires taste. Commands: `python3 scripts/vd.py init --profile style-profile.json --output-dir .`,
`python3 scripts/vd.py page --dir design-system/<slug> --name <page> --reason "…"`, `python3 scripts/vd.py validate --dir design-system/<slug> [--json]`.

## 1. Folder layout (contract §3)

```
design-system/<project-slug>/
├── MASTER.md                 # global contract (see §2 for the tool-generated form, §3 for coexistence)
├── style-profile.json        # Visual Direction Profile, schema vdp/1
├── tokens.json               # three layers + $extensions.vdp (token-derivation.md)
├── component-catalog.md      # rows of component-catalog.csv filtered by Applies To ∈ {kind, both}, rendered as sections
├── asset-guidelines.md
├── interaction-guidelines.md
├── visual-qa-checklist.md
├── CHANGELOG.md              # append-only, §5
├── migrations/               # optional, §6; one file per breaking token change
│   └── 0001-<slug>.md
└── pages/
    └── <page>.md             # overrides ONLY, §4
```

- `<project-slug>` = `safe_slug(project.name)`: lower-case, `[^a-z0-9_-]+ → -`, strip `-`, fallback `default` (identical to `design_system.safe_slug`).
- `<page>` uses the same slug rule. `pages/` is created empty by `init`.
- `init` writes every file **only if absent** (skipped files are listed, never overwritten silently); `--force` overwrites all tool-owned files except `MASTER.md` when it was not written by this tool (§3) and never `pages/<page>.md` or `CHANGELOG.md` (`pages/README.md` is tool-owned). `--json` prints `{"status", "design_system_dir", "created_files", "skipped_files", "overwritten_files", "master", "master_snippet"}`. An invalid profile exits 1 before anything is written.
- File ownership marker: every tool-written markdown starts with an HTML comment
  `<!-- generated-by: visual-direction vd.py <version>; profile-hash: <sha256[:12] of style-profile.json> -->`.
  `validate` uses it to know what it may judge as "stale" (profile hash mismatch → warning).

## 2. `MASTER.md` written by `vd.py init` (template: `templates/master-template.md`)

Sections, in order, all mandatory (validate checks the H2 headings exist):

| # | Heading | Content rule |
|---|---|---|
| 0 | title + LOGIC blockquote | identical wording to the existing `design_system.format_master_md` so downstream prompts that grep for `**LOGIC:**` keep working |
| 1 | `## Identity` | style id/name/family/confidence, mood, audience, orientation, principles, sources (from `style-profile.json`) |
| 2 | `## Visual Direction` | one table: shape, rendering, typography, palette strategy, iconography, illustration, motion — the VDP axes verbatim |
| 3 | `## Token Summary` | resolved tables generated from `tokens.json`: semantic colours with on-colour + contrast ratio; every primitive group as one row of `key=value`; typography roles. Values are *resolved* (hex, numbers) so a reader needs no JSON; the token path is always printed next to the value |
| 4 | `## Component Rules` | pointer to `component-catalog.md` + component count + the `VDP.components` free-text notes |
| 5 | `## Page Override Logic` | the five numbered rules (§4) including the drift budget (§7) with the project's numbers filled in |
| 6 | `## Intentional Exceptions` | table from `VDP.intentional_exceptions` (+ `status` column: `active|retired`) |
| 7 | `## Anti-Patterns (Do NOT Use)` | `VDP.anti_patterns`, one ❌ bullet each (same bullet style as existing MASTER.md) |
| 8 | `## QA Criteria` | `VDP.qa_criteria` as checkboxes + the three generated universal checks |
| 9 | `## Unknowns` | `VDP.unknowns` |
| 10 | `## Change Log` | pointer to `CHANGELOG.md` + last entry line |

Placeholders in `templates/master-template.md` use `{{name}}`, `{{#list}}…{{/list}}` for repetition and `{{.}}` for the
current item — a 40-line stdlib renderer is enough (no Jinja). Unresolved placeholders are a validate error
(regex `\{\{[^}]+\}\}` must not match the written file).

## 3. Coexistence with a `MASTER.md` from `search.py --persist`

`search.py --design-system --persist` already writes `design-system/<slug>/MASTER.md` (format:
`format_master_md` — "Global Rules / Component Specs / Style Guidelines / Anti-Patterns / Pre-Delivery Checklist").
That file is the project's global contract and is **never overwritten or rewritten** by `vd.py`.

Decision table for `vd.py init`:

| `MASTER.md` state | Action |
|---|---|
| absent | write from `master-template.md`; CHANGELOG entry `init: MASTER.md created` |
| present, first line contains `generated-by: visual-direction` | tool-owned → rewrite only with `--force`; otherwise untouched + warning. The header records `body-hash` (sha256[:12] of everything below it); if the body no longer matches (hand edits) or no hash is recorded, `--force` first moves the file to `MASTER.md.bak-<UTC timestamp>`, prints it, lists it under `backups` in `--json` and in the CHANGELOG entry |
| present, anything else (search.py or hand-written) | untouched. Print to stdout (and to `--json` as `master_snippet`) a ready-to-paste block, and write the same block to `MASTER.visual-direction.md` next to it so nothing is lost |

The paste block is exactly sections 2, 3, 5, 6 of §2 wrapped as:

```markdown
---

## Visual Direction
<!-- generated-by: visual-direction vd.py <version>; paste below "## Global Rules" of MASTER.md -->
…(Visual Direction table)…
### Token Summary
…
### Page Override Logic
…
### Intentional Exceptions
…
```

Precedence when both exist and disagree (e.g. search.py palette vs tokens.json): `tokens.json` wins for
anything the audit checks (colour, radius, font size, spacing, shadow, duration); `MASTER.md` prose wins for
layout pattern, CTA placement, section order. `validate` emits `warning: MASTER.md colour <hex> not in tokens.json`
for each `#RRGGBB` in MASTER.md that is not a resolved token value — a nudge, not a failure, because the
search.py file is not tool-owned.

## 4. Pages — `pages/<page>.md` inheritance rules

Skeleton written by `vd.py page --dir … --name <page> [--reason "…"] [--force]` (an existing page is skipped with a message and exit 0 unless `--force`, CC-10 c):

```markdown
<!-- generated-by: visual-direction vd.py <version>; page: <page>; profile-hash: <hash> -->
# <Page Title> Page Overrides

> **PROJECT:** <name> · **Page type:** <free text> · **Created:** <ISO date>
> ⚠️ Rules in this file **override** `MASTER.md` for this page only. Document deviations only.
> Every override needs a `reason`. Restating Master values is flagged by `vd.py validate`.

## Overrides

| Token / rule | Master value | Page value | Reason |
|---|---|---|---|
<!-- example: | component.tile.radius | {primitive.radius.lg} | {primitive.radius.md} | 6x8 grid leaves 2px between tiles at xl | -->

## Component remaps
- (component id) → (catalog variant or another component), reason

## Intentional exceptions (page scope)
| Scope | Rule | Reason | Expires |
|---|---|---|---|

## Notes
```

Rules enforced by `validate`:

1. **Overrides only.** Each row in `## Overrides` must have a non-empty `Reason`; a row whose `Page value`
   equals the `Master value` is a *restatement*. `N_restated ≥ 3` → error `page.copies-master` listing the rows
   (CC-10 d). 1–2 → warning `page.restates-master`. Independently, a page that carries ≥ 3 of the Master-only
   `## ` headings, or whose non-blank lines are ≥ 80 % identical to `MASTER.md`, is also `page.copies-master`.
2. **Token paths only.** `Token / rule` must be a path that exists in `tokens.json` or a component id from the
   catalog; unknown paths → error.
3. **Page value must be a token or a declared exception.** A literal (`#FF00AA`, `13px`) in `Page value` is
   allowed only if the same row (or the page's exceptions table) gives a reason — then the audit treats
   occurrences of that literal in that page's source as `intentional-exception`.
4. Pages cannot change `semantic.color.*` meanings or `$extensions.vdp.platformUnit`; such rows → error.
5. The drift budget (§7) is evaluated per page: only rows whose `Page value` is a **literal** (hex, `px`/`dp`/`pt`/`ms`, bare number,
   `rgba(…)`) count against it. A remap to a different **existing** token path (`{primitive.radius.lg}` → `{primitive.radius.md}`) is a
   legitimate override, not drift. Over budget → error `drift budget exceeded (<group>: n/limit)`.
6. Page `## Intentional exceptions` rows need `Expires`: an ISO date `YYYY-MM-DD` or the word `never` (the skeleton carries the hint); expired rows → warning, any other format → warning.

Resolution order at build time: page override → MASTER.md (tool section) → `tokens.json` → component catalog defaults.

## 5. `CHANGELOG.md` entry format

Append-only; newest at the bottom (tool appends, never sorts). One entry:

```markdown
## 2026-10-15T10:42:11Z · vd.py init · [tool]
- profile: style-profile.json (sha256 3f9a1c2b7d4e) · style: japanese-cute-puzzle · derivation: token-derivation.md v1
- created: MASTER.md, tokens.json, component-catalog.md, asset-guidelines.md, interaction-guidelines.md, visual-qa-checklist.md
- skipped (exists): —
- tokens: 17 semantic colours, 13 primitive groups, 8 components · unit logical · touch min 48
```

Grammar (validate checks each `## ` line):

```
## <ISO-8601 UTC> · <actor> · [tool|manual]
```

- `actor` ∈ `vd.py init | vd.py page <page> | vd.py validate | reference_analysis.py merge | <free text for manual>`.
- Body = 1–8 bullets; the tool always writes `profile:` first and `created:`/`changed:`/`skipped` next.
- `[manual]` entries are written by humans or by the assistant after editing files by hand; bullets must name the
  file(s) touched and, when a token value changed, the `token path: old → new` and `reason:` bullets.
- A token-changing entry must reference a migration note when §6 applies: `- migration: migrations/0002-radius-xl-to-lg.md`.

## 6. Migration notes (`migrations/NNNN-<slug>.md`)

Required when a **breaking** token change happens: a semantic or component token is removed/renamed, its
resolved value changes by more than the thresholds (colour ΔE-like distance ≥ 10 in RGB euclidean/4.4, radius
step change, font size step change, duration class change), or `platformUnit` changes. Not required for
additions or for primitive-only changes that leave resolved semantic values unchanged.

```markdown
# 0002 · radius class xl → lg
Date: 2026-10-20 · Author: … · CHANGELOG: 2026-10-20T09:00:00Z
## Why
(one paragraph; links to the decision — reference analysis id, user request, audit finding id)
## Token diff
| Path | Old | New |
|---|---|---|
| semantic.radius.control | {primitive.radius.xl} (16) | {primitive.radius.lg} (12) |
## Code impact
- find: `BorderRadius.circular(16)` / `rounded-2xl` / `border-radius: 16px` → replace with the token reference
- files (from `audit.py scan --contract tokens.json`): lib/ui/buttons.dart:12, …
## Verification
- `audit.py scan` after change: 0 findings of `radius.off-scale` for 16
- screenshot diff: `visual_qa.py diff before/home.png after/home.png` expected FAIL (intended), reviewed by …
## Rollback
- restore tokens.json from CHANGELOG commit <sha> and re-run the find/replace in reverse
```

Numbering is sequential, zero-padded 4 digits, never reused.

## 7. Drift budget

The number of ad-hoc (non-token) values a single screen/page may contain before `validate`/`audit` fail.
Written into MASTER.md §5 with the resolved numbers and into `tokens.json` as
`$extensions.vdp.driftBudget` (optional; defaults below apply when absent).

| Group | Budget per screen | Reason-required | Audit rule it maps to |
|---|---|---|---|
| colour (`#hex`, `rgb()`, `Color(0x…)`) | **0** | — | `color.off-palette`, `color.near-duplicate` |
| font family | **0** | — | `font-family.unlisted` |
| radius | **≤ 1** | yes | `radius.off-scale` |
| spacing | ≤ 2 | yes | `spacing.off-scale` |
| font size | ≤ 2 | yes | `font-size.off-scale` |
| shadow variant | 0 new variants (reuse `primitive.shadow.*`) | — | `shadow.variant-explosion` |
| duration | ≤ 1 | yes | `duration.off-scale` |
| icon library | 0 extra libraries | — | `icon.mixed-libraries` |

Counting rules: distinct values, not occurrences (`13px` used 5 times = 1); values that appear in the page's
`## Overrides` or exceptions tables with a reason do not count; values that are an exact resolved token value
never count. A screen = one `pages/<page>.md` scope, or for the audit, one source file / one screen directory
as the scanner groups it. Exceeding the budget is severity `high` in `findings.json`; within budget but
without a reason is `medium`.

## 8. `vd.py validate` summary (what fails vs warns)

| Check | Result |
|---|---|
| required VDP keys / enums | error |
| tokens.json required groups, reference integrity, string `$value`, contrast, unit consistency, `generatedFrom` matches profile (token-derivation.md §6) | error |
| MASTER.md: missing mandatory H2 (tool-owned only), unresolved `{{…}}` | error |
| MASTER.md not tool-owned: colours not in tokens | warning |
| page: restated ≥ N, unknown path, literal without reason, semantic remap, over drift budget | error |
| page: 1–2 restated, expired exception | warning |
| CHANGELOG: malformed `## ` line, token change without migration ref when §6 applies | error |
| profile-hash mismatch on tool-owned files | warning (`run vd.py init --force to regenerate`) |

Exit codes follow contract §5: `0` ok (warnings allowed), `1` any error, `2` usage/IO.
