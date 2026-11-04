# Audit workflow

How a visual / UX audit runs end to end, where each tool sits, and what a finding must answer before it is reported. Script paths are relative to the skill directory (see "Script Paths" in SKILL.md); the working directory stays at the project root.

## Positions

```
DISCOVER ──► AUDIT ──► PLAN ──► FIX ──► VERIFY ──► REPORT
   │           │         │        │        │          │
 inventory   scan +    ordered  tokens → re-scan +  PASS / FAIL /
 + contract  checklist fix list  shared → diff vs   BLOCKED / NOT RUN
   load      + diff    by sev.   screens  baseline  per cell
```

| Phase | What happens | Tool | Output |
|---|---|---|---|
| DISCOVER | Enumerate screens and platforms; run the scanner **without** a contract to see what the code actually uses (distinct colours, radii, sizes, families, shadows, durations, icon libraries, component names). Load the design contract if one exists (`design-system/<slug>/tokens.json`, `style-profile.json`, `pages/*.md`). | `python3 scripts/audit.py scan <dir> --json` | inventory, platform, file counts, variant-explosion recommendations |
| AUDIT (static) | Compare literals against the contract; every off-contract value becomes a finding with file:line. | `python3 scripts/audit.py scan <dir> --contract design-system/<slug>/tokens.json --profile design-system/<slug>/style-profile.json --out qa-logs/findings.json --md qa-logs/findings.md` | `findings.json` (schema `visual-audit/1`) |
| AUDIT (UX) | Walk `references/ux-audit-checklist.md` sections A–G per screen on screenshots or the running app; produce findings in the same shape, ids continuing the `VA-` sequence. | `python3 scripts/visual_qa.py checklist --profile … --screen <s>` | checklist with evidence per item |
| AUDIT (visual regression) | If captures exist, diff against per-device baselines. If the app cannot be run here, every cell is **NOT RUN** and the manifest documents how to capture. | `python3 scripts/visual_qa.py diff a.png b.png --json`, `python3 scripts/visual_qa.py manifest --stack <stack> --screens …` | PASS / FAIL / BLOCKED / NOT RUN per screen × device |
| PLAN | Group findings by `files_to_change`; order by severity and by dependency: **tokens → shared components → screens**. A screen fix that bypasses a shared component is a new duplicate. | — | fix plan (table: id, file, change, verify) |
| FIX | Apply the plan. Never silence a finding by adding an exception the contract does not have; propose it in `fix` and leave the severity. | — | code changes |
| VERIFY | Re-scan; compare before/after; re-diff screenshots. | `python3 scripts/audit.py compare before.json after.json` | resolved / new / unchanged counts, exit 0 only when nothing new at/above threshold |
| REPORT | One report: header (platform, contract, scanned/skipped), summary table, findings by severity, inventory, screenshot matrix with a status per cell, limitations. | markdown from `scan` + `compare` + checklist | the audit report |

## Inventory first

Run `scan` **without** `--contract` before anything else. The inventory tells you whether the project has a scale at all (4 radii or 19?), which icon libraries are in play, how many shadows exist and which component names are duplicated. Decide from it whether the contract is trustworthy or whether `vd.py init` (owned by the `visual-direction` skill) must produce one first. A contract that does not reflect the dominant values in the inventory produces hundreds of "findings" that are really a contract problem — say so instead of reporting them.

## What is certain vs. subjective

| Certain (report as `kind: rule`, `confidence: exact`) | Heuristic (`kind: recommendation`, `confidence: heuristic`) | Subjective (`kind: aesthetic`, severity ≤ Low) |
|---|---|---|
| A literal is not in the token set (colour, radius, font size, spacing, duration, family, shadow signature) | Touch-target size from a `SizedBox`/CSS box (padding and hit-test slop are invisible statically) | "Feels cramped", "looks cheap", "too playful" |
| Two icon libraries imported in one platform group | Duplicate component by name family + body comparison | Palette harmony, character appeal |
| Count of distinct variants project-wide | Contrast from a literal fg/bg pair in one CSS rule (gradients, images, anti-aliasing not modelled) | Motion "feel" without a measured duration |

Rule findings count toward `--fail-on`; aesthetic ones never do. If you cannot name the token path, guideline id or WCAG criterion in `violates`, the finding is not a rule.

## The seven questions every finding answers

A finding is complete only when the reader can act on it without re-investigating. The finding fields (`references/finding-format.md`) map to seven questions:

| # | Question | Field(s) |
|---|---|---|
| 1 | **Where** is it? | `file`, `line`, `evidence` (the literal source text, whitespace-collapsed) |
| 2 | **What is the evidence?** | `evidence`, `nearest` (nearest allowed value and distance), `inventory` counts in `message` |
| 3 | **How bad** is it, and why? | `severity` (+ the ladder reason in `message`: count, primary screen), `impact` (what a user or the brand sees) |
| 4 | **Which rule** does it break? | `rule`, `violates` (token path / profile anti-pattern / guideline / WCAG criterion) |
| 5 | **What is the fix?** | `fix` (replacement token or structural change; "if intentional, add to `pages/<screen>.md` intentional_exceptions") |
| 6 | **Which files** change? | `files_to_change` (both files for a duplicate pair; all shadow files for a variant explosion) |
| 7 | **How do we verify** it is gone? | `verify` ("re-run `audit.py scan`; VA-xxxx must be absent; `compare` lists it under resolved") |

A finding missing an answer to 1, 2 or 4 is downgraded to `aesthetic`; missing 5–7 is incomplete and must not be reported as done.

## Fix plan order

1. **Tokens / contract** — if the inventory shows the contract is wrong (e.g. the whole app uses 12 px radius and the contract says 8), fix the contract first with the `visual-direction` skill, then re-scan; many findings disappear legitimately.
2. **Shared components** — duplicates (`component.duplicate-implementation`), icon library consolidation, shadow signatures: fixing the canonical component fixes every screen that uses it.
3. **Screens** — remaining per-screen literals, in severity order; primary screens (`screens/`, `pages/`, HUD, gameplay) first.
4. **Exceptions** — anything the team decides is intentional goes into `style-profile.json` or `pages/<screen>.md` `intentional_exceptions`; the next scan reports it as `info`, still visible, never counted.

## Status vocabulary for the report

| Status | Meaning |
|---|---|
| PASS | Compared or checked, within threshold / no finding |
| FAIL | Compared or checked, finding present |
| BLOCKED | Could not be checked here (Pillow missing, size mismatch, unreadable capture, tool unavailable) — the reason is mandatory |
| NOT RUN | Nobody attempted it (no runtime, no capture, matrix row not mandatory) — the reason is mandatory |

BLOCKED and NOT RUN are never folded into PASS. A report with any BLOCKED cell is headed INCOMPLETE.
