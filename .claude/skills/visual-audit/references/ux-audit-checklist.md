# UI/UX audit checklist (procedure, not drift scanning)

Scope: the human/model-driven audit that runs **alongside** `scripts/audit.py`. The scanner finds
contract drift in code; this checklist finds usability and structure problems that no regex can see. It
produces findings in the same `references/finding-format.md` shape (so one report can hold both), with `kind` set per "Tagging guidance" below.

Inputs: the running app or screenshots (device matrix from `references/screenshot-qa.md`), `style-profile.json`
(`qa_criteria`, `anti_patterns`, `intentional_exceptions`), `tokens.json`, `design-system/<slug>/pages/*.md`,
and the UX guideline rows from `../ui-ux-pro-max/data/ux-guidelines.csv` (the `ui-ux-pro-max` skill's data) (cited by their `id`/title).
Evidence is mandatory: a finding without a screenshot path, file:line, or measurement is downgraded to
`kind: aesthetic`.

## Procedure

1. Enumerate screens (`python3 scripts/visual_qa.py manifest --stack <stack> --screens …`) and generate the per-screen item list (`python3 scripts/visual_qa.py checklist --profile … --screen <s>`). For each screen capture at least one device from each
   width class (phone / tablet / desktop as applicable) in default state.
2. Walk sections A–G below per screen; fill the evidence column before deciding severity.
3. Tag every item (Tagging guidance below). Merge with scanner findings; ids continue the `VA-` sequence.
4. Produce the fix plan: group by `files_to_change`, order by severity, state `verify` for each.

Severity reminder (`references/severity.md`): **Critical** blocks usability/accessibility (cannot complete the core
task, content unreadable, no way back); **High** visible brand/style break on a primary screen or ≥ 3
occurrences; **Medium** secondary screen / 1–2 occurrences; **Low** cosmetic; **Info** inventory only.

## A. Information architecture

| # | Check | Evidence to capture | Severity guidance | Maps to |
|---|---|---|---|---|
| A1 | One primary action per screen, visually dominant (size, colour = `semantic.color.primary`/`accent`) | screenshot with the candidate CTAs circled; count of equally weighted CTAs | ≥ 3 competing CTAs on a primary screen → High; 2 → Medium | ux-guidelines "visual hierarchy", `component-catalog` button.primary rule |
| A2 | Content grouped by task; related controls adjacent; spacing uses `primitive.spacing` steps between groups vs within groups (outer > inner) | annotated screenshot; measured gaps | inner ≥ outer gap → Medium | tokens.spacing, Gestalt proximity |
| A3 | Screen title / context visible without scrolling | top-of-viewport capture per device | missing on primary screen → High | ux-guidelines "orientation" |
| A4 | Game HUD: score / lives / timer / currency in consistent corners across gameplay screens | side-by-side captures of 2+ gameplay screens | position changes between screens → High (brand/style break) | game UI patterns (HUD anchors) in the `visual-direction` skill |
| A5 | Nothing essential hidden behind hover-only or long-press-only affordances on touch platforms | list of hover-only controls | any on mobile → High | ux-guidelines "touch affordance" |

## B. Navigation

| # | Check | Evidence | Severity | Maps to |
|---|---|---|---|---|
| B1 | Every non-root screen has a visible back/close within the top 15 % of the viewport (or system back works) | capture + hit-test note | missing → Critical (user trapped); below top band → Medium | platform guidelines (iOS/Android back), `component-catalog` popup.close |
| B2 | Popups/dialogs: dismiss via close button **and** scrim tap/back; destructive confirms require explicit action | interaction log | no dismiss path → Critical; scrim-only → Medium | component popup rules |
| B3 | Bottom nav / tab bar ≤ 5 items, labels present, active state uses `semantic.state.focus`/selected colour | capture of nav in two states | > 5 or no active state → Medium | ux-guidelines "navigation" |
| B4 | Deep links / web routes keep the same chrome (header, nav) as in-app navigation | two captures of the same screen reached both ways | differs → Medium | web adapter notes |
| B5 | Game flow: home → play → result → home loop reachable in ≤ 2 taps per hop; shop/reward screens always return to origin | flow diagram with tap counts | dead end → Critical; > 2 taps → Medium | game UI patterns flow loop (`visual-direction` skill) |

## C. Readability and typography

| # | Check | Evidence | Severity | Maps to |
|---|---|---|---|---|
| C1 | Body text ≥ 14 px/sp (web 16 px), captions ≥ 12; all sizes from `primitive.fontSize` | measured size (DOM / inspector / px count on capture) | body < 12 → Critical; < scale min → High | tokens.fontSize, `font-size.off-scale` |
| C2 | Contrast ≥ 4.5:1 body, ≥ 3:1 large text/icons, measured on the **rendered** background (gradients, images: sample the worst region) | hex pair + ratio + sampling location | < 3:1 body → Critical; 3–4.5 → High | WCAG 1.4.3, `text.contrast-risk` |
| C3 | Line length 45–80 chars (web), 30–40 on phone; line height from `primitive.lineHeight` | char count of a representative paragraph | > 100 chars → Medium | ux-guidelines typography |
| C4 | Only the contract families (`semantic.typography.display/body`); display family not used for body copy | font inspector / capture zoom | extra family → High (`font-family.unlisted`); role swap → Medium | tokens.typography |
| C5 | Text over imagery/characters has a scrim, outline (`primitive.outline`) or plate | capture of the worst overlap | unreadable → Critical; marginal → Medium | game UI patterns text-on-art rule (`visual-direction` skill) |
| C6 | Numbers in HUD/score use tabular figures or fixed width (no jitter) | two captures with different digit counts | layout shift → Medium | motion direction "no jitter" rule (`visual-direction` skill) |

## D. Touch and input UX

| # | Check | Evidence | Severity | Maps to |
|---|---|---|---|---|
| D1 | Every tappable target ≥ `minTouchTarget` (44 pt iOS / 48 dp Android / 44 px web) incl. padding; spacing between targets ≥ 8 | measured hit rect (inspector / overlay) | < 24 → Critical; < min → High on primary, Medium elsewhere | tokens.touchTarget, `touch.target-too-small` |
| D2 | Primary CTA within the bottom thumb zone on phones (lower 60 % of viewport) for gameplay/shop | capture with thumb-zone overlay | primary CTA in top 25 % on phone → Medium | game UI patterns thumb zone (`visual-direction` skill) |
| D3 | No accidental-tap risk: destructive/purchase buttons not adjacent to frequent actions; purchase has confirm | capture + spacing measure | adjacent purchase/claim without confirm → High | monetisation UX rows |
| D4 | Gestures have a visible alternative (swipe → also buttons) | list | gesture-only core action → High | accessibility: pointer alternatives |
| D5 | Keyboard/web: focus visible (`semantic.state.focus`), tab order follows reading order, Esc closes dialogs | tab-walk log | no visible focus → High; trap → Critical | WCAG 2.4.7, 2.1.2 |

## E. State coverage

| # | Check | Evidence | Severity | Maps to |
|---|---|---|---|---|
| E1 | Each interactive component shows default / hover (web) / pressed / focus / disabled per `semantic.state` | capture of each state (or storybook/preview) | missing pressed or disabled → Medium; disabled indistinguishable → High | tokens.semantic.state |
| E2 | Loading, empty, error, offline states exist for every data-driven screen | capture or code path reference | missing error state → High; missing empty → Medium | ux-guidelines "states" |
| E3 | Game: paused, game-over, level-complete, out-of-lives, reward-claimed states styled consistently with popup rules | captures | inconsistent popup chrome → High | component popup/reward |
| E4 | Long content / i18n expansion (+30 % text) does not clip or overflow | capture with pseudo-locale or long strings | clipped label on CTA → High | ux-guidelines i18n |
| E5 | Dark mode / reduced-motion honoured if the profile declares them (`motion.reduced_motion: respect`) | OS-setting toggle + capture | declared but ignored → Medium | style-profile motion |

## F. Feedback and motion

| # | Check | Evidence | Severity | Maps to |
|---|---|---|---|---|
| F1 | Every tap gives feedback within 100 ms (visual state change, haptic, or sound) | screen recording / frame count | none on primary CTA → High | motion direction response budget (`visual-direction` skill) |
| F2 | Durations from `primitive.duration`; no animation > `slow` on the critical path; skippable reward sequences | measured ms (recording) | > 1 s unskippable before gameplay → High | `duration.off-scale`, game UI reward rules (`visual-direction` skill) |
| F3 | Success/failure feedback uses `semantic.color.success/danger` plus a non-colour cue (icon, text, motion) | capture | colour-only feedback → High (colour-blind users) | WCAG 1.4.1 |
| F4 | Toasts/snackbars do not cover the primary CTA or HUD; auto-dismiss ≥ 4 s | capture during toast | covers CTA → Medium | component toast rule |
| F5 | Motion class matches profile (`snappy/soft/bouncy`): overshoot only if class is bouncy | recording vs profile | class mismatch on primary screens → Medium | style-profile motion.class |

## G. Accessibility (beyond C2/D1/D5)

| # | Check | Evidence | Severity | Maps to |
|---|---|---|---|---|
| G1 | Icon-only buttons have accessible names (`Semantics`, `tooltip`, `aria-label`, Unity `UQueryBuilder` name) | code grep + screen-reader pass | missing on primary actions → High | WCAG 4.1.2 |
| G2 | Text scales with OS font size (Flutter `textScaleFactor`, web rem, Compose sp) without clipping | capture at 130 % | clipping on primary screen → High | platform adapters |
| G3 | No information conveyed by colour alone (status, selected tile, rarity) | capture converted to greyscale | indistinguishable → High | WCAG 1.4.1 |
| G4 | Flashing content ≤ 3 flashes/s; large particle bursts have a reduced-motion variant | recording | > 3 Hz → Critical | WCAG 2.3.1 |
| G5 | Screen-reader order = visual order; decorative art marked as such | reader log | reads art labels / wrong order → Medium | WCAG 1.3.2 |

## Tagging guidance (`kind` field)

Full field semantics: `references/finding-format.md`; the ladder: `references/severity.md`.

| kind | Use when | Severity allowed | Counts toward `--fail-on`? |
|---|---|---|---|
| `rule` | The item maps to a contract value (tokens.json, profile enum, component-catalog rule) or a WCAG success criterion, **and** you captured measurable evidence | any | yes |
| `recommendation` | Best-practice guideline (ux-guidelines.csv row, platform HIG) not encoded in the contract, or a rule-level item whose evidence is heuristic (estimated size, sampled contrast) | ≤ High | yes |
| `aesthetic` | Taste/judgement ("feels cramped", "colour looks cheap") with no contract rule and no measurement; always include what measurement would make it a rule | ≤ Low | no |
| `intentional-exception` | Matches a `style-profile.json` / `pages/<page>.md` `intentional_exceptions` entry (scope + rule). Record the exception id in `violates` | info | no |

Rules of thumb: if you cannot name the contract path, guideline id or WCAG criterion in `violates`, it is
not a `rule`. If you cannot attach evidence, it is `aesthetic`. An exception must pre-exist in the
contract; the auditor never creates exceptions — they propose one in `fix` ("add to pages/shop.md
intentional_exceptions: …") and leave the finding at its real severity until the contract changes.

## Output

Same JSON as the scanner (`references/finding-format.md`) with `file` = screenshot path or source file, `line` = 0 when the
evidence is an image, `evidence` = measurement text ("CTA hit rect 36×36 pt, measured in Flutter
inspector"). Markdown: one section per screen, items ordered by severity, the tag in brackets after the id.
Completed checklist rows with no issue are listed once as `checked: A1 A2 … (no finding)` so coverage is auditable.
