# Token derivation rules — `style-profile.json` (vdp/1) → `tokens.json`

Version: `token-derivation.md v1` (the value written to `$extensions.vdp.derivation`).
Implementation: `scripts/vd_tokens.py` (stdlib only; every number below is reproduced there; `vd.py init` calls it).
Standalone: `python3 scripts/vd_tokens.py --profile style-profile.json [--seeds seeds.json] --out tokens.json`.
Where this document and the script disagree, this document wins.

Scope: deterministic. Same profile + same seeds ⇒ byte-identical `tokens.json`. No randomness,
no model judgement inside the derivation. Judgement happens *before* (choosing seeds / profile)
and *after* (intentional exceptions in MASTER.md / pages).

Conventions used in this document:

- `VDP.x.y` = a key in `style-profile.json`.
- `{primitive.color.brand.500}` = a token reference exactly as written into `$value`.
- All `$value`s are **strings** (never JSON numbers). Reason: `generate-tokens.cjs`
  `resolveReference()` does `if (result?.$value)` — a numeric `0` is falsy and the reference
  resolves to the raw object (`[object Object]` in CSS). Zero is written as `"0"`.
- `$type` values used: `color, dimension, shadow, number, duration, cubicBezier, fontFamily,
  fontWeight, string`. The generator ignores `$type`/`$description`; they exist for other consumers.
- Keys never contain `.` (references are split on `.`), so `button.primary` becomes the nested
  path `component.button.primary`.

---

## 0. Inputs and platform unit

### 0.1 Inputs

| Input | Source | Required |
|---|---|---|
| `VDP` | `style-profile.json`, already passed `vd.py validate` | yes |
| `seeds` | 6 seed colours `brand, secondary, accent, neutral, success, danger` (+ optional `warning`, `reward`), hex `#RRGGBB` | yes (see 0.2 for resolution order) |

### 0.2 Seed resolution order (first hit wins, per seed slot)

| Priority | Source | Mapping to seed slot |
|---|---|---|
| 1 | `VDP.palette.seeds.<slot>` (optional vdp/1 key, CC-9; `vd.py profile` fills it from the catalog row, the reference palette or the seed) · `VDP.palette.surfaces {background, surface, text, outline}` (filled from catalog `Seed Colors` positions 4–6 + an outline per `shape.outline.color_rule`, or from `palette_observed`) | direct |
| 2 | `--seed-design-system <ds.json>` (output of `search.py --design-system --json`) | `colors.primary→brand`, `colors.secondary→secondary`, `colors.accent→accent`, `colors.muted_foreground→neutral`, `colors.destructive→danger`; `success` from `colors.success` if present |
| 3 | `reference-analysis.json#palette_observed` | `role_guess == "primary"→brand`, `"secondary"→secondary`, `"accent"/"cta"→accent`, `"text"/"neutral"→neutral`; highest `share` wins within a role |
| 4 | `visual-styles.csv` row for `VDP.style.id`, column `Seed Colors` (`primary;secondary;accent;background;surface;text`, 6 hex values, `;`-separated) | `primary→brand`, `secondary→secondary`, `accent→accent`; `neutral` = hue of `text` with S ≤ 8, L 50 (CC-9); success/danger/warning from the seed or constants |
| 5 | Constants | `brand #2563EB, secondary #64748B, accent #0EA5E9, neutral #6B7280, success #16A34A, danger #DC2626` |

`warning` defaults to `#F5A524` and `reward` to its own gold `#FFC83D` (AD-7) when not supplied; an unseeded reward is treated
like a built-in status colour (§2.2 rule 4) and never aliases `warning`.
Seeds are normalised to upper-case `#RRGGBB` and echoed in `$extensions.vdp.seeds` so the output is reproducible.

### 0.3 Platform unit (`$extensions.vdp.platformUnit`)

Stack decides first; platforms only when stack is `other` / absent.

| `VDP.product.stack` | unit |
|---|---|
| `flutter`, `flutter-flame`, `react-native` | `logical` |
| `swiftui` | `pt` |
| `jetpack-compose` | `dp` |
| `unity-ugui`, `unity-ui-toolkit` | `px` (reference-resolution pixels) |
| `react`, `nextjs`, `vue`, `svelte`, `html-tailwind` | `px` |
| `other` / absent | platforms contain `web` or `desktop` → `px`; platforms == `{mobile-ios}` → `pt`; anything else → `dp` |

Dimension formatting: value `0` → `"0"`; unit `logical` → bare number string (`"16"`); otherwise
number + unit (`"16px"`, `"16dp"`, `"16pt"`). **Only `px` output is valid CSS**; the generator
still runs for other units (it does not parse values), but the CSS it emits is for inspection only.
Platform adapters (W2-D) translate.

---

## 1. Primitive layer

### 1.1 Colour ramps (`primitive.color.<ramp>.<step>`)

Ramps produced: `brand, secondary, accent, neutral, success, warning, danger` (+ `reward` when seeded),
each with steps `50,100,200,300,400,500,600,700,800,900`. Plus `primitive.color.white = #FFFFFF`,
`primitive.color.black = #000000`.

