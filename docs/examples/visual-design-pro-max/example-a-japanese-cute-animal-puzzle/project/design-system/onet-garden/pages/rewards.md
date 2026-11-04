<!-- generated-by: visual-direction vd.py 1.0.0; page: rewards; profile-hash: d350c253757e -->
# Rewards Page Overrides

> **PROJECT:** Onet Garden · **Page type:** reward reveal uses the slow motion tier and a full-screen celebratory overlay instead of the standard popup · **Created:** 2026-10-16
> ⚠️ Rules in this file **override** `MASTER.md` for this page only. Document deviations only.
> Every override needs a `reason`. Restating Master values is flagged by `vd.py validate`.

**Reason for this page file:** reward reveal uses the slow motion tier and a full-screen celebratory overlay instead of the standard popup

## Overrides

| Token / rule | Master value | Page value | Reason |
|---|---|---|---|
| `component.popup.enterDuration` | `{primitive.duration.base}` → 200ms | `{primitive.duration.reward}` → 750ms | the reward reveal is a T3 beat, not a T1 transition; `interaction-guidelines.md` ties 750 ms to medium rewards |
<!-- example: | component.tile.radius | {primitive.radius.lg} | {primitive.radius.md} | 6x8 grid leaves 2px between tiles at xl | -->

## Component remaps

- `popup.win` → full-screen celebratory overlay (no `component.popup.maxWidth`), reason: stars + chest + mascot do not fit a 360-wide panel on phone-s

## Intentional exceptions (page scope)

| Scope | Rule | Reason | Expires |
|---|---|---|---|
| reward-overlay | scrim at `primitive.opacity.scrimHeavy` (0.7) on neutral.900 instead of `semantic.color.overlay` (0.5); panel ignores `component.popup.maxWidth` 360 | full-screen reward beat; confetti must stay readable over the board | never |
<!-- Expires: an ISO date (YYYY-MM-DD) or the word never; expired rows are a validate warning -->

## Notes

- Overrides that remap a token to another existing token (`{a.b}` → `{c.d}`) are not drift; only literal values (hex, px, ms) count against the drift budget.

Hand-written for the docs example (see README.md, Verification level). The skeleton above the tables was created by `vd.py page`.
