# Motion Direction

Reference for the `visual-direction` skill. Turns `motion.class` and `motion.duration_scale` from the Visual Direction Profile (`vdp/1`) into concrete durations, easings and rules for games **and** apps. The GSAP skeletons in `data/motion.csv` of the `ui-ux-pro-max` skill remain the web source for hover/scroll/page-transition snippets; this file defines the hierarchy and the per-class scale that those snippets (and the Flutter/Flame/Unity equivalents) plug into.

Profile fields used: `motion.class` ∈ {static, snappy, soft, bouncy, dramatic}; `motion.duration_scale.{fast,base,slow}` (ms); `motion.easing` (free text, resolved by the table in §3); `motion.reduced_motion` ∈ {respect, ignore-decorative-only, ignore} — only `respect` is recommended; `product.kind`; `product.stack`.

---

## 1. Motion hierarchy (tiers)

Each tier has a fixed purpose, a duration band, and a rule for what happens when the band is exceeded. The band is absolute; `motion.class` moves the value *inside* the band (§2) but never outside it.

| Tier | Purpose | Duration band | Owner of the final state | If exceeded |
|---|---|---|---|---|
| T0 Feedback | prove the input was received (press, tap, toggle, tile select) | 80–150 ms | the control itself | feels laggy; players double-tap |
| T1 State change | a thing became another thing (tile matched, toggle flipped, tab switched, counter updated, card flipped) | 150–250 ms | the data model (the UI must show the final value by the end of the band) | state ambiguity; counters read wrong |
| T2 Navigation / transition | screen or popup enter/exit, sheet slide, level load reveal | 200–350 ms | the router | exit > 250 ms blocks the next tap; enter > 350 ms reads as loading |
| T3 Reward / celebration | stars, coin fly, chest, combo, level-up, jackpot | 400–900 ms per beat; escalation tiers in §1.1 | the celebration sequencer, **skippable** | > 1.2 s without skip = player taps through blindly |
| T4 Ambient / idle loop | mascot breathing, water shimmer, coin glint, cloud parallax, menu float | 1.5–6 s period, amplitude ≤ 2 % of element size (≤ 2 dp on tiles) | none (decorative) | distracts from the board; eats battery |
| T5 Instructional | tutorial hand, hint pulse, "jump to current" arrow | loop 1.2 s (tap) / `slow` x 2 (drag); stops on first correct input | the tutorial/hint controller | ignored by the player if it never stops |

Stacking rule: a single user action may trigger at most **one T0 + one T1 + one T3**. Two T3 beats in a row must be sequenced, not overlapped (second starts at ≥ 70 % of the first). T2 never overlaps T3 (celebration finishes or is skipped before navigation).

### 1.1 Reward escalation tiers (T3)

| Tier | Trigger examples | Total length (before skip allowed) | Elements | Haptic / audio | Particles (max, mid-tier device) | Screen effects |
|---|---|---|---|---|---|---|
| small | 1–2 stars; match of 3; mission claim; common chest item; daily reward day 1–6 | 400–500 ms | scale pop 1.0→1.15→1.0 on the reward; coin fly ≤ 12 coins | light haptic; 1 sfx | 20 | none |
| medium | 3 stars; combo x4–x6; rare item; day 7 reward; level-up | 600–750 ms | pop + ray burst behind item (rotate ≤ 6°/s) + 1-line caption ("Great!") | medium haptic; sfx + short sting | 60 | shake ≤ 4 dp, 2 cycles, ≤ 120 ms; **no** flash |
| jackpot | wheel jackpot; legendary/5-star pull; combo ≥ x7; chapter complete; first purchase bonus | 800–900 ms main beat + ≤ 300 ms hold; skippable at 1.2 s | anticipation (120 ms squash) → burst → item reveal with rarity frame → caption | heavy haptic (or 2 pulses); jingle ≤ 1.5 s | 150 | flash ≤ 120 ms at ≤ 60 % white; shake ≤ 6 dp; slow-motion ≤ 300 ms allowed in `dramatic` only |

