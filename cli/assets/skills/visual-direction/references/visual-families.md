# Visual Families — Art Direction Reference

Companion to `data/visual-styles.csv` (searched by `python3 scripts/vd.py styles "<query>" [--family <id>]`). Every style in the catalog belongs to exactly one of the ten
families below. A family is defined by **how form is drawn**, not by colour or theme: the same
pink can live in `cute-cartoon`, `candy-glossy` and `anime`. When a screen "feels off" the cause
is almost always that two families are present on it at once. This document tells you how to
recognise each family, what it is usually confused with, and what the mix looks like in practice
("drift smells"), so the audit and the profile builder can name the problem precisely.

Vocabulary used throughout:

- **Outline** — a drawn contour line. Specified as width in px at 1x and a colour rule.
- **Shade band** — the darker region that implies form. Specified by edge type (hard / soft) and
  colour logic (hue-shifted / tonal / grey).
- **Depth cue** — the one mechanism a family uses to lift an element off the page: hard offset
  shadow, soft shadow, side face, bevel, glow, paper edge, or none.
- **Tonal** — a darker or lighter version of the *same* hue (HSL lightness change, hue kept).

---

## cute-cartoon

**Styles:** japanese-cute-puzzle, cute-animal-onet, japanese-casual-game, soft-2d-cartoon,
cozy-pastel, kawaii-sticker

**Distinguishing traits**

| Axis | Rule |
|---|---|
| Shape | Rounded-blob silhouettes, superellipse tiles, convex panels; no acute angles; radius class lg–xl–pill. Heads 1.3–2x body width. |
| Outline | Present on characters and (usually) gameplay pieces: 2.5–4px, colour is a darker shade of the element's own fill (L −25 to −35), optionally hue-shifted toward purple. **Never #000.** Width is uniform; lines never taper. |
| Shading | flat, soft or soft-cel: at most one shade band, soft or hard edge, in the hue-shifted darker tone. One white highlight dot in eyes. |
| Depth cue | Hard offset shadow 3–6px in the outline colour under buttons; soft 12–18% black under popups only. |
| Palette | Pastel or mid-saturation base, 2–3 saturated accents reserved for CTA/reward/selection. |
| Typography | Rounded sans (Fredoka, Baloo 2, Nunito, M PLUS Rounded 1c, Zen Maru Gothic). Display 700–800, body 500–600. Title case or sentence case. |

Sub-dialects inside the family (allowed to co-exist within a project only if declared in the
profile): *outlined* (japanese-cute-puzzle, soft-2d-cartoon, kawaii-sticker) vs *outline-free
UI* (japanese-casual-game, cozy-pastel). Characters keep their outline in both.

**Commonly confused with**

- `candy-glossy` — the tell: candy-glossy has a *large radial specular* (25% of the element) and
  an inner light rim; cute-cartoon has at most a small top-left gloss ellipse and relies on the
  outline for definition. If you can see a reflection, it is candy-glossy.
- `anime` — the tell: anime outlines are near-black navy with line-weight variation and the
  shade band is hard-edged cel; cute-cartoon outlines are coloured, uniform, and shading is soft.
- `flat-modern` — the tell: flat-modern has no outlines at all and uses bottom-border "flat depth";
  cute-cartoon always outlines characters.

**Drift smells**

