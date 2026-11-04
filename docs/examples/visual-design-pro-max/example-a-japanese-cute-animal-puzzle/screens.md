# Onet Garden — screen specifications (hand-written)

Specs for seven screens of a portrait onet / tile-matching game on Flutter + Flame, written **against** the generated contract in `project/design-system/onet-garden/` (`tokens.json`, `component-catalog.md`, `MASTER.md`, `pages/*.md`) as regenerated after the last generator round: per-state button labels, `semantic.color.borderInteractive` for interactive outlines (panels keep `#FFDDAC`), `pressDuration` 90 ms, reward gold split from warning, brand.700 selection outline and neutral.900-tinted shadows; `vd.py validate` (which now also checks component-state contrast) reports `0 error(s), 0 warning(s)`. Every value below is a token path with its resolved value from `tokens.json`; catalog rules are quoted from `component-catalog.md` by component id. Nothing here was rendered or measured — see README "Verification level". Unit is `logical` (Flutter logical pixels; `$extensions.vdp.platformUnit`). Contrast ratios are computed from the hex values (WCAG relative luminance), not measured on a render.

Shared vocabulary used on every screen:

| Role | Token | Resolved |
|---|---|---|
| Page background | `semantic.color.background` (from `palette.surfaces.background`) | `#FFF6E9` |
| Panel / tile fill | `semantic.color.surface` | `#FFFFFF` |
| Brand / CTA fill | `semantic.color.primary` (= `brand.500`) | `#FF8FAB`, label `semantic.color.onPrimary` `#2E2A32` (6.54:1) |
| CTA hover / pressed | `semantic.color.primaryHover` (`brand.400`) / `semantic.color.primaryPressed` (`brand.700`) | `#FBBECD` with label `#2E2A32` (8.94:1) / `#BA4A66` with label `component.button.primary.fgPressed` `#FFFFFF` (4.93:1) |
| CTA outline and hard shadow | `component.button.primary.outlineColor` (`brand.800`), `component.button.primary.shadow` | `#972743` (3.64:1 against the fill), `0 4px 0 #972743, 0 8px 12px rgba(46,42,50,.14)` |
| Panel outlines (non-interactive) | `semantic.color.border` — `component.{card.borderColor, popup.outlineColor, hud.chip.outlineColor, progress.outlineColor}` | `#FFDDAC` |
| Interactive outlines | `semantic.color.borderInteractive` — `component.{tile.outlineColor, button.icon.outlineColor}`; secondary button outline = `brand.700` | `#A88655` (3.38:1 on white, 3.16:1 on the cream background) / `#BA4A66` (4.93:1 on white) |
| Outline rule | `semantic.outline.control` (= `primitive.outline.strong`) with `semantic.outline.colorRule = fill+3` | `3`; three ramp steps darker than a coloured fill (`brand.500` → `brand.800`); white panels use the two outline colours above |
| Selection | `component.tile.outlineColorSelected` = `primitive.color.brand.700` | `#BA4A66` — 4.93:1 on the white tile, 4.60:1 on the cream background, 2.29:1 against the CTA fill so a selected tile no longer reads as a button |
| Accent | `semantic.color.accent` (= `accent.500`) | `#FFD23F`, text `semantic.color.onAccent` `#2E2A32` (9.74:1) |
| Reward gold / warning | `semantic.color.reward` / `semantic.color.warning` (`warning.500`) | `#FFC83D` (text `#2E2A32` 9.09:1) / `#F5A524` (text `#2E2A32` 6.89:1) — separate tokens, but only 1.32:1 apart (H 43° vs 37°), and reward is 1.07:1 from the accent `#FFD23F` |
| Success / danger | `semantic.color.success` (`success.700`) / `semantic.color.danger` (`danger.600`) | `#107435` / `#BB1E1E`, both with white text (5.88:1 / 6.33:1); the success green is a contrast walk listed in `MASTER.md` → Unknowns |
| Text / muted text | `semantic.color.text` / `semantic.color.textMuted` (`neutral.600`) | `#4A3B5C` (9.47:1 on background) / `#6B6274` (5.41:1) |
| Radii | `semantic.radius.tile / control / container / popup / chip` | `12 / 16 / 24 / 32 / 9999` (tile is 8 on the gameplay page) |
| Shadows (`double-clay`, tinted with `neutral.900`) | `primitive.shadow.sm / md / lg`; component hard shadows | elevation `0 2px 0 rgba(46,42,50,.25), 0 4px 6px rgba(46,42,50,.12)` / `0 4px 0 …(.25), 0 8px 12px …(.14)` / `0 6px 0 …(.25), 0 12px 20px …(.18)`; tiles, chips, icon buttons, secondary button `0 2px 0 #56505E, 0 4px 6px rgba(46,42,50,.12)`; no pure black anywhere in `tokens.json` |
| Type roles | `semantic.typography.title / body / label / caption` | Fredoka 28/1.25/700 · Nunito 16/1.5/500 · Nunito 14/1.25/600 · Nunito 12/1.25/500 |
| Motion | `primitive.duration.fast / base / slow / reveal / reward / ambient`; `component.button.{primary,secondary,icon}.pressDuration` | `120 / 200 / 350 / 600 / 750 / 2500 ms`; press feedback **90 ms** |
| Easing | `primitive.easing.standard` / `enter` / `exit` / `emphasized` | `cubic-bezier(0.22, 1, 0.36, 1)` (no overshoot — used by progress and timer fills) / `cubic-bezier(0.34, 1.56, 0.64, 1)` (overshoot, entrances only) / `cubic-bezier(0.36, 0, 0.66, -0.56)` / `cubic-bezier(0.68, -0.6, 0.32, 1.6)` |
| Focus ring | `semantic.state.focus.ringColor` = `semantic.color.focusRing` (`brand.900`), ring width 3, offset 2 | `#740420` — 11.01:1 on the background, 11.79:1 on white, 5.49:1 against the CTA fill; checked by `vd.py validate` |
| Touch | `primitive.touchTarget.min` | `48` — every tappable element below has a hit area ≥ 48 × 48, even where the visual is smaller (AD-5) |
| Layers | `primitive.zIndex.hud / overlay / popup / toast` | `100 / 200 / 300 / 400` |
| Device frames | from `visual_qa.py manifest` (Example C) | phone-s 375 × 667 (status bar 20), phone-m 390 × 844 (47), phone-l 430 × 932 (59); bottom safe area assumed 0 / 34 / 34 (iOS home indicator — an assumption, not from the contract) |