Algorithm (HSL, H in 0–360, S and L in 0–100; convert with the standard RGB↔HLS formulas):

1. `(H, S, L) = hsl(seed)`. Step **500 is the seed itself** (verbatim, upper-cased).
2. `neutral := S < 10` (any ramp whose seed is that desaturated).
3. Lighter steps — `L_step = L + (99 − L) × f`, `S_step = S` if neutral else `S × (1 − 0.30 × f)`:

   | step | f |
   |---|---|
   | 400 | 0.40 |
   | 300 | 0.66 |
   | 200 | 0.82 |
   | 100 | 0.92 |
   | 50 | 0.97 |

4. Darker steps — `L_step = L − (L − 10) × g`; saturation **preserves the seed's HSL chroma**
   `C = S·(1 − |2L − 1|)` (S, L as fractions): `S_step = min(S, C / (1 − |2·L_step − 1|))`. A pastel seed (high S, high L, low C)
   therefore darkens into a muted shade instead of neon (`#FF8FAB` → 700 `#BA4A66`, previously `#FF0443`); a saturated mid-L
   seed changes little (`#2F6BFF` → 700 `#003ACA`, unchanged). Lighter steps are unchanged:

   | step | g |
   |---|---|
   | 600 | 0.20 |
   | 700 | 0.40 |
   | 800 | 0.60 |
   | 900 | 0.80 |

5. Hue is constant across the ramp. Convert back to RGB, round each channel to the nearest integer, format `#RRGGBB` upper-case.
6. Guard: if `relative_luminance(neutral.900) > 0.03` (seed too light), replace `neutral.900` with `#111111`. (Guarantees a usable dark text / outline colour.)

Properties the implementer can test: ramps are monotonic in L; a pastel seed (L ≈ 70) yields a
compressed light side and a full dark side; a neutral seed keeps its tint (warm/cool grey).

### 1.2 Spacing (`primitive.spacing.<key>`) — 4-based, same for game and app

| key | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 10 | 12 | 16 | 20 | 24 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| value | 0 | 4 | 8 | 12 | 16 | 20 | 24 | 32 | 40 | 48 | 64 | 80 | 96 |

(unit per §0.3; `$type: dimension`.)

### 1.3 Radius (`primitive.radius.<key>`) — fixed scale; `radius_class` selects the semantic picks (§2.3)

| key | none | xs | sm | md | lg | xl | 2xl | 3xl | full |
|---|---|---|---|---|---|---|---|---|---|
| value | 0 | 2 | 4 | 8 | 12 | 16 | 24 | 32 | 9999 |

### 1.4 Outline widths (`primitive.outline.<key>`)

| key | none | thin | regular | strong | heavy |
|---|---|---|---|---|---|
| value | 0 | 1 | 2 | 3 | 4 |

`semantic.outline.control` = the key whose value is closest to `VDP.shape.outline.width`
(ties → the smaller value); `null`/`0`/missing outline → `none`.

### 1.5 Shadow sets (`primitive.shadow.{none,sm,md,lg,inset}`) — selected by `VDP.rendering.shadow`

`N900` = resolved hex of `primitive.color.neutral.900`; `B500` = hex of `primitive.color.brand.500`;
`rgba(X, a)` = `rgba(r, g, b, a)` of hex X. Values are CSS `box-shadow` strings (`$type: shadow`); adapters translate.

| `rendering.shadow` | sm | md | lg | inset |
|---|---|---|---|---|
| `none` | `none` | `none` | `none` | `none` |
| `offset-soft` | `0 2px 4px rgba(0, 0, 0, 0.12)` | `0 4px 8px rgba(0, 0, 0, 0.14)` | `0 8px 16px rgba(0, 0, 0, 0.16)` | `inset 0 2px 4px rgba(0, 0, 0, 0.15)` |
| `soft-ambient` | `0 1px 2px rgba(0, 0, 0, 0.05)` | `0 4px 12px rgba(0, 0, 0, 0.08)` | `0 12px 32px rgba(0, 0, 0, 0.12)` | `inset 0 1px 2px rgba(0, 0, 0, 0.06)` |
| `hard-offset` | `2px 2px 0 N900` | `4px 4px 0 N900` | `6px 6px 0 N900` | `inset 2px 2px 0 N900` |
| `double-clay` | `0 2px 0 rgba(0, 0, 0, 0.25), 0 4px 6px rgba(0, 0, 0, 0.12)` | `0 4px 0 rgba(0, 0, 0, 0.25), 0 8px 12px rgba(0, 0, 0, 0.14)` | `0 6px 0 rgba(0, 0, 0, 0.25), 0 12px 20px rgba(0, 0, 0, 0.18)` | `inset 0 3px 0 rgba(0, 0, 0, 0.18)` |
| `glow` | `0 0 6px rgba(B500, 0.35)` | `0 0 12px rgba(B500, 0.45)` | `0 0 24px rgba(B500, 0.55)` | `inset 0 0 8px rgba(B500, 0.3)` |