Tier selection is by **rarity/magnitude**, not by mechanic (a common item from a chest gets `small`). The caption word set per tier is fixed per project (e.g. small: none; medium: "Great!" / "Nice!"; jackpot: "Amazing!" / "Jackpot!") so copy does not drift between screens.

---

## 2. `motion.class` → duration scale

Values are milliseconds. `fast/base/slow` are the three tokens written to `motion.duration_scale`; the remaining columns are derived and written to `tokens.json` `primitive.duration` so that code never invents a fourth number. Per CC-8 the token group carries `instant, fast, base, slow, reveal, reward, ambient`: `reward` = the **medium** reward beat of this table, `ambient` = the ambient period; `small ≈ reward × 0.67`, `jackpot ≈ reward × 1.2`. The *token* values for `fast/base/slow/reveal` are the `token-derivation.md` §1.10 row (they stay inside the bands below; `static` writes `0` for every token — the 80/120/150 here are the maximum fade an implementation may use for an un-animated state swap). `vd_tokens.py` emits these numbers; the audit rule `duration.off-scale` tolerates ±10 % of any listed value.

| `motion.class` | fast (T0) | base (T1) | slow (T2) | reward small / medium / jackpot (T3) | ambient period (T4) | overshoot allowed | character |
|---|---|---|---|---|---|---|---|
| `static` | 80 | 120 | 150 (crossfade only) | 0 / 0 / 0 — state swap + 150 ms fade; no particles | none | no | utility, kids-low-stim, accessibility-first; everything is a fade or an instant swap |
| `snappy` | 80 | 150 | 200 | 400 / 600 / 800 | 4000 | no | arcade, competitive, hyper-casual; ease-out only, no bounce |
| `soft` | 120 | 220 | 300 | 450 / 650 / 850 | 3000 | no | wellness, word, sorting, calm puzzle; ease-in-out, gentle scale |
| `bouncy` | 120 | 200 | 350 | 500 / 750 / 900 | 2500 | yes (≤ 1.15 scale, ≤ 8 dp translate) | cute cartoon, match-3, merge, kids; squash & stretch |
| `dramatic` | 150 | 300 | 500 (cap of band for exits is still 250: exits use base) | 500 / 750 / 900 + 300 hold | 2000 | yes (≤ 1.2 scale) | anime RPG, gacha, cinematic; anticipation + slow-mo |

Rules for profile authors:
- `motion.duration_scale` may deviate from the table by ± 20 % per token and must stay inside the tier bands of §1. `vd.py validate` checks the enum and numeric shape of `motion.duration_scale`; band checks are a `visual-audit` concern (`duration.off-scale`).
- `dramatic` exits still use `base` (300) — only *enters* and reward beats get `slow`.
- Gameplay input feedback (T0) never exceeds 150 ms in any class, including `dramatic`.
- `static` is not "no motion": T0 and T1 still exist as opacity/colour changes so the player sees their input registered.

---

## 3. Easing names per platform

Semantic easing roles map to concrete names. A profile's `motion.easing` free-text value resolves to one row of this table (e.g. `"spring-soft"` → the `bouncy` row).

