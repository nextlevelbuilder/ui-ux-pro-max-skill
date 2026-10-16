# Style Selection Workflow

How the `visual-direction` skill turns a request ("make it look like a cute Japanese puzzle game", "match these screenshots", "pick a style for our habit app") into a **Visual Direction Profile** (`style-profile.json`, schema `vdp/1`, documented in `visual-direction-profile.md`) and then into the project's design contract (`design-contract.md`). Every command below is run from the project root; `scripts/…` is relative to this skill's directory (see "Script Paths" in SKILL.md).

## 0. Decide the route first

| Signal in the request | Route | Entry command |
|---|---|---|
| Names a look, mood, art style, family or existing style id | **A — catalog** | `python3 scripts/vd.py styles "<query>"` |
| Names a game genre / app category but not a look | **B — genre** | `python3 scripts/vd.py genres "<query>"` |
| Supplies one screenshot/image/mockup to copy | **C — single reference** | `reference-analysis` skill → `python3 scripts/vd.py profile --reference …` |
| Supplies several images, possibly from different products | **D — multi-reference with roles** | `reference-analysis` skill (`merge`) → `python3 scripts/vd.py profile --reference …` |
| Names a game type **and** a look ("a match-3 in the Japanese cute puzzle style") | **A + B** | `--genre <id> --style <id>` |
| Mixes signals ("like these screenshots but as a match-3") | **D + B** or **C + A** | `--reference` combined with `--genre` and/or `--style` |

Ask the user **only for information no route can derive** (§5). Never ask for what the catalog or the references already answer.

## 1. Route A — catalog style

