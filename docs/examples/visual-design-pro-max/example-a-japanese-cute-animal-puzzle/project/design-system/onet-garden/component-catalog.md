<!-- generated-by: visual-direction vd.py 1.0.0; profile-hash: d350c253757e -->
# Component Catalog — Onet Garden

Filtered for `product.kind = game` (rows whose Applies To is `game` or `both`; 51 components) and style `japanese-cute-puzzle`.
Order of authority per component: **Tokens (authoritative)** from `tokens.json` → catalog rule (structure, variants, states) → **Style modifier (reference)**, the catalog/style prose. Where prose and tokens disagree (e.g. a pill vs a 16 radius, 2px vs 3px outline), the token value wins; record a deliberate deviation as an intentional exception, never by editing the prose (CC-11).
Rows specific to this product kind are rendered in full; shared rows (`Applies To = both`) are rendered compact — their full visual rules, variants, interaction, platform notes, anti-patterns and QA live in `data/component-catalog.csv` of the `visual-direction` skill. Style modifiers are printed once per group, naming the components they apply to.

Platform notes are filtered for stack `flutter-flame`.

## action

- **Style modifier (reference) for `button.primary`, `button.secondary`, `button.icon`, `button.destructive`:** Pill primary 56px tall, fill = primary, 3px darker-shade outline, 4px hard bottom shadow, label 18px 700 centred with 1px darker text shadow; secondary = surface fill with primary outline; pressed = translate 3px down and drop shadow in 90ms

### `button.primary` — Primary Button

- **Tokens (authoritative, `component.button.primary`):** radius=16 · height=56 · outlineWidth=3 · outlineColor=#972743 · shadow=0 4px 0 #972743, 0 8px 12px rgba(46, 42, 50, 0.14) · paddingX=24 · fontSize=22 · minWidth=160
- **Purpose:** The one action the screen wants taken; at most one per view
- **States:** default | hover (semantic.state.hover) | pressed (semantic.state.pressed: translateY offsetY, bg primaryPressed) | focus (semantic.state.focus ring) | disabled (semantic.state.disabled opacity, no shadow) | loading (primitive.opacity.loading, spinner replaces label, width locked)
- **Code reuse hint:** one Button component with variant prop {primary,secondary,destructive,icon}
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#button.primary`

### `button.secondary` — Secondary Button

- **Tokens (authoritative, `component.button.secondary`):** radius=16 · height=56 · outlineWidth=3 · outlineColor=#BA4A66 · shadow=0 2px 0 #56505E, 0 4px 6px rgba(46, 42, 50, 0.12) · paddingX=24 · fontSize=22
- **Purpose:** Alternative or lower-priority action next to a primary
- **States:** default | hover (bg component.button.secondary.bgHover) | pressed (bg bgPressed + state.pressed offset) | focus | disabled
- **Code reuse hint:** same Button component, variant=secondary
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#button.secondary`

### `button.icon` — Icon Button

- **Tokens (authoritative, `component.button.icon`):** radius=9999 · outlineWidth=3 · outlineColor=#A88655 · shadow=0 2px 0 #56505E, 0 4px 6px rgba(46, 42, 50, 0.12) · size=48
- **Purpose:** Single-icon control for close, settings, back, mute
- **States:** default | hover | pressed (scale 0.94, duration.fast) | focus | disabled | toggled
- **Code reuse hint:** Button variant=icon
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#button.icon`

### `button.destructive` — Destructive Button

- **Tokens (authoritative, `component.button.primary`):** radius=16 · height=56 · outlineWidth=3 · outlineColor=#972743 · shadow=0 4px 0 #972743, 0 8px 12px rgba(46, 42, 50, 0.14) · paddingX=24 · fontSize=22 · minWidth=160
- **Purpose:** Irreversible or data-losing action (delete, reset progress, sign out everywhere)
- **States:** default | hover (primitive.color.danger.700) | pressed (danger.800) | focus | disabled
- **Code reuse hint:** Button variant=destructive
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#button.destructive`

## board

### `board.tile` — Board Tile

- **Tokens (authoritative, `component.tile`):** radius=12 · outlineWidth=3 · outlineColor=#A88655 · shadow=0 2px 0 #56505E, 0 4px 6px rgba(46, 42, 50, 0.12) · gap=4 · minSize=48
- **Purpose:** The base playable cell; one state at a time; identical visual language in gameplay, tutorial, hint and previews.
- **Visual rules:** radius: shape.radius_class one step tighter (see game-ui-patterns section 0); stroke: shape.outline.width x0.66 (min 1dp) with shape.outline.color_rule; fill/frame: rendering.shading + rendering.highlight; shadow: rendering.shadow only if the style defines offset; face art: illustration.asset_rendering; cell pitch >=48dp, exception ladder 40-47dp recorded, never <36dp; gap <=25% of tile (soft-cel/clay) or <=12% (flat/pixel)
- **Variants:** square | rounded-blob (shape.silhouette) | hex | circle (bubble) | container (sorting) | letter (word)
- **States:** idle | selectable | selected (board.tile-selected) | matched | hinted | blocked | shuffling | drag-ghost | drop-valid | drop-invalid | cleared
- **Interaction:** Tap registers on pointer-up inside the cell; movement >12dp cancels; hit = full cell pitch (no dead gaps).
- **Platform notes:** Flutter: a Tile widget keyed by cell id, state via enum; Flame: SpriteComponent with a state machine, use priority for selected
- **Anti-patterns:** Empty cells drawn as faded tiles | blocked tiles that look like specials | ghost tiles after removal
- **QA:** Selected/hinted/blocked distinguishable in greyscale | radius and stroke ratio identical in tutorial, hint and shop preview | no tile under HUD or booster bar
- **Code reuse hint:** Single Tile component with a state enum; every other board.* component is a state of this one, not a new widget

### `board.tile-selected` — Selected Tile State

