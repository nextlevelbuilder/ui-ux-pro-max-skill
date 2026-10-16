---
date: 2026-10-15
session: visual-design-pro-max
severity: high
component: skills-visual-direction-reference-analysis-visual-audit
status: complete-uncommitted
---

# Visual Design Pro Max: three new skills, one design contract, verified against real code

## Context

Mission: extend UI UX Pro Max with art-direction, reference-image analysis, game UI, design-consistency and visual-QA capability as reusable skills, using real multi-agent execution where available. Work happened on branch `feat/visual-design-pro-max` from `main` @ 56ea9cf (clean tree). Baseline before any change: 300 pytest (`.claude/skills`) + 164 unittest (core) passing.

## What was built (real files, all under the repo)

- `.claude/skills/visual-direction/` — style/genre/component catalog (20 styles × 29 columns, 18 genres, 55 components), `vd.py` (styles/genres/components/profile/init/page/validate), `vd_tokens.py` (deterministic VDP → three-layer tokens.json compatible with the existing `generate-tokens.cjs`), 9 references incl. 4 platform adapters (Flutter/Flame, Unity uGUI + UI Toolkit, web, SwiftUI/Compose), master template.
- `.claude/skills/reference-analysis/` — evidence-graded image analysis workflow (observed / high / assumption / not-derivable), `reference_analysis.py` (validate/merge/extract-colors/to-profile/summary/template), human-description template for runtimes without image viewing.
- `.claude/skills/visual-audit/` — `audit.py` (static drift scanner for Dart, C#/USS/UXML, CSS/TSX/Vue/Svelte/Tailwind, Swift/Kotlin experimental; 12+ rule ids; contract and inventory modes; before/after compare), `visual_qa.py` (pixel diff, per-screen checklist, capture manifests), 7 references, a 20-file static drift fixture with a 40-finding oracle.
- Integration: `cli/scripts/sync-assets.mjs` bundles the three skills; orchestrator `SKILL.md` routing section; `README.md` section; `docs/VISUAL_DESIGN_PRO_MAX.md`; plugin manifests' descriptions; `CONTRIBUTING.md` note.
- Architecture: `docs/architecture/{REPOSITORY_MAP,ARCHITECTURE,INTEGRATION_CONTRACT,AGENT_WORK_PLAN,DEPENDENCY_MAP,ACCEPTANCE_CRITERIA}.md` (12 recorded contract changes).
- Examples: `docs/examples/visual-design-pro-max/example-{a,b,c}` (see verification levels in each README).

## Multi-agent execution (what actually ran)

Claude Desktop exposed a real `Agent` tool. Wave 1: eight discovery agents in parallel (style taxonomy, image intelligence, game UX, tokens/components, research & provenance, audit/lint, platform adapters, test plan) wrote proposals to the session scratchpad; the Principal merged them into the locked contract. Wave 2: four implementers in parallel on disjoint directories (W2-A visual-direction, W2-B reference-analysis, W2-C visual-audit, W2-D platform adapters), then W2-E examples ‖ W2-G docs, then W2-F independent QA. Three Wave 2 agents were killed mid-write by a usage-limit error and were resumed by message after re-verifying disk state; no rework was lost.

## Defects found by verification that the authors' tests missed

| Found by | Defect | Fix |
|---|---|---|
| Principal, real `flutter create` app | Dart named-colour regex ignored camelCase (`Colors.deepPurple`) | `[a-z][A-Za-z]*` + test |
| Principal, smoke | `vd.py profile --out` did not create parent dirs | mkdir parents |
| W2-E, Example B | reference route wrote the literal "display" as font family | classification string per CC-4 |
| W2-E, Example C | `box-shadow: var(--x)` counted as a literal shadow (false `shadow.unlisted` + variant explosion) | non-literal guard across extractors |
| W2-E | `--style` + `--genre` were mutually exclusive (mission requires combining) | combinable; genre supplies kind/screens/HUD |
| W2-E | reference→profile: px radius ladder → `pill`; "light tint" outline → `contrast-dark`; observed surfaces dropped; invented accent | px ladder, tint rule, `palette.surfaces`, accent from brand ramp |
| Principal, all 20 styles | catalog route ignored seed background/surface/text (dark-fantasy got a white background) | surfaces authoritative; test over all 20 rows |
| Principal, all 20 styles | on-colour rule darkened fills for white text (`#FF6B6B` → `#EE0000`) | pick best passing candidate, keep fill; walk only if none passes |
| QA pass 1 | `--out qa-logs/...` crashed on a missing directory (all writers) | parent dirs created; one-line errors, no tracebacks |
| QA pass 1 | stock Flutter app detected as `mixed`; scaffold Kotlin/Swift scanned | `pubspec.yaml` ⇒ flutter, scaffold folders skipped |
| QA pass 2 | fonts in Tailwind config / Google Fonts links never read | extractors added; 6 off-contract fonts found on repo pages |
| QA pass 2 / examples | one outline colour per panel type missing; pressed = outline; overshooting progress easing; neon dark steps on pastel seeds | one decorative + one interactive border, pressed ≠ outline, non-overshooting easing, chroma-preserving ramps |
| Example regeneration | pressed label 2.85:1, secondary label 2.15:1, tile outline 1.30:1 | per-state labels, `borderInteractive` ≥ 3:1, component-state contrast check in `vd.py validate` |
| QA pass 3 | focus ring < 3:1 in 14/20 styles; dark-theme button edge 2.16:1 | focus ring ≥ 3:1 vs background and surface, validated; dark-page edges step lighter |
| QA pass 3 | audit rejected values the contract itself defines (component durations, tinted shadows) | every layer of tokens.json joins the allowed sets |

## Test results (final)

All commands run on 2026-10-16 from the repo root on the final tree, after `node cli/scripts/sync-assets.mjs`.

| Gate | Command | Result |
|---|---|---|
| All bundled skills | `python3 -m pytest .claude/skills -q` | PASS: 796 passed, 1 skipped (baseline 300) |
| visual-direction | `python3 -m pytest .claude/skills/visual-direction -q` | PASS: 204 passed |
| reference-analysis | `python3 -m pytest .claude/skills/reference-analysis -q` | PASS: 104 passed |
| visual-audit | `python3 -m pytest .claude/skills/visual-audit -q` | PASS: 188 passed, 1 skipped (opt-in real-Flutter probe, set `VISUAL_AUDIT_FLUTTER_PROBE`) |
| Core search engine | `python3 -m unittest discover -s src/ui-ux-pro-max/scripts/tests -p 'test_*.py'` | PASS: 164 OK (unchanged) |
| Repo data gate | `npm --prefix cli run verify:data` | PASS: rc 0 (CSV, semantic, agent guide, catalog summary, relevance, 12/12 domains, 22/22 stacks, assets in sync) |
| Asset mirrors | `node cli/scripts/sync-assets.mjs --check` | PASS |
| CLI type check / build | `npx tsc --noEmit`, `npm run build` in `cli/` | PASS / PASS |
| CLI e2e | `npx playwright test` in `cli/` | 40 PASS, 1 BLOCKED: `preview.spec.ts` needs a Playwright browser binary not installed here (`npx playwright install chromium`); `preview/` untouched |
| CI path + bundled-skill contracts | Python replica of the two greps in `check-asset-sync.yml` | PASS: 0 violations |
| Python 3.8 syntax | `ast.parse(..., feature_version=(3, 8))` on 16 new files | PASS |
| Example contracts | `vd.py validate` on examples A and B | PASS: 0 errors, 0 warnings |
| Independent QA | `docs/architecture/QA_REPORT.md` passes 1–3 | No open High/Critical; examples rebuild byte-identical modulo timestamps |

Five CLI e2e tests failed on the first run because they hard-coded "6 sub-skills". They now derive the count from `listBundledSubSkills()`, and a new test asserts the three new skills are bundled.

## Acceptance criteria

| # | Criterion | Status |
|---|---|---|
| 1 | Architecture docs from real code | PASS |
| 2 | Skills integrated into the repo mechanism | PASS |
| 3 | Style selection by catalog / genre / reference | PASS |
| 4 | Visual Direction Profile schema + docs | PASS |
| 5 | Design contract with master + overrides | PASS |
| 6 | UI/UX + drift audit | PASS |
| 7 | Research and provenance rules | PASS |
| 8 | Implementation guidance per stack | PASS (documentation; Flutter/Unity guidance not exercised in a running app) |
| 9 | Automated tests for new modules | PASS |
| 10 | Three end-to-end examples with verification level | PASS |
| 11 | Tests run, nothing hidden | PASS (1 e2e BLOCKED, stated) |
| 12 | No serious regression | PASS |
| 13 | Usage and integration docs | PASS |
| 14 | Final report | PASS (this file) |

Evidence per row: `docs/architecture/ACCEPTANCE_CRITERIA.md`.

## Limitations and BLOCKED / NOT RUN items

- Screenshot capture of a running Flutter/Unity app: NOT RUN in this session (no app runtime exercised; `visual_qa.py manifest` emits instructions only). Pixel diff was tested on synthetic PNGs only.
- Unity: scanner covers USS/UXML/C# colour and timing literals on the static fixture only; no Unity project was opened. Swift/Kotlin extractors are experimental (no fixture).
- Web research: no network calls were made by any script; the provenance reference governs model/browser research. No external asset was downloaded.
- Image generation: not available; not claimed.
- Example B's reference is a repository-owned screenshot rendered with Playwright, not a user-provided game reference.
- 8 of 20 catalog styles keep a black default primary label because their seeded brand colour passes 4.5:1 only with black (CC-15). Each case is listed in that project's `MASTER.md` Unknowns for the art director to re-seed.
- Known Low leftovers (QA_REPORT.md): reward, warning and accent are close golds in Example A (non-colour cues used); `style.confidence` counts rules instead of weighing them; no automatic cross-check between an eye-estimated palette and `extract-colors`; catalog prose and tokens can disagree (the catalog states that tokens win); audit severity is count-based, so a partial fix can downgrade untouched findings (labelled in `compare`); web icon-library tie-break is alphabetical; SVG `font-family` attributes, `next/font` and `@font-face` URLs are not scanned.
- The session scratchpad was wiped by a usage-limit reset on 2026-10-16. Wave 1 proposal files and the pass-1 QA report were lost; their content survives in the shipped references, AGENT_WORK_PLAN.md and the contract changes. QA passes 2–3 are in the repo.
- Sub-agents ran without the user's global 8-item confirmation gate per step, under the mission's explicit authorisation to execute autonomously; nothing was committed, pushed, installed globally or downloaded beyond `npm ci` of the CLI's own locked dev dependencies into `cli/node_modules` (git-ignored).
- Nothing was committed or pushed; the branch holds uncommitted changes for review.

## Decisions

- Extend the existing `design-system/<slug>/` folder rather than a parallel structure; never overwrite a `MASTER.md` produced by `search.py --persist` (`MASTER.visual-direction.md` + paste block instead).
- Three skills instead of ten: capability boundaries follow inputs (images), outputs (contract) and verification (audit), not the brief's list.
- Sub-skills keep their own compact BM25 core and never import the orchestrator's `core.py` (matches repo convention; CI path contract).
- Independent real-code smoke is a mandatory gate (observation #24 in the task-observer log).