`none` key is always the literal `none`. **Shadow tint (AD-9):** every `rgba(0, 0, 0, a)` above is written as
`rgba(<neutral.900>, a)` — elevation shares the neutral/outline family — unless `VDP.rendering.shadow_tint = "black"`
(set by `vd.py profile` only when the style row asks for black or uncoloured shadows on a dark or flat style). For
`double-clay` the primitive uses a generic "hard" layer; component tokens replace it with the fill's edge step (§3.0)
because the generator cannot compose a reference inside a string.

### 1.6 Font size (`primitive.fontSize.<key>`) — by `VDP.product.kind`

| key | xs | sm | base | lg | xl | 2xl | 3xl | 4xl | display |
|---|---|---|---|---|---|---|---|---|---|
| `app` | 12 | 14 | 16 | 18 | 20 | 24 | 30 | 36 | 48 |
| `game` | 12 | 14 | 16 | 18 | 22 | 28 | 36 | 48 | 64 |

Unit per §0.3 (no `rem`; audit compares numbers). `primitive.fontFamily.display` / `.body` =
`VDP.typography.display` / `.body` verbatim (`$type: fontFamily`).

### 1.7 Line height (`primitive.lineHeight.<key>`, unitless, `$type: number`)

| tight | snug | normal | relaxed |
|---|---|---|---|
| `1.1` | `1.25` | `1.5` | `1.65` |

### 1.8 Icon size (`primitive.iconSize.<key>`) — by kind

| key | sm | md | lg | xl |
|---|---|---|---|---|
| `app` | 16 | 24 | 32 | 48 |
| `game` | 20 | 28 | 40 | 64 |

### 1.9 Touch target (`primitive.touchTarget.{min,recommended}`)

Per platform; the token is the **maximum** across `VDP.product.platforms`.

| platform | min | recommended |
|---|---|---|
| `mobile-ios` | 44 | 44 |
| `mobile-android` | 48 | 48 |
| `tablet` | 44 | 44 |
| `web` | 24 (WCAG 2.5.8) | 44 |
| `desktop` | 24 | 32 |

`$extensions.vdp.minTouchTarget` = the numeric `min` (JSON number, informational only).

### 1.10 Duration (`primitive.duration.<key>`, `$type: duration`, written as `"<n>ms"`) — by `VDP.motion.class`

Seven keys (CC-8): `instant, fast, base, slow, reveal, reward, ambient`. `reward` is the medium reward beat and `ambient` the idle-loop period from `motion-direction.md` §2.

| class | instant | fast | base | slow | reveal | reward | ambient |
|---|---|---|---|---|---|---|---|
| `static` | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `snappy` | 0 | 80 | 140 | 220 | 320 | 600 | 4000 |
| `soft` | 0 | 150 | 250 | 400 | 600 | 650 | 3000 |
| `bouncy` | 0 | 120 | 200 | 350 | 600 | 750 | 2500 |
| `dramatic` | 0 | 200 | 400 | 700 | 1000 | 750 | 2000 |

If `VDP.motion.duration_scale` is an object, its keys (`fast`, `base`, `slow`, … any of the seven) **override** the class row verbatim; keys it omits keep the class value.

### 1.11 Easing (`primitive.easing.<key>`, `$type: cubicBezier`; `$description` carries the human name)

| class | name | standard | enter | exit | emphasized |
|---|---|---|---|---|---|
| `static` | linear | `linear` | `linear` | `linear` | `linear` |
| `snappy` | standard-decelerate | `cubic-bezier(0.2, 0, 0, 1)` | `cubic-bezier(0, 0, 0.2, 1)` | `cubic-bezier(0.4, 0, 1, 1)` | `cubic-bezier(0.2, 0, 0, 1)` |
| `soft` | ease-in-out-soft | `cubic-bezier(0.4, 0, 0.2, 1)` | `cubic-bezier(0, 0, 0.2, 1)` | `cubic-bezier(0.4, 0, 1, 1)` | `cubic-bezier(0.25, 0.1, 0.25, 1)` |
| `bouncy` | spring-soft | `cubic-bezier(0.22, 1, 0.36, 1)` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | `cubic-bezier(0.36, 0, 0.66, -0.56)` | `cubic-bezier(0.68, -0.6, 0.32, 1.6)` |
| `dramatic` | expo-out | `cubic-bezier(0.16, 1, 0.3, 1)` | `cubic-bezier(0.16, 1, 0.3, 1)` | `cubic-bezier(0.7, 0, 0.84, 0)` | `cubic-bezier(0.87, 0, 0.13, 1)` |

Platform adapters map the name: Flutter `Curves.easeOutBack` for spring-soft, `Curves.easeOutCubic`
for standard-decelerate, etc. (W2-D defines that table; the token stores the bezier).

Easing roles (QA AD-4): `standard` never overshoots in any class (all y control points within [0, 1]) and is what
progress/timer fills use (`component.progress.fillEasing = {primitive.easing.standard}`), so a bar never shows more than
100 % or more time than is left. Overshoot is reserved for `enter` and `emphasized` (entrance scale, reward beats).

### 1.12 z-index ladder (`primitive.zIndex.<key>`, `$type: number`)

| base | raised | sticky | hud | overlay | popup | toast | tutorial | debug |
|---|---|---|---|---|---|---|---|---|
| 0 | 10 | 50 | 100 | 200 | 300 | 400 | 500 | 1000 |