- **Tokens (authoritative, `component.tile`):** radius=12 · outlineWidth=3 · outlineColor=#A88655 · shadow=0 2px 0 #56505E, 0 4px 6px rgba(46, 42, 50, 0.12) · gap=4 · minSize=48
- **Purpose:** Make the current selection unmistakable in a still frame, on any board colour.
- **Visual rules:** outline: shape.outline.width x1.5 in semantic.color.accent; scale 1.04-1.06; shadow one step up (rendering.shadow); optional inner glow 20%; transition motion.duration_scale.fast with class easing (bouncy: easeOutBack)
- **Variants:** outline+scale (default) | lift (sorting: translate -12dp, no outline) | outline-only (static class / reduced motion)
- **States:** entering | selected | deselecting (reverse, motion.duration_scale.fast)
- **Interaction:** Tap the selected tile again = deselect; tap a non-matching tile = move selection (no error state); tap a matching tile = board.match-effect.
- **Platform notes:** Render the selected tile above neighbours (Flame priority +1, Unity sibling index last, Web z-index) so the scaled outline is not clipped
- **Anti-patterns:** Colour-only selection | selected pulse that never stops | selection outline clipped by neighbouring tiles
- **QA:** Outline width measured = 1.5x idle | identifiable within 1s by an uninformed reviewer | not the same hue as hinted (warning)
- **Code reuse hint:** State of board.tile; shares accent outline token with nav.level-node current state

### `board.match-effect` — Match / Clear Effect

- **Tokens (authoritative, `component.tile`):** radius=12 · outlineWidth=3 · outlineColor=#A88655 · shadow=0 2px 0 #56505E, 0 4px 6px rgba(46, 42, 50, 0.12) · gap=4 · minSize=48
- **Purpose:** Acknowledge a successful match with a 1-frame flash and a pop that scales with combo tier.
- **Visual rules:** flash white 60% 1 frame; pop scale 1.15->0 or fade (motion.duration_scale.base); connection line for tile-match genres: shape.outline.width + 1dp in semantic.color.accent; particles per motion-direction tiers (small 20, medium 60, jackpot 150 on mid devices); particle colours from the tile's palette, not random
- **Variants:** pop | line+pop (onet) | explode (match-3 special) | fly-to-objective (collect genres) | fade (static class / reduced motion)
- **States:** playing | combo-escalated (caption + rays) | skipped
- **Interaction:** Input locked for the affected cells until onComplete; other cells stay tappable only in genres without cascades.
- **Platform notes:** Flutter: AnimationController per match batch; Flame: SequenceEffect + ParticleSystemComponent(count capped)
- **Anti-patterns:** Tiles vanishing instantly with no acknowledgement frame | effect longer than 250ms blocking the next move | particles over the HUD numerals
- **QA:** Flash visible in a 60fps capture | pop completes <=250ms | particle count <= tier cap | counter final value by frame 15
- **Code reuse hint:** EffectSequencer shared with reward.* for tiers; particle presets by tier in tokens

### `board.hint-highlight` — Hint Highlight

- **Tokens (authoritative, `component.tile`):** radius=12 · outlineWidth=3 · outlineColor=#A88655 · shadow=0 2px 0 #56505E, 0 4px 6px rgba(46, 42, 50, 0.12) · gap=4 · minSize=48
- **Purpose:** Point at one valid move with a pulsing outline and optional hand without disturbing the rest of the board.
- **Visual rules:** outline shape.outline.width x1.5 in semantic.color.warning; pulse 2 cycles of motion.duration_scale.slow; optional hand 48dp per iconography.style; arrow/line for pairs uses accent at shape.outline.width + 1dp
- **Variants:** outline-pulse | hand+outline | path-line (tile match)
- **States:** pulsing | paused (a tile is selected) | stopped (first user tap) | static (reduced motion: steady outline)
- **Interaction:** Stops on the first tap anywhere on the board; never consumes a second hint while active.
- **Platform notes:** Flame priority above tiles
- **Anti-patterns:** Hint highlighting a tile hidden under the HUD | pulse continuing after selection | same hue as selected
- **QA:** Hue = warning slot, distinct from accent | stops on first tap | target fully visible
- **Code reuse hint:** State of board.tile + shared pulse effect

### `board.shuffle-overlay` — Shuffle / Cascade Lock Overlay

- **Tokens (authoritative, `component.tile`):** radius=12 · outlineWidth=3 · outlineColor=#A88655 · shadow=0 2px 0 #56505E, 0 4px 6px rgba(46, 42, 50, 0.12) · gap=4 · minSize=48
- **Purpose:** Make the input-locked state visible while the board re-lays out.
- **Visual rules:** tiles fade to 50% then reposition then fade back (total <= 2x motion.duration_scale.slow); HUD shows a 'Shuffling...' plate (HudPlate) centred; boosters dimmed to 40%; no scrim over the board
- **Variants:** shuffle | cascade/gravity | board-reset (restart)
- **States:** locking | animating | unlocking (onComplete) | instant (static class / reduced motion: 150ms crossfade)
- **Interaction:** All board taps ignored (no error sound); pause remains tappable.
- **Platform notes:** Flutter: AnimationStatus.completed; Flame: SequenceEffect onComplete
- **Anti-patterns:** Tappable tiles mid-shuffle | timer still running during shuffle in timed modes without the plate | overlay darker than 50%
- **QA:** A tap during the sequence has no effect | 'Shuffling' plate visible | <=700ms total for bouncy class
- **Code reuse hint:** EffectSequencer + HudPlate

## commerce

### `commerce.shop-item` — Shop Item Card

- **Tokens (authoritative, `component.card`):** radius=24 · borderWidth=3 · shadow=0 2px 0 rgba(46, 42, 50, 0.25), 0 4px 6px rgba(46, 42, 50, 0.12) · padding=20 · gap=12
- **Purpose:** Sell a pack/bundle/booster with contents visible, one price tag, and at most one badge.
- **States:** idle | pressed (T0) | purchasing (price tag shows spinner) | owned (remove-ads: check + disabled) | limited (expiry chip, greys on expiry) | sold-out
- **Code reuse hint:** ShopCard = Card base + reward
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#commerce.shop-item`

### `commerce.price-tag` — Price Tag

- **Tokens (authoritative, `component.card`):** radius=24 · borderWidth=3 · shadow=0 2px 0 rgba(46, 42, 50, 0.25), 0 4px 6px rgba(46, 42, 50, 0.12) · padding=20 · gap=12
- **Purpose:** Display a price (real money or in-game currency) in one unmistakable component reused on every buy/continue/hint surface.
- **States:** idle | pressed (large only) | insufficient (danger outline + 'Get coins' routing) | loading (store price pending: skeleton, never '0') | discounted
- **Code reuse hint:** PriceTag component used by hud
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#commerce.price-tag`

## container

- **Style modifier (reference) for `panel.container`:** Rounded panel radius 28px, surface fill, 4px outline in secondary-darker, ribbon title plate overlapping the top edge by 50%; close button circular 44px top-right; entrance scale 0.85 to 1 with overshoot 1.04 in 260ms

