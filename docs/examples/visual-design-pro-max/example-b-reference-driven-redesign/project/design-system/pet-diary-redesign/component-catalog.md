<!-- generated-by: visual-direction vd.py 1.0.0; profile-hash: 73c0e76468b6 -->
# Component Catalog — Pet Diary Redesign

Filtered for `product.kind = app` (rows whose Applies To is `app` or `both`; 33 components) and style `reference-derived-custom`.
Order of authority per component: **Tokens (authoritative)** from `tokens.json` → catalog rule (structure, variants, states) → **Style modifier (reference)**, the catalog/style prose. Where prose and tokens disagree (e.g. a pill vs a 16 radius, 2px vs 3px outline), the token value wins; record a deliberate deviation as an intentional exception, never by editing the prose (CC-11).
Rows specific to this product kind are rendered in full; shared rows (`Applies To = both`) are rendered compact — their full visual rules, variants, interaction, platform notes, anti-patterns and QA live in `data/component-catalog.csv` of the `visual-direction` skill. Style modifiers are printed once per group, naming the components they apply to.

Platform notes are filtered for stack `flutter`.

## action

- **Style modifier (reference) for `button.icon`:** Circular 44px white button with 2px peach outline and orange glyph.

### `button.primary` — Primary Button

- **Tokens (authoritative, `component.button.primary`):** radius=16 · height=44 · outlineWidth=2 · outlineColor=#F8E4D6 · shadow=none · paddingX=20 · fontSize=16 · minWidth=96
- **Purpose:** The one action the screen wants taken; at most one per view
- **States:** default | hover (semantic.state.hover) | pressed (semantic.state.pressed: translateY offsetY, bg primaryPressed) | focus (semantic.state.focus ring) | disabled (semantic.state.disabled opacity, no shadow) | loading (primitive.opacity.loading, spinner replaces label, width locked)
- **Code reuse hint:** one Button component with variant prop {primary,secondary,destructive,icon}
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#button.primary`

### `button.secondary` — Secondary Button

- **Tokens (authoritative, `component.button.secondary`):** radius=16 · height=44 · outlineWidth=2 · outlineColor=#AC8558 · shadow=none · paddingX=20 · fontSize=16
- **Purpose:** Alternative or lower-priority action next to a primary
- **States:** default | hover (bg component.button.secondary.bgHover) | pressed (bg bgPressed + state.pressed offset) | focus | disabled
- **Code reuse hint:** same Button component, variant=secondary
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#button.secondary`

### `button.icon` — Icon Button

- **Tokens (authoritative, `component.button.icon`):** radius=9999 · outlineWidth=0 · outlineColor=transparent · shadow=none · size=48
- **Purpose:** Single-icon control for close, settings, back, mute
- **States:** default | hover | pressed (scale 0.94, duration.fast) | focus | disabled | toggled
- **Code reuse hint:** Button variant=icon
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#button.icon`

### `button.destructive` — Destructive Button

- **Tokens (authoritative, `component.button.primary`):** radius=16 · height=44 · outlineWidth=2 · outlineColor=#F8E4D6 · shadow=none · paddingX=20 · fontSize=16 · minWidth=96
- **Purpose:** Irreversible or data-losing action (delete, reset progress, sign out everywhere)
- **States:** default | hover (primitive.color.danger.700) | pressed (danger.800) | focus | disabled
- **Code reuse hint:** Button variant=destructive
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#button.destructive`

## commerce

### `commerce.shop-item` — Shop Item Card

- **Tokens (authoritative, `component.card`):** radius=24 · borderWidth=1 · shadow=none · padding=16 · gap=12
- **Purpose:** Sell a pack/bundle/booster with contents visible, one price tag, and at most one badge.
- **States:** idle | pressed (T0) | purchasing (price tag shows spinner) | owned (remove-ads: check + disabled) | limited (expiry chip, greys on expiry) | sold-out
- **Code reuse hint:** ShopCard = Card base + reward
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#commerce.shop-item`

### `commerce.price-tag` — Price Tag

- **Tokens (authoritative, `component.card`):** radius=24 · borderWidth=1 · shadow=none · padding=16 · gap=12
- **Purpose:** Display a price (real money or in-game currency) in one unmistakable component reused on every buy/continue/hint surface.
- **States:** idle | pressed (large only) | insufficient (danger outline + 'Get coins' routing) | loading (store price pending: skeleton, never '0') | discounted
- **Code reuse hint:** PriceTag component used by hud
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#commerce.price-tag`

## container

### `card.default` — Card

- **Tokens (authoritative, `component.card`):** radius=24 · borderWidth=1 · shadow=none · padding=16 · gap=12
- **Purpose:** Groups one entity (item, level, transaction) with its actions
- **States:** default | hover (interactive only) | pressed (interactive only, state.pressed) | selected | disabled
- **Code reuse hint:** Card(variant, selected, onTap) wrapper
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#card.default`

### `panel.container` — Panel

- **Tokens (authoritative, `component.card`):** radius=24 · borderWidth=1 · shadow=none · padding=16 · gap=12
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