### 1.13 Opacity (`primitive.opacity.<key>`, `$type: number`)

| disabled | hover | pressed | loading | scrim | scrimHeavy | muted | ghost | focusRing |
|---|---|---|---|---|---|---|---|---|
| 0.4 | 0.92 | 0.85 | 0.7 | 0.5 | 0.7 | 0.7 | 0.12 | 0.35 |

---

## 2. Semantic layer

### 2.1 Colour slots (`semantic.color.*`) — required 17 + extras

`strategy` = lower-cased `VDP.palette_strategy` (keyword match, substring).
`game` = `VDP.product.kind == "game"`.

| slot | default fill | notes |
|---|---|---|
| `primary` | `{primitive.color.brand.500}` | step may move darker by §2.2 |
| `onPrimary` | §2.2 | |
| `primaryHover` | primary step + 1 (`interaction_steps`, §2.6) | extra |
| `primaryPressed` | primary step + 2 — never equal to the outline / hard-shadow step (+3) | extra |
| `secondary` | `{primitive.color.secondary.500}` | §2.2 |
| `onSecondary` | §2.2 | |
| `accent` | `{primitive.color.accent.500}` (the seed itself) | §2.2 |
| `onAccent` | §2.2 | |
| `background` | strategy contains `pastel-base` → `{primitive.color.brand.50}`; contains `dark` but not `supports-dark` → `{primitive.color.neutral.900}` (dark-first); else `{primitive.color.neutral.50}` | |
| `surface` | light: `{primitive.color.white}`; dark-first: `{primitive.color.neutral.800}` | |
| `surfaceElevated` | §2.4 | |
| `border` | game: `{primitive.color.neutral.300}`; app: `{primitive.color.neutral.200}`; dark-first: `{primitive.color.neutral.700}` | |
| `overlay` | literal `rgba(N900, 0.5)` (0.5 = `primitive.opacity.scrim`) | literal because rgba cannot reference |
| `text` | light: `{primitive.color.neutral.900}`; dark-first: `{primitive.color.neutral.50}` | |
| `textMuted` | light: `{primitive.color.neutral.600}`; dark-first: `{primitive.color.neutral.300}` | 600 on white ≥ 4.5:1 by construction (L ≤ 46) |
| `success` | `{primitive.color.success.600}` | §2.2 |
| `onSuccess` | §2.2 | extra |
| `warning` | `{primitive.color.warning.500}` | §2.2 |
| `onWarning` | §2.2 | extra |
| `danger` | `{primitive.color.danger.600}` | §2.2 |
| `onDanger` | §2.2 | extra |
| `reward` | `{primitive.color.reward.500}` (seed or the `#FFC83D` default) | §2.2 |
| `onReward` | §2.2 | extra |
| `focusRing` | `{primitive.color.brand.400}` | extra |
| `borderInteractive` | `border` stepped (darker on light surfaces, lighter on dark, chroma kept) until ≥ 3:1 against `surface` and `background` (A-16, WCAG 1.4.11); `{semantic.color.border}` when it already passes | extra |

### 2.1a Observed surfaces (`VDP.palette.surfaces`, optional)

When the profile carries `palette.surfaces {background, surface, text, outline}` (filled by `vd.py profile --style/--genre` from the
catalog `Seed Colors` positions 4–6 — outline derived per `shape.outline.color_rule` — or by `--reference` from `palette_observed`;
`vd.py init` injects the catalog surfaces for a hand-written profile that has none), the surfaces are **authoritative**: the
light/dark decision follows the surface background (not the `dark` keyword). `border` follows `shape.outline.color_rule` applied to the background when no `outline`
surface is given: `darker-shade-of-fill` → background L−12 (light) or `neutral.700` (dark); `lighter-tint-of-fill` → `brand.200`; `contrast-dark` → the
surface text colour; other rules keep the §2.1 default (`neutral.700` on dark). The other slots use the literal hexes: `background`, `surface` (and `surfaceElevated` unless shading is
`flat`), `border` ← `outline`, and `text` when it reaches 4.5:1 on the background. `textMuted` walks `neutral.600 → 900` until it
passes 4.5:1 on that background; a background with relative luminance < 0.18 switches `textMuted` to `neutral.300` and, if the
observed text fails, `text` to `neutral.50`. The neutral ramp seed is derived from the observed text colour (§0.2 priority 3).
The surfaces are echoed in `$extensions.vdp.surfaces`. Dark-first strategies ignore surfaces.

### 2.2 `onX` selection (4.5:1 rule) — applies to primary, secondary, accent, success, warning, danger, reward

