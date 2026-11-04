# Game UI Patterns

Reference for the `visual-direction` skill. Applies when `product.kind == "game"` in the Visual Direction Profile (`style-profile.json`, schema `vdp/1`).

**Relation to the existing mobile rules.** Everything in `references/pro-rules.md` of the `ui-ux-pro-max` skill (touch target 44pt/48dp, safe areas, 4/8dp rhythm, icon discipline, light/dark contrast, reduced motion, screen-reader order) is assumed and **not repeated**. This file adds what games need beyond an app: a board that owns most of the screen, a HUD that must stay readable during motion, reward loops, currency, and popups that interrupt play. Where a game rule intentionally relaxes an app rule (dense tile grids, decorative display type), the relaxation is written here with its limit and must be recorded in `intentional_exceptions` of the profile.

**Profile fields referenced** (by exact key): `shape.radius_class`, `shape.silhouette`, `shape.outline.width`, `shape.outline.color_rule`, `rendering.shading`, `rendering.highlight`, `rendering.shadow`, `typography.display`, `typography.body`, `typography.case`, `palette_strategy`, `iconography.style`, `illustration.character_style`, `motion.class`, `motion.duration_scale.{fast,base,slow}`, `motion.reduced_motion`, `intentional_exceptions[]`.

Units: `dp` is used throughout; read as `pt` on iOS and logical pixels on Flutter/web. Portrait phone reference frame: 360 x 800 dp (Android) / 390 x 844 pt (iOS). Landscape and tablet notes are given where they differ.

---

## 0. Radius and outline resolution used by this file

The profile stores a class, not a number. This file uses the following resolution so that every rule below has a concrete value. (The numbers in `tokens.json` come from `token-derivation.md` §2.3 and are canonical where they differ — e.g. the `xl` popup resolves to `primitive.radius.3xl` = 32; the *relationships* — tile one step tighter than cards, popups one step looser than buttons — are the contract.)

| `shape.radius_class` | base (buttons, cards) | tile / board cell (one step tighter) | popup panel (one step looser, capped) | chip / pill |
|---|---|---|---|---|
| `none` | 0 | 0 | 0 | 0 |
| `sm` | 4 | 2 | 8 | 4 |
| `md` | 8 | 6 | 12 | 999 |
| `lg` | 12 | 8 | 16 | 999 |
| `xl` | 16 | 12 | 24 | 999 |
| `pill` | 999 (height/2) | 12 | 28 | 999 |

Outline: `shape.outline.width` is the stroke on primary buttons and the popup panel. Tiles use `outline.width` x 0.66 (minimum 1 dp, rounded to 0.5). HUD counters use the same width as tiles. Colour follows `shape.outline.color_rule` on every screen; no component may use a different rule (e.g. "black outline on buttons, white on tiles") unless listed as an intentional exception.

Shading: `rendering.shading` picks the fill treatment for *every* interactive surface. `rendering.highlight` and `rendering.shadow` apply to primary buttons, tiles, popup panels and reward items; they do **not** apply to text, HUD numerals or progress bars (keep those flat to stay readable over motion).

---

## 1. Game-specific layout, reach and gesture rules (beyond pro-rules)

### 1.1 Portrait screen zones (360 x 800 dp, one-hand right thumb; mirror for left)

| Zone | Vertical range | Reach cost | What goes here |
|---|---|---|---|
| Z1 System + HUD | 0 to safeTop + 64 dp | stretch | score, timer/moves, pause, settings, currency. Low-frequency taps only (pause ≤ 1 per minute). |
| Z2 Board | HUD bottom + 8 dp to booster bar top − 8 dp | mixed | the play area. Target 55–70 % of screen height in portrait. |
| Z3 Boosters / primary action | 800 − safeBottom − 96 to 800 − safeBottom | easy | boosters, hint, undo, shuffle, the single primary CTA on non-gameplay screens. |
| Z4 Bottom nav (non-gameplay) | 800 − safeBottom − 56 to 800 − safeBottom | easy | home / levels / shop / events / profile. Never shown during gameplay. |

Thumb-reach rule: any control a player taps more than once per 30 s of play must have its centre within 320 dp of the bottom edge and within 300 dp horizontally of the thumb side (i.e. not in the far top corner). Pause and settings are exempt (low frequency). Hint/undo/boosters are **not** exempt.

Landscape (tablet or forced landscape): HUD moves to a side column of 96–120 dp on the non-dominant side; boosters sit in the dominant-side column; board stays centred with ≥ 16 dp margin. Do not stretch the portrait HUD band across 1024 dp.

### 1.2 Board density and the touch-target exception

Pro-rules require 48 dp / 44 pt. Tile grids frequently cannot. The exception ladder:

| Cell pitch (tile + gap) | Status | Required mitigation |
|---|---|---|
| ≥ 48 dp | compliant | none |
| 40–47 dp | allowed with exception | hit area = full cell pitch (no gap dead zones); gap ≤ 4 dp; record `{"scope":"gameplay-board","rule":"cell pitch 40dp","reason":"8x10 grid on 360dp width"}` |
| 36–39 dp | allowed only for puzzle grids with select-then-select input (no drag) | plus: selection highlight ≥ 3 dp outline; mis-tap undo available; zoom not required |
| < 36 dp | not allowed | reduce grid columns or add level scroll/zoom |

Grid gap is never larger than 25 % of tile size (soft-cel and clay styles) or 12 % (flat/pixel) — larger gaps read as unrelated objects.

### 1.3 Gesture ownership (one primary gesture per region)

| Region | Primary gesture | Forbidden secondary gesture | Reason |
|---|---|---|---|
| Board (tap-select genres: onet, word grid, sorting) | tap | horizontal swipe (conflicts with iOS back / Android predictive back), long-press menus | mis-fire while scanning |
| Board (swap genres: match-3) | tap + drag ≤ 1 cell, tap-tap fallback | pinch, two-finger | drag threshold 12 dp; release outside cell cancels |
| Board (merge) | drag-and-drop | tap-to-auto-merge unless explicitly a setting | ambiguity between "inspect" and "merge" |
| Level map | vertical scroll + tap node | drag nodes, horizontal paging | the map is a list, not a canvas |
| Idle screens | tap-to-collect spam allowed | swipe between tabs | taps are the core loop |
| Popups | tap buttons, swipe-down to dismiss **only** for non-commercial sheets | tap-outside-to-accept | tap-outside must always equal "close", never "buy" |
| Edge 0–20 dp both sides | reserved for OS back gesture | any game gesture | Android 13+ / iOS edge swipe |