### `card.default` — Card

- **Tokens (authoritative, `component.card`):** radius=24 · borderWidth=3 · shadow=0 2px 0 rgba(46, 42, 50, 0.25), 0 4px 6px rgba(46, 42, 50, 0.12) · padding=20 · gap=12
- **Purpose:** Groups one entity (item, level, transaction) with its actions
- **States:** default | hover (interactive only) | pressed (interactive only, state.pressed) | selected | disabled
- **Code reuse hint:** Card(variant, selected, onTap) wrapper
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#card.default`

### `panel.container` — Panel

- **Tokens (authoritative, `component.card`):** radius=24 · borderWidth=3 · shadow=0 2px 0 rgba(46, 42, 50, 0.25), 0 4px 6px rgba(46, 42, 50, 0.12) · padding=20 · gap=12
- **Purpose:** Full-width section container on a screen (settings group, level-select panel, shop section)
- **States:** default | collapsed | expanded | disabled
- **Code reuse hint:** Panel(title, collapsible) composes list
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#panel.container`

## data

### `list.item` — List Item

- **Purpose:** Row in a list: leading visual, primary + secondary text, trailing value or control
- **States:** default | hover | pressed (bg primitive.color.neutral.100) | selected (bg primitive.color.brand.50, leading check) | disabled | swiped (reveals actions, app)
- **Code reuse hint:** ListItem(leading, title, subtitle, trailing, onTap)
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#list.item`

## feedback

### `feedback.toast-app` — Toast

- **Purpose:** Brief non-blocking confirmation or notice, optionally with one action
- **States:** entering (slide up duration.base easing.enter) | visible (4 s info, 6 s with action, 8 s error) | leaving (fade duration.fast) | paused (hover/focus holds timer)
- **Code reuse hint:** single Toast host at app root
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#feedback.toast-app`

### `feedback.toast` — Toast / Inline Banner

- **Purpose:** Short non-blocking message (e.g. 'Complete level 12 first', 'Not enough coins', 'Saved').
- **States:** entering (slide 16dp + fade, motion.duration_scale.base) | visible (2s info / 4s error) | exiting (fade 150ms) | queued (max 1 visible, next waits)
- **Code reuse hint:** Toast component shared app/game
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#feedback.toast`

### `progress.bar` — Progress Bar

- **Tokens (authoritative, `component.progress`):** radius=9999 · height=16 · outlineWidth=3 · outlineColor=#FFDDAC
- **Purpose:** Linear fill for timer, mission progress, level pre-sheet objectives, season pass and loading.
- **States:** empty | partial | full (optional 1-frame flash) | warning | danger | indeterminate (loading only)
- **Code reuse hint:** ProgressBar component reused by hud
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#progress.bar`

### `progress.stars` — Star Rating

- **Tokens (authoritative, `component.progress`):** radius=9999 · height=16 · outlineWidth=3 · outlineColor=#FFDDAC
- **Purpose:** Show 0-3 earned stars for a level consistently on win, map nodes, pre-level sheet and profile.
- **Visual rules:** star glyph from one asset in two states (earned: semantic.color.reward fill + shape.outline.width stroke; empty: semantic.color.border fill at 60%); sizes 12dp (node), 20dp (pre-sheet), 48-64dp (win); gap = 1/6 of size; optional crown layout (middle star 12% larger, raised 4dp); shading: rendering.shading on the 48dp+ size only
- **Variants:** 3-star | 5-star (anime RPG rarity) | crown-layout | score-threshold with labels
- **States:** empty | earned-1/2/3 | animating (win: stagger per motion.class) | new-best (sparkle once, small tier)
- **Interaction:** Non-interactive; on the pre-level sheet tapping stars shows thresholds.
- **Platform notes:** Flutter: Row of star widgets with a shared asset; Flame: SpriteComponent x3
- **Anti-patterns:** Different star glyphs between win and map | emoji stars | earned/empty distinguishable only by colour
- **QA:** Same glyph asset across win/map/profile captures | earned vs empty distinguishable in greyscale | sizes from {12,20,48,64}
- **Code reuse hint:** StarRow component; win animation via EffectSequencer

## hud

- **Style modifier (reference) for `hud.score`, `hud.timer`, `hud.moves`, `hud.currency`, `hud.hint-button`, `hud.undo-button`, `hud.pause-button`, `hud.booster-slot`:** Top bar 64px with coin/life/timer capsules (pill, surface fill, 2px outline); timer bar uses accent fill with rounded ends; never more than 3 capsules; gameplay grid gets at least 85% of vertical space in portrait

### `hud.score` — Score Counter

- **Tokens (authoritative, `component.hud.chip`):** radius=9999 · height=36 · outlineWidth=3 · outlineColor=#FFDDAC · shadow=0 2px 0 #56505E, 0 4px 6px rgba(46, 42, 50, 0.12) · paddingX=12 · fontSize=18
- **Purpose:** Show the running score during gameplay without competing with the constraint counter (moves/timer).
- **Visual rules:** plate fill: semantic.color.surface at >=85% opacity; stroke: shape.outline.width x0.66 with shape.outline.color_rule; radius: shape.radius_class one step tighter (tile radius); numerals: typography.display if tabular figures else typography.body bold, >=16dp; no rendering.shadow on HUD plates
- **Variants:** digits-only | digits+label | digits+best-score sub-line
- **States:** idle | incrementing (count-up <=250ms) | milestone (1.06 scale pulse, motion.duration_scale.fast) | hidden (kids learning)
- **Interaction:** Non-interactive; tap on plate may open score details only outside timed modes.
- **Platform notes:** Flutter: Text with FontFeature.tabularFigures(); Flame: TextComponent on a HudComponent with priority >= board
- **Anti-patterns:** Count-up longer than 1s hiding the real total | score larger than the moves/timer numerals | score plate casting a shadow over the board
- **QA:** Numerals >=16dp and >=4.5:1 vs plate | final value visible within 250ms of a match | plate width stable for 6 digits (no jitter)
- **Code reuse hint:** One HudPlate widget shared by hud.score, hud.moves, hud.timer, hud.currency; only the content slot differs

### `hud.timer` — Timer