1. A popup with a 2px black (#000) border on a screen where the tiles have coloured outlines —
   someone used the default stroke colour.
2. Pill buttons on the home screen and 8px-radius rectangles on the shop screen — two radius
   classes with no declared exception.
3. A chibi mascot (2:1 head ratio) next to a realistically proportioned promotional character
   — two illustration systems on one screen.

---

## anime

**Styles:** anime-inspired-game-ui, cel-shaded-adventure

**Distinguishing traits**

| Axis | Rule |
|---|---|
| Shape | Angular: diagonal cuts (15–20°), parallelograms, pointed banners; radius class sm (2–10px). Speed-line motifs. |
| Outline | Characters: clean 2–4px line in a near-black **navy** (e.g. #1A1F3A, #1D3557), thicker on the silhouette than on interior lines. UI: either a 1px bright accent edge on active elements (anime-inspired-game-ui) or a 2px navy outline on everything (cel-shaded-adventure). |
| Shading | cel: hard-edged bands, 2–3 tones, shadow tone hue-shifted toward purple/blue, never grey. |
| Depth cue | Glow (accent, blur 12–16px) or hard navy offset; blurred black drop shadows are foreign. |
| Palette | Dark navy base with one hot accent (anime-inspired-game-ui) **or** off-white base with saturated primaries (cel-shaded-adventure). Rarity ladders are fixed and global. |
| Typography | Condensed geometric sans, often italic, uppercase with +4–5% tracking; bold display faces with white or navy outline. |

**Commonly confused with**

- `dark-fantasy` — the tell: dark-fantasy uses *bevelled metal frames* and serif type; anime uses
  thin bright edges, diagonal cuts and condensed sans. Both can be dark; only one has ornament.
- `cute-cartoon` — the tell: proportion and line colour. Anime characters are 1:4 to 1:7 with
  navy lines; cute-cartoon is 1:1.5 to 2:1 with coloured lines.

**Drift smells**

1. A pill-shaped CTA on a screen full of parallelogram tabs — the button was imported from a
   casual template.
2. A chibi version of a hero on the gacha banner next to the full-proportion version in the
   hero list, both outlined differently — two character pipelines.
3. A 0 8px 24px blurred black shadow under a diagonal-cut panel — depth cue from flat-modern or
   minimal-app leaking in; anime panels use glow or a hard offset.

---

## painterly

**Styles:** hand-painted-storybook (dark-fantasy-game-ui also renders painterly but belongs to
its own family because its UI chrome is bevelled metal, see below)

**Distinguishing traits**

| Axis | Rule |
|---|---|
| Shape | Organic, irregular, 1–2px hand-drawn wobble on edges; no perfect circles; panels look like paper scraps or boards. Radius class md but the radius is never geometric. |
| Outline | None as a vector stroke. Edges exist because values differ; at most a painted 1px darker edge at ~40% opacity. |
| Shading | painterly: visible brush, soft gradients, warm key light from one declared direction. |
| Depth cue | Soft *tinted* shadow (violet-brown 20–25%, blur 10–16px); never grey or black. |
| Palette | Earth tones, no pure white, no pure black; one cool contrast colour. 4–8% paper-grain overlay on every surface. |
| Typography | Hand-lettered or humanist display, serif body, dark sepia. Line-height 1.5+. |

**Commonly confused with**

- `paper-craft` — the tell: paper-craft has *hard* offset shadows at a constant angle and
  crisp cut edges; painterly has *soft* tinted shadows and brushy edges.
- `dark-fantasy` — the tell: dark-fantasy wraps its painterly art in metal frames with bevels;
  painterly uses paper and wood with no metal and no bevel.

**Drift smells**

1. A vector-flat icon set (Lucide, Material) sitting on parchment panels — icons must be
   hand-drawn with the same brush texture.
2. A pure-white (#FFFFFF) input field or popup on a cream-and-sepia screen — the brightest
   element on screen should still carry the paper tint.
3. A confetti burst in saturated primaries on the reward screen — celebration here is light
   bloom and sparkle motes, not geometric confetti.

---

## toy-3d

**Styles:** colorful-toy-3d

**Distinguishing traits**

| Axis | Rule |
|---|---|
| Shape | Chunky rounded 3D forms with bevelled edges (radius 12–15% of size). UI buttons have a visible **side face** 6–8px tall in a darker shade. Radius class lg. |
| Outline | None on 3D objects. None on UI (the side face does the job). |
| Shading | clay: soft matte-plastic specular, broad, from a single studio key light. |
| Depth cue | Contact shadow (ambient-occlusion look, 20% black, blur 8px) under objects; side face under buttons. |
| Palette | High-saturation primaries (S 70–85%), one solid colour per object class, cream or soft-sky background, white reserved for highlights. No gradient fills in UI. |
| Typography | Extra-bold rounded with a 3px darker extrude. |

**Commonly confused with**

- `cute-cartoon` — the tell: outlines. If anything is outlined it is not toy-3d.
- `candy-glossy` — the tell: toy-3d specular is broad and matte (plastic); candy-glossy is a tight
  bright reflection (glass/jelly).

**Drift smells**

1. A 2D outlined sprite (coin, star) dropped into the 3D scene — the reward icons came from a
   cartoon kit.
2. A flat button with no side face next to block buttons with 6px side faces — a late-added
   "Settings" or "Privacy" button.
3. A vertical gradient on a panel competing with the scene lighting — the panel is trying to
   be glossy; toy-3d panels are flat plates with a side face.

---

## flat-modern

**Styles:** flat-vector-casual, neon-hypercasual, playful-edtech-app, (reference-derived-custom
fallback)

**Distinguishing traits**

| Axis | Rule |
|---|---|
| Shape | Rounded rectangles 12–16px or pills; geometric category icons; strict grids. |
| Outline | None. Separation by fill contrast. Selected state is a 2px ring in primary. |
| Shading | flat. The only "shade" is a 3–4px **bottom border** in a darker fill tone on buttons and tiles ("flat depth"). Neon-hypercasual replaces the bottom border with glow. |
| Depth cue | Bottom border (casual/edtech) or glow (neon). Popups may have one soft shadow. Nothing else. |
| Palette | Light neutral base with 1 primary + 1 secondary + state colours; category hues at equal lightness. Neon variant inverts to violet-black base with 2–3 full-saturation accents. |
| Typography | Geometric or rounded sans (Poppins, Rubik, Nunito, Montserrat), 700 headings, 500–600 body. |

**Commonly confused with**

- `minimal-app` — the tell: minimal-app has *no* bottom-border depth, *no* category hue system,
  and uses stroke icons; flat-modern uses two-tone filled icons and bottom-border buttons.
- `cute-cartoon` (japanese-casual-game sub-dialect) — the tell: japanese-casual-game still
  outlines its mascot and stickers; flat-modern outlines nothing.

**Drift smells**

1. One screen's primary button has a 4px bottom border and another's has a 0 4px 12px soft
   shadow — two depth cues.
2. Six category colours where two sit at visibly different lightness (one pastel, one deep) —
   the palette was extended ad hoc.
3. Stroke (Lucide) icons in settings and two-tone filled icons in the game — acceptable only if
   declared as an intentional exception for the settings scope.

---

## dark-fantasy

**Styles:** dark-fantasy-game-ui

**Distinguishing traits**

| Axis | Rule |
|---|---|
| Shape | Rectangular panels with 6–8px chamfers, ornamental corner brackets, pointed banner bottoms. Radius class sm. |
| Outline | Frames carry a **bevel pair**: 2px dark edge (L −35) + 1px inner light bevel (gold 40% / iron 30%). Character art has no outline. |
| Shading | painterly on art; metallic gradients (gold 3-stop, iron 2-stop) on chrome. |
| Depth cue | Deep shadows (50–60% black), inset shadows on slots, teal glow for magic/interactive. 20% vignette on every screen. |
| Palette | Warm near-black base (never #000), desaturated crimson, gold, parchment text, teal reserved for magic. |
| Typography | Serif display (Cinzel, Cormorant) in parchment or gold gradient with 1px dark outline; small-caps labels with +6% tracking. |

**Commonly confused with**

- `anime` — the tell: ornament and serif. Dark-fantasy has brackets, bevels and serif; anime has
  diagonal cuts, thin edges and condensed sans.
- `painterly` — the tell: metal. If the frame is bevelled metal it is dark-fantasy.

**Drift smells**

1. A flat rounded button (no bevel, 12px radius) inside an ornate bracketed popup — a system
   dialog pattern leaked into the game.
2. A gold gradient on an ordinary "Settings" label — gold is reserved for frames, premium
   currency and top rarity.
3. A pure #000 background behind a panel while other screens use the warm near-black — the
   overlay colour was not tokenised.

---

## retro-pixel

**Styles:** pixel-retro-arcade

**Distinguishing traits**

| Axis | Rule |
|---|---|
| Shape | Everything on an integer pixel grid at a fixed scale (3x–4x). Square corners or 1-pixel notches. Radius class none. |
| Outline | 1 native pixel in the palette's darkest blue-black; selective on sprites; UI boxes use a double border (1px light top-left, 1px dark bottom-right). |
| Shading | pixel: 3–4 tone ramps per colour, dithering for gradients, no anti-aliasing. |
| Depth cue | 1-pixel hard offset shadow. No blur anywhere. |
| Palette | Fixed 16–32 colour palette; no colour outside it, ever; dark blue base rather than black. |
| Typography | Pixel fonts only, integer scaled, uppercase titles. |

**Commonly confused with**

- `flat-modern` — the tell: any anti-aliased edge, any non-integer scale, any vector font means
  it is flat-modern wearing a pixel costume.

**Drift smells**

1. A sprite rotated 15° with anti-aliased edges — rotation must be pre-drawn as frames.
2. A smooth 0 → 100% fade-in on a popup — retro transitions are frame-stepped (3–4 discrete
   opacity steps or an instant swap).
3. A score counter in Inter or Roboto beside a pixel-font title — mixed font technologies.

---

## candy-glossy

**Styles:** glossy-candy-match3, premium-casual-game

**Distinguishing traits**

| Axis | Rule |
|---|---|
| Shape | Rounded jelly/candy forms, pills, bubbly panels 24–28px, bevelled store badges. Radius class md–lg. |
| Outline | A **rim pair**: 2px outer rim in own hue L −30 + 1px inner light rim (white 25–30%). Not an outline in the cartoon sense; it reads as an edge of a glass object. |
| Shading | glossy: large radial specular (white 70% → 0) covering ~25% of the element top-left, plus a small bright dot; buttons get a gloss top half with a hard edge at 50%. |
| Depth cue | Hard offset 4–5px in the darker rim colour **plus** a soft 25–30% black shadow; popups 40–45% black with a dim overlay. Two shadows are normal here and nowhere else. |
| Palette | Deep purple or navy base; piece hues equally spaced at equal S and L; pink primary; gold strictly for premium. Every interactive surface has a 2-stop vertical gradient (≤15% L delta). |
| Typography | Chunky display with gradient fill and 2px dark outline; white body on dark. |

**Commonly confused with**

- `cute-cartoon` — the tell: gradient + specular. If every button has a gradient and a gloss it
  is candy-glossy; cute-cartoon buttons are flat fills with an outline.
- `toy-3d` — the tell: specular size and sharpness. Candy is a tight bright reflection; toy is a
  broad matte one.

**Drift smells**

1. One matte (flat fill, no specular) piece type on a board of glossy pieces — usually the
   last-added special piece.
2. A gold gradient on the "Play" button — gold has leaked out of the premium tier.
3. A white, light-mode settings dialog over the purple board — a platform default dialog.

---

## paper-craft

**Styles:** paper-cutout

**Distinguishing traits**

| Axis | Rule |
|---|---|
| Shape | Cut edges with deliberate 1–2px jitter; layered rectangles with a visible 2–3px paper edge; corner radii intentionally varied within 8–14px; tags, tabs, tape. |
| Outline | None drawn. A 1px *lighter* paper edge on top of each layer. |
| Shading | flat, with 5–8% paper-fibre texture on every fill. No gradients. |
| Depth cue | **Hard** offset cast shadow 2px 3px 0 at 18% black, constant 45° angle on every layer; lifted elements may add one soft 10% shadow. |
| Palette | Muted craft tones (S 35–55%), one brighter accent, cut-paper white (#FDFBF5), dark slate text. |
| Typography | Hand-cut / stencil display, humanist body; headings sit on paper tags. |

**Commonly confused with**

- `painterly` — the tell: shadow hardness. Paper-craft shadows are hard and offset at a fixed
  angle; painterly shadows are soft and tinted.
- `flat-modern` — the tell: texture and jitter. Flat-modern edges are vector-perfect; paper-craft
  edges wobble and carry fibre texture.

**Drift smells**

1. A layer with a 0 6px 20px blurred shadow among layers with 2px 3px hard shadows — depth cue
   from minimal-app.
2. Two identical, pixel-perfect copies of the same tag — paper is cut by hand; duplicates must
   vary by at least 1px of jitter or rotation.
3. A neon or fully saturated accent on an otherwise muted palette — the reward screen was built
   from a different kit.

---

## minimal-app

**Styles:** minimal-modern-mobile

**Distinguishing traits**

| Axis | Rule |
|---|---|
| Shape | Rectangles with 10–12px radius, 20px sheet corners, pills only for chips/toggles; 1px hairline dividers; 16–24px gutters. |
| Outline | None decorative. 1px grey-200 border on inputs and on shadowless cards; 2px focus ring. |
| Shading | flat. Elevation by a 3–4% lightness delta between surface and background. |
| Depth cue | At most one shadow level on cards (0 1px 2px 6%) and one on sheets. Never coloured shadows. |
| Palette | White/near-white base, one brand primary under 10% of screen area, 5-step grey ramp, semantic state colours only. |
| Typography | System font first (SF Pro / Roboto / Inter), scale 12/14/16/20/24/32, weights 400/500/600, sentence case. |
| Icons | 1.5–2px stroke outline icons (Lucide, SF Symbols, Material Symbols Outlined); filled only for the selected tab. |

**Commonly confused with**

- `flat-modern` — the tell: bottom-border buttons, two-tone filled icons and a category hue
  system belong to flat-modern. Minimal-app has none of those.
- `cute-cartoon` (cozy-pastel) — the tell: cozy-pastel uses tinted shadows and 24–32px radii;
  minimal-app uses grey hairlines and 12px radii.

**Drift smells**

1. A second brand colour appearing on a single screen (e.g. a purple "Pro" badge on a blue app)
   without being a semantic state colour.
2. Every card carrying a shadow *and* a border — pick one depth cue per card class.
3. A celebratory confetti screen with gold gradients after completing a task — game reward
   grammar in an app context.

---

## Why consistency ≠ sameness

A consistent product is not one where every screen looks identical. Gameplay, menus and reward
moments have different jobs and are *expected* to differ. The question the audit must answer is
whether a difference is **declared and systematic** (intentional variation) or **accidental and
local** (drift). The five rules below draw that line concretely. Every intentional variation
must be recorded in `style-profile.json → intentional_exceptions` with a `scope` and a `reason`;
anything not recorded there is drift by definition.

### Rule 1 — Vary the *amount*, never the *mechanism*, of a depth cue

A family owns exactly one depth mechanism (hard offset, soft shadow, side face, bevel, glow,
paper edge). Screens may scale it — gameplay tiles get a 3px hard offset, a popup gets 6px — but
they may not swap it. *Intentional:* `scope: popup, rule: hard offset 6px instead of 4px, reason:
popups float above the board.* *Drift:* a popup with a 0 8px 24px blurred shadow on a screen
whose buttons use hard offsets.

### Rule 2 — Radius may step down for density, never up for emphasis

Gameplay grids are dense; a smaller radius class on tiles than on buttons is a legitimate,
declared exception (`scope: gameplay-hud, rule: tiles use lg instead of xl, reason: 10x14 grid`).
Going the other way — a single "special" button made pill-shaped on a screen of md-radius
buttons to make it pop — is drift. Emphasis comes from colour and scale (Rule 4), not from a new
silhouette.

### Rule 3 — Reward screens may raise saturation one step and add motion, but not new hues

The reward palette is the base palette pushed: accent at +10–15% saturation, gold only if the
style already defines gold, confetti limited to the 3–4 palette hues already in play, motion class
one notch stronger (`soft → bouncy`, `snappy → dramatic`) for ≤2 seconds. *Intentional:* mascot
scaled 1.1, accent-coloured sparkle, 260ms overshoot. *Drift:* a rainbow confetti asset, a new
"celebration orange" that appears nowhere else, or a 3D-rendered chest in a 2D outlined game.

### Rule 4 — Hierarchy within a screen is expressed by scale and colour weight, not by family switch

A primary CTA may be larger (56px vs 48px), use the primary fill while secondaries use surface
fill, and be the only element with an idle shine. It may **not** be glossy on a flat screen,
outlined on an outline-free screen, or set in a different type family. If a single element
needs a different rendering model to stand out, the base style is too loud and should be quieted,
not the element escalated.

### Rule 5 — Menus and system surfaces may be quieter than gameplay, but must be drawn with the same pen

Settings, privacy, account and store screens are allowed to drop decoration: fewer accents, no
mascots, no textures, smaller type. That is intentional *reduction*. What they must keep is the
family's drawing rules: the same outline colour logic (or absence of outline), the same radius
class, the same icon construction (filled two-tone vs stroke), the same depth cue, the same font
families. *Intentional:* settings list rows in surface colour with no shadows, declared as `scope:
settings, rule: no outline on list rows, reason: text density`. *Drift:* a settings page built
from the platform's default Material or Cupertino widgets with stroke icons and 4dp radii in a
game whose every other screen is xl-radius outlined cartoon.

**Operational test for the audit:** for any two screens, list (a) outline rule, (b) radius
class, (c) shading, (d) depth cue, (e) icon construction, (f) display + body font. If any item
differs and no `intentional_exceptions` entry covers that scope, raise a finding. If the
difference is only in magnitude (sizes, counts, saturation step, motion duration) and stays
within the family's stated ranges, it is variation, not drift.
