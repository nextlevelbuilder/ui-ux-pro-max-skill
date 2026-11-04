---
name: visual-audit
description: UI/UX and visual-consistency audit of an existing app or game. Use when asked to "audit UI", when screens look "inconsistent", for "style drift", "which screens are off-style", "screenshot compare" / visual regression, or a UI/UX review of an app or game across gameplay, menu, shop, settings and reward screens. Scans Flutter, Unity (USS/UXML/C#), web (CSS/TSX/Vue/Svelte/Tailwind) and native code against a design contract (tokens.json, style-profile.json), grades findings by severity with file:line evidence, diffs screenshots, and produces a fix plan.
argument-hint: "[project dir or screens to audit]"
license: MIT
metadata:
  author: ui-ux-pro-max
  version: "1.0.0"
---

# Visual Audit

Static drift scanner + UX checklist + screenshot regression QA for existing apps and games. Output: findings with evidence, severity, the violated rule, a fix, the files to change and a verification step; a fix plan ordered tokens → shared components → screens; a PASS / FAIL / BLOCKED / NOT RUN report.

## When to Use

- "Audit the UI", "review UX", "why does the shop look different from the home screen", "which screens are off-style"
- Visual consistency across gameplay / menu / shop / settings / reward screens (Flutter, Flame, Unity uGUI or UI Toolkit, React/Next/Vue/Svelte/Tailwind, SwiftUI/Compose)
- Style drift after a design contract exists (`design-system/<slug>/tokens.json`, `style-profile.json`) — hard-coded colours, radii, font sizes, spacing, durations, families, shadows, mixed icon libraries, duplicate components, small touch targets, low contrast
- Screenshot compare / visual regression against per-device baselines
- Not for: defining the style or the contract (that is the `visual-direction` skill), copying a look from reference images (`reference-analysis` skill), generating tokens or CSS (`design-system` skill)

## Script Paths

Script paths in this skill and its `references/` are relative to the directory that contains this SKILL.md, not to the project: `scripts/<file>` is this skill's own `scripts/` folder, and `../<skill>/scripts/<file>` is a sibling sub-skill installed alongside it. Build the full path from that directory (Claude Code reports it as the skill's base directory when the skill loads) and keep the working directory at the project root — the scripts read and write project files such as `docs/brand-guidelines.md`, `assets/design-tokens.json` or `src/` relative to it.

## Workflow

Full procedure: `references/audit-workflow.md`.

1. **Inventory first** — `python3 scripts/audit.py scan <dir> --json` without a contract. Read the inventory (distinct colours, radii, sizes, families, shadows, durations, icon libraries, component names, platform). Decide whether the contract is trustworthy; if there is none, hand off to the `visual-direction` skill (`vd.py init`) before auditing against one.
2. **Load the contract** — `design-system/<slug>/tokens.json` (+ `style-profile.json` for `intentional_exceptions`, `anti_patterns`, duration/family fallbacks, preferred icon library; `pages/<screen>.md` for overrides).
3. **Scan** — `python3 scripts/audit.py scan <dir> --contract design-system/<slug>/tokens.json --profile design-system/<slug>/style-profile.json --out qa-logs/findings.json --md qa-logs/findings.md`. Exit 1 means findings at/above `--fail-on` (default `high`). Rules: `references/drift-rules.md`; ladder: `references/severity.md`.
4. **UX checklist** — `python3 scripts/visual_qa.py checklist --profile design-system/<slug>/style-profile.json --screen <screen>` per screen (ids: `home gameplay level-select pause win lose settings shop rewards profile tutorial`, or any `pages/<name>.md` next to the profile; anything else exits 2), then walk `references/ux-audit-checklist.md` A–G on screenshots or the running app. Hand-written findings use the same shape (`references/finding-format.md`) and continue the `VA-` ids.
5. **Screenshot QA** — if the app can be run and captured: `python3 scripts/visual_qa.py manifest --stack <stack> --screens home,gameplay,shop` for capture instructions (never executed by the script), capture with the project's own tooling, then `python3 scripts/visual_qa.py diff baseline.png current.png --threshold 0.5 --json` per screen × device. If it cannot be run here, every cell is **NOT RUN** with the reason, and the static procedure in `references/visual-qa-without-runtime.md` applies. Method and device matrix: `references/screenshot-qa.md`.
6. **Fix plan** — group by `files_to_change`, order by severity, then by dependency: **tokens → shared components → screens**. Propose exceptions in `fix`; never add them yourself.
7. **Re-scan and compare** — `python3 scripts/audit.py scan … --out qa-logs/after.json` then `python3 scripts/audit.py compare qa-logs/findings.json qa-logs/after.json` (resolved / new / unchanged; exit 1 only on new findings at/above threshold).
8. **Report** — header (platform, contract, scanned/skipped), summary table, findings by severity, inventory, screenshot matrix with PASS / FAIL / BLOCKED / NOT RUN per cell, limitations. BLOCKED and NOT RUN are never folded into PASS; any BLOCKED cell makes the report INCOMPLETE.