### 1.4 Layer stack (z-order) — identical on every screen

1. background / parallax
2. board or content
3. HUD (gameplay) or top bar (other screens)
4. in-world effects (match particles, coin fly) — may overlap HUD, never overlap popups
5. toast / inline hint banner
6. scrim + popup
7. reward celebration layer (confetti, flash) — above popup panel, below buttons' hit test
8. tutorial hand / spotlight mask
9. system dialogs (OS permission, ad SDK)

A reward effect that renders *under* the popup it belongs to, or a toast that renders *over* a popup, is a QA failure.

### 1.5 HUD legibility over motion

HUD numerals use `typography.display` only when the display face has tabular figures or a numeral-safe variant; otherwise `typography.body` bold. Minimum numeral size 16 dp (score), 14 dp (currency), 18 dp (timer/moves — the one number players glance at mid-move). Numerals must sit on a plate (fill + `shape.outline.width` x 0.66 stroke, radius = tile radius) so that board particles behind never reduce contrast below 4.5:1. Plate opacity ≥ 0.85.

---

## 2. Genre family profiles

Each family lists what differs from the default; the screen sections below assume the default and call out genre deltas.

### 2.1 Casual tile matching (onet / Pikachu / mahjong-connect)
- **Loop:** select tile A, select identical tile B, path must be clear (≤ 2 turns). Time or move limit per level.
- **Board:** 6x8 to 10x14 cells portrait. Cell pitch 36–48 dp (see 1.2). Selection is two-step → the *selected* state must be unmistakable (3 dp outline + 4 % scale + lift shadow).
- **HUD must-haves:** timer bar (not just digits), hint count, shuffle count, pause. Score is secondary (can be small).
- **Signature feedback:** connection line drawn between matched pair for `motion.duration_scale.fast` ms, then tiles pop. The line must be visible even in `motion.class: static` (draw as a 1-frame flash).
- **Lose trigger:** timer zero, or no valid pair and no shuffles (auto-shuffle policy must be shown in tutorial).
- **Pitfalls:** timer colour change without countdown audio/haptic; shuffle animation that lets the player tap during re-layout; hint that highlights a pair hidden under the HUD.

### 2.2 Match-3 (swap, line/cluster clearing)
- **Loop:** swap adjacent pieces to make 3+, cascades, objectives (collect N, clear jelly, bring items down).
- **Board:** 7x9 to 9x11; cell pitch 40–48 dp. Objectives panel in HUD is mandatory and must list up to 4 objectives with icon + remaining count.
- **HUD must-haves:** moves (large, Z1 centre), objectives (Z1 left), score (small), boosters (Z3). Timer only in timed modes.
- **Signature feedback:** cascade combo escalation (small → medium → jackpot tiers from `motion-direction.md`); special-piece creation has its own effect; "last 5 moves" pulses the moves counter once per move.
- **Lose trigger:** moves zero with objectives remaining → out-of-moves screen with +5 moves continue offer (rules in 3.5).
- **Pitfalls:** input accepted during cascade; objectives icon not matching the board piece art; "sugar-crush" end-of-level effect longer than 3 s without skip.

### 2.3 Merge (merge-2 / merge-3, board merge)
- **Loop:** drag identical items together to level them up; board is an inventory; energy gate.
- **Board:** 7x9 to 8x10; cell pitch ≥ 44 dp because drag needs finger clearance; dragged item scales 1.15 and offsets 24 dp above the finger.
- **HUD must-haves:** energy (with refill timer), currency, order/quest tray (what to merge for). Moves/timer absent.
- **Board states extra:** `locked` (cobweb / bubble), `generator-ready`, `generator-cooldown` (ring timer), `can-merge-target` (pulse when an identical item is being dragged).
- **Pitfalls:** merge target highlight that is the same colour as selection; order tray hiding bottom board row; sell confirmation missing (irreversible).

### 2.4 Sorting (water sort, ball sort, parking jam, goods sort)
- **Loop:** pick a container, pick a destination; limited containers; optional undo/add-container boosters.
- **Board:** 4–12 containers, each 56–80 dp wide; containers are tall, so the board is a flex-wrap with 2–3 rows. Tap targets are the whole container (≥ 56 dp wide, full height).
- **HUD must-haves:** level number, undo (with count), add-container, hint, restart. Timer absent unless mode says so.
- **Selected state:** the top layer *lifts* out of the container (translate −12 dp, `motion.duration_scale.fast`), not an outline; outline is reserved for the hint destination.
- **Lose trigger:** no legal move → show "No moves left" sheet with undo/restart, no scrim darker than 50 % (player wants to inspect the board).
- **Pitfalls:** undo that silently costs currency; restart without confirm after ≥ 10 moves; containers too close for 56 dp finger.

### 2.5 Word (crossword, word-connect, anagram wheel, word search)
- **Loop:** drag over letters on a wheel/grid or tap letters in order; words fill a crossword.
- **Board:** letter wheel ≥ 240 dp diameter, letter targets ≥ 48 dp; crossword cells 28–40 dp (display only, not tappable → no exception needed). Current word preview sits between crossword and wheel at 24 dp numeral size.
- **HUD must-haves:** coins, hint (reveal letter) with price, shuffle letters (free), level/chapter. No timer (unless daily challenge).
- **Signature feedback:** correct word → letters fly from preview to crossword cells (`base` duration per letter, 40 ms stagger). Wrong word → preview shakes 4 dp, 2 cycles, with light haptic.
- **Pitfalls:** drag path line that hides letters; extra-word jar hidden under safe area; hint price shown only after tap.

