# Multi-Reference Reconciliation

How to combine 2..N reference images into one `reference-analysis.json` without silently averaging them. Three mechanisms: **roles** (who owns a topic), **conflicts** (same topic, different values), and **context differences** (intentional per-screen variation). This document is written for `scripts/reference_analysis.py merge` and for the agent filling the JSON by hand.

## 1. Roles

### 1.1 The ten roles

`color, shapes, characters, buttons, hud, popup, icons, typography, layout, motion`. A role is a **topic lease**: the owning reference is the source of truth for every rule on that topic. Exactly one reference may own a role; a role may be unowned.

### 1.2 Topic → role map

Used by validation (R-RULE-2, R-CONF-2) and by conflict detection. A rule's `target` or a conflict's `topic` maps to a role as follows (first match wins, match on substring, lower-case):

| Topic / target contains | Role |
|---|---|
| `character`, `mascot`, `illustration`, `avatar` | `characters` |
| `button`, `cta`, `chip` | `buttons` |
| `hud`, `counter`, `progress`, `timer`, `lives`, `score`, `top bar` | `hud` |
| `popup`, `dialog`, `modal`, `sheet`, `toast`, `overlay` | `popup` |
| `icon`, `glyph` | `icons` |
| `palette`, `color`, `colour`, `hue`, `saturation`, `contrast` | `color` |
| `radius`, `outline`, `silhouette`, `corner`, `shape`, `shading`, `shadow`, `highlight`, `elevation` | `shapes` |
| `typography`, `font`, `label case`, `weight`, `text style` | `typography` |
| `layout`, `grid`, `spacing`, `density`, `hierarchy`, `safe area`, `tab-bar`, `navigation` | `layout` |
| `motion`, `animation`, `easing`, `transition`, `timing` | `motion` |
| anything else | `null` (unowned topic; handled like an unowned role) |

Precedence note: a topic like "button corner radius" contains both `button` and `radius`. The table is ordered by **component first**: if the topic names a component (`button`, `hud`, `popup`, `icon`, `character`), that component's role wins; `shapes` and `color` apply to generic/global geometry and palette. The script checks the rows in exactly the order printed above.

### 1.3 Assigning roles from the user's words

| User says | Assignment |
|---|---|
| "image 1 is the colour reference, image 2 is the button reference" | ref-1: `["color"]`; ref-2: `["buttons"]`; all other roles unowned. |
| "copy this look" (single image) | that reference owns **all ten roles** except `motion` (owned only if the input is a sequence). |
| "image 1 is the main one, image 2 just for the popup" | ref-1: every role except `popup` and `buttons`; ref-2: `["popup", "buttons"]` (a popup reference carries its buttons unless the user says otherwise; record this inference as an `assumption` observation). |
| "use both" / no roles given | apply §3 default precedence after asking once. |
| "image 2 overrides image 1 for X" | move role(s) for X from ref-1 to ref-2 (`merge --roles ref-2:<x>` does this: a role named in `--roles` is removed from every other reference). |

Record the assignment basis in `references[].provenance.note` (`"roles assigned by user"` / `"roles assigned by default precedence, user accepted"`; `merge --roles` appends `"roles assigned at merge"`).

### 1.4 Hand-assignment rules

- A role cannot be split between references ("ref-1 for primary button colour, ref-2 for secondary button colour" is not expressible). Resolve by giving `buttons` to one reference and recording the other reference's detail as a `context:` rule or an `unknowns` note.
- A `viewed_by: "none"` reference should own nothing (R-VIEW-1). If the user insists, keep the role but produce no rules from it; the role is "reserved".
- `merge` MUST exit 1 with `role 'buttons' owned by ref-1 and ref-2` when two inputs claim the same role. It never picks silently.
- After roles are settled, a rule on an owned topic that derives only from a non-owner reference is dropped by `merge` with a warning naming the rule id (R-RULE-2 applied at merge time).

## 2. Conflict detection

Run after all observations are collected. Compare observations pairwise across references.

### 2.1 Definition

Two observations `a`, `b` are a **candidate conflict** when all hold:

1. `a.refs` and `b.refs` are disjoint (they describe different images).
2. Same `category`.
3. Same **topic key**: a normalised short phrase the agent writes into the statement's leading noun phrase (e.g. "panel corner radius", "label case", "outline colour", "button silhouette"). The agent SHOULD begin each statement with its topic key followed by a colon to make this mechanical; `merge` compares the text before an early colon (otherwise the first 4 words), lower-cased, stripped of articles.
4. The observed values differ in class, not in degree. Differences are material when they cross a class boundary: radius class (`none/sm/md/lg/xl/pill`), shading enum, label case (`title/upper/lower/sentence`), outline present/absent, outline colour rule (`black/darker-shade/none`), icon style (`filled/outline/two-tone`), font classification (`rounded-sans/geometric-sans/humanist/serif/display/pixel`), layout pattern. A 20% vs 25% radius is the same class (`xl`) and is **not** a conflict. `merge` cannot judge classes; it treats any two statements with the same topic key and different text as a candidate, so write one class per statement and keep same-class observations textually identical or under different topic keys.

Observations graded `not-derivable` never take part in conflict detection.

### 2.2 Decision

```
topic_role = map(topic)                      # §1.2
owner      = reference owning topic_role     # or null

if owner is null:
    conflicts += {topic, between: refs(a) ∪ refs(b), status: "open",
                  resolution: "No reference owns role <topic_role>. <value a> (<ref-a>) vs
                               <value b> (<ref-b>); user must assign the role or declare
                               the difference intentional."}
    rules derived from a or b are dropped (warning names them); no rule is written for the topic.
else:
    winning value = the observation whose refs include owner
    conflicts += {topic, between: ..., status: "resolved",
                  resolution: "<owner> wins (role <topic_role>): <winning value> globally.
                               <loser value> from <loser ref> recorded; ask user whether
                               <loser screen_type> should intentionally differ."}
    rules += rule with the winning value, target = topic key, scope "global", derived_from = [winning obs]
    a cross-ref observation (refs = both) records the difference, confidence = min of both.
```

