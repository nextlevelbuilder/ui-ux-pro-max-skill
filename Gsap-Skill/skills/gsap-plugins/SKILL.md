---
name: gsap-plugins
description: Official GSAP skill for GSAP plugins — registration, ScrollToPlugin, ScrollSmoother, Flip, Draggable, Inertia, Observer, SplitText, ScrambleText, SVG and physics plugins, CustomEase, EasePack, CustomWiggle, CustomBounce, GSDevTools. Use when the user asks about a GSAP plugin, scroll-to, flip animations, draggable, SVG drawing, or plugin registration.
license: MIT
---

# GSAP Plugins

## When to Use This Skill

Apply when using or reviewing code that uses GSAP plugins: registering plugins, scroll-to, flip/FLIP animations, draggable elements, SVG (DrawSVG, MorphSVG, MotionPath), text (SplitText, ScrambleText), physics, easing plugins (CustomEase, EasePack, CustomWiggle, CustomBounce), or GSDevTools. ScrollTrigger has its own skill (gsap-scrolltrigger).

**Related skills:** For core tweens use **gsap-core**; for ScrollTrigger use **gsap-scrolltrigger**; for React use **gsap-react**.

## Licensing & Install (important)

Every GSAP plugin is **free**, including for commercial use. Since [Webflow's acquisition of GSAP](https://gsap.com/blog/webflow-GSAP/), Club GSAP is no longer a paid tier and **no plugin requires a membership, license key, or auth token** — this includes formerly Club-only plugins (**SplitText**, **MorphSVG**, etc.).

- ✅ Install everything from the public `gsap` npm package: `npm install gsap`. All plugins are included — import them as `gsap/SplitText`, `gsap/MorphSVGPlugin`, etc.
- ❌ Do **not** generate an `.npmrc` with a GreenSock auth token, suggest the private `npm.greensock.com` registry, or tell users to sign up for Club GSAP to access a plugin. Those instructions are outdated.

## Registering Plugins

Register each plugin once so GSAP (and bundlers) know to include it. Use **gsap.registerPlugin()** with every plugin used in the project:

```javascript
import gsap from "gsap";
import { ScrollToPlugin } from "gsap/ScrollToPlugin";
import { Flip } from "gsap/Flip";
import { Draggable } from "gsap/Draggable";

gsap.registerPlugin(ScrollToPlugin, Flip, Draggable);
```

- ✅ Register before using the plugin in any tween or API call.
- ✅ In React, register at top level or once in the app (e.g. before first useGSAP); do not register inside a component that re-renders. useGSAP is a plugin that needs to be registered before use.

## Scroll

### ScrollToPlugin

Animates scroll position (window or a scrollable element). Use for “scroll to element” or “scroll to position” without ScrollTrigger.

```javascript
gsap.registerPlugin(ScrollToPlugin);

gsap.to(window, { duration: 1, scrollTo: { y: 500 } });
gsap.to(window, { duration: 1, scrollTo: { y: "#section", offsetY: 50 } });
gsap.to(scrollContainer, { duration: 1, scrollTo: { x: "max" } });
```

**ScrollToPlugin — key config (scrollTo object):**

| Option | Description |
|--------|-------------|
| `x`, `y` | Target scroll position (number), or `"max"` for maximum |
| `element` | Selector or element to scroll to (for scroll-into-view) |
| `offsetX`, `offsetY` | Offset in pixels from the target position |

### ScrollSmoother

Smooth scroll wrapper (smooths native scroll). Requires ScrollTrigger and a specific DOM structure (content wrapper + smooth wrapper). Use when smooth, momentum-style scroll is needed. See GSAP docs for setup; register after ScrollTrigger. DOM structure would look like: 

```html
<body>
	<div id="smooth-wrapper">
		<div id="smooth-content">
			<!--- ALL YOUR CONTENT HERE --->
		</div>
	</div>
	<!-- position: fixed elements can go outside --->
</body>
```

## DOM / UI

### Flip

Capture state with `Flip.getState()`, then apply changes (e.g. layout or class changes), then use `Flip.from()` to animate from the previous state to the new state (FLIP: First, Last, Invert, Play). Use when animating between two layout states (lists, grids, expanded/collapsed).

```javascript
gsap.registerPlugin(Flip);

const state = Flip.getState(".item");
// change DOM (reorder, add/remove, change classes)
Flip.from(state, { duration: 0.5, ease: "power2.inOut" });
```

**Flip — key config (Flip.from vars):**

| Option | Description |
|--------|-------------|
| `absolute` | Use `position: absolute` during the flip (default: `false`) |
| `nested` | When true, only the first level of children is measured (better for nested transforms) |
| `scale` | When true, scale elements to fit (avoids stretch); default `true` |
| `simple` | When true, only position/scale are animated (faster, less accurate) |
| `duration`, `ease` | Standard tween options |

#### More information

https://gsap.com/docs/v3/Plugins/Flip

### Draggable

Makes elements draggable, spinnable, or throwable with mouse/touch. Use for sliders, cards, reorderable lists, or any drag interaction.

```javascript
gsap.registerPlugin(Draggable, InertiaPlugin);

Draggable.create(".box", { type: "x,y", bounds: "#container", inertia: true });
Draggable.create(".knob", { type: "rotation" });
```

**Draggable — key config options:**

| Option | Description |
|--------|-------------|
| `type` | `"x"`, `"y"`, `"x,y"`, `"rotation"`, `"scroll"` |
| `bounds` | Element, selector, or `{ minX, maxX, minY, maxY }` to constrain drag |
| `inertia` | `true` to enable throw/momentum (requires InertiaPlugin) |
| `edgeResistance` | 0–1; resistance when dragging past bounds |
| `cursor` | CSS cursor during drag |
| `onDragStart`, `onDrag`, `onDragEnd` | Callbacks; receive event and target |
| `onThrowUpdate`, `onThrowComplete` | Callbacks when inertia is active |

### Inertia (InertiaPlugin)

Works with Draggable for momentum after release, or track the inertia/velocity of any property of any object so that it can then seamlessly glide to a stop using a simple tween. Register with Draggable when using `inertia: true`:

```javascript
gsap.registerPlugin(Draggable, InertiaPlugin);
Draggable.create(".box", { type: "x,y", inertia: true });
```

Or track velocity of a property: 
```javascript
InertiaPlugin.track(".box", "x");
```

Then use `"auto"` to continue the current velocity and glide to a stop: 

```javascript
gsap.to(obj, { inertia: { x: "auto" } });
```

### Observer

Normalizes pointer and scroll input across devices. Use for swipe, scroll direction, or custom gesture logic without tying directly to scroll position like ScrollTrigger.

```javascript
gsap.registerPlugin(Observer);

Observer.create({
  target: "#area",
  onUp: () => {},
  onDown: () => {},
  onLeft: () => {},
  onRight: () => {},
  tolerance: 10
});
```

**Observer — key config options:**

| Option | Description |
|--------|-------------|
| `target` | Element or selector to observe |
| `onUp`, `onDown`, `onLeft`, `onRight` | Callbacks when swipe/scroll passes tolerance in that direction |
| `tolerance` | Pixels before direction is detected; default 10 |
| `type` | `"touch"`, `"pointer"`, or `"wheel"` (default: `"touch,pointer"`) |

## Text

### SplitText

Splits an element’s text into characters, words, and/or lines (each in its own element) for staggered or per-unit animation. Use when animating text character-by-character, word-by-word, or line-by-line. Returns an instance with **chars**, **words**, **lines** (and **masks** when `mask` is set). Restore original markup with **revert()** or let **gsap.context()** revert. Integrates with **gsap.context()**, **matchMedia()**, and **useGSAP()**. API: **SplitText.create(target, vars)** (target = selector, element, or array).

```javascript
gsap.registerPlugin(SplitText);

const split = SplitText.create(".heading", { type: "words, chars" });
gsap.from(split.chars, { opacity: 0, y: 20, stagger: 0.03, duration: 0.4 });
// later: split.revert() or let gsap.context() cleanup revert
```

With **onSplit()** (v3.13.0+), animations run on each split and on re-split when **autoSplit** is used; returning a tween/timeline from **onSplit()** lets SplitText clean up and sync progress on re-split:

```javascript
SplitText.create(".split", {
  type: "lines",
  autoSplit: true,
  onSplit(self) {
    return gsap.from(self.lines, { y: 100, opacity: 0, stagger: 0.05, duration: 0.5 });
  }
});
```

**SplitText — key config (SplitText.create vars):**

| Option | Description |
|--------|-------------|
| **type** | Comma-separated: `"chars"`, `"words"`, `"lines"`. Default `"chars,words,lines"`. Only split what is needed (e.g. `"words, chars"` if not using lines) for performance. Avoid chars-only without words/lines or use **smartWrap: true** to prevent odd line breaks. |
| **charsClass**, **wordsClass**, **linesClass** | CSS class on each split element. Append `"++"` to add an incremented class (e.g. `linesClass: "line++"` → `line1`, `line2`, …). |
| **aria** | `"auto"` (default), `"hidden"`, or `"none"`. Accessibility: `"auto"` adds `aria-label` on the split element and `aria-hidden` on line/word/char elements so screen readers read the label; `"hidden"` hides all from readers; `"none"` leaves aria unchanged. Use `"none"` plus a screen-reader-only duplicate if nested links/semantics must be exposed. |
| **autoSplit** | When `true`, reverts and re-splits when fonts finish loading or when the element width changes (and lines are split), avoiding wrong line breaks. **Animations must be created inside onSplit()** so they target the newly split elements; **return** the animation from **onSplit()** for automatic cleanup and time-sync on re-split. |
| **onSplit(self)** | Callback when split completes (and on each re-split if **autoSplit** is `true`). Receives the SplitText instance. Returning a GSAP tween or timeline enables automatic revert/sync of that animation when re-splitting. |
| **mask** | `"lines"`, `"words"`, or `"chars"`. Wraps each unit in an extra element with `overflow: clip` for mask/reveal effects. Only one type; access wrappers on the instance’s **masks** array (or use class `-mask` if a class is set). |
| **tag** | Wrapper element tag; default `"div"`. Use `"span"` for inline (note: transforms like rotation/scale may not render on inline elements in some browsers). |
| **deepSlice** | When `true` (default), nested elements (e.g. `<strong>`) that span multiple lines are subdivided so lines don’t stretch vertically. Only applies when splitting lines. |
| **ignore** | Selector or element(s) to leave unsplit (e.g. `ignore: "sup"`). |
| **smartWrap** | When splitting **chars** only, wraps words in a `white-space: nowrap` span to avoid mid-word line breaks. Ignored if words or lines are split. Default `false`. |
| **wordDelimiter** | Word boundary: string (default `" "`), RegExp, or `{ delimiter: RegExp, replaceWith: string }` for custom splitting (e.g. zero-width joiner for hashtags, or non-Latin). |
| **prepareText(text, parent)** | Function that receives raw text and parent element; return modified text before splitting (e.g. to insert break markers for languages without spaces). |
| **propIndex** | When `true`, adds a CSS variable with index on each split element (e.g. `--word: 1`, `--char: 2`). |
| **reduceWhiteSpace** | Collapse consecutive spaces; default `true`. From v3.13.0 also honors line breaks and can insert `<br>` for `<pre>`. |
| **onRevert** | Callback when the instance is reverted. |

**Tips:** Split only what is animated (e.g. skip chars if only animating words). For custom fonts, split after they load (e.g. `document.fonts.ready.then(...)`) or use **autoSplit: true** with **onSplit()**. To avoid kerning shift when splitting chars, use CSS `font-kerning: none; text-rendering: optimizeSpeed;`. Avoid `text-wrap: balance`; it can interfere with splitting. SplitText does not support SVG `<text>`.

**Learn more:** [SplitText](https://gsap.com/docs/v3/Plugins/SplitText/)

### ScrambleText

Animates text with a scramble/glitch effect. Use when revealing or transitioning text with a scramble.

```javascript
gsap.registerPlugin(ScrambleTextPlugin);

gsap.to(".text", {
  duration: 1,
  scrambleText: { text: "New message", chars: "01", revealDelay: 0.5 }
});
```

## SVG

### DrawSVG (DrawSVGPlugin)

Reveals or hides the stroke of SVG elements by animating `stroke-dashoffset` / `stroke-dasharray`. Works on `<path>`, `<line>`, `<polyline>`, `<polygon>`, `<rect>`, `<ellipse>`. Use when “drawing” or “erasing” strokes.

**drawSVG value:** Describes the **visible segment** of the stroke along the path (start and end positions), not “animate from A to B over time.” Format: `"start end"` in percent or length. Examples: `"0% 100%"` = full stroke; `"20% 80%"` = stroke only between 20% and 80% (gaps at both ends). The tween animates from the element’s **current** segment to the **target** segment — e.g. `gsap.to("#path", { drawSVG: "0% 100%" })` goes from whatever it is now to full stroke. Single value (e.g. `0`, `"100%"`) means start is 0: `"100%"` is equivalent to `"0% 100%"`. 

**Required:** The element must have a visible stroke — set `stroke` and `stroke-width` in CSS or as SVG attributes; otherwise nothing is drawn.

```javascript
gsap.registerPlugin(DrawSVGPlugin);

// draw from nothing to full stroke
gsap.from("#path", { duration: 1, drawSVG: 0 });
// or explicit segment: from 0–0 to 0–100%
gsap.fromTo("#path", { drawSVG: "0% 0%" }, { drawSVG: "0% 100%", duration: 1 });
// stroke only in the middle (gaps at ends)
gsap.to("#path", { duration: 1, drawSVG: "20% 80%" });
```

**Caveats:** Only affects stroke (not fill). Prefer single-segment `<path>` elements; multi-segment paths can render oddly in some browsers. Contents of `<use>` cannot be visually changed. **DrawSVGPlugin.getLength(element)** and **DrawSVGPlugin.getPosition(element)** return stroke length and current position.

**Learn more:** [DrawSVG](https://gsap.com/docs/v3/Plugins/DrawSVGPlugin)

### MorphSVG (MorphSVGPlugin)

Morphs one SVG shape into another by animating the `d` attribute (path data). Start and end shapes do not need the same number of points — MorphSVG converts to cubic beziers and adds points as needed. Use for icon-to-icon morphs, shape transitions, or path-based animations. Works on `<path>`, `<polyline>`, and `<polygon>`; `<circle>`, `<rect>`, `<ellipse>`, and `<line>` are converted internally or via **MorphSVGPlugin.convertToPath(selector | element)** (replaces the element in the DOM with a `<path>`).

**morphSVG value:** Can be a **selector** (e.g. `"#lightning"`), an **element**, **raw path data** (e.g. `"M47.1,0.8 73.3,0.8..."`), or for polygon/polyline a **points string** (e.g. `"240,220 240,70 70,70 70,220"`). For full config use the **object form** with **shape** as the only required property.

```javascript
gsap.registerPlugin(MorphSVGPlugin);

// convert primitives to path first if needed:
MorphSVGPlugin.convertToPath("circle, rect, ellipse, line");

gsap.to("#diamond", { duration: 1, morphSVG: "#lightning", ease: "power2.inOut" });
// object form:
gsap.to("#diamond", {
  duration: 1,
  morphSVG: { shape: "#lightning", type: "rotational", shapeIndex: 2 }
});

```

**MorphSVG — key config (morphSVG object):**

| Option | Description |
|--------|-------------|
| **shape** | _(Required.)_ Target shape: selector, element, or raw path string. |
| **type** | `"linear"` (default) or `"rotational"`. Rotational uses angle/length interpolation and can avoid kinks mid-morph; try it when linear looks wrong. |
| **map** | How segments are matched: `"size"` (default), `"position"`, or `"complexity"`. Use when start/end segments don’t line up; if none work, split into multiple paths and morph each. |
| **shapeIndex** | Offsets which point in the start path maps to the first point in the end path (avoids shape “crossing over” or inverting). Number for single-segment paths; **array** for multi-segment (e.g. `[5, 1, -8]`). Negative reverses that segment. Use **shapeIndex: "log"** once to log the auto-calculated value, then paste the number/array into the tween. **findShapeIndex(start, end)** (separate utility) provides an interactive UI to find a good value. Only applies to closed paths. |
| **smooth** | (v3.14+). Adds smoothing points. Number (e.g. `80`), `"auto"`, or object: `{ points: 40 \| "auto", redraw: true \| false, persist: true \| false }`. `redraw: false` keeps original anchors (perfect fidelity, less even spacing). `persist: false` removes added points when the tween ends. Use when the default morph looks jagged or unnatural. |
| **curveMode** | Boolean (v3.14+). Interpolates control-handle angle/length instead of raw x/y to avoid kinks on curves. Try if a morph has a mid-morph kink. |
| **origin** | Rotation origin for **type: "rotational"**. String: `"50% 50%"` (default) or `"20% 60%, 35% 90%"` for different start/end origins. |
| **precision** | Decimal places for output path data; default `2`. |
| **precompile** | Array of precomputed path strings (or use **precompile: "log"** once, copy from console). Skips expensive startup calculations; use for very complex morphs. Only for `<path>` (convert polygon/polyline first). |
| **render** | Function(rawPath, target) called each update — e.g. draw to canvas. RawPath is an array of segments (each segment = array of alternating x,y cubic bezier coords). |
| **updateTarget** | When using **render** (e.g. canvas-only), set **updateTarget: false** so the original `<path>` is not updated. **MorphSVGPlugin.defaultUpdateTarget** sets default. |

**Utilities:** **MorphSVGPlugin.convertToPath(selector | element)** converts circle/rect/ellipse/line/polygon/polyline to `<path>` in the DOM. **MorphSVGPlugin.rawPathToString(rawPath)** and **stringToRawPath(d)** convert between path strings and raw arrays. The plugin stores the original `d` on the target (e.g. for tweening back: `morphSVG: "#originalId"` or the same element).

**Tips:** For twisted or inverted morphs, set **shapeIndex** (use `"log"` or findShapeIndex()). For multi-segment paths, **shapeIndex** is an array (one value per segment). Precompile only when the first frame is slow; it does not fix jank during the tween (simplify the SVG or reduce size if needed).

**Learn more:** [MorphSVG](https://gsap.com/docs/v3/Plugins/MorphSVGPlugin)

### MotionPath (MotionPathPlugin)

Animates an element along an SVG path. Use when moving an object along a path (e.g. a curve or custom route).

```javascript
gsap.registerPlugin(MotionPathPlugin);

gsap.to(".dot", {
  duration: 2,
  motionPath: { path: "#path", align: "#path", alignOrigin: [0.5, 0.5] }
});
```

**MotionPath — key config (motionPath object):**

| Option | Description |
|--------|-------------|
| `path` | SVG path element, selector, or path data string |
| `align` | Path element or selector to align the target to |
| `alignOrigin` | `[x, y]` origin (0–1); default `[0.5, 0.5]` |
| `autoRotate` | Rotate element to follow path tangent |
| `curviness` | 0–2; path smoothing |

### MotionPathHelper

Visual editor for MotionPath (alignment, offset). Use during development to tune path alignment.

```javascript
gsap.registerPlugin(MotionPathPlugin, MotionPathHelperPlugin);

const helper = MotionPathHelper.create(".dot", "#path", { end: 0.5 });
// adjust in UI, then use helper.path or helper.getProgress() in your animation
```

## Easing

### CustomEase

Custom easing curves (cubic-bezier or SVG path). Use when a built-in ease is not enough. Basic usage is covered in gsap-core; register when using:

```javascript
gsap.registerPlugin(CustomEase);
const ease = CustomEase.create("name", ".17,.67,.83,.67");
gsap.to(".el", { x: 100, ease: ease, duration: 1 });
```

### EasePack

Adds more named eases (e.g. SlowMo, RoughEase, ExpoScaleEase). Register and use the ease names in tweens.

### CustomWiggle

Wiggle/shake easing. Use when a value should “wiggle” (multiple oscillations).

### CustomBounce

Bounce-style easing with configurable strength.

## Physics

### Physics2D (Physics2DPlugin)

2D physics (velocity, angle, gravity). Use when animating with simple physics (e.g. projectiles, bouncing).

```javascript
gsap.registerPlugin(Physics2DPlugin);

gsap.to(".ball", {
  duration: 2,
  physics2D: {
    velocity: 250,
    angle: 80,
    gravity: 500
  }
});
```

### PhysicsProps (PhysicsPropsPlugin)

Applies physics to property values. Use for physics-driven property animation.

```javascript
gsap.registerPlugin(PhysicsPropsPlugin);

gsap.to(".obj", {
  duration: 2,
  physicsProps: {
    x: { velocity: 100, end: 300 },
    y: { velocity: -50, acceleration: 200 }
  }
});
```

## Development

### GSDevTools

UI for scrubbing timelines, toggling animations, and debugging. Use during development only; do not ship. Register and create an instance with a timeline reference.

```javascript
gsap.registerPlugin(GSDevTools);
GSDevTools.create({ animation: tl });
```

## Other

### Pixi (PixiPlugin)

Integrates GSAP with PixiJS for animating Pixi display objects. Register when animating Pixi objects with GSAP.

```javascript
gsap.registerPlugin(PixiPlugin);

const sprite = new PIXI.Sprite(texture);
gsap.to(sprite, { pixi: { x: 200, y: 100, scale: 1.5 }, duration: 1 });
```

## Best practices

- ✅ Register every plugin used with **gsap.registerPlugin()** before first use.
- ✅ Use **Flip.getState()** → DOM change → **Flip.from()** for layout transitions; use **Draggable** + **InertiaPlugin** for drag with momentum.
- ✅ Revert plugin instances (e.g. `SplitTextInstance.revert()`) when components unmount or elements are removed.

## Do Not

- ❌ Use a plugin in a tween or API without registering it first (**gsap.registerPlugin()**).
- ❌ Ship GSDevTools or development-only plugins to production.

### Learn More

https://gsap.com/docs/v3/Plugins/