Contract notes before coding:
1. **Prose vs tokens (A-4).** The style prose says "pill" buttons, 28 px popups and 2 px HUD outlines; the tokens resolve `control 16`, `popup 32`, `chip outline 3`. These specs follow the tokens.
2. The two label-contrast defects of the previous round are **resolved in the tokens**: pressed CTA label `#FFFFFF` on `#BA4A66` (4.93:1, A-14) and secondary label `#BA4A66` on white (4.93:1, A-15). `MASTER.md` → Unknowns records the secondary step ("primary-family label stepped from #FF8FAB to brand.700 (#BA4A66) to reach 4.5:1").

---

## 1. Home

Purpose: one tap to play, a glance at currency and daily streak, entry to shop/settings. Catalog: `menu.list`, `button.primary`, `button.icon`, `hud.currency`, `reward.streak`, `nav.bottom-bar`.

| Element | Spec |
|---|---|
| Background | `semantic.color.background` `#FFF6E9`; garden illustration band in the top 35 % at `primitive.opacity.muted` 0.7 so the title keeps 4.5:1 |
| Title "Onet Garden" | `semantic.typography.display` Fredoka 64/1.1/700 in `semantic.color.text` `#4A3B5C`; no text shadow (not in the tokens) |
| Top-right icon buttons (settings, mail) | `component.button.icon`: size `{primitive.touchTarget.recommended}` 48, icon `{primitive.iconSize.md}` 28 in `#4A3B5C`, bg `#FFFFFF`, outline 3 `semantic.color.borderInteractive` `#A88655`, radius `full`, press feedback `pressDuration` 90 ms, shadow `0 2px 0 #56505E, 0 4px 6px rgba(46,42,50,.12)` |
| Currency capsule (coins) — tappable, opens the shop | `component.hud.chipInteractive` (the tappable variant): height 36, radius 9999, paddingX `{primitive.spacing.3}` 12, font `{primitive.fontSize.lg}` 18/700, icon 20, outline 3 `semantic.color.borderInteractive` `#A88655` (3.38:1 on white — tappable capsules no longer wear the decorative panel border), shadow `0 2px 0 #56505E, 0 4px 6px rgba(46,42,50,.12)`. **Hit area 48 × ≥ 48** (`primitive.touchTarget.min`): 6 of invisible padding above and below the 36 plate; ≥ 8 between neighbouring capsules. Catalog `hud.currency`: never more than 3 capsules |
| Play button | `component.button.primary`: height 56, minWidth 160 (full width minus 2 × `semantic.spacing.screenGutter` 16 on phones), bg `#FF8FAB`, label `{primitive.fontSize.xl}` 22/700 `#2E2A32` (6.54:1), radius 16, outline 3 `#972743`, shadow `0 4px 0 #972743, 0 8px 12px rgba(46,42,50,.14)`; hover `#FBBECD` (label 8.94:1); pressed: translateY `component.button.primary.pressedOffsetY` 4, bg `#BA4A66`, label `component.button.primary.fgPressed` `#FFFFFF` (4.93:1), shadow `primitive.shadow.none`, the `#972743` outline stays visible (1.59:1 against the pressed fill), within `component.button.primary.pressDuration` 90 ms |
| Secondary actions (Levels, Shop) | `component.button.secondary`: height 56, surface fill, outline 3 `#BA4A66`, label `#BA4A66` (4.93:1 on white; 4.54:1 on the `#FDF3F6` pressed fill), hover `brand.50` `#FEF8F9`, pressed `brand.100` `#FDF3F6`, `pressDuration` 90 ms, shadow `0 2px 0 #56505E, …` |
| Daily streak | `reward.streak`; counter in `semantic.typography.label` 14/600; flame glyph in `semantic.color.reward` `#FFC83D` with a 2 `#A88655` outline (the bare gold is 1.44:1 on the cream); not tappable (the streak calendar opens from the reward popup) |
| Bottom bar | `nav.bottom-bar`: 4 items, each hit area ≥ 48 × 56; active item fill `brand.100` `#FDF3F6` + icon `#FF8FAB`, inactive icon `#6B6274`; height ≥ 56 + safe area |
| Idle motion | mascot breathing loop `primitive.duration.ambient` 2500 ms; disabled under reduced motion (`interaction-guidelines.md`) |

