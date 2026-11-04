<!-- generated-by: visual-direction vd.py 1.0.0; page: shop; profile-hash: d350c253757e -->
# Shop Page Overrides

> **PROJECT:** Onet Garden · **Page type:** limited-time offer cards need a saturated promo accent and a countdown chip that the menu never shows · **Created:** 2026-10-16
> ⚠️ Rules in this file **override** `MASTER.md` for this page only. Document deviations only.
> Every override needs a `reason`. Restating Master values is flagged by `vd.py validate`.

**Reason for this page file:** limited-time offer cards need a saturated promo accent and a countdown chip that the menu never shows

## Overrides

| Token / rule | Master value | Page value | Reason |
|---|---|---|---|
| `component.card.radius` | `{semantic.radius.container}` → 24 | `{semantic.radius.popup}` → 32 | the single hero offer card is a popup-class object (catalog `popup.offer`: radius one step looser, ≤ 28–32); regular pack cards keep 24 |
<!-- example: | component.tile.radius | {primitive.radius.lg} | {primitive.radius.md} | 6x8 grid leaves 2px between tiles at xl | -->

## Component remaps

- `commerce.shop-item` hero variant → `popup.offer` rules for the one 'Best value' card, reason: one hero per shop screen (catalog `commerce.shop-item`)
- offer-card outline → `primitive.color.accent.700` (#CA9D0A, already in the ramp) instead of `semantic.color.border` (#FFDDAC), reason: the gold outline is the only cue separating the reward-class offer from regular packs

## Intentional exceptions (page scope)

| Scope | Rule | Reason | Expires |
|---|---|---|---|
| shop-countdown-chip | `hud.chip` fill uses `semantic.color.warning` (#F5A524) instead of surface | the chip must read as 'expiring' at a glance; warning is the contract's expiry colour and the palette strategy allows a third saturated accent for reward moments | 2026-12-31 |
<!-- Expires: an ISO date (YYYY-MM-DD) or the word never; expired rows are a validate warning -->

## Notes

- Overrides that remap a token to another existing token (`{a.b}` → `{c.d}`) are not drift; only literal values (hex, px, ms) count against the drift budget.

Hand-written for the docs example (see README.md, Verification level). The skeleton above the tables was created by `vd.py page`.