1. Search: `python3 scripts/vd.py styles "cute japanese puzzle pastel" -n 5` (add `--family cute-cartoon` to stay inside one family — CC-11; `--json` for machine output). Output lists id, name, family, radius class, shading, motion class and "best for".
2. Choose the top result unless `Avoid For` (visible in `--json`) names the product. If two results tie, prefer the one whose `Best For` names the product kind; show both to the user only when they differ in family (see `visual-families.md` — mixing families is the main drift risk).
3. Build: `python3 scripts/vd.py profile --style <id> --platform mobile-ios,mobile-android --stack flutter-flame --project "<Name>" --out style-profile.json`
   - `product.kind` is derived from the style row (genre `Kind` when route B, otherwise the style's keywords/family); `product.audience` defaults to the catalog `Audience` text.
   - Typography families are extracted from the row's `Typography Direction`; when no family can be read the classification string is written and `unknowns` says so (CC-4).
   - `palette.seeds` (CC-9) comes from the row's `Seed Colors`: `primary→brand`, `secondary→secondary`, `accent→accent`, neutral derived from the text colour.
4. Unknown id → exit 1 with the closest ids (difflib); the script never fabricates a style. Zero search results → exit 0, `count: 0`, suggestions (CC-10 a).

## 2. Route B — genre

1. `python3 scripts/vd.py genres "onet animal link puzzle"` → genre id, kind and its `Default Styles` (ordered by fit).
2. `python3 scripts/vd.py profile --genre onet-animal-puzzle --platform mobile-android --stack flutter-flame --out style-profile.json`
   - The **first** default style drives route A; the genre adds `product.genre`, `product.kind`, audience, its anti-patterns and a `genre_profile` block (core screens, HUD elements, interactions, reward loop, touch and performance rules) that `vd.py init` folds into `interaction-guidelines.md`.
   - To pick another style, pass `--genre <id> --style <id>` together: the style supplies every visual field, the genre supplies `product.kind`, `product.genre`, audience, anti-patterns and the `genre_profile` block, and both appear in `sources[]`. A genre whose default style is missing from the catalog is an error, never a guess.
3. Game genres map to the screen and HUD rules in `game-ui-patterns.md`; app genres to the app rows of `data/component-catalog.csv`.

## 3. Route C — single reference

1. Hand the image(s) to the `reference-analysis` skill. It produces `reference-analysis.json` (`vdp-reference-analysis/1`): references with **roles**, graded observations, rules with `derived_from`, `not_derivable`, `palette_observed`.
2. `python3 scripts/vd.py profile --reference reference-analysis.json --platform mobile-android --out style-profile.json`
   - Without `--style`, `style.id = reference-derived-custom` (CC-3). That catalog row is a template with enum-valid fallbacks (`flat-modern`, `md`, `soft`, `soft`) that the rules overwrite.
   - Only rules with confidence `observed` or `high` populate contract fields; `assumption` rules, open conflicts and `not_derivable[]` go to `unknowns`. `context:<screen>` rules become `intentional_exceptions`.
   - Rule target → field: `palette → palette_strategy`; `radius → shape.radius_class` from the **median px** found in the rule and its observations (≤2 none, ≤6 sm, ≤10 md, ≤16 lg, ≤32 xl, >32 pill); without px evidence the named class wins and `pill`/`fully rounded`/`circular` alone give `pill` (those words only set `shape.silhouette` when px evidence exists); `outline → shape.outline` (`light tint / lighter / tint of` → `lighter-tint-of-fill`, `darker shade` → `darker-shade-of-fill`, `black / dark / navy` → `contrast-dark`); `shading → rendering.*`; `typography → typography.*` (classification phrases built from the rule and observation text, never a placeholder — CC-4, same clause rule as the `reference-analysis` skill's `to-profile`: clauses mentioning body / caption / sub-label / subtitle / regular / humanist give `typography.body`, e.g. `humanist sans`, the rest give `typography.display`, e.g. `bold rounded geometric sans`; without body evidence body = display minus its weight word, e.g. `rounded sans`, plus an `unknowns` entry); `icon → iconography`; `character → illustration`; `motion → motion.class`; every other target (`button.primary`, `hud`, `popup`, `card`, `chip`, …) → `components[target]`.
   - `palette_observed` seeds `palette.seeds` (`primary→brand`, `secondary`, `accent|cta→accent`, `text|neutral→neutral`, highest share wins) and fills `palette.surfaces {background, surface, text, outline}` so the semantic background/surface/text/border tokens use the observed colours instead of grey defaults; the whole list is kept in `palette.observed`. When no accent is observed the accent seed is derived from the brand ramp (`brand.700`) and recorded in `unknowns` — never invented.
   - `anti_patterns` from references are negations of `no / never / not` clauses in observed/high rules (`Do not use …`), never the rule text itself; a negation needs ≥ 4 words after "Do not" and no `except`/`unless` qualifier, otherwise it is dropped; without a negation the catalog defaults stay.
   - `product.kind` is inferred from the references (`gameplay`/`shop` screens or `hud`/`characters` roles → game); override with `--genre`.
   - A `_partial` vdp/1 fragment from `reference_analysis.py to-profile` is accepted in place of the analysis; `vd.py profile` completes and strips it (CC-3). The fragment's fields are **honoured, not recomputed** (shape, rendering, typography, components, exceptions, principles, unknowns, `sources[0].roles`, and `product.kind` unless `--genre` supplies it); its `palette.observed` goes through the same derivation as the raw route, so both routes give the same `palette.seeds` and `palette.surfaces`. Explicit fragment `seeds`/`surfaces` fill only the slots the observations do not cover. Result: `--reference frag.json` and `--reference analysis.json` agree except for `sources` and tool-written `unknowns` wording (regression-tested).
3. `style.confidence` is `high` when ≥ 5 global rules are observed/high and no conflict is open, otherwise `assumption`.

## 4. Route D — multi-reference with roles

1. Each reference owns roles (`color, shapes, characters, buttons, hud, popup, icons, typography, layout, motion`); exactly one owner per role. The `reference-analysis` skill assigns them from the user's wording ("colours from the first, buttons from the second"), resolves conflicts and `merge`s the files (disjoint ids required — CC-10 e).
2. Run the same `profile --reference merged.json` command. The `sources[0].roles` list is the union of owned roles.
3. **With `--style <id>` or `--genre <id>`** the catalog profile is built first and the reference rules override **only the roles the references own** (CC-3). Rules outside owned roles are reported in `unknowns` ("rule not applied") so nothing is silently dropped.
4. Combine with `--seed-design-system ds.json` (output of the `ui-ux-pro-max` skill's `search.py "<query>" --design-system --json`) to fill the gaps a reference cannot give: missing seed slots (`destructive→danger`, `success`) and font families when the reference only yields a classification. The seed never overrides an explicit catalog or reference value; it is recorded as a `design-system-seed` source.

## 5. Ask only for what is missing

| Field | Derivable from | Ask when |
|---|---|---|
| `product.platforms` | nothing — always a flag | always required (`--platform`) |
| `product.stack` | nothing | optional; defaults to `other` (unit then follows the platforms) |
| `product.kind` | genre `Kind`; style keywords; reference screen types | the inference is wrong — rerun with `--genre` |
| `project.name` | `--project`; else genre or style name | the folder slug matters to the user |
| font families | catalog row; reference (classification only) ; seed | `unknowns` contains "family not identified" |
| motion class | catalog; reference *sequences* only | only static references were given |
| reward colour | never from the catalog | the product has a reward loop and the brand owns a reward colour → add `palette.seeds.reward` |

Record every answer in the profile (`unknowns` shrinks, `sources` grows); do not keep answers only in chat.

## 6. Decision rules

- **One family per product.** If the chosen style, the references and the seed point at different families (`visual-families.md`), stop and ask which one wins; write the loser's traits as `intentional_exceptions` only when the user insists.
- **Catalog is canonical for structure, style row for visuals** (CC-11): `component-catalog.csv` decides variants/states; the style row and `components` notes decide how they look. `vd.py init` renders both ("Style modifier").
- **References beat catalog for owned roles; catalog beats references elsewhere; seed fills gaps only.**
- **Never invent a value.** Not derivable → `unknowns`, and the token derivation uses its documented default (`token-derivation.md` §0.2 constants).
- **Confidence is written, not implied.** `style.confidence` and every reference rule carry one of `observed, high, assumption, not-derivable`.

## 7. Produce and persist

1. Review the printed profile (`vd.py profile` without `--out` prints JSON to stdout) and fix obvious misreads by hand — the JSON is the contract, not the catalog text.
2. `python3 scripts/vd.py init --profile style-profile.json --output-dir .` → `design-system/<slug>/` with `MASTER.md` (or `MASTER.visual-direction.md` plus a paste block when a `MASTER.md` from `search.py --persist` already exists), `style-profile.json`, `tokens.json`, `component-catalog.md`, `asset-guidelines.md`, `interaction-guidelines.md`, `visual-qa-checklist.md`, `CHANGELOG.md`, `pages/README.md`. Existing files are skipped and listed; `--force` rewrites tool-owned files only.
3. `python3 scripts/vd.py validate --dir design-system/<slug>` — exit 0 before any implementation starts.
4. Web stacks: `node ../design-system/scripts/generate-tokens.cjs --config design-system/<slug>/tokens.json -o src/styles/tokens.css`. Other stacks: `references/platforms/*.md`.
5. Per-screen deviations: `python3 scripts/vd.py page --dir design-system/<slug> --name shop --reason "promo layout"` and fill the Overrides table; `validate` rejects pages that copy the master.
6. After implementation: `visual-audit` skill (`audit.py scan --contract design-system/<slug>/tokens.json`) closes the loop; findings that are intentional go back into `pages/<page>.md` or `intentional_exceptions`.

## 8. Worked examples

```bash
# A: catalog
python3 scripts/vd.py styles "kawaii sticker merge" -n 3
python3 scripts/vd.py profile --style kawaii-sticker --platform mobile-ios,mobile-android --stack flutter --project "Sticker Merge" --out style-profile.json

# B: genre
python3 scripts/vd.py profile --genre productivity-app --platform web,desktop --stack nextjs --project "Ledger Lite" --out style-profile.json

# C: single reference, kind inferred, seed fills the font gap
python3 scripts/vd.py profile --reference reference-analysis.json --seed-design-system ds.json --platform mobile-android --stack flutter-flame --out style-profile.json

# A + B: a game type in a chosen look
python3 scripts/vd.py profile --genre match-3 --style japanese-cute-puzzle --platform mobile-ios,mobile-android --stack flutter-flame --project "Candy Garden" --out style-profile.json

# D: references own colour + buttons, catalog owns the rest (works with --genre, --style or both)
python3 scripts/vd.py profile --reference merged.json --style japanese-cute-puzzle --platform mobile-ios,mobile-android --stack flutter-flame --out style-profile.json

# persist + check
python3 scripts/vd.py init --profile style-profile.json --output-dir . --json
python3 scripts/vd.py validate --dir design-system/sticker-merge --json
```