Every finding answers seven questions: where (file:line, evidence), evidence, severity and impact, which token / rule / guideline is violated, the fix, the files to change, how to verify.

## Commands

| Command | Purpose | Exit |
|---|---|---|
| `python3 scripts/audit.py scan <dir> [--contract tokens.json] [--profile style-profile.json] [--platform auto\|flutter\|unity\|web\|native\|mixed] [--format json\|md] [--out file] [--md report.md] [--fail-on critical\|high\|medium\|low\|none] [--tolerance N] [--near-threshold D] [--exclude GLOB] [--primary GLOB] [--json]` | Drift scan; inventory mode without `--contract`; markdown to stdout, JSON with `--json`; with `--out`/`--md` only a one-line summary goes to stdout | 0 clean · 1 findings at/above `--fail-on` or malformed contract · 2 usage/IO |
| `python3 scripts/audit.py compare before.json after.json [--fail-on …] [--out result.json] [--json]` | resolved / new / unchanged / changed_severity on `(rule, file, evidence)`; lines ignored | 0 · 1 new at/above threshold · 2 bad input |
| `python3 scripts/audit.py rules [--json]` | Rule table (id, category, kind, severity, confidence) | 0 |
| `python3 scripts/visual_qa.py diff a.png b.png [--threshold 0.5] [--tolerance 16] [--ignore x0,y0,x1,y1]… [--out diff.png] [--json]` | Pixel diff; threshold is **percent**; bbox exclusive; clusters; ignore regions | 0 PASS · 1 FAIL · 3 BLOCKED (Pillow missing, unreadable, size mismatch) · 2 usage |
| `python3 scripts/visual_qa.py checklist --profile style-profile.json [--screen gameplay] [--format md\|json] [--out file]` | `qa_criteria` + generic per-screen items, all NOT RUN; `--screen` must be a known id or a `pages/<name>.md` next to the profile | 0 · 1 invalid profile · 2 missing profile / unknown screen |
| `python3 scripts/visual_qa.py manifest --stack <stack> --screens a,b [--devices …] [--profile …] [--out screens.json] [--json]` | Capture instructions per screen × device (`<screen>_<device>.png`), marked not executed; stacks `flutter flutter-flame unity-ugui unity-ui-toolkit web swiftui jetpack-compose` | 0 · 2 unsupported stack |
| `python3 scripts/visual_qa.py devices [--json]` | Device matrix (phone-s/m/l, tablet, desktop) | 0 |

Empty directory → exit 0, `scanned_files: 0`, warning. Unknown platform → generic patterns on every supported extension plus a warning. `--platform <x>` forces the label and restricts scanning to that platform's files. A stock Flutter app is `flutter`: its `android/ ios/ macos/ linux/ windows/` glue (and the Flutter `web/` shell) is skipped unless `--platform native`. `--out`/`--md` paths such as `qa-logs/findings.json` create their parent folders; any unexpected error prints one `error:` line and exits 2.

