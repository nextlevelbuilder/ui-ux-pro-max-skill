# Severity

One ladder for scanner findings, checklist findings and screenshot findings, so a report can be sorted and gated with a single `--fail-on` threshold.

## Ladder

| Severity | Meaning | Examples |
|---|---|---|
| **Critical** | Blocks usability or accessibility with no heuristic doubt (human-measured; the scanner never emits it) | measured tappable control < 24 px; no way back from a screen; body text < 12 px; flashing > 3 Hz; focus trap |
| **High** | Visible brand/style break on a primary screen, or the same drift ≥ 3 times project-wide (systemic) | off-palette CTA colour on the shop screen; `15` px text in four files; HUD anchors moving between gameplay screens; measured contrast < 3:1 |
| **Medium** | Secondary screen or 1–2 occurrences; every heuristic finding (touch target, contrast, duplicate component) | off-scale radius in one component; duplicate button implementation; two icon libraries; `SizedBox` 32 px around an `IconButton`; `#FFD43B` on `#FFF8F0` in one CSS rule |
| **Low** | Cosmetic, no user impact | near-duplicate colour (Δ ≤ 12); one off-grid padding; a shadow signature not in the contract |
| **Info** | Inventory only / intentional exception | finding matched by `intentional_exceptions`; kept in JSON for auditability, never gates |

## Scanner algorithm

```
primary(file)  = a path segment in {screens, pages, app, views, routes}
                 OR "hud" / "gameplay" anywhere in the path (case-insensitive)
                 OR the file matches a --primary glob
count(rule, v) = occurrences of the same normalised value for the same rule, project-wide
ladder         = HIGH if count >= 3 or primary(file) else MEDIUM
```

Per-rule final severity:

| Rule | Severity |
|---|---|
| `color.off-palette`, `radius.off-scale`, `font-size.off-scale`, `font-family.unlisted` | ladder |
| `color.near-duplicate` | low, always |
| `spacing.off-scale` | low; medium when count ≥ 3; never high (cosmetic noise) |
| `duration.off-scale` | medium; high when count ≥ 3; `primary` ignored (timing is not a visible brand break) |
| `shadow.variant-explosion` | medium, one per project |
| `shadow.unlisted` | low per occurrence |
| `icon.mixed-libraries` | medium; high when ≥ 3 libraries in one platform group |
| `component.duplicate-implementation` | medium |
| `touch.target-too-small` | medium, always (heuristic cap, CC-10h); a smallest dimension < 24 is flagged in the message for the human to confirm on device |
| `text.contrast-risk` | medium, always (heuristic cap); the ratio is in the message, the rendered contrast must be measured by hand |
| `*.variant-explosion` (inventory mode) | medium |
| any rule matched by `intentional_exceptions` | info |

Heuristic rules (touch, contrast, duplicate component) never exceed **Medium**: their evidence is a static guess at a rendered property. The scanner therefore never emits Critical or heuristic Highs; Critical and High on those topics come from human-written findings whose evidence is a measurement (hit rect in the inspector, sampled contrast on the rendered background).

## Why counts and primary screens

- **Count ≥ 3** means the value is systemic: three files share the same wrong number, so a shared constant or component is missing, and the fix belongs at the token level. It is also what a user sees across screens.
- **Primary screen** means visibility: a single off-palette CTA on the shop or home screen is seen by every player; the same literal in a debug panel is not.
- `--primary <glob>` lets a project name its own primary paths (`"src/game/**"`), and `app/` can be removed from the default set by scanning with `--exclude` if a Flutter `lib/app/` bootstrap folder inflates severities.

## Gating

| Command | Exit 0 | Exit 1 | Exit 2 | Exit 3 |
|---|---|---|---|---|
| `audit.py scan` | nothing at/above `--fail-on` (default `high`); `--fail-on none` always | findings at/above threshold; malformed contract/profile JSON | dir missing, contract/profile file missing, unknown `--platform`, bad flags | — |
| `audit.py compare` | no `new` finding at/above `--fail-on` | new findings at/above threshold | file missing / unparsable / wrong schema | — |
| `visual_qa.py diff` | PASS | FAIL | usage (negative threshold, bad rectangle) | BLOCKED (Pillow missing, unreadable, size mismatch) |
| `visual_qa.py checklist` | ok | invalid profile (no `qa_criteria`, bad JSON) | profile missing | — |
| `visual_qa.py manifest` | ok | — | unsupported stack / device, profile missing | — |

`info` findings and `kind: intentional-exception` never trip a threshold. Recommended CI gate: `--fail-on high` on pull requests, `--fail-on medium` on release branches after the first clean-up, `compare` with `--fail-on medium` to stop new drift while a backlog is being paid down.

## Downgrades and upgrades by hand

- A scanner finding whose fix is confirmed impossible on the platform (e.g. Unity uGUI text contrast on a sprite) becomes `aesthetic` with the reason in `message`; it stays in the report.
- A checklist finding without a measurement is `aesthetic` and ≤ low until evidence is attached.
- Do not downgrade by adding an exception the contract does not carry; propose the exception in `fix`, keep the severity, let the contract owner decide.