### 2.6 Idle / incremental (tap-to-earn, factory, tycoon)
- **Loop:** income accrues; tap to collect; buy upgrades; prestige.
- **Board:** scrolling scene (vertical or 2.5D). Tap-collect targets ≥ 56 dp because taps are rapid. Collect bubbles float but never move while the finger is down.
- **HUD must-haves:** primary currency (large, with per-second rate), secondary/premium currency, offline-earnings popup on return (with 2x via ad), upgrade bar (Z3, scrollable). Score/timer absent.
- **Numbers:** abbreviate from 1 000 → `1K`, 1 000 000 → `1M`, then `B`, `T`, `aa`, `ab` …; never show more than 4 significant characters in the HUD; full value on tap/hold.
- **Pitfalls:** upgrade button that changes width as price grows (layout jitter); currency counter animating so slowly the player cannot tell whether the purchase succeeded (counter must settle within 1 s).

### 2.7 Kids learning (ages 3–8: tracing, matching, phonics, counting)
- **Loop:** short activities with a host character; no fail state; sticker rewards.
- **Board:** targets ≥ 64 dp (small fingers + motor precision); drag tolerance (drop zone) ≥ 1.5x the dragged item; no double-tap, no long-press.
- **HUD must-haves:** home/exit behind a parental gate (hold 3 s or math question), activity progress (dots, max 5), host character. **No** timer, no score numerals, no currency in the activity.
- **Visual:** `shape.radius_class` forced to `xl` or `pill`; `shape.outline.width` ≥ 3 dp; `rendering.shading` soft-cel or clay; every icon paired with audio label; text optional.
- **Rewards:** celebration after every activity (medium tier), stickers collected in a book; never a locked chest or spin wheel (COPPA / family policy; avoid chance mechanics).
- **Pitfalls:** any purchase CTA inside the activity; external links without gate; ads interrupting the activity; text-only instructions.

### 2.8 Anime casual RPG (gacha-lite, auto-battle, collection)
- **Loop:** stage selection → auto/semi-auto battle → loot → upgrade characters → gacha pulls.
- **Screens beyond the shared set:** character detail, team formation, gacha pull, stage result. Battle HUD = skill buttons (Z3, 56–64 dp, cooldown ring), speed toggle (1x/2x), auto toggle, wave counter, HP bars per unit.
- **Visual:** `illustration.character_style` drives portrait framing (bust crop with 8 % head margin); rarity colour ramp is a palette slot (`reward` plus up to 5 rarity hues) and must be identical in gacha, inventory, shop and result.
- **Gacha rules:** show rates in ≤ 1 tap (platform policy); pull animation skippable after 1.5 s; pity counter visible; result screen lists every item with rarity frame before any "pull again" CTA.
- **Pitfalls:** "pull again" positioned where the skip tap lands; rarity colours diverging between screens; cooldown shown by colour only.

---

## 3. Screens

Legend used in every screen: **Purpose** · **Hierarchy** (reading order 1→n) · **Mandatory** · **Optional** · **Visual rules** (profile-tied) · **Interaction** · **Anti-patterns** · **QA** (binary checks a screenshot reviewer can tick).

### 3.1 Gameplay HUD

**Purpose.** Keep the win condition, the constraint (moves/time), and the escape hatches (pause, hint, boosters) visible without stealing attention from the board.

**Hierarchy.** 1 constraint (moves or timer) → 2 objective / target score → 3 score → 4 boosters → 5 currency → 6 pause.

**Mandatory.** Constraint counter; objective or score; pause (top corner, 48 dp); at least one assist control (hint or undo or shuffle) with remaining count or price.

**Optional.** Currency (show only if spendable from this screen); combo meter; level number; settings shortcut (prefer inside pause); streak/multiplier badge.

**Visual rules.**
- HUD band height 56–72 dp (+ safeTop). Never two stacked bands; if objectives need a second row, it becomes a 36 dp sub-band and total ≤ 96 dp.
- Plates: fill `semantic.color.surface` at ≥ 85 % opacity, stroke `shape.outline.width` x 0.66, radius = tile radius from §0; `rendering.shadow` is **not** applied to HUD plates (shadows over the board add noise).
- Numerals: see §1.5. Timer uses a bar (full width of plate, 6–8 dp tall) plus digits; moves use digits only.
- Icons follow `iconography.style`; a booster slot is 56 x 56 dp (icon 32 dp) with count badge 18 dp at top-right, badge font 11 dp bold.
- `motion.class` drives counter changes: `static` → instant; `snappy` → 120 ms count-up; `soft`/`bouncy` → count-up + 1.06 scale pulse; `dramatic` → same as bouncy plus 80 ms glow. Timer last 10 s: digits pulse every second regardless of class (informational motion survives reduced motion).

**Interaction.**
- Pause 48 dp minimum, top corner, Z1; one tap, no hold.
- Boosters in Z3; tapping a booster enters an *armed* state (slot outline grows to `outline.width` x 2, board shows valid targets, a cancel X appears at the slot) — never auto-apply on tap.
- Hint tap: free uses first, then price; price must be visible on the slot before tap.
- No HUD element may change size or position during gameplay except badges' numbers.

**Anti-patterns.**
- Timer colour change without audio/haptic countdown (colour-only state; also fails colour-blind players).
- Score that animates for > 1 s and hides the actual total during that time.
- Currency with a "+" that opens the shop *during* a timed level without pausing the timer.
- Booster bar overlapping the bottom board row.
- Objective icon drawn in a different art style than the board piece it refers to.

**QA.**
- [ ] HUD band ≤ 96 dp total including sub-band; board top edge ≥ 8 dp below it.
- [ ] Constraint counter ≥ 18 dp numerals on a plate; contrast ≥ 4.5:1 against the plate.
- [ ] Pause is in a corner and ≥ 48 dp hit box (hit box may exceed visual).
- [ ] Every booster slot shows count or price before tap.
- [ ] No HUD element overlaps the board bounding box.
- [ ] Plate stroke colour matches `shape.outline.color_rule` applied to the plate fill.

### 3.2 Board and tile states

**Purpose.** Every tile communicates exactly one state at a time; the state vocabulary is the same in tutorial, gameplay and hint overlays.

**State vocabulary and required visual deltas** (deltas are relative to `idle`; the *same* delta set is reused on every screen that shows tiles, including the shop preview and tutorial):