## 2. Level selection

Purpose: pick the next level; status readable in greyscale. Catalog: `nav.level-node`, `progress.stars`, `chip.filter`, `button.icon`.

| Element | Spec |
|---|---|
| Map path | background `#FFF6E9`; path stroke `semantic.color.border` `#FFDDAC` at `semantic.outline.control` 3 |
| Level node (tappable) | `nav.level-node`: 56–64 blob (silhouette `rounded-blob`) — ≥ 48 hit area by construction; number `{primitive.fontSize.base}` 16/700 on the node fill with ≥ 4.5:1; stroke 3 per `colorRule fill+3`; **current**: +15 % scale, outline ×2 (6) in `semantic.color.accent` `#FFD23F`, mascot pin; **locked**: saturation −60 %, padlock, no number; **completed** (AD-10): fill `primitive.color.success.200` `#CEF2DB`, ring 3 in `semantic.color.success` `#107435`, number in `semantic.color.text` `#4A3B5C` plus a check glyph. Arithmetic: ring vs cream map `#FFF6E9` = **5.49:1** (≥ 3:1 for a non-text boundary), number on the fill = **8.38:1** (≥ 4.5:1), fill vs map 1.13:1 (decorative). The full `#107435` fill (white number 5.88:1) is kept for the *current* chapter's completed-badge only, so the darkest saturated colour no longer dominates a pastel map |
| Stars under node | `progress.stars`: 12 each, gap `{primitive.spacing.1}` 4, filled `semantic.color.reward` `#FFC83D`, empty `neutral.300` `#D2CED6`, each with a 1.5 outline in `#A88655` so the gold reads on the cream (1.44:1 without it); not tappable |
| Chapter header | `semantic.typography.title` Fredoka 28; chapter chest = `reward.chest` locked state |
| Current-node pulse | period 2500 ms (`primitive.duration.ambient`), `primitive.easing.standard` |
| Back button | `component.button.icon` (48) top-left at `semantic.spacing.screenGutter` 16 + safe top |
| Filter chips (optional: "Events") | `chip.filter`: visual height 36, radius `chip`, selected fill `brand.100` + outline `#BA4A66`, idle outline 3 `semantic.color.borderInteractive` `#A88655`; **hit area 48 high** (6 padding above and below), ≥ 8 between chips |

