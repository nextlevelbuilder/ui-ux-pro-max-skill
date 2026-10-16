# Dependency Map

```
                 ┌──────────────── src/ui-ux-pro-max (frozen) ────────────────┐
                 │ search.py --design-system --json  (optional seed)          │
                 └──────────────┬─────────────────────────────────────────────┘
                                │ JSON only (no python import across skills)
reference-analysis ──json──► visual-direction ──design-system/<slug>/── ► visual-audit
   (B)                          (A,C,F,G,I,J)        tokens.json,            (D,E,H)
                                                      style-profile.json
                                       │
                                       └── tokens.json ──► design-system/scripts/generate-tokens.cjs (web CSS/Tailwind)
```

## Build/ship dependencies
| Artifact | Depends on | Mechanism |
|---|---|---|
| `cli/assets/skills/<new>` | `.claude/skills/<new>` + `subSkills` list | `npm --prefix cli run sync:assets` |
| CLI install of new skills | `cli/assets/skills/*` | `listBundledSubSkills()` (dynamic, no code change) |
| Plugin install | `.claude/skills/*` | `.claude-plugin/plugin.json` `"skills"` (no change) |
| CI tests | `scripts/tests/test_*.py` | `python3 -m pytest .claude/skills` |
| Path contract | every `*.md` under both skill trees | `check-asset-sync.yml` + `test_skill_script_paths.py` |

## Runtime dependencies
| Component | Required | Optional | Degradation |
|---|---|---|---|
| vd.py, vd_core.py | Python 3.8+ stdlib | — | — |
| reference_analysis.py | stdlib | Pillow (extract-colors) | prints `BLOCKED: Pillow not installed`, exit 3 |
| audit.py | stdlib | — | unknown platform → scans generic patterns, warns |
| visual_qa.py diff | stdlib | Pillow | BLOCKED, exit 3 |
| Screenshot capture | runtime of the target app (Flutter/Unity/browser) | Playwright | manifest only; status NOT RUN |

## Execution order (Wave 2)
1. W2-A (visual-direction core) ‖ W2-B (reference-analysis) ‖ W2-C (visual-audit) ‖ W2-D (platform adapters) — independent file sets.
2. W2-E examples (needs A, B, C CLIs) → W2-F independent QA (needs everything) → W2-G docs/integration (needs real features).
3. Principal: sync assets, full gate, final audit, journal.
