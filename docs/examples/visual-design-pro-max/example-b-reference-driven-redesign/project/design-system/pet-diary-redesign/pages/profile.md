<!-- generated-by: visual-direction vd.py 1.0.0; page: profile; profile-hash: 73c0e76468b6 -->
# Profile Page Overrides

> **PROJECT:** Pet Diary Redesign · **Page type:** settings rows are grouped lists: the destructive sign-out row uses semantic.color.danger instead of the brand orange that carries every other emphasis · **Created:** 2026-10-16
> ⚠️ Rules in this file **override** `MASTER.md` for this page only. Document deviations only.
> Every override needs a `reason`. Restating Master values is flagged by `vd.py validate`.

**Reason for this page file:** settings rows are grouped lists: the destructive sign-out row uses semantic.color.danger instead of the brand orange that carries every other emphasis

## Overrides

| Token / rule | Master value | Page value | Reason |
|---|---|---|---|
| `component.card.radius` | `{semantic.radius.container}` → 24 | `{primitive.radius.xl}` → 16 | grouped settings lists stack 4–6 rows per card; 24 wastes 8 per group on a utility screen |
<!-- example: | component.tile.radius | {primitive.radius.lg} | {primitive.radius.md} | 6x8 grid leaves 2px between tiles at xl | -->

## Component remaps

- `button.primary` → `button.destructive` for 'sign out' and 'delete diary', reason: catalog `confirm.destructive` + `button.destructive` own `semantic.color.danger`; reference rule-1 reserves brand orange for emphasis, so a page must remap the component rather than recolour the primary button

## Intentional exceptions (page scope)

| Scope | Rule | Reason | Expires |
|---|---|---|---|
| profile-settings | grouped settings rows use `menu.list` density (44 rows) instead of card spacing | settings is a utility screen; the reference shows no settings screen (not derivable) | 2026-12-31 |
<!-- Expires: an ISO date (YYYY-MM-DD) or the word never; expired rows are a validate warning -->

## Notes

- Overrides that remap a token to another existing token (`{a.b}` → `{c.d}`) are not drift; only literal values (hex, px, ms) count against the drift budget.

Hand-written for the docs example (see README.md, Verification level). The skeleton above the tables was created by `vd.py page`.