## Finding shape (schema `visual-audit/1`)

`id, rule, severity, category, file, line, evidence, message, violates, nearest, impact, fix, files_to_change, verify, kind` (+ `confidence: exact|heuristic`). `kind` ∈ `rule | recommendation | aesthetic | intentional-exception`; only `rule` and `recommendation` count toward `--fail-on`. Minimum rule ids: `color.off-palette color.near-duplicate radius.off-scale font-size.off-scale font-family.unlisted spacing.off-scale shadow.variant-explosion duration.off-scale icon.mixed-libraries component.duplicate-implementation touch.target-too-small text.contrast-risk` (+ `shadow.unlisted`, `<category>.variant-explosion` in inventory mode). Details: `references/finding-format.md`.

## Hand-offs

| Need | Route |
|---|---|
| No contract, or the inventory shows the contract is wrong | `visual-direction` skill owns `design-system/<slug>/` (`vd.py profile / init / validate / page`); audit again afterwards |
| The user supplies screenshots or reference images to define the look | `reference-analysis` skill → `visual-direction` skill |
| Extra web-only hard-code check | `design-system` skill: `node ../design-system/scripts/validate-tokens.cjs --dir src/`, a web-only complement, not a replacement: it scans `.css .scss .ts .tsx .js .jsx .vue .svelte` only (not `.html`, and it skips `globals.css`), flags every hex/px literal regardless of the contract, and does not read Dart, USS or C#. This skill's scanner compares against the contract and covers all stacks |
| Token CSS / Tailwind config from `tokens.json` | `design-system` skill: `node ../design-system/scripts/generate-tokens.cjs --config tokens.json -o tokens.css` |
| Product/style/palette search while writing the report | `ui-ux-pro-max` skill (`search.py`) |

## References

| Topic | File |
|---|---|
| End-to-end procedure, positions, the seven questions, fix-plan order | `references/audit-workflow.md` |
| Finding JSON / markdown, `kind` tagging, compare output | `references/finding-format.md` |
| Every rule id: detection, severity, false positives; contract loading; file routing | `references/drift-rules.md` |
| Severity ladder, algorithm, exit-code gating | `references/severity.md` |
| UX audit checklist A–G with evidence and severity guidance | `references/ux-audit-checklist.md` |
| Pixel-diff method, device matrix, capture guidance, status rules | `references/screenshot-qa.md` |
| Static verification when the app cannot run (labels, Tailwind/Flutter/Unity procedures) | `references/visual-qa-without-runtime.md` |

## Limitations

- Static heuristics, not a parser: computed values (`radius * 2`), theme extensions, CSS-in-JS template literals with interpolation, multi-line `BoxShadow(` beyond one nesting level, Unity `.asset`/prefab YAML colours and sprite/texture UI are not inspected.
- Swift and Kotlin patterns are experimental and untested against a fixture; Unity coverage is USS/UXML + C# literals only and fixture-tested only.
- Touch-target, duplicate-component and contrast rules are heuristics (`confidence: heuristic`, `[heuristic]` in the message) and are capped at Medium: padding, hit-test slop, gradients and anti-aliasing are invisible statically — confirm on device and raise the severity by hand with a measurement.
- The pixel diff is a regression gate, not an art-director judgement: a wrong baseline passes forever; it says where pixels changed, not whether the screen is on-brand or usable.
- `visual_qa.py` never captures screenshots; the manifest is instructions for the project's own tooling. Real Flutter/Unity captures are NOT RUN unless someone runs them. Pillow is optional; without it `diff` reports BLOCKED (exit 3) instead of crashing.
- Tests: `python3 -m pytest` on this skill's `scripts/tests/` (static fixture `scripts/tests/fixtures/drift-project/`, not a runnable app).