If the owner is `viewed_by: none`, treat as `owner is null` (nothing can win from an unviewed image). A conflict whose topic already exists in `conflicts` (authored by hand) is not detected again.

### 2.3 Same reference, different values

Two values inside **one** image (home-screen buttons are pills, the home-screen tab bar is `xl`) are never a conflict; they are a component-level distinction. Write separate rules with different `target` values (`button.primary` vs `tab-bar`) and let the shape rule enumerate the classes ("two radius classes: pill for buttons, xl for containers").

### 2.4 Conflict record hygiene

- One conflict per topic. If three references disagree, `between` lists all three.
- A conflict is never deleted when resolved; `status` changes to `resolved` and `resolution` says why.
- When the user later assigns a role or confirms intent, update the conflict in place and add an observation with `evidence: "user confirmation <date>"`.

## 3. Precedence when the user gives no roles

Ask **once**, in one message, offering the default so the user can accept with "ok":

> "I have N images. Unless you tell me otherwise I will treat `<label of candidate A>` as the main screen (owns colour, shapes, HUD, layout, characters, icons, typography) and `<label of candidate B>` as the popup/button reference (owns buttons, popup). Reply `ok` or give your own assignment."

Candidate selection, in order:

1. **Main-screen candidate**: the reference whose `screen_type` is `home`, else `gameplay`, else the one the user listed first. It owns `shapes, hud, layout, color, characters, icons, typography`.
2. **Popup/button candidate**: the reference with `screen_type: popup` that shows the most distinct button states/variants (count visible buttons; ties → the one with a visible primary + secondary pair). It owns `buttons, popup`. If no popup reference exists, `buttons` and `popup` go to the main-screen candidate.
3. **Motion**: owned only by a sequence input (gif/video/frames); otherwise unowned and listed under `not_derivable`.
4. Remaining references own nothing and contribute observations only (they can still create context rules and conflicts).

If the user does not answer before analysis must proceed (non-interactive run), apply the default and set `provenance.note: "roles assigned by default precedence; not confirmed by user"` on every reference; `to-profile` then adds the `unknowns` line `"role assignment was defaulted; confirm before promoting rules to MASTER"`. In that case **no rule from the default assignment may exceed confidence `high`**, and conflicts resolved by default ownership keep `status: "resolved"` but the resolution text MUST contain the phrase `"by default precedence"`.

## 4. Intentional context differences vs conflicts

A difference between two references is a **context difference**, not a conflict, when **either**:

- the user stated it ("the popup buttons are deliberately uppercase"), or
- the two references have different `screen_type` **and** the differing topic is in the context-sensitive list: `density/spacing`, `hud visibility`, `button size`, `overlay/dim`, `tile radius inside grids`, `label case on CTA buttons`, `icon size`, and the user, when asked once, confirmed it is intentional.

Record a context difference as:

- one cross-ref observation stating both values with refs to both references;
- a rule with `scope: "context:<screen_type>"` of the differing reference, `target` the component, `derived_from` the observation(s) from that reference;
- **no** entry in `conflicts`.

`to-profile` maps `context:` rules to `intentional_exceptions[]` in the Visual Direction Profile (`{"scope": "popup", "rule": "<statement>", "reason": "observed in ref-2 (rule-4)"}`).

If the user has not confirmed, it stays a conflict: resolved when a role owner exists (§2.2), open otherwise. The resolution text already asks the question; the agent repeats it in its summary to the user. Never convert a conflict into a context rule on the agent's own judgement.

## 5. `merge` behaviour summary

```bash
python3 scripts/reference_analysis.py merge ref-1.json ref-2.json --out reference-analysis.json [--roles ref-1:color,shapes ref-2:buttons,popup] [--json]
```

Input: 2..N `reference-analysis.json` files (one per image is the usual case, produced by separate analysis passes). Each input must validate on its own.

1. Concatenate `references`, `observations`, `rules`; ids are authored and **must be disjoint across inputs** (`ref-1` in two files is a collision → exit 1, nothing written). Number the second image's observations from where the first stopped (`obs-10`, …) or use any disjoint scheme.
2. Apply `--roles` (if given): each named reference gets exactly the listed roles; a role named anywhere in `--roles` is removed from every other reference. Then enforce role uniqueness (exit 1 on duplicate owner, message `role 'x' owned by ref-a and ref-b (file-a, file-b)`).
3. Drop rules on owned topics that derive only from a non-owner reference (warning).
4. Concatenate `conflicts` (same topic in two inputs: keep the first, merge `between`, warn), `not_derivable` (dedupe case-insensitively), `palette_observed`.
5. Run conflict detection (§2) over the merged observations; append conflicts, cross-ref observations and winning rules; drop rules caught in an open conflict (warning naming the rule id).
6. Re-derive rule confidence from observations (R-RULE-1) and downgrade silently if the authored value is too high, printing a warning; drop rules whose observations are all `not-derivable`.
7. Validate the result (`references/extraction-schema.md` §8); write only when valid, otherwise print errors and exit 1 without writing.
8. Print a short report: references, roles table, conflicts (open/resolved), rules count by confidence, observation and not-derivable counts. `--json` prints the same as an object.

The command is pure with respect to its inputs: input files are never modified.
