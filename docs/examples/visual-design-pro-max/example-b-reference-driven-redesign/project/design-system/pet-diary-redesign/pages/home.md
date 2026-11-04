<!-- generated-by: visual-direction vd.py 1.0.0; page: home; profile-hash: 73c0e76468b6 -->
# Home Page Overrides

> **PROJECT:** Pet Diary Redesign · **Page type:** quick-action tiles use the two secondary tints (blue, mint) that the global palette rule reserves for category tiles only (reference rule-8, context:home) · **Created:** 2026-10-16
> ⚠️ Rules in this file **override** `MASTER.md` for this page only. Document deviations only.
> Every override needs a `reason`. Restating Master values is flagged by `vd.py validate`.

**Reason for this page file:** quick-action tiles use the two secondary tints (blue, mint) that the global palette rule reserves for category tiles only (reference rule-8, context:home)

## Overrides

| Token / rule | Master value | Page value | Reason |
|---|---|---|---|
| `component.card.padding` | `{primitive.spacing.4}` → 16 | `{primitive.spacing.5}` → 20 | the three quick-action cards are 3-up with a centred 48 icon tile; 16 makes the tile touch the card edge on phone-s (reference uses 20 12) |
<!-- example: | component.tile.radius | {primitive.radius.lg} | {primitive.radius.md} | 6x8 grid leaves 2px between tiles at xl | -->

## Component remaps

- `nav.bottom-bar` active item → `chip.filter` selected look (pill plate at brand 12 % alpha), reason: reference rule-7 'peach pill + orange icon/label'

## Intentional exceptions (page scope)

| Scope | Rule | Reason | Expires |
|---|---|---|---|
| home-quick-actions | icon tiles use `primitive.color.secondary.500` (#BFDBFE, 玩耍) and mint #BBF7D0 (健康) — mint is outside `tokens.json` | observed in obs-3 / rule-8 (`context:home`); add a mint ramp to `palette.seeds` before shipping | 2026-12-31 |
<!-- Expires: an ISO date (YYYY-MM-DD) or the word never; expired rows are a validate warning -->

## Notes

- Overrides that remap a token to another existing token (`{a.b}` → `{c.d}`) are not drift; only literal values (hex, px, ms) count against the drift budget.

Hand-written for the docs example (see README.md, Verification level). The skeleton above the tables was created by `vd.py page`.