| State | Visual delta | Motion (`motion.duration_scale`) | Audio/haptic |
|---|---|---|---|
| idle | base fill per `rendering.shading`; tile radius §0; stroke `outline.width` x 0.66 | none; ambient wobble allowed only for `bouncy`/`dramatic`, amplitude ≤ 2 dp, period ≥ 2 s, ≤ 10 % of tiles at once | — |
| selectable (valid move exists for the current selection) | +4 % brightness or subtle inner glow; no size change | none | — |
| selected | outline `outline.width` x 1.5 in `semantic.color.accent`; scale 1.04–1.06; shadow lifted one step (`rendering.shadow`) | `fast` ms ease-out | light tap sfx + light haptic |
| matched (pair confirmed) | flash to white 60 % for 1 frame then pop out: scale 1.15 → 0 or fade out | `base` ms; `static` class → fade 100 ms | match sfx; medium haptic at combo ≥ 3 |
| hinted | pulsing outline `semantic.color.warning` 2 cycles (`slow` ms each) + optional arrow/finger; pulse pauses while a tile is selected | loop, stops on first user tap | soft chime once |
| blocked (frozen/locked/chained) | overlay sprite with ≥ 60 % coverage; tile saturation −40 %; no outline change on tap | tap → 3 dp shake, `fast` ms | dull sfx |
| shuffling | all tiles fade to 50 % → reposition → fade back; input blocked; HUD shows "Shuffling…" plate | total ≤ 2 x `slow` ms; `static` → instant swap + 150 ms crossfade | whoosh |
| drag-ghost (merge/sort) | item at 1.15 scale, 24 dp above the finger, 80 % opacity; origin cell shows dashed outline | follows finger with no lag smoothing > 1 frame | — |
| drop-valid / drop-invalid | target cell outline accent (valid) / danger (invalid) `outline.width` x 1.5 | `fast` ms | — |
| cleared (board slot after removal) | empty cell drawn as background with 30 % inset dot grid or nothing (per style), never a "ghost tile" | — | — |

**Visual rules.** Tile face art follows `illustration.asset_rendering`; tile frame follows `rendering.shading` + `rendering.highlight`. Tile radius one step tighter than buttons (§0). For `rendering.shading: pixel`, radius is forced to `none` and outline 1 dp — record as intentional exception if the profile says otherwise.

**Interaction.** Tap registers on pointer-up inside the cell; movement > 12 dp before up cancels (prevents scroll-tap conflict). Select-then-select: tapping the selected tile again deselects; tapping a non-matching tile moves the selection (does not error).

**Anti-patterns.** Selected state that only changes colour (fails on saturated boards); hint pulse continuing while the player already selected something; matched tiles removed instantly with no frame of acknowledgement; blocked tiles that look like special tiles; empty cells drawn as faded tiles (players try to tap them).

**QA.**
- [ ] A still screenshot with one tile selected: the selected tile is identifiable within 1 s by a reviewer who was not told which one.
- [ ] Selected outline width = 1.5 x the idle outline (measure).
- [ ] Hinted and selected use different hue slots (`warning` vs `accent`).
- [ ] Blocked overlay covers ≥ 60 % of the tile.
- [ ] No tile is partially hidden under the HUD or booster bar.

### 3.3 Pause menu

**Purpose.** Stop the clock, confirm it stopped, offer resume / restart / quit / settings.

**Hierarchy.** 1 "Paused" title + frozen constraint (e.g. "0:42 left") → 2 Resume → 3 Restart → 4 Settings (sound, music, vibration, language) → 5 Quit to map.

**Mandatory.** Resume as the primary button; the paused value shown; music/sfx/vibration toggles (so players do not have to leave the level); scrim.

**Optional.** Level objective recap; "How to play"; booster inventory (read-only).

**Visual rules.** Panel radius = popup radius (§0); panel stroke `shape.outline.width`; `rendering.shadow` offset-soft or per profile; scrim 55–70 % (board must be visibly *behind*, not blacked out, so the player trusts the state is preserved). Resume = `button.primary` from `components`; Restart/Quit = secondary (outline only). Title in `typography.display`, `typography.case` applied.

**Interaction.** Resume is in Z3 or the panel's bottom (closest to the thumb); Android back = Resume; tap-outside = Resume. Quit requires a confirm popup if progress ≥ 1 move. Entering pause takes `base` ms; the timer visibly stops *before* the panel appears (freeze digits on frame 1).

**Anti-patterns.** "Continue" wording reused for Resume (clashes with the paid continue); a shop CTA inside pause during timed modes; toggles that resume the game when tapped; Quit next to Resume at the same visual weight.

**QA.**
- [ ] Resume is the only filled primary button.
- [ ] Constraint value displayed in the panel matches the HUD value under the scrim.
- [ ] Scrim between 55 and 70 % (sample a board pixel).
- [ ] Panel radius ≥ button radius and ≤ 28 dp.

### 3.4 Win screen

**Purpose.** Reward, show what was earned, and move the player to the next level in two taps or fewer.

**Hierarchy.** 1 Stars / grade (earned-stars animation) → 2 "Level N complete" → 3 Score + best → 4 Rewards earned (coins, items) → 5 Primary CTA "Next" → 6 Secondary (Replay, Map) → 7 Optional bonus (double via ad, chest).

**Mandatory.** Stars or grade; score; rewards with the currency icon used in the HUD; Next CTA; a path back to the map.

**Optional.** Leaderboard rank delta; mission progress ticks (max 2 lines); social share; "x2 reward" rewarded ad (must be a separate, honest button).

**Visual rules.** Panel = popup radius; the celebration layer (confetti, rays) renders behind the panel content but over the scrim; rays rotate ≤ 6°/s. Stars 48–64 dp each, gap 8 dp, 3rd star centred and 12 % larger if the style uses a crown layout. `motion.class` tiers: `static` → stars appear instantly; `snappy` → 150 ms each, 100 ms stagger; `soft`/`bouncy` → 300 ms each with overshoot, 180 ms stagger; `dramatic` → 450 ms each, 250 ms stagger, flash 80 ms. Reward chips use `reward` palette slot; coin fly to the HUD counter completes within 1 s.

**Interaction.** Next is a 56 dp tall full-width primary button at the panel bottom; tap anywhere during the star animation skips to the final state (never skips the *screen*). The rewarded-ad bonus button is *not* the primary and shows the ad icon.

