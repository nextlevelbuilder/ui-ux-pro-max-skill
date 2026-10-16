# Acceptance Criteria (Definition of Done, measurable)

Status vocabulary: **PASS / FAIL / BLOCKED / NOT RUN**. Final report must fill every row.

| # | Criterion | Evidence required | Status |
|---|---|---|---|
| 1 | Architecture docs based on real code | `docs/architecture/{REPOSITORY_MAP,ARCHITECTURE,INTEGRATION_CONTRACT,AGENT_WORK_PLAN,DEPENDENCY_MAP,ACCEPTANCE_CRITERIA}.md` exist, cite real paths | PASS — 7 files in docs/architecture/ incl. QA_REPORT.md |
| 2 | New skills integrated into the repo skill mechanism | 3 dirs under `.claude/skills/`, mirrored in `cli/assets/skills/`, `npm --prefix cli run check:assets` exits 0 | PASS — 3 skills under .claude/skills/ and cli/assets/skills/; `check:assets` rc 0 |
| 3 | Style selection by catalog / genre / reference | `vd.py styles`, `vd.py genres`, `vd.py profile --reference` each produce a VDP; tests cover all three routes | PASS — catalog, genre, genre+style and reference routes tested (vd.py tests) and used in examples A/B |
| 4 | VDP schema + docs | `references/visual-direction-profile.md` matches `vd.py validate` behaviour; invalid profile rejected with exit 1 | PASS — `visual-direction-profile.md`; invalid profiles rejected with exit 1 (QA pass 1: 0 mismatches) |
| 5 | Design contract with master + overrides | `vd.py init` creates the folder; existing MASTER.md untouched without `--force`; `vd.py page` + `validate` flag override files that copy master | PASS — init/page/validate tested; foreign MASTER.md never overwritten; hand-edited MASTER.md backed up on --force |
| 6 | UI/UX + drift audit | `audit.py scan` on fixture reports ≥6 rule ids with file:line evidence; `compare` shows delta | PASS — fixture oracle 40 findings / 13 rule ids; compare delta in examples A and C; real Flutter app + repo HTML spot-checked |
| 7 | Research & provenance rules | `references/research-and-provenance.md` includes source ranking, license classes, attribution record format; examples cite sources with class | PASS — `research-and-provenance.md` (tiers, licence classes, attribution record) |
| 8 | Implementation guidance per stack | `references/platforms/{flutter-flame,unity,web,mobile-native}.md` map every token group to code | PASS — 4 platform adapters; every token path verified to exist in generated tokens |
| 9 | Automated tests for new modules | pytest files for vd, reference_analysis, audit, visual_qa; all pass locally | PASS — 496 new pytest tests (visual-direction 204, reference-analysis 104, visual-audit 188 incl. 1 opt-in skip) |
| 10 | Three end-to-end examples with verification level | `docs/examples/visual-design-pro-max/example-{a,b,c}/README.md` each state what was executed vs. hand-written | PASS — 3 examples; READMEs state EXECUTED / HAND-WRITTEN / NOT RUN; QA rebuilt A/B/C byte-identical modulo timestamps |
| 11 | Tests executed, nothing hidden | Output of `pytest .claude/skills`, `npm --prefix cli run verify:data` (or its parts) pasted in the final report with counts | PASS — results in the journal; 1 e2e test BLOCKED (missing Playwright browser), stated |
| 12 | No regression | Baseline 300 pytest + 164 unittest still pass; `check:assets` passes; `validate-agent-guide.py` passes | PASS — baseline 300 pytest + 164 unittest still pass; verify:data rc 0; 5 CLI e2e tests updated for 9 bundled skills |
| 13 | Usage + integration docs | `docs/VISUAL_DESIGN_PRO_MAX.md` covers prerequisites, Claude Code vs Desktop vs other assistants, limitations | PASS — docs/VISUAL_DESIGN_PRO_MAX.md, README section, CONTRIBUTING note, orchestrator routing |
| 14 | Final report | `docs/journals/<date>-visual-design-pro-max.md`: changes, test results, limitations, BLOCKED items | PASS — docs/journals/261015-1300-visual-design-pro-max.md |

Known-in-advance limitation rows (must appear in the report): real Flutter/Unity app screenshot QA = NOT RUN unless executed; Unity scanner = fixture-tested only; web research = model activity, scripts never fetch.
