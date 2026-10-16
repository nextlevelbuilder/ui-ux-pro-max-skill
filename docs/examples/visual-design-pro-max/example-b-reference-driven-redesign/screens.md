# Pet Diary Redesign — three screens under the derived contract (hand-written)

Specs for **home**, **diary / log** and **profile / settings** written against the contract that `vd.py profile --reference` + `vd.py init` produced in `project/design-system/pet-diary-redesign/` — *as generated*, including the derivation errors documented in `ground-truth-check.md`. Each screen declares exactly one intentional functional exception, recorded with `vd.py page` (skeleton) and filled by hand in `project/design-system/pet-diary-redesign/pages/{home,diary,profile}.md`; `vd.py validate` exits 0 on the result. Nothing was rendered. Unit `logical` (Flutter).

Where the derived value is known to be wrong versus the reference, the row says **[contract-fix]**: fix it in `style-profile.json` / `tokens.json` for the whole product, never as a page override.

## Contract vocabulary (resolved from `tokens.json`)

Final regeneration: the contract below is the output of the scripts after all fix rounds (including per-state button labels and `borderInteractive`); `vd.py validate` reports 0 errors, 0 warnings. Rows marked **[confirm]** are graded unknowns the user must answer; rows marked **[contract-fix]** are places where the derived value still disagrees with the reference for a known reason.

