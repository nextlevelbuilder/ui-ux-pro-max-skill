<!-- generated-by: visual-direction vd.py 1.0.0; profile-hash: d350c253757e -->
# Interaction Guidelines — Onet Garden

Motion class `bouncy` · easing `spring-soft` · reduced motion: respect · unit `logical`.

## Durations (tokens.json#primitive.duration)

| Token | Value | Use |
|---|---|---|
| `primitive.duration.instant` | 0ms | state swap, no animation |
| `primitive.duration.fast` | 120ms | T0 input feedback (press, select, hover) |
| `primitive.duration.base` | 200ms | T1 transitions (open/close, move) |
| `primitive.duration.slow` | 350ms | T2 reveals and progress fills |
| `primitive.duration.reveal` | 600ms | screen / popup entrance |
| `primitive.duration.reward` | 750ms | T3 medium reward beat (small ≈ ×0.67, jackpot ≈ ×1.2) |
| `primitive.duration.ambient` | 2500ms | T4 idle loop period (breathing, shimmer) |

## Easing (tokens.json#primitive.easing)

| Role | Curve |
|---|---|
| `standard` | `cubic-bezier(0.22, 1, 0.36, 1)` |
| `enter` | `cubic-bezier(0.34, 1.56, 0.64, 1)` |
| `exit` | `cubic-bezier(0.36, 0, 0.66, -0.56)` |
| `emphasized` | `cubic-bezier(0.68, -0.6, 0.32, 1.6)` |

## Touch and pointer

- Minimum target `48`, recommended `48` (max across platforms mobile-ios, mobile-android).
- Press feedback within `primitive.duration.fast`; release inside bounds fires the action.
- Hover is a no-op on touch platforms; focus ring 3 / offset 2 in `semantic.color.focusRing`.

## States (tokens.json#semantic.state)

| State | Opacity | Offset Y | Shadow |
|---|---|---|---|
| hover | {primitive.opacity.hover} | 0 | — |
| pressed | {primitive.opacity.pressed} | 4 | {primitive.shadow.none} |
| focus | — | — | — |
| disabled | {primitive.opacity.disabled} | 0 | {primitive.shadow.none} |

## Reduced motion

- `prefers-reduced-motion` / platform accessibility setting → T3/T4 beats become instant state swaps with a ≤150 ms fade; T0/T1 keep opacity and colour changes only.
- Never flash more than 3 times per second; never require motion to understand state.

## Game-specific

- Gameplay input feedback (T0) never exceeds 150 ms in any motion class.
- Reward tiers by magnitude, not mechanic: small / medium / jackpot; captions and particle caps are fixed per project.
- HUD stays readable during board motion: no shadows on HUD plates, numerals ≥ 16 logical px.
- Genre touch rules (Onet Animal Puzzle): Tiles min 44x44 logical even on 10x14 boards (scale the board to fit, never shrink tiles below 40); selection feedback within 1 frame; link path visible 120-200ms; booster buttons 64px with 8px gap; tap only, no gestures
- Key interactions: tap-select-tile, tap-second-tile-to-link, path-draw-feedback, booster-tap, shuffle, hint
- Reward loop: Level clear -> 1-3 stars by remaining time -> coins -> boosters; daily login chest; collection album unlocks animal species
- Full rules: `motion-direction.md` and `game-ui-patterns.md` in the `visual-direction` skill references.