1. Candidates, in order of preference: the **seed text colour** (`palette.surfaces.text`, literal hex), `D = primitive.color.neutral.900` (after the §1.1 guard) and `W = #FFFFFF`; `#000000` (`{primitive.color.black}`) is a **last resort** used only when it is the sole candidate reaching 4.5:1 — each such use is recorded in `$extensions.vdp.contrastNotes` (several styles forbid pure black; seed a darker text colour or a different fill to avoid it).
2. Compute WCAG 2.x contrast of the fill at its default step against the candidates. If any reaches 4.5:1, pick the **highest-contrast passing candidate** and **keep the fill unchanged** — a brand seed is never darkened while a passing on-colour exists.
3. Only when no candidate (including black) reaches 4.5:1, move the fill **one ramp step toward the opposite luminance of the best candidate** (light candidate → 600→700→…; dark candidate → 400→300→…) and repeat from 2. The semantic slot then points at the new step; `XHover`/`XPressed` shift with it. Every walk is recorded as `"<role>: fill darkened|lightened from #… to #… for contrast"` in `$extensions.vdp.contrastNotes` and copied into the MASTER.md Unknowns section by `vd.py init`. If the ramp end is reached still failing, keep that step and let `vd.py validate` report it (§6) — the script never silently picks a failing pair.
4. **Built-in status colours are not brand colours.** `success`, `warning` and `danger` that are *not seeded* (no
   `palette.seeds.<slot>`, no catalog / design-system seed, no `--seeds` entry) use the same candidates as every fill
   (seed text colour, `neutral.900`, white) but never `#000000`. The highest-contrast passing candidate wins and the fill
   is kept (a gold warning/reward stays gold with dark text); only when none of the three passes does the fill walk
   **darker one ramp step at a time** from its default step (success 600, warning 500, danger 600). Each walk is
   recorded as `"<role>: built-in status fill darkened from #… to #… for contrast (…)"` in
   `$extensions.vdp.contrastNotes`, copied into `style-profile.json#unknowns` by `vd.py profile` and listed once in
   MASTER.md § Unknowns, so a changed hue is always visible. With the default success seed `#16A34A` this walk happens
   for every style (600 → 700, white text). A
   status slot that *is* seeded counts as style-seeded and follows steps 1–3 (fill kept, black only as the last
   resort). An unseeded `reward` aliases the contrast-checked `warning` fill and on-colour.
5. Style-seeded fills (`primary`, `secondary`, `accent`, and `reward` when seeded) never walk while any candidate,
   black included, passes: all 20 catalog seeds have a passing candidate (regression-tested); the cases that need
   black are listed in `contrastNotes`.
5. Outlined display text (game titles with `outline.width ≥ 2` and outline colour = `fill.700` or `neutral.900`) is **exempt** from 4.5:1 in audits but must be declared in MASTER.md "Intentional exceptions"; the tokens still carry a passing `onX`.

Worked results: pastel pink `#F48FB1` → dark text 6.27:1, fill kept; `cute-animal-onet` accent `#FF6B6B` → seed text `#2F4A3A` passes, fill kept (previously darkened to `#EE0000`); `minimal-modern-mobile` primary `#2F6BFF` → text 4.3 / white 4.0 fail, black 4.8 passes → fill kept with `onPrimary = black` (previously `#0049FC`).

### 2.3 Radius picks (`semantic.radius.{control,container,popup,tile,chip}`) by `VDP.shape.radius_class`

| class | control | container | popup | tile | chip |
|---|---|---|---|---|---|
| `none` | none | none | none | none | none |
| `sm` | sm | md | md | xs | sm |
| `md` | md | lg | lg | sm | md |
| `lg` | lg | xl | 2xl | md | full |
| `xl` | xl | 2xl | 3xl | lg | full |
| `pill` | full | 2xl | 3xl | lg | full |

Each is written as `{primitive.radius.<key>}`.

### 2.4 Elevation and `surfaceElevated` by `VDP.rendering.shading`

| shading | `elevation.method` | `surfaceElevated` (light) | `elevation.raised` | `elevation.elevated` | `elevation.floating` |
|---|---|---|---|---|---|
| `flat` | `tint` | `{primitive.color.neutral.100}` | shadow.none | shadow.none | shadow.md |
| `soft`, `soft-cel`, `glossy`, `clay` | `shadow` | `{primitive.color.white}` | shadow.sm | shadow.md | shadow.lg |
| `cel`, `pixel` | `outline` | `{primitive.color.white}` | shadow.none | shadow.none | shadow.md |
| `painterly`, `realistic` | `shadow` | `{primitive.color.white}` | shadow.sm | shadow.lg | shadow.lg |

Dark-first: `surfaceElevated = {primitive.color.neutral.700}` for every shading. `elevation.method`
is a `$type: string` token (`tint|shadow|outline`) that component rules and the audit read.

### 2.5 Outline (`semantic.outline.*`)

| token | value |
|---|---|
| `control` | `{primitive.outline.<key>}` per §1.4 |
| `colorRule` | string from `VDP.shape.outline.color_rule`: `darker-shade-of-fill → "fill+3"`, `lighter-tint-of-fill → "fill.200"`, `contrast-dark → "neutral.900"`, `border-token → "semantic.color.border"`, else `"none"` |

**One outline family (QA AD-2).** Component outlines come from the single rule above, applied two ways:

- **Filled controls** (`button.primary`): `fill+3` → the fill's own ramp at the *edge* step (fill step + 3, e.g. `brand.800` for a
  `brand.500` fill); `fill.200` → `{primitive.color.<fill ramp>.200}`; `contrast-dark` / `border-token` → `{semantic.color.border}`;
  `none` → `transparent`.