| Role | Token | Resolved |
|---|---|---|
| Page background | `semantic.color.background` (from `palette.surfaces.background`) | `#FFF7ED` — matches the reference |
| Card fill | `semantic.color.surface` | `#FFFFFF` |
| Brand | `semantic.color.primary` (`brand.500`) | `#F97316`; on-colour `semantic.color.onPrimary` `#322C2A` (4.90:1) |
| Brand tints | `primitive.color.brand.100 / 200 / 300` | `#FBF2EB / #F8E4D6 / #F5CFB4` |
| Secondary (blue tile tint) | `semantic.color.secondary` (`secondary.500`) | `#BFDBFE` |
| Accent | `semantic.color.accent` (`brand.700`) | `#B24C05` on white (5.34:1) **[confirm: placeholder derived from the brand ramp, flagged in `unknowns`]** |
| Text / muted | `semantic.color.text` / `semantic.color.textMuted` | `#9A3412` (6.88:1 on background) / `#746662` (5.18:1) — text matches the reference |
| Border | `semantic.color.border` (from `palette.surfaces.outline`) | `#FED7AA` — matches the reference |
| Danger | `semantic.color.danger` | `#BB1E1E` on white (6.33:1) |
| Warning / reward | `semantic.color.warning` / `semantic.color.reward` (unseeded defaults) | `#F5A524` (text `#322C2A` 6.73:1) / `#FFC83D` (text `#322C2A` 8.88:1) — separate tokens **[confirm: the reference shows no reward colour]** |
| Success | `semantic.color.success` | `#107435` on white (5.88:1) — darkened from `#138B3F` for contrast; listed in `MASTER.md` → Unknowns |
| CTA states | `semantic.color.primaryHover` / `primaryPressed`; `component.button.primary.fgPressed`, `pressDuration` | hover `#F3AB79` with `#322C2A` (7.14:1); pressed `#B24C05` with `#FFFFFF` (5.34:1); press feedback 90 ms |
| Radii | `semantic.radius.control / container / popup / tile / chip` | `16 / 24 / 32 / 12 / 9999` — control 16 matches the reference's `--radius-btn` |
| Outline | `semantic.outline.control` (`primitive.outline.regular`); `semantic.color.borderInteractive` | `2`; `colorRule = fill.200` → primary button outline `brand.200 #F8E4D6`; cards, chips and progress keep the observed peach `semantic.color.border #FED7AA`; tiles and the secondary button use `semantic.color.borderInteractive #AC8558` (3.36:1 on white, 3.16:1 on the cream) |
| Shadows | `primitive.shadow.sm / md / lg` | all `none` **[contract-fix → the reference's double shadows; obs-6 was misgraded, "exact shadow values" is in `unknowns`]** |
| Fonts | `primitive.fontFamily.display / body` | `"bold rounded geometric sans"` / `"humanist sans"` (CC-4 classifications, split per obs-7) **[confirm → Fredoka / Nunito]** |
| Type scale | `primitive.fontSize.xs / sm / base / lg / xl / 2xl / display` | `12 / 14 / 16 / 18 / 20 / 24 / 48` |
| Type roles | `semantic.typography.title / body / label / caption` | display 24/1.25/700 · body 16/1.5/400 · body 14/1.25/600 · body 12/1.25/500 |
| Motion | `primitive.duration.fast / base / slow` | `150 / 250 / 400 ms` (class `soft`) **[confirm: base → 200 per CSS; motion is in `unknowns`]** |
| Focus ring | `semantic.state.focus.ringColor` (`brand.600`), width 3, offset 2 | `#DD5E06` — 3.48:1 on the background, 3.70:1 on white (1.32:1 against the CTA fill; the offset keeps it over the background) |
| Touch | `primitive.touchTarget.min` | `48` |
| Components | `component.button.primary` height 44 · paddingX `spacing.5` 20 · fontSize 16/700 · minWidth 96 · radius `control` 16 · outline 2 `brand.200`; `component.button.secondary` outline 2 `#AC8558`, label `#B24C05` (5.34:1 on white); `component.button.icon` size 48 · icon 24 · bg transparent · radius `full` · no outline; `component.card` radius 24 · padding `spacing.4` 16 · border `outline.thin` 1 `#FED7AA` · gap 12; `component.hud.chip` height 32 · fontSize 14/700 · radius `chip` · icon 16 · outline thin `border` (decorative); tappable chips use `component.hud.chipInteractive` (outline 1 `#AC8558`, 32 visual inside a 48 hit area); `component.tile` radius 12 · outline 2 `#AC8558` · selected outline `#B24C05` · bgSelected `brand.100` · gap 8 · minSize 48; `component.popup` radius 32 · padding 20 · maxWidth 480 | from `tokens.json#component` |

Catalog (app rows, `component-catalog.md`): `nav.top-bar`, `nav.bottom-bar`, `card.default`, `list.item`, `menu.list`, `button.icon`, `button.primary`, `button.destructive`, `confirm.destructive`, `chip.filter`, `input.text`, `badge.count`, `indicator.notification`, `state.empty`, `sheet.bottom`.

---

## 1. Home

Page file `pages/home.md` — override `component.card.padding` 16 → 20 (3-up cards with a centred 48 tile); remap: active nav item → `chip.filter` selected look; **intentional exception `home-quick-actions`**: the icon tiles use `semantic.color.secondary` `#BFDBFE` and mint `#BBF7D0` (outside `tokens.json`), reason: reference rule-8 `context:home`, expires 2026-12-31 (until a mint ramp is added to `palette.seeds`).

| Element | Spec |
|---|---|
| App bar (`nav.top-bar`) | height 56 + safe top; logo tile 36 with radius `semantic.radius.tile` 12 and a `brand.500 → brand.300` gradient (reference 135°); title `semantic.typography.title` 24/700 in `semantic.color.text`; right: two `component.button.icon` (bell with `indicator.notification` dot in `#F97316`, gear) — size 48, glyph 28, fill transparent per the tokens **[contract-fix: the reference has white 44 px plates with `--shadow-card`; the transparent, shadowless icon button follows from `rendering.shadow = none` (obs-6) — answer the shadow unknown and this row changes]** |
| Hero pet card (`card.default`) | radius `semantic.radius.container` 24 (reference 28 — within the rule-2 ladder, keep 24), padding **20** (page override), border 1 `#FED7AA` (reference: 2 px — `component.card.borderWidth` is `outline.thin`; raise to `outline.regular` at profile level if the 2 px frame matters), centred: avatar 120 circle (`primitive.radius.full`) with the peach→orange gradient, name in `title` 24/700, breed line in `caption` 12 `#746662`, 3 stats in a row (value `primitive.fontSize.xl` 20/700 in `#F97316`, label `caption` 12 muted), gap `primitive.spacing.6` 24 |
| Quick actions "今日待办" | section title `label` 14/600; 3 equal cards (`card.default`, radius 24 → reference 20 is the same class), each with a 48 × 48 icon tile radius 12 (`semantic.radius.tile`) in peach `brand.200` `#F8E4D6`, blue `#BFDBFE`, mint `#BBF7D0` (**exception**), glyph 26 in `semantic.color.text`, label `label` 14/600; whole card tappable, min height 48 |
| Activity list "今日动态" | `list.item` inside `card.default`: leading time `caption` 12 muted min-width 48, 12 px dot `#F97316` (`primitive.radius.full`), title `body` 16 (reference 0.95rem) 700, subtitle `caption` muted; row gap `component.card.gap` 12 |
| Bottom nav (`nav.bottom-bar`) | 4 items, 72 high + safe bottom, top border 1 `#FED7AA` (reference 2 px, see hero card note); active item = `chip.filter` selected plate (`brand.100` `#FBF2EB`, radius `chip`) with icon + label in `#F97316`; inactive `#746662`; transition `primitive.duration.fast` 150 ms **[confirm: reference uses 200 ms]** |
| Motion | card press: `semantic.state.pressed` (opacity 0.85) over 150 ms; no hover on touch; reduced motion: colour change only |
| QA | `qa_criteria` from the profile: one orange carries all emphasis (brand mark, stat values, dot, active nav) — the mint/blue tiles are the recorded exception; every tap target ≥ 48 |

## 2. Diary / log

Page file `pages/diary.md` — override `component.card.radius` 24 → 16 (`primitive.radius.xl`) for row-height elements; remap `card.default` → `list.item` for rows; **intentional exception `diary-list`**: rows drop `component.card.shadow` (none anyway in this contract) and use a 1 px divider (`primitive.outline.thin`) instead of the 2 px outline, reason: a dense chronological list needs eight rows above the fold; the outline stays on the day-group header card; expires `never`.

| Element | Spec |
|---|---|
| App bar | title "日记" `title` 24/700; right `component.button.icon` "search"; optional `chip.filter` row below (全部 / 喂食 / 玩耍 / 健康): height 32 (`component.hud.chip.height`), radius `chip`, selected `brand.100` + text `#F97316`, unselected surface + outline thin `#E8E5E4` |
| Day group header | `card.default` with radius **16** (page override) and the full 2 px outline, containing the date in `label` 14/600 and a count `badge.count` (16 high, `#F97316` on white) |
| Entry row (`list.item`) | min height 56, horizontal padding `primitive.spacing.4` 16, divider 1 `#FED7AA` between rows (**exception**), leading time `caption` 12 muted (min-width 48), category dot 12 in `#F97316` — category colour is **not** used for the dot (rule-1: one orange carries emphasis; the category is in the chip, not the dot), title `body` 16/700 `#322C2A`, note `caption` 12 muted, trailing chevron 20 (`primitive.iconSize.sm`) muted |
| Swipe actions | reveal width 96 (`component.button.primary.minWidth`): edit = `button.secondary` look (surface, `#B24C05` label 5.34:1, `#AC8558` outline), delete = `button.destructive` (`#BB1E1E` fill, white text, 6.33:1); delete confirms via `confirm.destructive` |
| Add entry FAB | `component.button.primary` geometry as a 56 circle (`primitive.radius.full`; the contract's `control` radius is 16, so the FAB is a documented variant) in `#F97316`, glyph 28 in `#322C2A` (4.90:1 — tight; the reference puts white glyphs on orange, which fails 4.5:1 — keep the dark on-colour from the tokens), bottom-right at 16 + nav height; outline 2 `brand.200 #F8E4D6` per `component.button.primary.outlineColor` |
| Empty state (`state.empty`) | cat silhouette 120 in `#746662` at `primitive.opacity.muted` 0.7, text `body` 16 muted, CTA `button.primary` 44 high |
| Pull-to-refresh / load | `state.loading`: skeleton rows at `primitive.opacity.loading` 0.7, shimmer `primitive.duration.ambient` 3000 ms |
| Motion | row expand/collapse `primitive.duration.base` 250 ms **[confirm: reference 200 ms]**, `primitive.easing.standard` |

## 3. Profile / settings

Page file `pages/profile.md` — override `component.card.radius` 24 → 16 for grouped settings lists; remap `button.primary` → `button.destructive` for "sign out" and "delete diary" (reference rule-1 reserves orange for emphasis; a page never recolours the primary button); **intentional exception `profile-settings`**: grouped rows use `menu.list` density (44-high rows) instead of card spacing, reason: utility screen; the reference shows no settings screen (not derivable), expires 2026-12-31 (review once the settings screen is designed).

| Element | Spec |
|---|---|
| Header card | `card.default` radius 24 (not overridden here — it is a hero-class card), padding 16, border 1 `#FED7AA` (reference 2 px): avatar 72 circle with the peach→orange gradient, owner name `title` 24/700, pet count `caption` muted, "edit" as `button.secondary` 44 high (surface fill, `#F97316` text, outline 2) |
| Settings groups (`menu.list` in `card.default`) | radius **16** (page override), rows 44 high (**exception**), label `body` 16, value `label` 14/600 muted, leading glyph 20 in `#F97316`, divider 1 `#FED7AA`; groups: 宠物 (pets), 提醒 (reminders), 外观 (appearance), 账号 (account) |
| Toggles | thumb 24 on a 44 × 24 pill, on-fill `#F97316`, off-fill `neutral.300` `#D6D0CE`, 150 ms **[confirm: reference 200 ms]**; no outline (`component.button.icon.outlineWidth` precedent: `primitive.outline.none`) |
| Reminder time picker | opens `sheet.bottom`: radius `semantic.radius.popup` 32 on the top corners, padding `component.popup.padding` 20, grabber 4 × 32 `neutral.300`, scrim `semantic.color.overlay` `rgba(50,44,42,.5)` |
| Appearance → dark mode | **not derivable** (reference `not_derivable[]`): the row exists, the dark palette does not; ship as `state.disabled` (opacity 0.4) with a "coming soon" `caption` until a dark ramp is derived |
| Sign out / delete diary | `button.destructive` (**remap**): fill `#BB1E1E`, white label 16/700 (6.33:1), radius `control`, 44 high, full width inside the last group; both confirm through `confirm.destructive` (popup radius 32, primary action red, cancel = `button.secondary`) |
| Version line | `caption` 12 muted centred, 24 below the last group |
| QA | no information by colour alone: destructive rows also carry the trash/exit glyph; every row ≥ 44 high (exception) but tap targets stay ≥ 48 wide; `qa_criteria` "palette seeds match palette_observed roles" now holds for background/text/border (`palette.surfaces`); the open items are the graded unknowns in `ground-truth-check.md` |

---

### One exception per screen — summary

| Screen | Exception (page-scope) | Functional reason | Recorded in |
|---|---|---|---|
| home | secondary tints (blue `#BFDBFE`, mint `#BBF7D0`) on the quick-action icon tiles | category recognition at a glance; reference rule-8 `context:home` | `pages/home.md` (exception row, expires 2026-12-31) + `style-profile.json#intentional_exceptions[0]` (generated from rule-8) |
| diary | rows use a 1 px divider, no outline/elevation; row cards radius 16 | eight entries above the fold in a chronological log | `pages/diary.md` (override + exception, `never`) |
| profile | 44-high `menu.list` rows; destructive actions remapped to `button.destructive`; group radius 16 | utility density; destructive ≠ brand emphasis | `pages/profile.md` (override + remap + exception, 2026-12-31) |

All three page files passed `vd.py validate` (exit 0, `logs/07-validate-final.txt`). In the first round the same content was rejected once for colour remaps in the Overrides table; the regenerated validator counts literals only, so the accepted version was re-applied directly.