- **Tokens (authoritative, `component.progress`):** radius=9999 · height=8 · outlineWidth=0 · outlineColor=transparent
- **Purpose:** Linear fill for timer, mission progress, level pre-sheet objectives, season pass and loading.
- **States:** empty | partial | full (optional 1-frame flash) | warning | danger | indeterminate (loading only)
- **Code reuse hint:** ProgressBar component reused by hud
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#progress.bar`

## hud

### `hud.currency` — Currency Wallet

- **Tokens (authoritative, `component.hud.chip`):** radius=9999 · height=32 · outlineWidth=1 · outlineColor=#FED7AA · shadow=none · paddingX=12 · fontSize=14
- **Purpose:** Show spendable balances (soft coin, premium gem, lives/energy) with one consistent icon per currency everywhere.
- **States:** idle | increment (coin-fly lands then 1.06 pulse; final value shown within 250ms) | decrement (number flashes danger 1 frame then settles) | insufficient (shake 3dp, motion.duration_scale.fast) | refilling (mm:ss under the icon)
- **Code reuse hint:** HudPlate + CurrencyIcon component (single source of the asset path)
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#hud.currency`

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

### `input.text` — Text Input

- **Purpose:** Single-line text entry with label, helper and error
- **Visual rules:** height: 44 (app, touchTarget.min on mobile); bg: semantic.color.surface; outline: primitive.outline.thin semantic.color.border, focus primitive.outline.regular semantic.color.primary + ring semantic.state.focus; radius: semantic.radius.control; paddingX: primitive.spacing.3; text: semantic.typography.body; label: semantic.typography.label; helper/error: semantic.typography.caption in textMuted / semantic.color.danger
- **Variants:** default | with-leading-icon | with-trailing-action (clear, visibility) | multiline | search (chip radius)
- **States:** default | hover (border neutral.400) | focus | filled | error (outline danger, helper danger) | disabled (bg neutral.100) | read-only
- **Interaction:** focus shows ring; clear action appears when filled; error clears on next valid input; Enter submits single-field forms
- **Platform notes:** iOS: keyboard type and textContentType set; Android: IME action set, Material outlined style; web: label element bound, autocomplete attribute, 16px font minimum to prevent zoom
- **Anti-patterns:** placeholder as the only label | error shown before first blur | height below touchTarget.min on mobile
- **QA:** label visible and bound | error state readable without colour (icon or text) | focus ring visible on all backgrounds
- **Code reuse hint:** TextField(label, helper, error, leading, trailing); error row shared with state.error inline

### `chip.filter` — Filter Chip

- **Tokens (authoritative, `component.hud.chip`):** radius=9999 · height=32 · outlineWidth=1 · outlineColor=#FED7AA · shadow=none · paddingX=12 · fontSize=14
- **Purpose:** Toggleable filter or category selector in a horizontal row
- **States:** default | hover | pressed | selected | focus | disabled
- **Code reuse hint:** Chip(selected, onToggle, leading, trailing)
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#chip.filter`

## navigation

- **Style modifier (reference) for `nav.top-bar`, `nav.tabs`, `nav.bottom-bar`:** Bottom nav active state = peach pill + orange icon/label; max 4–5 items.

### `nav.top-bar` — Top App Bar

- **Tokens (authoritative, `component.card`):** radius=24 · borderWidth=1 · shadow=none · padding=16 · gap=12
- **Purpose:** Screen title, back/close and up to two contextual actions
- **Visual rules:** height: 56 (app) in platform unit; bg: semantic.color.surface; title: semantic.typography.title at fontSize primitive.fontSize.lg; actions: button.icon; divider: primitive.outline.thin in semantic.color.border when content scrolled; zIndex: primitive.zIndex.sticky
- **Variants:** default | large-title (collapses on scroll) | transparent-over-media | search
- **States:** default | scrolled (divider or elevation.raised) | collapsed large-title
- **Interaction:** back/close on the leading edge; actions trailing; title not tappable
- **Platform notes:** iOS: navigation bar with large title option, back chevron + previous title; Android: top app bar, back arrow, overflow menu; web: sticky header, skip link before it
- **Anti-patterns:** more than two trailing actions | title truncation without tooltip on web | custom back icon
- **QA:** height from token | safe-area top inset applied | title contrast >= 4.5:1
- **Code reuse hint:** AppBar(title, leading, actions) using button.icon for actions

### `nav.tabs` — Tabs

- **Tokens (authoritative, `component.card`):** radius=24 · borderWidth=1 · shadow=none · padding=16 · gap=12
- **Purpose:** Switch between sibling views of the same screen
- **Visual rules:** height: 48; indicator: 3 units high in semantic.color.primary with radius primitive.radius.full; label: semantic.typography.label; active fg: semantic.color.primary; inactive fg: semantic.color.textMuted; bg: semantic.color.surface; divider: primitive.outline.thin semantic.color.border
- **Variants:** fixed (2-4 equal width) | scrollable (5+) | segmented (app, pill container)
- **States:** default | active | hover | pressed | focus | disabled
- **Interaction:** tap switches; swipe between panels on mobile; indicator slides duration.base easing.standard
- **Platform notes:** iOS: segmented control idiom for <= 3 tabs; Android: Material tabs; web: role=tablist, arrow-key navigation
- **Anti-patterns:** tabs as a navigation bar between screens | icons without labels in fixed tabs | more than 5 fixed tabs
- **QA:** active tab distinguishable without colour alone (indicator) | touch target >= touchTarget.min | indicator motion respects reduced motion
- **Code reuse hint:** Tabs(items, value, onChange); indicator position derived, not hard-coded