- **Surface-filled elements** (`popup`, `tile`, `card.borderColor`, `hud.chip`, `button.icon`, `progress`, `button.secondary`): the
  single surface-outline colour `{semantic.color.border}` (`transparent` when the rule is `none`; the secondary button keeps
  `{semantic.color.border}` so it stays visible). `semantic.color.border` itself follows the rule on the background (§2.1a);
  for `contrast-dark` without surfaces it is `neutral.900`.
- A brand/accent outline on a surface is used only when the profile says so explicitly: `shape.outline.secondary_button =
  "primary"` (set by `vd.py profile` when the style's Button Rule says the secondary button has a primary outline/border)
  → `button.secondary.outlineColor = {semantic.color.primary}`. No other component ever takes a brand/accent step as outline.

### 2.6 States (`semantic.state.{hover,pressed,focus,disabled}`)

**Interaction steps (QA AD-3).** For a filled control at ramp step *s*: hover = *s*+1, pressed = *s*+2, edge (outline and the
`double-clay` hard-shadow layer) = *s*+3, so the pressed fill never equals the outline or the shadow and stays in the fill's ramp.
Fills at 700 or darker have no room for three darker steps: hover = *s*−1, pressed = *s*−2 and the edge takes the darkest free
step. The secondary button presses from `brand.50` (hover) to `brand.100` (pressed) on its surface fill.

`pressedOffset` by `VDP.rendering.shadow`: `none 0, offset-soft 1, soft-ambient 1, hard-offset 2, double-clay 4, glow 0`.

| state | opacity | offsetY | shadow | color / ring |
|---|---|---|---|---|
| `hover` | `{primitive.opacity.hover}` | `0` | — | `color: {semantic.color.primaryHover}` |
| `pressed` | `{primitive.opacity.pressed}` | `pressedOffset` (unit per §0.3) | `{primitive.shadow.inset}` for offset-soft/soft-ambient, else `{primitive.shadow.none}` | `color: {semantic.color.primaryPressed}` |
| `focus` | — | — | — | `ringWidth: 3`, `ringOffset: 2`, `ringColor: {semantic.color.focusRing}` |
| `disabled` | `{primitive.opacity.disabled}` | `0` | `{primitive.shadow.none}` | — |

Semantics for implementers: pressed on a `double-clay` button = translate down by `offsetY` **and**
drop the hard shadow layer (height collapses); hover on touch platforms is a no-op.

### 2.7 Typography roles (`semantic.typography.<role>.{fontFamily,fontSize,lineHeight,fontWeight}`)

| role | family | size | lineHeight | weight |
|---|---|---|---|---|
| `display` | display | display | tight | 700 |
| `title` | display | 2xl | snug | 700 |
| `body` | body | base | normal | game 500 / app 400 |
| `label` | body | sm | snug | 600 |
| `caption` | body | xs | snug | 500 |

### 2.8 Spacing roles (`semantic.spacing.*`)

| inset | stack | inline | section | screenGutter |
|---|---|---|---|---|
| spacing.4 | spacing.3 | spacing.2 | spacing.8 | game spacing.4 / app spacing.5 |

---

## 3. Component layer defaults (`component.*`)

### 3.0 Shared rules

- `fill ramp` for outline/shadow colour = the ramp behind the component's `bg` (`brand` for primary button, `neutral` for surfaces).
- **Shadow rule:** `rendering.shadow == double-clay` → literal string = §1.5 row with `rgba(0,0,0,0.25)` replaced by the fill's **edge-step** hex for filled controls (e.g. `0 4px 0 #BE002F, 0 8px 12px rgba(0, 0, 0, 0.14)` for a `#FF8FAB` fill) and by `neutral.700` for surface elements; else `elevation.method == shadow` → `{primitive.shadow.<step>}`; else `{primitive.shadow.none}`.
- `H` = control height: game 56, app 44. `PX` = horizontal padding key: game `6`, app `5`. `FS` = label size key: game `xl`, app `base`.
- `iconRadius` = `{primitive.radius.full}` when `radius_class ∈ {lg, xl, pill}` else `{semantic.radius.control}`.

### 3.1 `component.button.primary`

| token | value |
|---|---|
| bg / fg | `{semantic.color.primary}` / `{semantic.color.onPrimary}` |
| bgHover / bgPressed | `{semantic.color.primaryHover}` / `{semantic.color.primaryPressed}` |
| outlineWidth / outlineColor | `{semantic.outline.control}` / colorRule on `brand` |
| radius | `{semantic.radius.control}` |
| shadow | shadow rule, step `md` |
| height / minWidth | `H` / game 160, app 96 |
| paddingX / fontSize / fontWeight | `{primitive.spacing.PX}` / `{primitive.fontSize.FS}` / `700` |
| pressedOffsetY | `{semantic.state.pressed.offsetY}` |

### 3.2 `component.button.secondary`

| token | value |
|---|---|
| bg / fg | `{semantic.color.surface}` / `{semantic.color.primary}` |
| bgHover / bgPressed | `{primitive.color.brand.50}` / `{primitive.color.brand.100}` |
| outlineWidth | `{semantic.outline.control}` if `outline.width > 0` else `{primitive.outline.regular}` |
| outlineColor | `{semantic.color.primary}` when colorRule ∈ {none, semantic.color.border}; else colorRule on `brand` |
| radius / height / paddingX / fontSize | as primary |
| fontWeight | game 700 / app 600 |
| shadow | `double-clay` → literal on `neutral`, step `sm`; else `{primitive.shadow.none}` |

### 3.3 `component.button.icon`

| token | value |
|---|---|
| size | `{primitive.touchTarget.recommended}` |
| iconSize | `{primitive.iconSize.md}` |
| bg / fg | game `{semantic.color.surface}` / app `transparent`; `{semantic.color.text}` |
| radius | `iconRadius` |
| outlineWidth / outlineColor | game: `{semantic.outline.control}` / colorRule on `neutral`; app: `{primitive.outline.none}` / `transparent` |
| shadow | game: shadow rule on `neutral`, step `sm`; app: `{primitive.shadow.none}` |

### 3.4 `component.card`

| token | value |
|---|---|
| bg / fg | `{semantic.color.surface}` / `{semantic.color.text}` |
| radius | `{semantic.radius.container}` |
| padding / gap | game `{primitive.spacing.5}`, app `{primitive.spacing.4}` / `{primitive.spacing.3}` |
| borderWidth | game with shadow elevation → `{semantic.outline.control}`; else `{primitive.outline.thin}` |
| borderColor | `{semantic.color.border}` |
| shadow | `{semantic.elevation.raised}` |

### 3.5 `component.popup`

| token | value |
|---|---|
| bg / fg | `{semantic.color.surfaceElevated}` / `{semantic.color.text}` |
| radius | `{semantic.radius.popup}` |
| padding | game `{primitive.spacing.6}`, app `{primitive.spacing.5}` |
| shadow / scrim | `{semantic.elevation.floating}` / `{semantic.color.overlay}` |
| outlineWidth / outlineColor | game: `{semantic.outline.control}` / colorRule on `brand`; app: none / `transparent` |
| maxWidth | game 360, app 480 |
| zIndex | `{primitive.zIndex.popup}` |
| enterDuration / enterEasing | `{primitive.duration.base}` / `{primitive.easing.enter}` |

### 3.6 `component.hud.chip`

| token | value |
|---|---|
| bg / fg | `{semantic.color.surface}` / `{semantic.color.text}` |
| radius | `{semantic.radius.chip}` |
| height | game 36, app 32 |
| paddingX / fontSize / fontWeight | `{primitive.spacing.3}` / game `lg`, app `sm` / `700` |
| iconSize | `{primitive.iconSize.sm}` |
| outlineWidth / outlineColor | game: `{semantic.outline.control}` / colorRule on `neutral`; app: `{primitive.outline.thin}` / `{semantic.color.border}` |
| shadow | game: shadow rule on `neutral`, `sm`; app: none |
| zIndex | `{primitive.zIndex.hud}` |

### 3.7 `component.tile`

| token | value |
|---|---|
| bg / bgSelected | `{semantic.color.surface}` / `{primitive.color.brand.100}` |
| radius | `{semantic.radius.tile}` |
| outlineWidth / outlineColor / outlineColorSelected | `{semantic.outline.control}` / colorRule on `neutral` / `{semantic.color.primary}` |
| shadow | shadow rule on `neutral`, `sm` |
| gap | game `{primitive.spacing.1}`, app `{primitive.spacing.2}` |
| minSize | `{primitive.touchTarget.min}` |

### 3.8 `component.progress`

| token | value |
|---|---|
| track / fill / fillReward | `{primitive.color.neutral.200}` / `{semantic.color.primary}` / `{semantic.color.reward}` |
| height | game 16, app 8 |
| radius | `{primitive.radius.full}` |
| outlineWidth / outlineColor | game: `{semantic.outline.control}` / colorRule on `neutral`; app: none / `transparent` |
| fillDuration / fillEasing | `{primitive.duration.slow}` / `{primitive.easing.standard}` |

---

### 3.9 Component states — post-pass on the assembled tree

Runs after all layers exist (it needs resolved hexes); every change is recorded in `$extensions.vdp.contrastNotes`.

| Rule | Behaviour |
|---|---|
| Hover fill | `bgHover` (and `semantic.color.primaryHover`) is the fill's ramp step one **lighter** when the default label (`onPrimary`) is dark, one **darker** when it is light — whichever keeps the default label ≥ 4.5:1 (the other direction is tried second) — and never equal to the fill, the pressed fill or the outline. Only if neither direction works does hover fall back to the per-state label search below |
| A-14 primary label | candidates seed text, `neutral.900`, white: the one with the highest **minimum** contrast over `bg`, `bgHover`, `bgPressed` becomes `fg`; if none passes on all three, `fg` stays `onPrimary` and `fgHover` / `fgPressed` are chosen only for the states where it fails. `#000000` is a **per-state** last resort (noted in `contrastNotes`), never chosen for all states at once; a state whose best label still fails moves its fill one ramp step until one passes. `bgPressed` keeps fill + 2 (AD-3) |
| A-15 secondary label | the primary-ramp step closest to the primary fill (darker on light surfaces, lighter on dark) that reaches ≥ 4.5:1 on `bg`, `bgHover`, `bgPressed`; on dark surfaces hover/press use dark brand tints (`brand.900` → `brand.800`) instead of `brand.50/100`; an explicit primary outline takes the first step in the same direction reaching ≥ 3:1 vs surface and background |
| A-16 interactive outlines | `tile.outlineColor`, `button.icon.outlineColor`, `button.secondary.outlineColor` (unless explicitly primary) → `{semantic.color.borderInteractive}`; card, popup, HUD chip and progress keep `{semantic.color.border}` |
| panel labels | `card`, `popup`, `hud.chip`, `button.icon` keep `semantic.color.text` when it passes on their own fill, else the best candidate for that fill |
| N3-2 focus ring | `semantic.color.focusRing` (→ `semantic.state.focus.ringColor`, width 3 ≥ 2) = the brand-ramp step nearest the primary, moving away from the page luminance, that reaches ≥ 3:1 against **both** `background` and `surface` and differs from the fill, hover, pressed and resting outline colours; fallback: the brand fill stepped (chroma kept) until it passes |
| N3-3 dark-page edge | on a dark `background` (relative luminance < 0.18) a filled control's outline and double-clay hard layer step **lighter** in the brand ramp (never onto fill/hover/pressed) until ≥ 3:1 against the page, else `borderInteractive`; controls without an outline are identified by their label (≥ 4.5:1 on every state) |
| Tappable HUD capsules | `component.hud.chipInteractive` = `hud.chip` with `outlineColor = {semantic.color.borderInteractive}` (width ≥ thin) for wallet/currency capsules whose `+` opens the shop; display-only capsules (score, timer, moves) keep `hud.chip` |
| AD-6 press feedback | `component.button.{primary,secondary,icon}.pressDuration` = `{primitive.duration.fast}` when ≤ 90 ms, else literal `90ms` |
| AD-8 selected tile | `bgSelected` stays `brand.100`; `outlineColorSelected` = the brand step nearest 700 reaching ≥ 3:1 against the tile fill |

## 4. `$extensions.vdp` block (top level, sibling of `primitive`)

```json
"$extensions": {
  "vdp": {
    "schema": "vdp-tokens/1",
    "platformUnit": "logical",
    "minTouchTarget": 48,
    "motionClass": "bouncy",
    "generatedFrom": "japanese-cute-puzzle",
    "productKind": "game",
    "seeds": {"brand": "#F48FB1", "secondary": "#7FD1C1", "accent": "#FFB347", "neutral": "#7D7470",
              "success": "#5CC46B", "danger": "#F26B6B", "warning": "#F5A524", "reward": "#FFC83D"},
    "derivation": "token-derivation.md v1"
  }
}
```

Required by the contract: `platformUnit, minTouchTarget, motionClass, generatedFrom`. Added:
`schema, productKind, seeds, derivation, driftBudget` (`design-contract.md` §7 defaults; `vd.py validate` reads it for
page drift checks; the audit reads `platformUnit` to parse source values). The generator ignores `$extensions` entirely (it only reads
`primitive`, `semantic`, `component`, `dark`).

## 5. Optional `dark` layer

Emitted only when `strategy` contains `supports-dark`. Shape mirrors the generator's expectation
(`dark.semantic.color.*`, emitted under `.dark {}`):

| slot | value |
|---|---|
| background / surface / surfaceElevated / border | neutral.900 / neutral.800 / neutral.700 / neutral.700 |
| text / textMuted | neutral.50 / neutral.300 |
| primary / onPrimary | brand.400 / §2.2 steps 1–2 only (no darkening walk; validate warns if < 4.5) |
| overlay | literal `rgba(0, 0, 0, 0.6)` |

## 6. Validation hooks (what `vd.py validate` checks on tokens.json)

| check | rule |
|---|---|
| required groups | contract §4.2 list present under `primitive`; 17 required `semantic.color` slots; `semantic.state.{hover,pressed,focus,disabled}` |
| reference integrity | every `{a.b.c}` resolves to a leaf with `$value`; no cycles |
| no numeric `$value` | all leaves are strings (generator safety) |
| contrast | every `onX` vs resolved `X` ≥ 4.5:1; `textMuted` vs `background` ≥ 4.5:1 |
| component states | **error**: any component label (`fg`/`fgHover`/`fgPressed` of buttons, card, popup, HUD chip) < 4.5:1 on its state background; **error**: focus ring < 3:1 against `background` or `surface`; **warning** (`contrast.interactive-boundary`): an interactive outline (tile, tile selected, icon button, secondary button, `hud.chipInteractive`) < 3:1 against its own fill or the background, or an outlined filled control on a dark background whose edge and fill are both < 3:1 against the page |
| unit consistency | every `dimension` string ends with the `$extensions.vdp.platformUnit` suffix (or is `"0"`); `logical` values are bare numbers and are not unit-checked |
| provenance | `$extensions.vdp.generatedFrom == style-profile.json#style.id` |