**Anti-patterns.** Reward popup that hides the completed board state entirely before the player saw the last match (delay the popup ≥ 600 ms after the last match effect); "Next" that triggers an interstitial without warning on the first 3 levels; x2 ad button styled as primary and Next as ghost; confetti over the buttons blocking hit tests.

**QA.**
- [ ] Next is the single primary and sits at the panel bottom.
- [ ] Stars count matches the score threshold shown (if thresholds shown).
- [ ] Currency icon identical (same asset) to the HUD icon.
- [ ] Celebration particles do not overlap button labels in the captured frame after 900 ms.

### 3.5 Lose / out-of-moves screen (continue offer rules)

**Purpose.** Tell the player why they lost, offer a *fair* continue, and keep retry one tap away.

**Hierarchy.** 1 Reason ("Out of moves" / "Time's up") → 2 Objective status (e.g. "3 of 8 collected") → 3 Continue offer (price + what you get) → 4 Retry → 5 Map/quit.

**Mandatory.** Reason; progress toward objective; a free path (Retry) at the same hit size as the paid path; price in the real currency with the current balance next to it.

**Optional.** Rewarded-ad continue (clearly labelled with ad icon); booster suggestion for next attempt; "lives" counter if the game uses lives.

**Continue offer rules.**
1. Scrim ≤ 60 % — the board stays visible so the player can judge whether continuing is worth it.
2. The paid button states the exact exchange: "+5 moves · 900 coins". Never "Continue" alone.
3. The decline path is a real button (≥ 48 dp, label "Retry" or "Give up", contrast ≥ 4.5:1), not an "x" in the corner only, and not placed where a stray tap from the lost-move area lands (keep ≥ 24 dp from the last board tap zone).
4. No artificial countdown on the decision. If the design insists on one (live-ops pressure), minimum 10 s, no price change when it expires, and expiry = decline.
5. Max 1 paid continue prompt per attempt. A second failure shows Retry as primary and the paid offer as secondary.
6. Insufficient balance → the button reads "Get coins" and routes to the shop; it never charges premium currency implicitly or triggers a store sheet without an intermediate screen.
7. Rewarded-ad continue, when present, is a separate button with the ad glyph and the words "Watch ad"; never auto-plays.
8. Price text uses `typography.body` bold ≥ 14 dp; it is not inside the button's icon badge.

**Visual rules.** Same panel style as Win (radius, stroke, shadow) — only the header art changes (sad mascot per `illustration.character_style`). Danger hue used only on the reason line, not on the retry button. No celebration layer.

**Interaction.** Android back = decline. Buttons are vertically stacked: paid continue (if any) → Retry → Map; or, if retry is primary (rule 5), Retry on top.

**Anti-patterns.** Dark-pattern continue buttons: confirmshaming labels ("No, I like losing"), decline rendered at < 3:1 contrast, "x" that accepts the purchase, the price revealed only on the confirmation sheet, pre-selected "use booster" checkboxes, timers under 10 s. Also: lose popup shown before the last tile's fail animation finishes (< 400 ms after loss).

**QA.**
- [ ] Price and balance visible on the same panel.
- [ ] Decline button width ≥ 50 % of the paid button width and ≥ 48 dp tall.
- [ ] No countdown, or countdown ≥ 10 s.
- [ ] Scrim ≤ 60 % (sample a board pixel).
- [ ] Reason text uses `danger` hue; Retry button does not.

### 3.6 Level select (map vs list)

**Purpose.** Show where the player is, what is next, and what is locked, in a scroll that always lands on the current level.

**Choose the layout.**

| Criterion | Map (path + nodes) | List / grid |
|---|---|---|
| Content | ≥ 100 levels, themed worlds, decorative world art budget exists | ≤ 60 levels or chapter-based (word games, sorting) |
| Scroll | vertical only, 1 node per 110–140 dp of travel; current node auto-centred on entry | vertical grid 4–5 columns, cell 64 dp, chapter headers sticky |
| Node | 56–64 dp circle/blob per `shape.silhouette`; number 16 dp bold; stars 12 dp under the node | 56 dp square per `radius_class`, number 16 dp, stars inside |
| Current | +15 % scale, pulse per `motion.class`, mascot or pin above | accent outline x 2 + "Play" caption |
| Locked | desaturated −60 % + padlock glyph; no number | same |
| Completed | star tier shown; node fill `success` or chapter colour | same |

**Hierarchy.** 1 current level node → 2 Play CTA (Z3, sticky) → 3 next locked node → 4 world/chapter title → 5 side rail (events, chest progress) → 6 bottom nav.

**Mandatory.** Current level visually unique; Play button in Z3 that opens the current level's pre-level sheet (objective + booster pick) — one tap to start; lives/energy indicator if used.

**Optional.** Chapter completion chest; friends' avatars on nodes; event portal; daily-bonus hook.

**Visual rules.** Nodes use `rendering.shading` and `shape.silhouette` (a `rounded-blob` silhouette gives blob nodes, `geometric` gives circles). Path stroke width = `shape.outline.width` + 2 dp, dashed for not-yet-reached segments. Locked nodes do **not** use the `disabled` opacity from `semantic.state` alone (too subtle on art backgrounds) — they also drop saturation and gain a padlock.

**Interaction.** Tap on current or completed node = pre-level sheet; tap on a locked node = toast "Complete level N first" (no shake longer than `fast` ms). Map scroll is vertical; horizontal drag is ignored (reserved for OS back). "Jump to current" button appears after the player scrolls > 1 screen away.

**Anti-patterns.** Current level not centred on entry; Play button whose level number differs from the highlighted node; locked nodes tappable with a shop upsell; map world art with text contrast < 4.5:1 for node numbers; nodes under the bottom nav.

**QA.**
- [ ] Current node is within the middle 50 % of the viewport on first paint.
- [ ] Play CTA label includes the level number and matches the highlighted node.
- [ ] Locked vs completed vs current are distinguishable in greyscale.
- [ ] Node numerals ≥ 4.5:1 contrast against the node fill.

### 3.7 Home / lobby

Many casual games merge Home with Level select (map-as-home). When separate:

**Purpose.** One primary action (Play), the currency wallet, and the live-ops entry points without looking like a billboard.