- **Tokens (authoritative, `component.hud.chip`):** radius=9999 · height=36 · outlineWidth=3 · outlineColor=#FFDDAC · shadow=0 2px 0 #56505E, 0 4px 6px rgba(46, 42, 50, 0.12) · paddingX=12 · fontSize=18
- **Purpose:** Show remaining time as a bar plus digits so the constraint is readable at a glance mid-move.
- **Visual rules:** bar 6-8dp tall, full plate width, radius: pill cap; fill: semantic.color.primary, switches to warning <20% and danger <10%; digits >=18dp on the shared HudPlate; stroke: shape.outline.width x0.66
- **Variants:** bar+digits (default) | ring (sorting/merge energy) | digits-only (landscape side column)
- **States:** running | warning (<20%, bar colour + audio tick) | critical (<10%, 1Hz digit blink + haptic each second) | paused (digits frozen, bar dimmed 60%) | expired (0:00, danger, shake 3dp)
- **Interaction:** Non-interactive. Pause is a separate control (hud.pause-button); tapping the timer never pauses.
- **Platform notes:** Flutter: LinearProgressIndicator avoided (theme coupling), use custom painter; Flame: RectangleComponent width tween with Curves.linear
- **Anti-patterns:** Colour change without audio/haptic cue | timer that pauses for celebration while the level is still live | bar animated in steps instead of linear drain
- **QA:** Digits >=18dp | warning and critical states have a non-colour cue (blink/audio/haptic) | drain is linear (no easing) | frozen digits on first pause frame
- **Code reuse hint:** Shares HudPlate with hud.score; bar reuses progress.bar with height override 8dp

### `hud.moves` — Moves Counter

- **Tokens (authoritative, `component.hud.chip`):** radius=9999 · height=36 · outlineWidth=3 · outlineColor=#FFDDAC · shadow=0 2px 0 #56505E, 0 4px 6px rgba(46, 42, 50, 0.12) · paddingX=12 · fontSize=18
- **Purpose:** Show remaining moves as the dominant HUD number in move-limited genres (match-3, tile match).
- **Visual rules:** largest HUD numeral: >=20dp (18dp minimum) on HudPlate; plate centred in Z1 or on the dominant side; stroke: shape.outline.width x0.66; label 'Moves' 11dp typography.body uppercase only if typography.case allows
- **Variants:** digits | digits+label | digits with +N bonus badge (after continue)
- **States:** idle | decrement (1.06 scale pulse per move, motion.duration_scale.fast) | low (<=5, warning colour + single pulse per move) | zero (danger, triggers popup.lose after last effect) | bonus-added (+5 badge flies in, motion.duration_scale.base)
- **Interaction:** Non-interactive. Tapping shows objective recap only in untimed modes.
- **Platform notes:** Flutter/Flame: same as hud.score
- **Anti-patterns:** Moves counter smaller than score | decrement animation longer than one move interval | moves hidden behind the objectives panel
- **QA:** Largest numeral in the HUD | low state visible in greyscale (pulse/outline, not colour only) | value updates within 250ms of the move
- **Code reuse hint:** HudPlate + progress.stars-style badge for bonus

### `hud.currency` — Currency Wallet

- **Tokens (authoritative, `component.hud.chip`):** radius=9999 · height=36 · outlineWidth=3 · outlineColor=#FFDDAC · shadow=0 2px 0 #56505E, 0 4px 6px rgba(46, 42, 50, 0.12) · paddingX=12 · fontSize=18
- **Purpose:** Show spendable balances (soft coin, premium gem, lives/energy) with one consistent icon per currency everywhere.
- **States:** idle | increment (coin-fly lands then 1.06 pulse; final value shown within 250ms) | decrement (number flashes danger 1 frame then settles) | insufficient (shake 3dp, motion.duration_scale.fast) | refilling (mm:ss under the icon)
- **Code reuse hint:** HudPlate + CurrencyIcon component (single source of the asset path)
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#hud.currency`

### `hud.hint-button` — Hint Button

- **Tokens (authoritative, `component.hud.chip`):** radius=9999 · height=36 · outlineWidth=3 · outlineColor=#FFDDAC · shadow=0 2px 0 #56505E, 0 4px 6px rgba(46, 42, 50, 0.12) · paddingX=12 · fontSize=18
- **Purpose:** Offer a hint with its remaining free count or price visible before the tap.
- **Visual rules:** slot 56x56dp (visual) with icon 32dp from iconography.style; count badge 18dp top-right (11dp bold); price chip (commerce.price-tag small) under the icon when no free hints remain; radius: shape.radius_class; stroke: shape.outline.width; shading: rendering.shading; highlight: rendering.highlight
- **Variants:** free-count | priced | ad-rewarded (ad glyph in badge) | disabled (no valid hint, 40% opacity)
- **States:** idle | pressed (T0 scale 0.94, 80-150ms) | cooldown (ring, linear) | armed (not used; hints apply immediately) | disabled
- **Interaction:** Single tap applies the hint (highlights one valid move for 2 pulse cycles). Lives in Z3 within thumb reach.
- **Platform notes:** Flutter: a Booster-slot widget shared with hud.undo-button and hud.booster-slot; Flame: ButtonComponent
- **Anti-patterns:** Price revealed only after tap | hint highlighting a tile under the HUD | hint button in the top corner (out of thumb reach)
- **QA:** Count or price visible in a still frame | >=48dp hit | within 320dp of the bottom edge in portrait
- **Code reuse hint:** BoosterSlot base component; hint = slot with hintIcon + countOrPrice slot

### `hud.undo-button` — Undo Button

- **Tokens (authoritative, `component.hud.chip`):** radius=9999 · height=36 · outlineWidth=3 · outlineColor=#FFDDAC · shadow=0 2px 0 #56505E, 0 4px 6px rgba(46, 42, 50, 0.12) · paddingX=12 · fontSize=18
- **Purpose:** Revert the last move in genres where it is a core mechanic (sorting, merge, word) with its count or price visible.
- **Visual rules:** same slot as hud.hint-button (56dp, icon 32dp arrow-counter-clockwise per iconography.style); count badge; radius: shape.radius_class; stroke: shape.outline.width; shading: rendering.shading
- **Variants:** free-unlimited (no badge) | counted | priced | ad-rewarded
- **States:** idle | pressed | disabled (nothing to undo, 40% opacity, no tap sound) | priced-insufficient (shake, routes to shop)
- **Interaction:** Single tap reverts one move with the reverse of the move animation (motion.duration_scale.base). Never a confirm popup for undo.
- **Platform notes:** Flutter/Unity share BoosterSlot
- **Anti-patterns:** Undo that silently charges currency | undo without reverse animation (board jumps) | undo placed next to restart with identical styling
- **QA:** Count/price visible before tap | disabled state distinguishable in greyscale | the reverse animation <=250ms
- **Code reuse hint:** BoosterSlot base component

