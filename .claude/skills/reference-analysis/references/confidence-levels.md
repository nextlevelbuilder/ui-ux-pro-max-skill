# Confidence Levels

Every observation, rule and palette entry in `reference-analysis.json` carries one of four confidence values. The value is not a feeling; it is the outcome of the decision tests below. Apply the tests in order and stop at the first that passes.

## The four levels

| Level | Meaning | Who could disagree? |
|---|---|---|
| `observed` | A fact a second viewer of the same image would restate in the same words without interpretation. Counting, locating, naming a visible colour family, naming a visible shape. | Nobody looking at the same pixels. |
| `high` | An interpretation that follows from observed facts by a single, conventional inference step; the alternative explanations are implausible. | A specialist, rarely. |
| `assumption` | A plausible guess that fills a gap: the image is consistent with it, but also with at least one other reasonable reading, or it depends on information outside the image (device scale, rendering pipeline, intent). | Any careful reviewer. |
| `not-derivable` | The information does not exist in the input (static image, written description) and no amount of looking will produce it. Record it so nobody fabricates it later. | Everyone: there is nothing to see. |

Ordering for comparison: `observed` > `high` > `assumption` > `not-derivable`.

## Decision tests (apply in order)

```
T0  Did anyone actually view the image (viewed_by = model-vision) or read a
    description of it (viewed_by = human-description)?
      NO  → not-derivable (and the reference may own no rules)
T1  Is the information absent from a static frame by nature?
    (timing, easing, hover/pressed states, sound, haptics, pixel values at
    device scale, font family NAME, behaviour of screens not shown)
      YES → not-derivable
T2  Can the statement be verified by pointing at a region and re-reading it,
    with no "because" or "probably" needed?
      YES → observed
T3  Does the statement follow from observed facts by ONE conventional step,
    and would you be surprised to be wrong?
      YES → high
T4  Otherwise → assumption
```

Additional constraints:

- A statement reached only through a `human-description` input is capped at `high`, never `observed`, because the agent is relaying someone else's reading. The `evidence` field must cite the description ("user description, paragraph 2"). `validate` enforces this (R-VIEW-3).
- A statement that mixes a fact and a guess ("the button is a pill, probably 48px tall") must be split into two observations with their own confidence. Never average.
- Numbers are `observed` only when expressed relative to something visible in the frame (percent of element height, ratio of width). Absolute units (px, dp, pt) are `assumption` unless the user supplied the device and scale.
- A rule's confidence is the minimum confidence of the observations it is `derived_from` (R-RULE-1). A rule may never be `not-derivable`; if the only supporting observation is not-derivable, the rule does not exist and the topic goes to `not_derivable`.
- `palette_observed[].role_guess` is always `assumption` (see `references/extraction-schema.md`, extract-colors); the `hex` and `share` values from the script are `observed`.

## Twelve classified example statements

| # | Statement | Level | Why (test that fired) |
|---|---|---|---|
| 1 | "The frame contains four icons in a bottom bar." | `observed` | T2: count and location, re-checkable. |
| 2 | "The primary button corners are a full semicircle (radius = half height)." | `observed` | T2: geometric relation visible in the frame. |
| 3 | "The dominant background colour is a light pastel pink." | `observed` | T2: colour family + area, no interpretation. |
| 4 | "Outlines are a darker shade of each element's fill, not black." | `high` | T3: one inference step from sampled colours on 3+ elements; alternative (black at low opacity) is visibly ruled out by hue retention. |
| 5 | "The display font is a heavy rounded geometric sans." | `high` | T3: classification from letterforms; ruling out humanist/serif is conventional. |
| 6 | "The display font is Fredoka." | `not-derivable` | T1: family NAME cannot be proven from a raster; the user or the asset must confirm. Record classification separately as `high`. |
| 7 | "The popup panel is 80% of the screen width." | `observed` | T2: ratio relative to the frame; measurement by eye is acceptable at ±5%. |
| 8 | "The primary button is 56 dp tall." | `assumption` | T4: absolute unit requires device scale that the image does not carry. |
| 9 | "Buttons bounce on press." | `not-derivable` | T1: motion is absent from a static frame. |
| 10 | "White label on the orange fill is roughly 3:1 contrast." | `assumption` | T4: sampled colours are approximate and anti-aliasing/outline affect the real ratio; useful as a risk flag only. |
| 11 | "The mascot uses the same outline colour as the UI panels." | `high` | T3: comparable dark brown on both, same apparent width class; a slightly different hex would not change the rule. |
| 12 | "The shop screen probably uses the same card style as the home screen." | `not-derivable` | T1: the shop screen was not provided; a screen that was not shown has no observations. (Do not downgrade to assumption: there is no image.) |

## Promotion rule to MASTER

Only rules with confidence `observed` or `high` may be written into the project's global contract (`MASTER.md`, `style-profile.json` top-level fields, `tokens.json`). Concretely, `scripts/reference_analysis.py to-profile` and `../visual-direction/scripts/vd.py profile --reference` apply:

| Rule confidence | Where it goes in the Visual Direction Profile |
|---|---|
| `observed`, `high`, scope `global` | the matching top-level field (`shape`, `rendering`, `typography`, `components`, `palette_strategy`, `iconography`, `illustration`) plus one `qa_criteria` line |
| `observed`, `high`, scope `context:<screen>` | `intentional_exceptions[]` with `scope: "<screen>"` and `reason: "observed in <obs-ids> (<rule-id>)"` |
| `assumption`, any scope | `unknowns[]` as `"assumption (<rule-id>, assumption): <statement>"` — never a top-level field, never a token value |
| open conflict | `unknowns[]` as `"open conflict on <topic> between <ref-a>, <ref-b>"` |
| `not_derivable[]` entries | `unknowns[]` verbatim, prefixed `"not derivable from references: "` |

An `assumption` is promoted only when the user confirms it in writing; the confirming message is then recorded as a new observation with `evidence: "user confirmation <date>"` and `confidence: "high"`, and the rule is re-derived from it.

The profile's `style.confidence` is `high` when at least five global rules are `observed`/`high` and no conflict is open; otherwise `assumption`.
