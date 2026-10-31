<!-- generated-by: visual-direction vd.py 1.0.0; page: gameplay; profile-hash: d350c253757e -->
# Gameplay Page Overrides

> **PROJECT:** Onet Garden · **Page type:** board tiles need a tighter radius than menu cards · **Created:** 2026-10-16
> ⚠️ Rules in this file **override** `MASTER.md` for this page only. Document deviations only.
> Every override needs a `reason`. Restating Master values is flagged by `vd.py validate`.

**Reason for this page file:** board tiles need a tighter radius than menu cards

## Overrides

| Token / rule | Master value | Page value | Reason |
|---|---|---|---|
| `component.tile.radius` | `{semantic.radius.tile}` → 12 | `{primitive.radius.md}` → 8 | portrait board 6 across × 8 down at tile 53 (375 wide) / 56 (390, 430): 12 is 21–23 % of the tile height = xl class (CC-5); catalog `board.tile` asks for one step tighter than `shape.radius_class` (xl → lg, 12–20 %) → 8 = 14–15 % |
| `component.hud.chip.shadow` | `0 2px 0 #56505E, 0 4px 6px rgba(46,42,50,.12)` | `{primitive.shadow.none}` | `interaction-guidelines.md` Game-specific: no shadows on HUD plates, readability during board motion |
<!-- example: | component.tile.radius | {primitive.radius.lg} | {primitive.radius.md} | 6x8 grid leaves 2px between tiles at xl | -->

## Component remaps

- `board.tile-selected` → outline-only variant when reduced motion is on, reason: catalog `board.tile-selected` states; scale pulse is dropped

## Intentional exceptions (page scope)

| Scope | Rule | Reason | Expires |
|---|---|---|---|
<!-- Expires: an ISO date (YYYY-MM-DD) or the word never; expired rows are a validate warning -->

## Notes

- Overrides that remap a token to another existing token (`{a.b}` → `{c.d}`) are not drift; only literal values (hex, px, ms) count against the drift budget.

- Board arithmetic (AD-1): tile = min(56, floor((W − 2 × 16 − 5 × 4) / 6)) with `semantic.spacing.screenGutter` 16 and master `component.tile.gap` 4 → 375: 53 (board 338 × 452), 390 / 430: 56 (356 × 476). Cell pitch 57 / 60 ≥ 48, so no density exception from `game-ui-patterns.md` §1.2 is needed.

Hand-written for the docs example (see README.md, Verification level). The skeleton above the tables was created by `vd.py page`.