### `hud.pause-button` — Pause Button

- **Tokens (authoritative, `component.hud.chip`):** radius=9999 · height=36 · outlineWidth=3 · outlineColor=#FFDDAC · shadow=0 2px 0 #56505E, 0 4px 6px rgba(46, 42, 50, 0.12) · paddingX=12 · fontSize=18
- **Purpose:** Stop the game clock and open popup.pause from a stable corner position.
- **Visual rules:** 48dp hit (visual 40dp allowed), icon 24dp 'pause' from iconography.style, top corner of Z1 at 16dp gutters + safeTop; plate style: HudPlate; radius: shape.radius_class; stroke: shape.outline.width x0.66
- **Variants:** icon-only | icon+label (tablet)
- **States:** idle | pressed | hidden (tutorial step in progress, kids mode uses parental gate instead)
- **Interaction:** One tap, no hold. Opens popup.pause in motion.duration_scale.base; timer digits freeze on frame 1 before the panel appears.
- **Platform notes:** Flutter: pause the game loop, not just the overlay; Flame: game.pauseEngine() after freezing the HUD
- **Anti-patterns:** Pause inside the booster bar (Z3) | pause hidden behind the notch | pause that opens settings instead of a pause panel
- **QA:** >=48dp hit box | in a corner of Z1 | timer value under the scrim equals the value in the pause panel
- **Code reuse hint:** IconPlateButton shared with settings gear and close buttons

### `hud.booster-slot` — Booster Slot

- **Tokens (authoritative, `component.hud.chip`):** radius=9999 · height=36 · outlineWidth=3 · outlineColor=#FFDDAC · shadow=0 2px 0 #56505E, 0 4px 6px rgba(46, 42, 50, 0.12) · paddingX=12 · fontSize=18
- **Purpose:** Hold a consumable power-up with count or price and an explicit armed state before use.
- **Visual rules:** 56x56dp slot (64dp on tablet), icon 32dp booster art per illustration.asset_rendering, count badge 18dp top-right, price chip when count=0; radius: shape.radius_class; stroke: shape.outline.width; armed stroke x2 in semantic.color.accent; shading: rendering.shading; highlight: rendering.highlight; shadow: rendering.shadow one step on armed
- **Variants:** count | priced | locked (padlock, unlocks at level N) | ad-rewarded | empty (dashed outline, add glyph)
- **States:** idle | pressed | armed (outline x2 + cancel X 24dp at top-left + board shows valid targets) | consuming (icon shrinks 1.0->0.8->1.0 in motion.duration_scale.base, count decrements) | disabled during cascade | locked
- **Interaction:** Tap = arm; tap again or tap X = cancel; tap a valid board target = consume. Never auto-apply on tap. Max 4 slots in Z3; row never scrolls.
- **Platform notes:** Flutter: BoosterSlot widget with a ValueListenable count; Flame: SpriteButtonComponent + child TextComponent
- **Anti-patterns:** Booster applied on first tap | slot bar overlapping the bottom board row | locked slots that open the shop on tap before level N
- **QA:** Count or price or lock visible in a still | armed state identifiable with a cancel affordance | slot bar bottom edge >=8dp above the board and inside safe area
- **Code reuse hint:** BoosterSlot base component (hint/undo/shuffle/booster share it)

## indicator

### `badge.count` — Count Badge

- **Purpose:** Small numeric count on an icon or tab (unread, items, lives)
- **States:** hidden (0) | visible | updating (scale 1 -> 1.2 -> 1, duration.fast, easing.emphasized)
- **Code reuse hint:** Badge(count|dot) attached via a wrapper, not positioned per call-site
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#badge.count`

### `indicator.notification` — Notification Indicator

- **Purpose:** Dot or pulse marking new content on an entry point (tab, icon, level node)
- **States:** hidden | visible | pulsing (first 3 s only)
- **Code reuse hint:** NotificationDot(variant) attached through the same wrapper as badge
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#indicator.notification`

## input

### `chip.filter` — Filter Chip

- **Tokens (authoritative, `component.hud.chip`):** radius=9999 · height=36 · outlineWidth=3 · outlineColor=#FFDDAC · shadow=0 2px 0 #56505E, 0 4px 6px rgba(46, 42, 50, 0.12) · paddingX=12 · fontSize=18
- **Purpose:** Toggleable filter or category selector in a horizontal row
- **States:** default | hover | pressed | selected | focus | disabled
- **Code reuse hint:** Chip(selected, onToggle, leading, trailing)
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#chip.filter`

## navigation

### `menu.list` — Menu

- **Purpose:** Short list of commands anchored to a trigger (overflow, context, dropdown)
- **States:** closed | opening (duration.fast, easing.enter, origin at trigger) | open | item-hover | item-pressed | item-disabled
- **Code reuse hint:** Menu(trigger, items) reusing list
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#menu.list`

### `nav.level-node` — Level Node

- **Tokens (authoritative, `component.card`):** radius=24 · borderWidth=3 · shadow=0 2px 0 rgba(46, 42, 50, 0.25), 0 4px 6px rgba(46, 42, 50, 0.12) · padding=20 · gap=12
- **Purpose:** Represent one level on the map or list with current/locked/completed status readable in greyscale.
- **Visual rules:** 56-64dp node, shape per shape.silhouette (rounded-blob -> blob, geometric -> circle); number 16dp bold with >=4.5:1 on the node fill; stars 12dp under (map) or inside (list) via progress.stars; stroke: shape.outline.width; shading: rendering.shading; current: +15% scale + accent outline x2 + pin/mascot; locked: saturation -60% + padlock, no number; completed: fill semantic.color.success or chapter colour; path stroke shape.outline.width + 2dp, dashed ahead
- **Variants:** map-node | list-cell (56dp square, radius: shape.radius_class) | chapter-chest-node | event-node
- **States:** locked | current (pulse per motion.class, period 2.5s) | completed-1/2/3-stars | failed-last-attempt (small retry badge) | friends-present (avatar 20dp)
- **Interaction:** Tap current/completed = pre-level sheet; tap locked = toast 'Complete level N first'. No drag. Map scroll vertical only; auto-centre current node on entry; 'jump to current' after >1 screen scroll.
- **Platform notes:** Flutter: CustomScrollView with the current node centred via initial offset; Flame: camera.follow on entry
- **Anti-patterns:** Current node not centred on entry | locked nodes opening the shop | node numbers on busy art <4.5:1 | nodes under the bottom nav
- **QA:** Current node in the middle 50% of the viewport on first paint | states distinguishable in greyscale | number contrast >=4.5:1 | 110-140dp travel per node on maps
- **Code reuse hint:** LevelNode component with status enum; stars via progress.stars

