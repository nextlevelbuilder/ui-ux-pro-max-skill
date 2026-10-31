<!-- generated-by: visual-direction vd.py 1.0.0; profile-hash: 73c0e76468b6 -->
# Interaction Guidelines — Pet Diary Redesign

Motion class `soft` · easing `ease-in-out-soft` · reduced motion: respect · unit `logical`.

## Durations (tokens.json#primitive.duration)

| Token | Value | Use |
|---|---|---|
| `primitive.duration.instant` | 0ms | state swap, no animation |
| `primitive.duration.fast` | 150ms | T0 input feedback (press, select, hover) |
| `primitive.duration.base` | 250ms | T1 transitions (open/close, move) |
| `primitive.duration.slow` | 400ms | T2 reveals and progress fills |
| `primitive.duration.reveal` | 600ms | screen / popup entrance |
| `primitive.duration.reward` | 650ms | T3 medium reward beat (small ≈ ×0.67, jackpot ≈ ×1.2) |
| `primitive.duration.ambient` | 3000ms | T4 idle loop period (breathing, shimmer) |

## Easing (tokens.json#primitive.easing)

| Role | Curve |
|---|---|
| `standard` | `cubic-bezier(0.4, 0, 0.2, 1)` |
| `enter` | `cubic-bezier(0, 0, 0.2, 1)` |
| `exit` | `cubic-bezier(0.4, 0, 1, 1)` |
| `emphasized` | `cubic-bezier(0.25, 0.1, 0.25, 1)` |

## Touch and pointer

- Minimum target `48`, recommended `48` (max across platforms mobile-ios, mobile-android).
- Press feedback within `primitive.duration.fast`; release inside bounds fires the action.
- Hover is a no-op on touch platforms; focus ring 3 / offset 2 in `semantic.color.focusRing`.

## States (tokens.json#semantic.state)

| State | Opacity | Offset Y | Shadow |
|---|---|---|---|
| hover | {primitive.opacity.hover} | 0 | — |
| pressed | {primitive.opacity.pressed} | 0 | {primitive.shadow.none} |
| focus | — | — | — |
| disabled | {primitive.opacity.disabled} | 0 | {primitive.shadow.none} |

## Reduced motion

- `prefers-reduced-motion` / platform accessibility setting → T3/T4 beats become instant state swaps with a ≤150 ms fade; T0/T1 keep opacity and colour changes only.
- Never flash more than 3 times per second; never require motion to understand state.

## App-specific

- Motion confirms, never decorates: every T2/T3 animation must change a state the user asked for.
- Lists and sheets use `primitive.easing.enter` / `exit`; page transitions ≤ `primitive.duration.reveal`.
- Full rules: `motion-direction.md` in the `visual-direction` skill references.