**Hierarchy.** 1 Play (level N) → 2 wallet (coins, premium, lives) → 3 daily reward hook (if unclaimed) → 4 events (max 2 cards) → 5 mascot / scene → 6 bottom nav.

**Mandatory.** Play CTA (Z3, 56 dp tall, full-width minus 32 dp gutters, `button.primary`); wallet in Z1 with "+" only if the shop is open; settings gear (Z1, 48 dp); bottom nav (Z4) or equivalent.

**Optional.** Daily-reward button with red-dot badge; event cards; season pass bar; friends; news.

**Visual rules.** Scene art respects `illustration.character_style`; mascot never overlaps the Play button. Max **3** promotional surfaces visible at once (event card, pass bar, offer badge) — the fourth goes behind a tab. Badges (red dot) 10 dp with 1.5 dp outline matching `outline.color_rule`.

**Interaction.** Play is reachable without scrolling on 360x640 dp. No auto-opening offer popups on the first 3 sessions; afterwards at most 1 auto popup per session, opened ≥ 1 s after the lobby is interactive.

**Anti-patterns.** Two primary buttons (Play + Buy); auto-popups stacking (offer → daily → event); wallet "+" during the first session before the shop is unlocked; bottom nav with > 5 items; nav icons without labels.

**QA.**
- [ ] Exactly one filled primary button above the fold.
- [ ] ≤ 3 promotional surfaces visible.
- [ ] Bottom nav has 3–5 items, each labelled, active item uses the accent slot.
- [ ] Mascot bounding box does not intersect the Play button.

### 3.8 Settings

**Purpose.** Audio, haptics, notifications, language, account, support, legal — with no gameplay or commerce inside.

**Hierarchy.** 1 Sound / Music / Vibration toggles → 2 Notifications → 3 Language → 4 Account (cloud save, link) → 5 Support, Privacy, Terms, Restore purchases → 6 Version string.

**Mandatory.** Three toggles with icons; a Close/Back; Restore purchases (iOS requirement if IAP exists); privacy link; version.

**Optional.** Reduced-motion toggle (in addition to honouring the OS setting); colour-blind mode; left-hand mode (mirrors Z3 controls); data deletion request.

**Visual rules.** Toggles follow `radius_class` (pill for `lg`+, rounded-rect for `sm`/`md`). Row height 56 dp; icons 24 dp from `iconography.style`. Uses `typography.body` only; display face only for the title. No `rendering.highlight` gloss on toggles.

**Interaction.** Toggles take effect immediately with a 1-frame audio sample for Sound. Account actions (sign out, delete) open a confirm popup (3.5-style decline rules apply in reverse: the destructive action is the secondary).

**Anti-patterns.** Shop entry inside settings; "Rate us" as the first row; toggles that look like buttons; legal links hidden behind scroll on a non-scrolling panel.

**QA.**
- [ ] Sound/Music/Vibration are the first three rows.
- [ ] Restore purchases present when the profile lists commerce components.
- [ ] Version string visible at the bottom.

### 3.9 Shop

**Purpose.** Sell currency, boosters and offers with honest prices, consistent price tags, and nothing that pretends to be gameplay.

**Hierarchy.** 1 wallet (sticky top) → 2 featured / limited offer (max 1 hero card) → 3 currency packs (grid 2–3 cols) → 4 boosters → 5 remove-ads → 6 restore purchases link.

**Mandatory.** Wallet matching the HUD icons; price tag component (`commerce.price-tag`) identical on every item; item content list (what you get) visible without expanding; "Best value" / "Popular" badge rules (max one of each); timer on limited offers with real expiry.

**Optional.** First-purchase bonus; bundle comparison; daily free gift (treated as a reward, not a sale).

**Visual rules.** Item cards use `radius_class` base radius, `rendering.shading`, `rendering.shadow`; hero card may use `rendering.highlight` and a ribbon. Price tag: pill, fill `semantic.color.primary` or a dedicated `commerce` slot if the palette defines one; real-money prices in `typography.body` bold ≥ 16 dp, currency prices show the coin icon at 16 dp + number. "Best value" badge max 1; "Popular" badge max 1; badge is a ribbon or corner chip 20 dp tall.

**Interaction.** Tapping a pack opens the platform purchase sheet directly (no intermediate confirm for real money — the store sheet *is* the confirm); currency-priced items get a confirm popup only when the price ≥ 20 % of the balance. Limited-offer timers count down live; when expired the card disappears or greys with "Expired" — never re-arms silently.

**Anti-patterns.** Fake timers that reset; "x" close that is < 44 dp or appears after a delay; prices in different fonts/sizes across cards; pack content hidden behind an info icon; currency icons that differ from the HUD; a "free" badge on an item that costs premium currency; shop reachable from inside a kids-learning activity.

**QA.**
- [ ] All price tags identical in size, font, radius (overlay two cards: no difference).
- [ ] ≤ 1 "Best value" and ≤ 1 "Popular".
- [ ] Close button ≥ 44 dp, visible at t = 0.
- [ ] Wallet icons identical to HUD icons.
- [ ] Limited offer shows a visible expiry time (hh:mm:ss or "ends in 2 d").

### 3.10 Rewards

Shared rules for every reward surface, then per mechanic.

**Shared.** Rewards live on the `reward` palette slot (plus rarity ramp if defined); reward items use `reward.card` with the same radius/stroke as shop items; claiming is one tap; a claimed item visibly moves to the wallet (coin fly ≤ 1 s, counter settles ≤ 1 s); every reward popup can be closed within 2 s of opening (skip for the animation, close for the popup); the board/scene behind stays at ≤ 70 % scrim. Celebration tier from `motion-direction.md` depends on rarity, never on the mechanic (a common item from a chest gets the small tier).

**Daily login (calendar).**
- Hierarchy: today's reward (highlighted, 1.1 scale) → Claim CTA → the week/month grid → streak note.
- Grid: 7 cells per row, 48 dp cells, day 7 cell 1.5x wide with the big reward; claimed = check overlay + −40 % saturation; today = accent outline x 2 + pulse; future = normal.
- Rules: Claim is primary; "x2 with ad" secondary; auto-open at most once per calendar day, ≥ 1 s after lobby interactive; missing a day does **not** reset progress on the calendar (streak mechanics live in Streak, not here).
- QA: today's cell identifiable in greyscale; Claim button is the only primary; 7-cell rows aligned to an 8 dp grid.