### `menu.list` — Menu

- **Purpose:** Short list of commands anchored to a trigger (overflow, context, dropdown)
- **States:** closed | opening (duration.fast, easing.enter, origin at trigger) | open | item-hover | item-pressed | item-disabled
- **Code reuse hint:** Menu(trigger, items) reusing list
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#menu.list`

### `nav.bottom-bar` — Bottom Navigation Bar

- **Tokens (authoritative, `component.card`):** radius=24 · borderWidth=1 · shadow=none · padding=16 · gap=12
- **Purpose:** Move between lobby, levels, shop, events, profile; hidden during gameplay.
- **States:** idle | active | badged | hidden (gameplay, tutorial, full-screen popups) | disabled (locked tab with padlock until level N)
- **Code reuse hint:** Same bar for app and game (apps: 3-5 destinations)
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#nav.bottom-bar`

## overlay

### `dialog.modal` — Modal Dialog

- **Tokens (authoritative, `component.popup`):** radius=32 · outlineWidth=0 · outlineColor=transparent · shadow=none · padding=20 · maxWidth=480
- **Purpose:** Blocking decision or short form that must be resolved before continuing
- **States:** entering (duration.base, easing.enter, scale 0.95 -> 1 + fade) | open | leaving (duration.fast, easing.exit) | busy (actions disabled)
- **Code reuse hint:** one Dialog component
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#dialog.modal`

### `sheet.bottom` — Bottom Sheet

- **Tokens (authoritative, `component.popup`):** radius=32 · outlineWidth=0 · outlineColor=transparent · shadow=none · padding=20 · maxWidth=480
- **Purpose:** Non-blocking tasks, pickers and filters anchored to the bottom edge
- **Visual rules:** bg: semantic.color.surfaceElevated; radius: semantic.radius.popup on top corners only; handle: 36 x 4 pill in semantic.color.border; padding: component.popup.padding; shadow: semantic.elevation.floating; scrim: semantic.color.overlay; zIndex: primitive.zIndex.overlay
- **Variants:** modal (scrim) | persistent (no scrim, peek height) | full-height
- **States:** collapsed (peek) | expanded | dragging | dismissing
- **Interaction:** drag handle and content drag; snap points at peek/half/full; swipe down dismisses; duration.slow with easing.standard on snap
- **Platform notes:** iOS: respects safe area bottom inset; Android: Material bottom sheet, back closes; web: converts to dialog.modal above 768px width
- **Anti-patterns:** sheet taller than 90% viewport without full-height variant | content scroll fighting sheet drag | missing safe-area padding
- **QA:** handle visible and >= 24 tall hit area | snap animation <= duration.slow | keyboard pushes sheet up on inputs
- **Code reuse hint:** BottomSheet with snapPoints prop; shares shell styling with dialog.modal

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

### `popup.confirm` — Confirm Dialog

- **Tokens (authoritative, `component.popup`):** radius=32 · outlineWidth=0 · outlineColor=transparent · shadow=none · padding=20 · maxWidth=480
- **Purpose:** Guard irreversible or costly actions (quit level, sell item, spend >=20% balance, delete account) with a clear primary and a safe decline.
- **States:** open | processing (primary shows spinner, both disabled) | closed
- **Code reuse hint:** PopupPanel compact variant
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#popup.confirm`

### `popup.offer` — Offer / Promo Popup

- **Tokens (authoritative, `component.popup`):** radius=32 · outlineWidth=0 · outlineColor=transparent · shadow=none · padding=20 · maxWidth=480
- **Purpose:** Present a time-limited or contextual bundle honestly: contents, real price, visible expiry, instant close.
- **States:** entering (>=1s after lobby interactive, max 1 auto per session after session 3) | open | expired (greys with 'Expired', never re-arms silently) | purchasing (store sheet) | closed
- **Code reuse hint:** PopupPanel + commerce
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#popup.offer`

## reward

### `reward.mission-item` — Mission Row

- **Tokens (authoritative, `component.card`):** radius=24 · borderWidth=1 · shadow=none · padding=16 · gap=12
- **Purpose:** One quest row with icon, title, progress, reward chip and a single action (Go / Claim).
- **States:** in-progress (Go) | claimable (Claim primary + one 1.02 pulse on entry) | claimed (check, saturation -40%, moves to bottom) | locked (unlocks at level N) | expired
- **Code reuse hint:** ListRow base + progress
- **Full row:** visual rules, variants, interaction, platform notes, anti-patterns and QA in `data/component-catalog.csv#reward.mission-item`

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