### `nav.bottom-bar` — Bottom Navigation Bar

- **Tokens (authoritative, `component.card`):** radius=24 · borderWidth=3 · shadow=0 2px 0 rgba(46, 42, 50, 0.25), 0 4px 6px rgba(46, 42, 50, 0.12) · padding=20 · gap=12
- **Purpose:** Move between lobby, levels, shop, events, profile; hidden during gameplay.
- **States:** idle | active | badged | hidden (gameplay, tutorial, full-screen popups) | disabled (locked tab with padlock until level N)
- **Code reuse hint:** Same bar for app and game (apps: 3-5 destinations)
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#nav.bottom-bar`

## overlay

- **Style modifier (reference) for `dialog.modal`:** Rounded panel radius 28px, surface fill, 4px outline in secondary-darker, ribbon title plate overlapping the top edge by 50%; close button circular 44px top-right; entrance scale 0.85 to 1 with overshoot 1.04 in 260ms

### `dialog.modal` — Modal Dialog

- **Tokens (authoritative, `component.popup`):** radius=32 · outlineWidth=3 · outlineColor=#FFDDAC · shadow=0 6px 0 rgba(46, 42, 50, 0.25), 0 12px 20px rgba(46, 42, 50, 0.18) · padding=24 · maxWidth=360
- **Purpose:** Blocking decision or short form that must be resolved before continuing
- **States:** entering (duration.base, easing.enter, scale 0.95 -> 1 + fade) | open | leaving (duration.fast, easing.exit) | busy (actions disabled)
- **Code reuse hint:** one Dialog component
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#dialog.modal`

### `overlay.tooltip` — Tooltip

- **Purpose:** Short label or hint on hover/long-press/focus; never essential information
- **States:** hidden | showing (delay 400ms hover, immediate on focus, duration.fast fade) | visible | hiding
- **Code reuse hint:** Tooltip(content, placement) wrapping the trigger
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#overlay.tooltip`

### `confirm.destructive` — Destructive Confirmation

- **Purpose:** Second step before an irreversible action; names the object and the consequence
- **States:** open | busy (destructive button loading, cancel disabled) | done (closes, toast with result)
- **Code reuse hint:** Dialog + Button(destructive) composition
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#confirm.destructive`

## popup

- **Style modifier (reference) for `popup.pause`, `popup.win`, `popup.lose`, `popup.confirm`, `popup.offer`:** Rounded panel radius 28px, surface fill, 4px outline in secondary-darker, ribbon title plate overlapping the top edge by 50%; close button circular 44px top-right; entrance scale 0.85 to 1 with overshoot 1.04 in 260ms

### `popup.pause` — Pause Menu

- **Tokens (authoritative, `component.popup`):** radius=32 · outlineWidth=3 · outlineColor=#FFDDAC · shadow=0 6px 0 rgba(46, 42, 50, 0.25), 0 12px 20px rgba(46, 42, 50, 0.18) · padding=24 · maxWidth=360
- **Purpose:** Confirm the clock stopped and offer resume, restart, settings toggles and quit.
- **Visual rules:** panel radius: shape.radius_class one step looser (popup radius, <=28dp); stroke: shape.outline.width; shadow: rendering.shadow; scrim 55-70% semantic.color.overlay; title typography.display with typography.case; Resume = button.primary; Restart/Quit secondary outline; toggles row 56dp
- **Variants:** compact (resume/restart/quit + 3 toggles) | with objective recap | with booster inventory (read-only)
- **States:** opening (motion.duration_scale.base) | open | confirming-quit | closing (ease-in, <=250ms)
- **Interaction:** Resume at the bottom (thumb); Android back = Resume; tap-outside = Resume; Quit needs confirm after >=1 move.
- **Platform notes:** Flutter: overlay route with barrierDismissible=true mapped to resume; Flame: game.overlays.add
- **Anti-patterns:** 'Continue' label on Resume | shop CTA inside pause in timed modes | Quit styled like Resume
- **QA:** Exactly one filled button | scrim sampled 55-70% | panel radius >= button radius
- **Code reuse hint:** PopupPanel base (header slot, body slot, button stack slot) shared by popup.win/lose/confirm/offer and reward popups

### `popup.win` — Win Screen

- **Tokens (authoritative, `component.popup`):** radius=32 · outlineWidth=3 · outlineColor=#FFDDAC · shadow=0 6px 0 rgba(46, 42, 50, 0.25), 0 12px 20px rgba(46, 42, 50, 0.18) · padding=24 · maxWidth=360
- **Purpose:** Celebrate, list earnings, and move to the next level in <=2 taps.
- **Visual rules:** PopupPanel; stars 48-64dp gap 8dp (3rd star 12% larger if crown layout); reward chips in semantic.color.reward; celebration layer behind panel content, above scrim; rays rotate <=6deg/s; Next = button.primary 56dp full width at panel bottom; x2-ad secondary with ad glyph; palette per palette_strategy (saturated accents for rewards)
- **Variants:** stars | grade (S/A/B) | score-only (word/sorting) | sticker (kids)
- **States:** entering (>=600ms after last match effect) | stars-animating (skippable to final) | settled | exiting
- **Interaction:** Tap anywhere during star animation = jump to final state, never dismiss. Next CTA single primary. Ad bonus never primary.
- **Platform notes:** Flutter: showDialog over the game route, star AnimationController sequence; Flame: overlay
- **Anti-patterns:** Popup covering the board before the last match was seen | x2-ad styled as primary | confetti blocking button hit tests | interstitial on Next in the first 3 levels
- **QA:** Next is the single primary at the bottom | currency icon identical to HUD | no particles over button labels after 900ms | star count matches threshold text
- **Code reuse hint:** PopupPanel + progress.stars + reward.card + EffectSequencer

### `popup.lose` — Lose / Out-of-moves Screen