**Spin wheel.**
- Wheel ≥ 260 dp diameter, 6–8 segments, segment labels ≥ 12 dp bold with icon 24 dp; pointer at 12 o'clock, 24 dp, `outline.width` stroke.
- Spin button in Z3; cost shown on the button ("Spin · 1 free" / "Spin · 50 coins" / "Spin · watch ad").
- Motion: spin ≥ 3 full turns, 2.5–4 s total, ease-out (`Curves.easeOutQuart` / `Ease.OutQuart`); the result segment lands fully under the pointer (no half-segment ambiguity); ticking sfx per segment edge; result popup appears ≥ 300 ms after stop.
- Rules: no "near-miss" animation that stops on a jackpot and then creeps to the next segment; rates visible if real money can buy spins; not used in kids learning.
- QA: pointer centred on the winning segment in the final frame; segment count 6–8; spin cost visible before tap.

**Treasure chest.**
- Chest sprite 120–160 dp; rarity frame uses the rarity ramp; "Open" primary; key/cost shown on the button.
- Open sequence: shake (`fast` x 2) → lid pop (`base`) → items fly out in a 180 ms stagger (max 5 items visible; "+3 more" overflow chip) → items settle into a 3-column grid with rarity frames → Collect/OK.
- Rules: skippable after 1.5 s (tap = reveal all); each item uses `reward.card`; lock icon on the chest if a key is needed, with the key count next to it.
- QA: all items visible with rarity frame before the Collect button is enabled; chest art uses the same `rendering.shading` as tiles.

**Missions (daily/weekly).**
- `reward.mission-item` row 72 dp: icon 40 dp → title (14 dp) + progress bar (6 dp) + "3/5" → reward chip (coin icon + amount) → Claim/Go button 80 x 40 dp.
- States: in-progress (Go), claimable (Claim, primary, row gets a 1.02 scale pulse once on entry), claimed (check, −40 % saturation, moves to bottom). Max 5 visible per tab; reset timer at the top ("Resets in 5 h 12 m").
- Rules: "Go" deep-links to the exact screen or level mode; never to the shop. Claim is instant (no confirm).
- QA: rows share identical heights; claimable rows above in-progress rows; reward chip uses the HUD coin icon.

**Streak.**
- Streak counter (flame or badge per `illustration.character_style`) with day count 20 dp bold; a 7-dot track; "streak freeze" item count if used.
- Rules: losing a streak is communicated *before* it happens (banner "Play today to keep your 6-day streak") and *after* with a recovery offer at most once; the recovery offer follows continue-offer rules (price visible, decline real).
- QA: streak day count on lobby and in the reward popup match; freeze count visible if the mechanic exists.

### 3.11 Profile

**Purpose.** Identity, progress, achievements, and account/social actions.

**Hierarchy.** 1 avatar + name + level/trophies → 2 key stats (max 4 tiles: levels, stars, best score, play days) → 3 achievements/badges grid → 4 collection (stickers/characters) → 5 account & social (edit, friends, link, sign out).

**Mandatory.** Avatar (editable, 80–96 dp, frame per `shape.silhouette`); display name with edit affordance; at least one progress stat; account link status.

**Optional.** Frames/titles shop link; leaderboard rank; share card.

**Visual rules.** Stat tiles use base radius, `typography.display` for numbers (24 dp), body for labels (12 dp); achievement badges 56 dp in a 4-column grid; locked badges −60 % saturation + padlock. Rarity ramp identical to rewards and shop.

**Interaction.** Name edit is a text field inside a popup, with a profanity-safe default; avatar picker is a sheet with 64 dp items; sign out needs confirm.

**Anti-patterns.** Shop upsell as the first row; stats that differ from Home (e.g. different star count); name field accepting > 16 characters without truncation plan.

**QA.**
- [ ] Avatar ≥ 80 dp and has an edit affordance.
- [ ] Stat values equal those shown on Home/Win screens in the same capture session.
- [ ] Badge grid aligned to the 8 dp grid, 4 columns on 360 dp.

### 3.12 Tutorial / first run

**Purpose.** Teach one mechanic per step, on the real board, with no ability to get lost and no commerce.

**Hierarchy.** 1 spotlighted target (tile/button) → 2 one-line instruction (≤ 60 characters, `typography.body` 16 dp on a plate) → 3 pointing hand / mascot → 4 Skip (after step 2, top corner, 44 dp, low emphasis).

**Mandatory.** Spotlight mask (scrim 60–70 % with a cut-out 8 dp larger than the target); input locked to the target (taps elsewhere do nothing, no error sound); instruction plate anchored ≥ 16 dp from the target and never covering the board rows the player needs; progress dots if > 3 steps.

**Optional.** Mascot speech bubble; voice-over (mandatory for kids learning); replay from settings.

**Visual rules.** Hand cursor 48 dp, follows `iconography.style`; tap gesture animation = 1.0 → 0.85 → 1.0 over `base` ms, loop every 1.2 s; drag gesture = hand moves A→B over `slow` ms, loop. For `motion.class: static`, the hand still animates (it is instructional, exempt from reduced motion, but respects the OS setting by switching to a static arrow).

**Interaction.** Step advances only on the correct action; the tutorial never times out; Skip hides after 3 levels; no popups, offers, ads or rewards until the tutorial ends (one small-tier celebration at the end is allowed). The tutorial uses the same tile state visuals as gameplay (§3.2) — it is a QA failure if tutorial "selected" differs from gameplay "selected".

**Anti-patterns.** Instruction text over the board; spotlight cut-out tighter than the target (clips the outline); forced tutorial for experienced-player features on every new mechanic; multi-paragraph text; mascot covering the next target; shop/booster promo during tutorial.

**QA.**
- [ ] Cut-out is 8 ± 2 dp larger than the target on each side.
- [ ] Instruction ≤ 60 characters, ≥ 16 dp, on a plate with ≥ 4.5:1 contrast.
- [ ] Hand does not overlap the target's centre 50 %.
- [ ] No currency, shop or ad element visible in tutorial captures.

---

## 4. Cross-screen consistency matrix