## 3. Gameplay (board, HUD, hint, undo, timer, score, pause)

Page file: `pages/gameplay.md` (overrides: `component.tile.radius` 12 → 8 — one step tighter than the xl shape class at these tile sizes; `component.hud.chip.shadow` → `primitive.shadow.none`). Catalog: `board.tile`, `board.tile-selected`, `board.match-effect`, `board.hint-highlight`, `board.shuffle-overlay`, `hud.score`, `hud.timer`, `hud.hint-button`, `hud.undo-button`, `hud.pause-button`.

### Board layout (AD-1: the board must fit 375 and 390 widths with ≥ 48 touch tiles)

Portrait onet board: **6 columns across × 8 rows down** (the genre's default size is listed as "6x8 to 10x14 cells portrait" in `game-ui-patterns.md`; the short side goes across). Gutter `semantic.spacing.screenGutter` 16 each side, gap = master `component.tile.gap` `{primitive.spacing.1}` 4, tile capped at 56.

`tile = min(56, floor((W − 2 × 16 − 5 × 4) / 6))`

| Device | Width available | Tile | Board W × H | Cell pitch (hit area) | Vertical budget (status + HUD 64 + board + tool row 72 + bottom safe) | Board share of the region between HUD and tool row |
|---|---|---|---|---|---|---|
| phone-s 375 × 667 | 375 − 32 = 343 → (343 − 20) / 6 = 53.8 | **53** | 6 × 53 + 5 × 4 = **338** × 8 × 53 + 7 × 4 = **452** | 57 | 20 + 64 + 452 + 72 + 0 = **608 ≤ 667** (59 spare) | 452 / (667 − 20 − 64 − 72) = 452 / 511 = **88 %** |
| phone-m 390 × 844 | 390 − 32 = 358 → (358 − 20) / 6 = 56.3 | **56** (cap) | **356** × 8 × 56 + 28 = **476** | 60 | 47 + 64 + 476 + 72 + 34 = **693 ≤ 844** (151 spare) | 476 / 627 = **76 %** |
| phone-l 430 × 932 | 398 → 63.0 | **56** (cap) | **356** × **476** | 60 | 59 + 64 + 476 + 72 + 34 = **705 ≤ 932** | 476 / 703 = **68 %** |

- Every cell pitch is ≥ 48 (57 / 60), so `primitive.touchTarget.min` holds with **no** density exception; `game-ui-patterns.md` §1.2's 40–47 dp exception ladder is not used. The hit area is the full cell pitch (tile + half the gap on each side), so there are no dead zones between tiles.
- Width is the binding constraint. The profile's "grid gets at least 85 % of vertical space" is met on phone-s (88 %) and **not** on taller phones at 6 × 8 (76 % / 68 %): the board is centred in its region and the spare height is margin. Level design may use taller boards there — 6 × 10 at tile 56 is 10 × 56 + 9 × 4 = 596 = 95 % of phone-m's 627 and 85 % of phone-l's 703 — but columns stay 6 so the width arithmetic above is unchanged. This is a level-design choice, not a contract exception.
- 8 × 6 *landscape* (8 tiles across) does not fit a phone in portrait: 8 × 48 + 7 × 4 = 412 > 358 even at the 48 minimum. That was the first-round error QA flagged as AD-1.

### Elements

| Element | Spec |
|---|---|
| **Board tile — idle** | `component.tile`: 53 (phone-s) / 56 (phone-m, phone-l), fill `#FFFFFF`, radius **8 on this page** (`{primitive.radius.md}`, master 12), outline `component.tile.outlineWidth` 3 in `component.tile.outlineColor` = `semantic.color.borderInteractive` `#A88655` (3.38:1 against the white tile, 3.16:1 against the cream board — the outline itself now draws the tile edge, A-16), shadow `component.tile.shadow` `0 2px 0 #56505E, 0 4px 6px rgba(46,42,50,.12)`, gap 4 |
| Tile face | chibi animal per `illustration.asset_rendering` ("vector flat with one soft shade band, hue-shifted toward purple"); gloss ellipse top-left 30 % white over the top 35 % (`catalog_rules.highlight_rule`) |
| **Selected** | `board.tile-selected`: outline ×1.5 = 4.5 → 4 (`primitive.outline.heavy`) in `component.tile.outlineColorSelected` `brand.700` `#BA4A66` (4.93:1 on white; against the idle `#A88655` outline 1.46:1, so selection is carried by hue — rose vs tan — plus the 3 → 4 width and the scale), fill `component.tile.bgSelected` `brand.100` `#FDF3F6` (1.09:1 — decorative only), shadow one step up (`primitive.shadow.md`), transition `primitive.duration.fast` 120 ms with `primitive.easing.enter` (the bouncy overshoot is wanted on this pop) |
| **Matched / clearing** | `board.match-effect`: path line between the pair at outline + 1 = 4 in `#FFD23F`; tiles scale to 0 over `primitive.duration.base` 200 ms with `primitive.easing.exit` `cubic-bezier(0.36, 0, 0.66, -0.56)`; particle burst ≤ 8 sprites in palette colours only |
| **Hinted** | `board.hint-highlight`: outline ×1.5 in `semantic.color.warning` `#F5A524`, pulse 2 cycles of `primitive.duration.slow` 350 ms, then static; stops on first tap; under reduced motion: steady outline. The low-time timer uses the same warning gold, so the hint adds a non-colour cue: a 48 hand glyph over the hinted pair; reward stars no longer share this colour (`semantic.color.reward #FFC83D`) |
| **Blocked / shuffling** | `board.shuffle-overlay`: scrim `semantic.color.overlay` `rgba(46,42,50,0.5)` at `primitive.zIndex.overlay` 200, label `semantic.typography.title` |
| **HUD plate (score / timer / moves)** — not tappable | `component.hud.chip` values (height 36, radius 9999, outline 3 `#FFDDAC`, font 18/700) with **shadow `primitive.shadow.none` on this page** (override); `zIndex` `primitive.zIndex.hud` 100. Max 3 plates (profile `components.hud`) |
| Score | `hud.score`: numerals ≥ 16 in Fredoka with tabular figures (fallback Nunito 700); count-up ≤ 250 ms → `primitive.duration.base` 200; milestone pulse 1.06 scale in 120 ms |
| Timer | `hud.timer`: 8-high bar inside the plate (a documented variant: `component.progress.height` is 16); fill `component.progress.fill` `#FF8FAB` → `semantic.color.warning` `#F5A524` under 20 % → `semantic.color.danger` `#BB1E1E` under 10 %; track `component.progress.track` `#E6E4E8`; bar animates with `component.progress.fillEasing` = `primitive.easing.standard` `cubic-bezier(0.22, 1, 0.36, 1)` — no overshoot, so the bar never shows more time than is left; digits ≥ 18; critical: 1 Hz digit blink + haptic |
| Hint button | `hud.hint-button` slot 56 × 56 (≥ 48), `primitive.iconSize.md` 28 glyph; count badge `badge.count` in `#FFD23F`; priced state shows `commerce.price-tag` small (32 high) **inside** the 56 slot — the slot is the tap target, the tag is not tappable on its own |
| Undo button | `hud.undo-button`: same 56 slot, arrow-counter-clockwise glyph, counted badge; disabled = `semantic.state.disabled` opacity `primitive.opacity.disabled` 0.4, shadow none, no tap sound |
| Pause button | `hud.pause-button`: 48 hit area (visual 40 allowed), icon 20 (`primitive.iconSize.sm`), top-left at 16 + safe top; opens `popup.pause` |
| Pause popup | `component.popup`: bg `#FFFFFF`, radius 32, padding `{primitive.spacing.6}` 24, outline 3 `#FFDDAC`, shadow `primitive.shadow.lg`, maxWidth 360, scrim `semantic.color.overlay`, enter `primitive.duration.base` 200 ms with `primitive.easing.enter`; Resume = `button.primary` (56), Restart / Quit = `button.secondary` (56, label `#BA4A66` 4.93:1); Quit confirmation via `confirm.destructive` with `semantic.color.danger` `#BB1E1E` |
| Saturation budget | QA `anti_patterns`: ≤ 3 saturated hues on the board — primary `#FF8FAB`, accent `#FFD23F`, warning/danger only in timer states |

## 4. Settings

Purpose: sound, music, haptics, language, restore purchases, privacy. Catalog: `menu.list`, `list.item`, `chip.filter`, `confirm.destructive`, `state.disabled`.

| Element | Spec |
|---|---|
| Sheet | `panel.container` on `#FFF6E9`; groups as `card.default`: radius 24, padding `{primitive.spacing.5}` 20, border 3 `#FFDDAC` (`component.card.borderColor`), shadow `semantic.elevation.raised` (= `primitive.shadow.sm`), gap `{primitive.spacing.3}` 12 |
| Rows | `list.item`: min height 48 (the whole row is the tap target), label `semantic.typography.body` Nunito 16/500, value `semantic.typography.label` 14/600 in `#6B6274`; divider `primitive.outline.thin` 1 in `#FFDDAC` |
| Toggles | thumb 28 (`iconSize.md`) on a 48 × 28 pill (`radius.chip`), on-fill `#FF8FAB`, off-fill `neutral.300` `#D2CED6`; **hit area 48 × 48** (the row label is also tappable); animate `primitive.duration.fast` 120 ms with `primitive.easing.standard` |
| Language picker | `chip.filter` row (36 visual / 48 hit), idle outline `#A88655`, selected chip `brand.100` fill + outline `#BA4A66` |
| Restore purchases / Reset progress | `button.secondary` (56); Reset opens `confirm.destructive`: destructive action = `button.destructive` with `semantic.color.danger` `#BB1E1E` on white (6.33:1) |
| Version / legal | `semantic.typography.caption` Nunito 12/500 `#6B6274` |

## 5. Shop

Page file: `pages/shop.md` (override: hero offer card radius 24 → 32; remaps: hero card → `popup.offer` rules, offer outline → `primitive.color.accent.700` `#CA9D0A`; exception `shop-countdown-chip`, warning fill, expires 2026-12-31). Catalog: `commerce.shop-item`, `commerce.price-tag`, `popup.offer`, `badge.count`, `hud.currency`.

| Element | Spec |
|---|---|
| Wallet (tappable: scrolls to the coin packs) | `component.hud.chipInteractive` (36, outline 3 `#A88655`) top-right — the decorative `component.hud.chip` (`#FFDDAC`) is kept for non-tappable plates such as the countdown chip; **hit area 48 × ≥ 48** — 6 of padding above and below the plate, same rule as the Home capsule (AD-5) |
| Grid | 2 columns on phones, gap `{primitive.spacing.2}` 8 (catalog "grid 2–3 columns, 8dp gap"), outer gutter 16 → card width on phone-s (375 − 32 − 8) / 2 = 167.5 |
| Pack card | `commerce.shop-item` on `card.default`: radius 24, border 3 `#FFDDAC`, shadow `primitive.shadow.sm`, contents as `reward.card` xs rows; **one** badge max ("Best value" / "Popular") as a 20-high corner chip in `#FFD23F` with `#2E2A32` text (9.74:1), not tappable |
| Price tag (the buy control) | `commerce.price-tag` large: pill (`radius.chip`), **height 48** = `primitive.touchTarget.min` (the catalog row says 44 dp for the large tag; the contract's own QA criterion "All interactive targets ≥ 48 logical" wins — AD-5), full card width minus 16; fill `semantic.color.primary` `#FF8FAB`, text Nunito 16/700 `#2E2A32` (6.54:1), coin glyph 16 left of the number; pressed fill `#BA4A66` with the label switching to `fgPressed` `#FFFFFF` (4.93:1), press feedback 90 ms; insufficient funds: outline `semantic.color.danger` `#BB1E1E` + "Get coins" routing; loading: skeleton, never "0". The small (32) tag appears only inside a larger tappable parent |
| Hero offer card | per page override: radius **32** (`semantic.radius.popup`), outline `primitive.color.accent.700` `#CA9D0A` (remap; the only gold-outlined object on the screen), ribbon title plate overlapping the top edge by 50 % (profile `components.popup`), hero art ≤ 40 % of card height (`popup.offer`); its close X is a `component.button.icon` (48), not the catalog's 44 |
| Countdown chip | `component.hud.chip` geometry with fill `semantic.color.warning` `#F5A524` and text `#2E2A32` (6.89:1) — page exception; `hh:mm:ss`; not tappable; greys on expiry via `state.disabled` opacity 0.4 and never re-arms silently (`popup.offer` states) |
| Remove ads | `commerce.shop-item` remove-ads variant; owned state = check + `state.disabled` |
| Purchase flow | pressed → `semantic.state.pressed` (offset 4, opacity 0.85) → store sheet; success toast `feedback.toast` at `primitive.zIndex.toast` 400 in `semantic.color.success` `#107435` + a non-colour cue (check glyph) |
| Saturation budget | palette strategy allows a third saturated accent on reward moments; the warning chip is that third hue — hence the dated exception |

## 6. Win screen

Catalog: `popup.win`, `progress.stars`, `reward.card`, `button.primary`, `button.secondary`.

| Element | Spec |
|---|---|
| Entrance | `popup.win` states: enters ≥ 600 ms after the last match effect → `primitive.duration.reveal` 600; panel scale 0.85 → 1 with overshoot (profile `components.popup`) using `primitive.easing.enter`, duration `primitive.duration.base` 200 |
| Panel | `component.popup`: `#FFFFFF`, radius 32, padding 24, outline 3 `#FFDDAC`, shadow `primitive.shadow.lg`, maxWidth 360, scrim `rgba(46,42,50,0.5)`, zIndex 300 |
| Ribbon title | "Level 12 clear!" in `semantic.typography.title` Fredoka 28/700 on a `#FF8FAB` plate overlapping the panel top by 50 %, text `#2E2A32` |
| Stars | `progress.stars` 48–64 each (`primitive.iconSize.xl` 64 for the middle star if the crown layout is used), gap 8, filled `semantic.color.reward` `#FFC83D` on the white panel (1.55:1 — a 2 `#A88655` star outline carries the shape), pop-in staggered 180 ms; skippable to the final state by tapping anywhere on the panel |
| Earnings | `reward.card` 64–88 square: radius 16 (`semantic.radius.control`), outline 3, amount chip "×12" 12/700 bottom-centre, rarity frame default `semantic.color.reward` `#FFC83D` |
| Celebration layer | behind panel content, above the scrim; confetti of 3 shapes max (circle, star, heart) in palette colours; rays rotate ≤ 6°/s; bounce to 1.1 scale on the reward beat `primitive.duration.reward` 750 ms (synced to sound) |
| Next | `component.button.primary` full width at the panel bottom (height 56, radius 16, `#FF8FAB`, outline `#972743`) |
| ×2 reward (ad) | `button.secondary` (56) with ad glyph + `commerce.price-tag` ad variant ("Watch ad") inside it |
| Reduced motion | T3 beat becomes an instant state swap with ≤ 150 ms fade (`interaction-guidelines.md`) |

## 7. Unified reward UI (chest, daily login, mission rows, wheel)

Page file: `pages/rewards.md` (override: `component.popup.enterDuration` 200 → 750 ms; remap `popup.win` → full-screen overlay; exception `reward-overlay`: heavier scrim 0.7, no `maxWidth`). One reward frame reused everywhere so a sticker earned on the win screen looks identical in the chest and in the shop pack.

| Element | Spec |
|---|---|
| Reward frame (`reward.card`) | 64–88 square (96 hero), radius 16, outline 3 in the rarity ramp (default `semantic.color.reward` `#FFC83D`, selected `semantic.color.accent` `#FFD23F` ×1.5 = 4), fill `#FFFFFF`, gloss top-left 30 %; states: revealing (scale 0 → 1.1 → 1 over `primitive.duration.base` 200 ms with `primitive.easing.enter`, stagger 180 ms), claimed (check overlay, saturation −40 %), overflow chip "+3 more"; tappable cards are ≥ 64, so ≥ 48 |
| Chest (`reward.chest`) | sprite 120–160 in the chibi rendering; ready state bounces every 2500 ms (`primitive.duration.ambient`); opening: shake ×2 at `fast` 120 → lid pop at `base` 200 → items stagger 180; result grid 3 columns of `reward.card`, gap 8, max 5 + overflow; Open = `button.primary` (56) with key/cost `commerce.price-tag` small inside it |
| Full-screen overlay | per page exception: scrim neutral.900 `#2E2A32` at `primitive.opacity.scrimHeavy` 0.7 (master `semantic.color.overlay` is 0.5), no `component.popup.maxWidth`; panel radius 32 and outline 3 `#FFDDAC` kept; enter at `primitive.duration.reward` 750 ms (page override) with `primitive.easing.emphasized` `cubic-bezier(0.68, -0.6, 0.32, 1.6)`; close X = `component.button.icon` 48 (the catalog row's "close X 44dp" is below the contract minimum — AD-5) |
| Daily login (`reward.daily-login`) | 7 cells of `reward.card` 64, today's cell outline `#FFD23F` ×1.5, claimed cells at saturation −40 %, day-7 cell 96 hero with the chest; Claim = `button.primary` |
| Mission row (`reward.mission-item`) | `list.item` height ≥ 48 + `component.progress`: track `#E6E4E8`, fill `#FF8FAB` (`fillReward` `#FFC83D` on completion), height 16, radius `full`, outline 3 `#FFDDAC`, fill animates `component.progress.fillDuration` 350 ms with `component.progress.fillEasing` `cubic-bezier(0.22, 1, 0.36, 1)` — no overshoot past the real value |
| Spin wheel (`reward.wheel`) | 8 segments alternating `brand.100` `#FDF3F6` / `secondary.100` `#F2F9F8` (1.02:1 to each other, so fills alone do not separate them) **separated by 3 dividers in `semantic.color.borderInteractive` `#A88655`** (AD-10). Arithmetic: divider vs `#FDF3F6` = **3.11:1**, divider vs `#F2F9F8` = **3.17:1** — both ≥ 3:1 for a non-text boundary; outer rim 3 `#A88655` against the white popup = 3.38:1. Prize icons sit centred in each segment; pointer `#FFD23F` with a 2 `#A88655` outline; spin uses `primitive.easing.exit` into a 2500 ms settle, result card = `reward.card` hero; Spin = `button.primary` (56) |
| Confetti / particles | 3 shapes, palette colours only, cap 60 sprites; reduced motion: single static burst image, no loop |
| Character | mascot cheer pose in the same chibi style as Home (QA criterion "Reward screen uses the same character style as home") |

---

### Cross-screen QA hooks (from `MASTER.md`)

- Every `onX` pair in the `MASTER.md` colour table passes 4.5:1 (lowest: `textMuted` 5.41:1, `success` 5.88:1), and so do the component states `vd.py validate` now checks: CTA default 6.54:1, hover 8.94:1, pressed 4.93:1; secondary label 4.93:1. Non-text boundaries ≥ 3:1: interactive outlines `#A88655` 3.16–3.38:1, selection `#BA4A66` 4.60–4.93:1, wheel dividers 3.11–3.17:1, completed-node ring 5.49:1.
- All interactive targets ≥ 48 logical (AD-5): tiles 53–56 with 57–60 pitch, buttons 56, icon buttons 48, price tag 48, chips and capsules 36 visual inside 48 hit areas, pause 40 visual inside 48, toggles 48, list rows 48. Non-interactive plates (HUD score/timer/moves, countdown chip, badges, small price tags inside buttons) may stay smaller.
- No colour, font family, radius or duration outside `tokens.json` without a `pages/<page>.md` entry — the three page files are the complete list of deviations for this project.
- Pressed state visible within 100 ms: `component.button.*.pressDuration` is 90 ms (AD-6), so the token itself satisfies the QA criterion; `primitive.duration.fast` 120 ms stays for selection and HUD feedback.