- **Tokens (authoritative, `component.popup`):** radius=32 · outlineWidth=3 · outlineColor=#FFDDAC · shadow=0 6px 0 rgba(46, 42, 50, 0.25), 0 12px 20px rgba(46, 42, 50, 0.18) · padding=24 · maxWidth=360
- **Purpose:** State the loss reason, show objective progress, offer a fair continue, keep retry one tap away.
- **Visual rules:** PopupPanel; scrim <=60% (board visible); reason line in semantic.color.danger only; progress line (e.g. '3 of 8'); continue button shows '+5 moves - 900 coins' with price via commerce.price-tag and balance beside; Retry secondary (or primary after the first decline) >=48dp; no celebration layer; sad mascot per illustration.character_style
- **Variants:** paid-continue | ad-continue (separate button with ad glyph) | retry-only (second failure, no-continue genres) | lives-based
- **States:** entering (>=400ms after fail animation) | open | insufficient-balance ('Get coins' routes to shop) | countdown (only if >=10s; expiry = decline) | exiting
- **Interaction:** Android back = decline. Buttons stacked vertically: continue -> Retry -> Map. Decline >=24dp away from the last board tap zone. Max 1 paid prompt per attempt.
- **Platform notes:** Model charges only after the platform/currency confirm; never auto-deduct premium currency; log decline as a real event
- **Anti-patterns:** Confirmshaming decline labels | decline at <3:1 contrast | X that accepts the purchase | price hidden until confirm | countdown <10s | pre-ticked booster checkboxes
- **QA:** Price and balance on the same panel | decline >=48dp and >=50% of continue width | scrim <=60% | no countdown or >=10s | danger hue only on the reason line
- **Code reuse hint:** PopupPanel + commerce.price-tag + ButtonStack

### `popup.confirm` — Confirm Dialog

- **Tokens (authoritative, `component.popup`):** radius=32 · outlineWidth=3 · outlineColor=#FFDDAC · shadow=0 6px 0 rgba(46, 42, 50, 0.25), 0 12px 20px rgba(46, 42, 50, 0.18) · padding=24 · maxWidth=360
- **Purpose:** Guard irreversible or costly actions (quit level, sell item, spend >=20% balance, delete account) with a clear primary and a safe decline.
- **States:** open | processing (primary shows spinner, both disabled) | closed
- **Code reuse hint:** PopupPanel compact variant
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#popup.confirm`

### `popup.offer` — Offer / Promo Popup

- **Tokens (authoritative, `component.popup`):** radius=32 · outlineWidth=3 · outlineColor=#FFDDAC · shadow=0 6px 0 rgba(46, 42, 50, 0.25), 0 12px 20px rgba(46, 42, 50, 0.18) · padding=24 · maxWidth=360
- **Purpose:** Present a time-limited or contextual bundle honestly: contents, real price, visible expiry, instant close.
- **States:** entering (>=1s after lobby interactive, max 1 auto per session after session 3) | open | expired (greys with 'Expired', never re-arms silently) | purchasing (store sheet) | closed
- **Code reuse hint:** PopupPanel + commerce
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#popup.offer`

## reward

- **Style modifier (reference) for `reward.card`, `reward.daily-login`, `reward.wheel`, `reward.chest`, `reward.mission-item`, `reward.streak`:** Reward popups go one saturation step higher (accent plus gold); confetti of 3 shapes max (circle, star, heart) in palette colours; mascot cheer pose; sparkle burst 6-8 rays; bounce to 1.1 scale synced to sound

### `reward.card` — Reward Item Card

- **Tokens (authoritative, `component.card`):** radius=24 · borderWidth=3 · shadow=0 2px 0 rgba(46, 42, 50, 0.25), 0 4px 6px rgba(46, 42, 50, 0.12) · padding=20 · gap=12
- **Purpose:** Represent one earned or purchasable item with amount and rarity in exactly the same frame on every screen.
- **Visual rules:** card 64-88dp square (96dp hero); radius: shape.radius_class; stroke: shape.outline.width; rarity frame colour from the rarity ramp (semantic.color.reward for default); shading: rendering.shading; highlight: rendering.highlight; amount chip bottom-centre 'x12' 12dp bold; icon art per illustration.asset_rendering
- **Variants:** currency | booster | character/sticker | chest | locked-silhouette
- **States:** idle | revealing (scale 0->1.1->1 motion.duration_scale.base, stagger 180ms) | claimed (check overlay, saturation -40%) | selected (accent outline x1.5) | overflow ('+3 more' chip)
- **Interaction:** Tap shows a tooltip/description sheet; never purchases. Long-press optional for details.
- **Platform notes:** Flutter: RewardCard widget
- **Anti-patterns:** Different card frames between win, chest and shop | rarity colour differing between screens | amount hidden inside the art
- **QA:** Overlay cards from win/chest/shop: identical radius, stroke, chip | rarity ramp identical across captures | amount legible >=12dp
- **Code reuse hint:** RewardCard component; reward chip in reward.mission-item is RewardCard size xs

### `reward.daily-login` — Daily Login Calendar

- **Tokens (authoritative, `component.card`):** radius=24 · borderWidth=3 · shadow=0 2px 0 rgba(46, 42, 50, 0.25), 0 4px 6px rgba(46, 42, 50, 0.12) · padding=20 · gap=12
- **Purpose:** Show the week/month calendar with today's claimable reward and one Claim action.
- **Visual rules:** 7 cells per row 48dp (day 7 cell 1.5x wide); cells use reward.card xs; today: accent outline x2 + pulse per motion.class; claimed: check + saturation -40%; future: idle; Claim = button.primary 56dp; 'x2 with ad' secondary; PopupPanel; streak note 12dp
- **Variants:** 7-day | 28/30-day grid (4 rows, scrolls to today) | with-streak-note
- **States:** auto-opened (max 1/day, >=1s after lobby) | today-claimable | claimed-today (Claim disabled, 'Come back tomorrow' + countdown) | catch-up (missed day shown, no reset)
- **Interaction:** One tap Claim; coin-fly to hud.currency <=1s; closes on Claim unless x2-ad is pending; close X 44dp.
- **Platform notes:** Flutter GridView.count(7)
- **Anti-patterns:** Today's cell not distinguishable in greyscale | claim requiring a second confirm | calendar reset on a missed day (that is streak logic, keep it separate)
- **QA:** Today identifiable in greyscale | single primary button | 7 cells aligned to 8dp grid | day-7 reward visibly larger
- **Code reuse hint:** PopupPanel + reward.card grid

### `reward.wheel` — Spin Wheel