**Identical** = same component instance / same token values on every screen where it appears; any difference is a finding. **May vary** = the listed variations are allowed when recorded in `intentional_exceptions` with the given reason; anything else is a finding.

| Component / attribute | Must be identical across | May vary (allowed intentional variation → reason) |
|---|---|---|
| Currency icon + numeral style (`hud.currency`) | HUD, lobby, shop, win, lose, rewards, profile | size: 16 dp in HUD vs 20 dp in shop wallet → wallet is a focus element there |
| Primary button (`button.primary`: radius, stroke, shading, label case, height 56 dp) | all screens | width: full-width in popups vs 160 dp in lobby → layout; label text only |
| Secondary button (outline only) | all screens | none |
| Popup panel (popup radius, stroke, shadow, close button 44 dp top-right) | pause, win, lose, confirm, offer, rewards, settings | header art (mascot pose/colour) → emotional tone; scrim opacity 55–70 % |
| Tile state visuals (§3.2 deltas) | gameplay, tutorial, hint overlay, shop booster preview, level pre-sheet | size: shop preview may scale to 0.75x → thumbnail; never change outline ratio |
| Star / grade asset | HUD objective, win, level nodes, profile stats | size: 12 dp on map nodes, 48–64 dp on win → hierarchy |
| Price tag (`commerce.price-tag`) | shop, lose continue, hint button, spin button, offers | fill: real-money vs soft-currency may use two defined slots → distinguish money from coins (must be documented) |
| Progress bar (`progress.bar`: height, radius, fill slot) | HUD timer, missions, level pre-sheet, season pass | height: 6 dp in lists vs 8 dp in HUD timer → glanceability; colour: timer may switch to `warning` below 20 % and `danger` below 10 % with audio/haptic cue |
| Icon family (`iconography.style`, stroke) | all | none (mixing filled/outline is a finding) |
| Display font and case (`typography.display`, `typography.case`) | all titles | decorative display allowed to break case rule for the game logo only |
| Rarity colour ramp | gacha, chest, inventory, shop, profile | none |
| Red-dot badge | nav, lobby buttons, missions tab, shop | none |
| Close "x" (position top-right, 44 dp, same glyph) | every dismissible popup | hidden on blocking confirms where buttons are the only exit → safety |
| Bottom nav (`nav.bottom-bar`) | lobby, levels, shop, events, profile | hidden on gameplay, tutorial, full-screen popups → focus |
| Scrim opacity | pause 55–70 %, win/lose ≤ 60 %, rewards ≤ 70 %, confirm 60 % | tutorial 60–70 % with cut-out → spotlight |
| Toast (`feedback.toast`) position (above Z3, 16 dp gutters) and duration (2 s) | all | duration 4 s for error toasts with action → readability |
| Mascot / character style (`illustration.character_style`) | lobby, win, lose, tutorial, shop hero | pose and expression → tone; never redraw in a different rendering |
| Motion class + duration scale | all | reward tier escalation per `motion-direction.md`; gameplay feedback may use `fast` only |
| Safe-area insets | all | none |
| Outline colour rule (`shape.outline.color_rule`) | all | none |
| Radius class relationships (§0 table) | all | pixel shading forces `none` on tiles → art style |

Reviewer procedure: capture HUD, lobby, shop, win, lose, one reward popup, one tile-selected gameplay frame; overlay the shared components at the same scale; any pixel-level difference in radius, stroke, icon glyph or fill slot that is not in `intentional_exceptions` is a `component.duplicate-implementation` or `radius.off-scale` finding for `visual-audit`.

---

## 5. Genre x screen applicability

| Screen | tile-match | match-3 | merge | sorting | word | idle | kids | anime RPG |
|---|---|---|---|---|---|---|---|---|
| Gameplay HUD | timer+hint+shuffle | moves+objectives+boosters | energy+orders | undo+add+hint | coins+hint+shuffle | currency+rate | progress dots only | skills+HP+speed |
| Board states | full set | full set + specials | locked/generator/drag | lift-select | wheel + grid | tap-collect | drag tolerance 1.5x | n/a (battle) |
| Pause | yes | yes | no (no clock) | yes | yes | no | exit gate | yes (battle) |
| Win | yes | yes | order complete toast | yes | yes | prestige | sticker celebration | stage result |
| Lose + continue | timer/no-pair | out-of-moves | no | no-moves (undo offer) | no (hint offer) | no | never | defeat → retry/upgrade |
| Level select | map or list | map | n/a (single board) | list | chapter list | n/a | activity carousel | stage map |
| Home/lobby | map-as-home | map-as-home | board-as-home | list-as-home | chapter-as-home | scene-as-home | activity hub | lobby with character |
| Settings | yes | yes | yes | yes | yes | yes | parent area | yes |
| Shop | yes | yes | yes | yes | yes | yes | parent-gated, no chance items | yes + gacha rates |
| Rewards | daily, wheel, chest, missions, streak | all | daily, chest, missions | daily, missions | daily, missions, streak | offline earnings, chest | stickers only | daily, missions, gacha, chest |
| Profile | light | full | light | light | light | light | none (parent) | full + collection |
| Tutorial | 3 steps | 4–6 steps | 3 steps | 2 steps | 2 steps | 2 steps | voice-led every activity | 6–10 steps staged |

---

## 6. Reviewer quick checklist (all game screens)

- [ ] One filled primary button per screen (popups included).
- [ ] Board/scene visible behind every popup (scrim ≤ 70 %; lose ≤ 60 %).
- [ ] Constraint counter (moves/timer) ≥ 18 dp numerals on a plate.
- [ ] Shared components overlay-identical across captures (§4).
- [ ] Every price visible before tap; every decline button real (≥ 48 dp, ≥ 4.5:1).
- [ ] No countdown < 10 s on any purchase decision.
- [ ] Tile selected/hinted/blocked distinguishable in greyscale.
- [ ] Reward effects never cover button labels after 900 ms.
- [ ] Bottom nav absent on gameplay; present and labelled elsewhere.
- [ ] Cell pitch ≥ 40 dp or recorded exception; nothing < 36 dp.
- [ ] Tutorial uses gameplay tile states unchanged.
- [ ] Nothing commercial in kids-learning activities or tutorials.