| Role | Used for | CSS `cubic-bezier` | GSAP | Flutter `Curves.*` | Flame `EffectController` | Unity DOTween `Ease.*` / AnimationCurve |
|---|---|---|---|---|---|---|
| ease-out (standard exit of a press, snappy state change) | `snappy` T0/T1, all T2 enters | `cubic-bezier(0.25, 1, 0.5, 1)` (outQuart) | `power3.out` | `Curves.easeOutQuart` | `EffectController(duration: d, curve: Curves.easeOutQuart)` | `Ease.OutQuart` / `AnimationCurve.EaseInOut(0,0,1,1)` with tangent adjusted or custom keys (0,0,2,0)-(1,1,0,0) |
| ease-in-out (symmetric, calm) | `soft` T1/T2 | `cubic-bezier(0.65, 0, 0.35, 1)` (inOutCubic) | `power2.inOut` | `Curves.easeInOutCubic` | `curve: Curves.easeInOutCubic` | `Ease.InOutCubic` / `AnimationCurve.EaseInOut` |
| ease-in (exits only) | all T2 exits, popup dismiss | `cubic-bezier(0.5, 0, 0.75, 0)` (inQuart) | `power3.in` | `Curves.easeInQuart` | `curve: Curves.easeInQuart` | `Ease.InQuart` |
| overshoot / back (bouncy state change) | `bouncy` T1, popup enter, tile select | `cubic-bezier(0.34, 1.56, 0.64, 1)` (outBack) | `back.out(1.7)` | `Curves.easeOutBack` | `curve: Curves.easeOutBack` | `Ease.OutBack` (overshoot 1.7) |
| elastic / spring (reward pop, jackpot reveal) | `bouncy` T3, `dramatic` T3 reveal | approximate with `linear(...)` spring or GSAP | `elastic.out(1, 0.5)` | `Curves.elasticOut` (amplitude via `ElasticOutCurve(0.6)`) | `curve: ElasticOutCurve(0.6)` or `SequenceEffect([ScaleEffect.to(1.15), ScaleEffect.to(1.0)])` | `Ease.OutElastic` (amplitude 1, period 0.5) |
| expo in-out (cinematic) | `dramatic` T2 enters, slow-mo ramps | `cubic-bezier(0.87, 0, 0.13, 1)` (inOutExpo) | `expo.inOut` | `Curves.easeInOutExpo` | `curve: Curves.easeInOutExpo` | `Ease.InOutExpo` |
| linear | timer bar drain, progress fill, wheel tick audio sync | `linear` | `none` | `Curves.linear` | `curve: Curves.linear` | `Ease.Linear` |
| decelerate long (spin wheel, scroll settle) | wheel 2.5–4 s spin | `cubic-bezier(0.16, 1, 0.3, 1)` (outExpo) | `expo.out` | `Curves.easeOutExpo` | `curve: Curves.easeOutExpo` | `Ease.OutExpo` |

Class → default role: `static` → ease-out for fades; `snappy` → ease-out / ease-in; `soft` → ease-in-out / ease-in; `bouncy` → overshoot / elastic (T3) / ease-in (exits); `dramatic` → expo in-out (enters) / elastic (reveal) / ease-in (exits).

Platform notes:
- **Flutter / Flame:** write durations as `Duration(milliseconds: tokens.duration.base)`; one `AnimationController` per T2 transition; tile effects via `ScaleEffect`/`OpacityEffect`/`MoveEffect` with `EffectController(duration: seconds)` — Flame takes **seconds**, convert `ms / 1000`. Use `SequenceEffect` for escalation beats, `onComplete` to re-enable input. Particles: `ParticleSystemComponent` with `count` capped per §5.
- **Unity uGUI / UI Toolkit:** DOTween `SetEase`, `SetUpdate(true)` for UI that must animate while `Time.timeScale = 0` (pause menu). UI Toolkit: `transition-duration`/`transition-timing-function` in USS with `ease-out-cubic` etc.; the USS enum lacks back/elastic — use a `ValueAnimation` with `Easing.OutBack`. Particles via `ParticleSystem` with `maxParticles` set to the §5 cap.
- **Web (CSS / GSAP):** compositor-only properties (`transform`, `opacity`); `will-change` only on elements that animate within the next frame; `prefers-reduced-motion` via `matchMedia` as in `motion.csv`; GSAP `timeline()` for T3 beats with `.add(label)` so skip = `timeline.progress(1)`.
- **SwiftUI / Compose:** SwiftUI `.spring(response: 0.3, dampingFraction: 0.6)` ≈ `bouncy` T1; `.easeOut(duration:)` ≈ `snappy`; Compose `tween(durationMillis, easing = FastOutSlowInEasing)` ≈ `soft`, `spring(dampingRatio = Spring.DampingRatioMediumBouncy)` ≈ `bouncy`. Respect `UIAccessibility.isReduceMotionEnabled` / `Settings.Global.ANIMATOR_DURATION_SCALE`.