- **Tokens (authoritative, `component.card`):** radius=24 · borderWidth=3 · shadow=0 2px 0 rgba(46, 42, 50, 0.25), 0 4px 6px rgba(46, 42, 50, 0.12) · padding=20 · gap=12
- **Purpose:** Random reward with 6-8 segments, honest landing, visible spin cost.
- **Visual rules:** wheel >=260dp diameter, segments alternate two fills from palette_strategy (pastel base) with reward icons 24dp + label 12dp bold; pointer 24dp at 12 o'clock with shape.outline.width stroke; rim stroke shape.outline.width x1.5; Spin = button.primary in Z3 with cost text ('Spin - 1 free' / '50 coins' / 'Watch ad'); rendering.highlight gloss on the hub only
- **Variants:** 6-segment | 8-segment | premium-wheel (rarity ramp) | ad-only
- **States:** idle (slow ambient rotate <=3deg/s, bouncy/dramatic only) | spinning (>=3 turns, 2.5-4s, easeOutQuart/Ease.OutQuart/expo.out) | stopped (>=300ms hold) | result (popup with reward.card) | no-spins (button shows cost)
- **Interaction:** One tap to spin; input locked while spinning; result popup requires a tap to close; no re-spin button on the result for 1s.
- **Platform notes:** Flutter: RotationTransition with easeOutQuart to a precomputed angle; Flame: RotateEffect.to
- **Anti-patterns:** Near-miss creep past the jackpot | segment labels <12dp | pointer off-centre on stop | spin cost hidden until tap | used in kids learning
- **QA:** Pointer centred on the winning segment in the final frame | 6-8 segments | cost visible before tap | spin duration 2.5-4s
- **Code reuse hint:** Wheel component; result reuses PopupPanel + reward.card

### `reward.chest` — Treasure Chest

- **Tokens (authoritative, `component.card`):** radius=24 · borderWidth=3 · shadow=0 2px 0 rgba(46, 42, 50, 0.25), 0 4px 6px rgba(46, 42, 50, 0.12) · padding=20 · gap=12
- **Purpose:** Reveal a bundle of items with a skippable open sequence and rarity frames.
- **Visual rules:** chest sprite 120-160dp per illustration.asset_rendering and rendering.shading; rarity frame/glow from the rarity ramp; key/cost on the Open button (button.primary); result grid 3 columns of reward.card with 8dp gap; max 5 cards + '+N more' overflow; PopupPanel
- **Variants:** common | rare | epic/legendary | timed (unlock countdown) | keyed
- **States:** locked (padlock + key count) | ready (bounce per motion.class, period 2.5s) | opening (shake fast x2 -> lid pop base -> items stagger 180ms) | revealed (Collect enabled) | collected
- **Interaction:** Tap Open; tap during the sequence after 1.5s reveals all; Collect/OK closes; coin-fly for currency items.
- **Platform notes:** Flutter AnimationController sequence; Flame SequenceEffect
- **Anti-patterns:** Collect enabled before all items are visible | chest art in a different rendering than tiles | timed chest that charges on tap without showing the price
- **QA:** All items visible with rarity frames before Collect is enabled | skippable at 1.5s | chest uses the same shading as tiles | key/cost visible when locked
- **Code reuse hint:** PopupPanel + reward.card grid + EffectSequencer jackpot/medium tiers

### `reward.mission-item` — Mission Row

- **Tokens (authoritative, `component.card`):** radius=24 · borderWidth=3 · shadow=0 2px 0 rgba(46, 42, 50, 0.25), 0 4px 6px rgba(46, 42, 50, 0.12) · padding=20 · gap=12
- **Purpose:** One quest row with icon, title, progress, reward chip and a single action (Go / Claim).
- **States:** in-progress (Go) | claimable (Claim primary + one 1.02 pulse on entry) | claimed (check, saturation -40%, moves to bottom) | locked (unlocks at level N) | expired
- **Code reuse hint:** ListRow base + progress
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#reward.mission-item`

### `reward.streak` — Streak Indicator

- **Tokens (authoritative, `component.card`):** radius=24 · borderWidth=3 · shadow=0 2px 0 rgba(46, 42, 50, 0.25), 0 4px 6px rgba(46, 42, 50, 0.12) · padding=20 · gap=12
- **Purpose:** Show the daily streak count and warn before it breaks.
- **Visual rules:** badge 32dp (lobby) / 48dp (popup) per illustration.character_style (flame/star); day count 20dp bold; 7-dot track 8dp dots gap 6dp with semantic.color.reward fill; freeze count chip if the mechanic exists; radius: shape.radius_class
- **Variants:** lobby-badge | popup-track | banner-warning ('Play today to keep your 6-day streak')
- **States:** active | at-risk (banner, once per day) | broken (recovery offer max once, continue-offer rules apply) | frozen
- **Interaction:** Tap opens the streak popup; recovery offer has a real decline.
- **Platform notes:** Local-day boundary with server validation; share the number source with profile stats
- **Anti-patterns:** Streak number differing between lobby and popup | recovery offer without a visible price | daily shaming copy
- **QA:** Lobby and popup counts equal | 7 dots aligned | at-risk banner shown before loss, not only after
- **Code reuse hint:** Badge + progress segmented variant

## state

### `state.loading` — Loading State

- **Purpose:** Content is being fetched or computed; keeps layout stable
- **States:** idle | loading (> 300ms before showing) | timed-out (> 10 s shows state.error with retry)
- **Code reuse hint:** LoadingState(variant) + Skeleton primitive
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#state.loading`

### `state.empty` — Empty State

- **Purpose:** Nothing to show yet; explains why and offers the next step
- **States:** default | with-action | compact (inside panels, no illustration)
- **Code reuse hint:** EmptyState(illustration, title, body, action)
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#state.empty`

### `state.error` — Error State

- **Purpose:** Something failed; says what, whether it is the user's fault, and how to recover
- **States:** default | retrying (action shows state.loading inline) | resolved (fades out duration.base)
- **Code reuse hint:** ErrorState(variant, onRetry)
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#state.error`

### `state.success` — Success State

- **Purpose:** Confirms a completed action without stealing the screen
- **States:** entering (duration.base, easing.enter, check draws in) | visible | auto-dismiss (toast only)
- **Code reuse hint:** SuccessState(variant) sharing the inline shell with state
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#state.success`

### `state.disabled` — Disabled State

- **Purpose:** A control exists but is not actionable right now; must explain why when possible
- **States:** disabled | disabled-with-reason (tooltip or helper text)
- **Code reuse hint:** a shared disabled modifier on every interactive component, never per-component colours
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#state.disabled`
