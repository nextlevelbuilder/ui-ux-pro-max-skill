<!-- generated-by: visual-direction vd.py 1.0.0; page: diary; profile-hash: 73c0e76468b6 -->
# Diary Page Overrides

> **PROJECT:** Pet Diary Redesign · **Page type:** the log is a dense chronological list: rows drop the card elevation and use a 1 px border divider so eight entries fit above the fold · **Created:** 2026-10-16
> ⚠️ Rules in this file **override** `MASTER.md` for this page only. Document deviations only.
> Every override needs a `reason`. Restating Master values is flagged by `vd.py validate`.

**Reason for this page file:** the log is a dense chronological list: rows drop the card elevation and use a 1 px border divider so eight entries fit above the fold

## Overrides

| Token / rule | Master value | Page value | Reason |
|---|---|---|---|
| `component.card.radius` | `{semantic.radius.container}` → 24 | `{primitive.radius.xl}` → 16 | 24 on a 56-high row reads as a pill and collides with the time label; 16 keeps the reference's 'cards 20–28, tiles 12–14' ladder for a row-height element |
<!-- example: | component.tile.radius | {primitive.radius.lg} | {primitive.radius.md} | 6x8 grid leaves 2px between tiles at xl | -->

## Component remaps

- `card.default` → `list.item` for diary rows, reason: catalog `list.item` already defines the leading time label and the 1 divider instead of a card frame

## Intentional exceptions (page scope)

| Scope | Rule | Reason | Expires |
|---|---|---|---|
| diary-list | rows drop `component.card.shadow` (elevation none) and use a 1 divider (`primitive.outline.thin`) instead of the 2 peach outline (`semantic.color.border` #FED7AA) | the log is a dense chronological list; elevation on every row halves the rows above the fold; the outline stays on the day-group header card | never |
<!-- Expires: an ISO date (YYYY-MM-DD) or the word never; expired rows are a validate warning -->

## Notes

- Overrides that remap a token to another existing token (`{a.b}` → `{c.d}`) are not drift; only literal values (hex, px, ms) count against the drift budget.

Hand-written for the docs example (see README.md, Verification level). The skeleton above the tables was created by `vd.py page`.