---

## 4. Rules

### 4.1 Motion must not hide business state
- The data model updates **first**; the animation plays *toward* the already-true value. The counter, balance, moves and objective numbers must display the final value no later than the end of the T1 band (≤ 250 ms), even if coins are still flying (fly animation lands on an already-updated counter and plays a small pulse, not a count-up from the old value).
- A purchase, claim or continue is confirmed by a state change visible within 300 ms (wallet number, button state, item ownership). Celebration may continue after, never instead.
- Popups appear only after the triggering gameplay effect has finished or been skipped: win/lose popup ≥ 600 ms after the last match effect starts, ≤ 1.5 s after it ends.
- The board never re-lays out behind a popup; if the next level must preload, it does so with the popup fully opaque (≥ 95 %) over it.
- A timer never visually pauses unless the game state is paused; a paused timer freezes digits on the first frame of the pause transition.
- Skipping a T3 beat jumps to the *final* state of every element in the beat (stars, counters, item list) — never leaves half-flown coins.

### 4.2 Reduced motion (`motion.reduced_motion: respect`)
When the OS setting is on (or the in-game toggle, §3.8 of `game-ui-patterns.md`):
- T0 keeps opacity/colour feedback (no scale, no translate).
- T1 becomes a ≤ 150 ms crossfade; tile match = fade out; no overshoot; no squash.
- T2 becomes a 150 ms crossfade; no slide, no scale.
- T3 drops particles, shake, flash, rays and slow-mo; keeps the final composition and a single 150 ms fade; audio and haptic remain (they carry the reward feeling).
- T4 ambient loops are disabled entirely (parallax stops; mascot holds a neutral frame).
- T5 instructional motion switches to a static pointer/arrow; the hint pulse becomes a steady outline.
- Informational motion that encodes state (timer bar drain, progress fill, cooldown ring) **remains** — it is not decoration. The last-10-seconds timer pulse remains (it is a warning) but as an opacity blink, not a scale pulse.
- Autoplaying wheels/chest openings run at the same length but as fades; the result is shown at the same time so that reduced-motion players are not faster or slower at claiming.

Profile values `ignore-decorative-only` and `ignore` are recorded for legacy projects but should produce a `vd.py validate` warning for `product.kind: game` with kids audiences.

### 4.3 Performance budget
- Animate **only** `transform` and `opacity` on the UI layer (web: no `width/height/top/left/box-shadow` animation; Flutter: `Transform`/`Opacity`/`FadeTransition`, not `AnimatedContainer` on size inside the board; Unity: avoid layout-group rebuilds, animate `RectTransform.localScale`/`CanvasGroup.alpha`, never `sizeDelta` per frame on the board).
- Frame budget 16.6 ms at 60 fps (8.3 ms at 120 Hz devices): UI animation work ≤ 2 ms per frame; the board simulation owns the rest. No more than 2 simultaneous full-screen effects (scrim + celebration layer).
- Particle caps (simultaneous alive particles, all emitters summed): low-end 60 · mid 150 · high 300. Small/medium/jackpot tiers in §1.1 are sized for mid; on low-end scale counts by 0.4, on high by 1.0 (never exceed the jackpot count — "more particles" is not "more reward").
- Max 1 shadow-blur animation per frame; prefer baked shadow sprites for `rendering.shadow` on moving tiles.
- Ambient loops: ≤ 10 % of visible tiles animate at once; parallax layers ≤ 3; mascot idle ≤ 12 fps sprite sheet or a single bone loop.
- Textures for effects ≤ 512 px per sheet on mobile; particle sprites ≤ 64 px.
- Every T3 beat has a hard stop: total timeline length is known before it starts, and a `skip` jumps to the end state (§4.1).

### 4.4 Never animate during gameplay input
While a pointer is down on the board, or within 100 ms after a board tap:
- No HUD element changes size, position or layout (badge numbers may change text).
- Tiles under or adjacent to the pointer do not move, scale (other than the T0 press feedback of the touched tile) or re-sort.
- Hint pulses pause; ambient tile wobble pauses on the touched tile and its neighbours.
- No popup, toast, offer or ad may open; queued items open ≥ 300 ms after pointer-up and only when no cascade/shuffle is in progress.
- Shuffle, cascade and gravity sequences **lock input** and show the locked state (HUD "Shuffling…" plate or dimmed boosters); input unlocks on the sequencer's `onComplete`, never on a timer guess.
- Timed modes: the timer never pauses for celebration (combo captions play over a running clock) unless the level is complete.
- Drag genres: the dragged ghost follows the pointer with ≤ 1 frame of smoothing; no spring lag on the ghost (spring is allowed on the *drop*).

### 4.5 Apps (non-game) — what changes
Same tiers, same class table. Differences: T3 is reserved for genuine achievements (onboarding complete, goal reached, payment success) and uses `small` or `medium` only; T4 is limited to loading indicators and hero illustrations; T5 is coach-marks only. Navigation transitions follow the platform (iOS push 350 ms ease-in-out, Android shared-axis 300 ms, web 200–250 ms); the class only scales within the band.

---

## 5. Class-specific do / don't

| Class | Do | Don't |
|---|---|---|
| `static` | instant state swaps + ≤ 150 ms fades; keep audio/haptic; keep informational motion | add "a little bounce" anywhere; use particles |
| `snappy` | ease-out everything; exits faster than enters (≈ 0.7x); crisp 1-frame match flash | overshoot; captions longer than 400 ms; rays |
| `soft` | ease-in-out; opacity-led transitions; scale ≤ 1.06 | shake; flash; squash & stretch |
| `bouncy` | overshoot on enter; squash 0.9/1.1 on tile land; coins arc, not straight lines | overshoot on exits (exits are ease-in); overshoot above 1.15; bounce the HUD plates |
| `dramatic` | anticipation (120 ms) before big reveals; slow-mo ≤ 300 ms; letterbox on jackpot (optional) | exits longer than 250 ms; dramatic beats on common rewards; slow-mo during a running timer |

---

## 6. QA criteria (screenshot / video reviewer)

Record with a 60 fps screen capture; check frames.

- [ ] Tap/press feedback visible within 150 ms of the touch frame (≤ 9 frames at 60 fps).
- [ ] After a match, counters show their final value by frame 15 (250 ms) even if coins are still flying.
- [ ] Popup enter completes within 350 ms; popup exit within 250 ms; the next screen is tappable on the frame after exit ends.
- [ ] Reward beats: small ≤ 500 ms, medium ≤ 750 ms, jackpot ≤ 900 ms + 300 ms hold; a tap at 1.2 s skips to the final state with no half-state elements.
- [ ] No two celebrations overlap by more than 30 % of the first's length.
- [ ] Particle count in any frame ≤ the device-tier cap (count sprites in a paused frame, or read the emitter cap in code).
- [ ] Shake amplitude ≤ 4 dp (medium) / 6 dp (jackpot); flash ≤ 120 ms and ≤ 60 % white.
- [ ] Reduced-motion capture: no particles, no scale/translate on T1–T3, timer bar and cooldown rings still animate, hand cursor static.
- [ ] During a pointer-down frame on the board, HUD bounding boxes identical to the previous frame.
- [ ] Shuffle/cascade: a tap during the sequence has no effect and the HUD shows the locked state.
- [ ] Ambient: ≤ 10 % of tiles moving in any frame; amplitude ≤ 2 dp.
- [ ] Easing matches the class: `snappy` curves end fast with no overshoot; `bouncy` shows ≤ 1 overshoot cycle; `soft` is symmetric; `dramatic` has a visible anticipation frame before jackpot reveals.
- [ ] Durations in code equal `tokens.json` `primitive.duration` values (audit rule `duration.off-scale`); no ad-hoc 337 ms.
- [ ] Spin wheel: ≥ 3 full turns, 2.5–4 s, ends with the pointer centred on a segment, no reverse creep.
