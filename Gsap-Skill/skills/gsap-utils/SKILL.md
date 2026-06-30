---
name: gsap-utils
description: Official GSAP skill for gsap.utils — clamp, mapRange, normalize, interpolate, random, snap, toArray, wrap, pipe. Use when the user asks about gsap.utils, clamp, mapRange, random, snap, toArray, wrap, or helper utilities in GSAP.
license: MIT
---

# gsap.utils

## When to Use This Skill

Apply when writing or reviewing code that uses **gsap.utils** for math, array/collection handling, unit parsing, or value mapping in animations (e.g. mapping scroll to a value, randomizing, snapping to a grid, or normalizing inputs).

**Related skills:** Use with **gsap-core**, **gsap-timeline**, and **gsap-scrolltrigger** when building animations; CustomEase and other easing utilities are in **gsap-plugins**.

## Overview

**gsap.utils** provides pure helpers; no need to register. Use in tween vars (e.g. function-based values), in ScrollTrigger or Observer callbacks, or in any JS that drives GSAP. All are on **gsap.utils** (e.g. `gsap.utils.clamp()`).

**Omitting the value: function form.** Many utils accept the value to transform as the **last** argument. If you omit that argument, the util returns a **function** that accepts the value later. Use the function form when you need to clamp, map, normalize, or snap many values with the same config (e.g. in a mousemove handler or tween callback). **Exception: random()** — pass **true** as the last argument to get a reusable function (do not omit the value); see [random()](https://gsap.com/docs/v3/GSAP/UtilityMethods/random()).

```javascript
// With value: returns the result
gsap.utils.clamp(0, 100, 150); // 100

// Without value: returns a function you call with the value later
let c = gsap.utils.clamp(0, 100);
c(150);  // 100
c(-10);  // 0
```

## Clamping and Ranges

### clamp(min, max, value?)

Constrains a value between min and max. Omit **value** to get a function: `clamp(min, max)(value)`.

```javascript
gsap.utils.clamp(0, 100, 150); // 100
gsap.utils.clamp(0, 100, -10); // 0

let clampFn = gsap.utils.clamp(0, 100);
clampFn(150); // 100
```

### mapRange(inMin, inMax, outMin, outMax, value?)

Maps a value from one range to another. Use when converting scroll position, progress (0–1), or input range to an animation range. Omit **value** to get a function: `mapRange(inMin, inMax, outMin, outMax)(value)`.

```javascript
gsap.utils.mapRange(0, 100, 0, 500, 50);  // 250
gsap.utils.mapRange(0, 1, 0, 360, 0.5);   // 180 (progress to degrees)

let mapFn = gsap.utils.mapRange(0, 100, 0, 500);
mapFn(50);  // 250
```

### normalize(min, max, value?)

Returns a value normalized to 0–1 for the given range. Inverse of mapping when the target range is 0–1. Omit **value** to get a function: `normalize(min, max)(value)`.

```javascript
gsap.utils.normalize(0, 100, 50);   // 0.5
gsap.utils.normalize(100, 300, 200); // 0.5

let normFn = gsap.utils.normalize(0, 100);
normFn(50); // 0.5
```

### interpolate(start, end, progress?)

Interpolates between two values at a given progress (0–1). Handles numbers, colors, and objects with matching keys. Omit **progress** to get a function: `interpolate(start, end)(progress)`.

```javascript
gsap.utils.interpolate(0, 100, 0.5);       // 50
gsap.utils.interpolate("#ff0000", "#0000ff", 0.5); // mid color
gsap.utils.interpolate({ x: 0, y: 0 }, { x: 100, y: 50 }, 0.5); // { x: 50, y: 25 }

let lerp = gsap.utils.interpolate(0, 100);
lerp(0.5); // 50
```

## Random and Snap

### random(minimum, maximum[, snapIncrement, returnFunction]) / random(array[, returnFunction])

Returns a random number in the range **minimum**–**maximum**, or a random element from an **array**. Optional **snapIncrement** snaps the result to the nearest multiple (e.g. `5` → multiples of 5). **To get a reusable function**, pass **true** as the last argument (**returnFunction**); the returned function takes no args and returns a new random value each time. This is the only util that uses `true` for the function form instead of omitting the value.

```javascript
// immediate value: number in range
gsap.utils.random(-100, 100);        // e.g. 42.7
gsap.utils.random(0, 500, 5);        // 0–500, snapped to nearest 5

// reusable function: pass true as last argument
let randomFn = gsap.utils.random(-200, 500, 10, true);
randomFn();  // random value in range, snapped to 10
randomFn();  // another random value

// array: pick one value at random
gsap.utils.random(["red", "blue", "green"]);  // "red", "blue", or "green"
let randomFromArray = gsap.utils.random([0, 100, 200], true);
randomFromArray();  // 0, 100, or 200
```

**String form in tween vars:** use `"random(-100, 100)"`, `"random(-100, 100, 5)"`, or `"random([0, 100, 200])"`; GSAP evaluates it per target.

```javascript
gsap.to(".box", { x: "random(-100, 100, 5)", duration: 1 });
gsap.to(".item", { backgroundColor: "random([red, blue, green])" });
```

### snap(snapTo, value?)

Snaps a value to the nearest multiple of **snapTo**, or to the nearest value in an array of allowed values. Omit **value** to get a function: `snap(snapTo)(value)` (or `snap(snapArray)(value)`).

```javascript
gsap.utils.snap(10, 23);     // 20
gsap.utils.snap(0.25, 0.7);  // 0.75
gsap.utils.snap([0, 100, 200], 150); // 100 or 200 (nearest in array)

let snapFn = gsap.utils.snap(10);
snapFn(23); // 20
```

Use in tweens for grid or step-based animation:

```javascript
gsap.to(".x", { x: 200, snap: { x: 20 } });
```

### shuffle(array)

Returns a new array with the same elements in random order. Use for randomizing order (e.g. stagger from "random" with a copy).

```javascript
gsap.utils.shuffle([1, 2, 3, 4]); // e.g. [3, 1, 4, 2]
```

### distribute(config)

**Returns a function** that assigns a value to each target based on its position in the array (or in a grid). Used internally for advanced staggers; use it whenever you need values spread across many elements (e.g. scale, opacity, x, delay). The returned function receives `(index, target, targets)` — either call it manually or pass the result directly into a tween; GSAP will call it per target with index, element, and array.

**Config (all optional):**

| Property | Type | Description |
|----------|------|-------------|
| `base` | Number | Starting value. Default `0`. |
| `amount` | Number | Total to distribute across all targets (added to base). E.g. `amount: 1` with 100 targets → 0.01 between each. Use **each** instead to set a fixed step per target. |
| `each` | Number | Amount to add between each target (added to base). E.g. `each: 1` with 4 targets → 0, 1, 2, 3. Use **amount** instead to split a total. |
| `from` | Number \| String \| Array | Where distribution starts: index, or `"start"`, `"center"`, `"edges"`, `"random"`, `"end"`, or ratios like `[0.25, 0.75]`. Default `0`. |
| `grid` | String \| Array | Use grid position instead of flat index: `[rows, columns]` (e.g. `[5, 10]`) or `"auto"` to detect. Omit for flat array. |
| `axis` | String | For grid: limit to one axis (`"x"` or `"y"`). |
| `ease` | Ease | Distribute values along an ease curve (e.g. `"power1.inOut"`). Default `"none"`. |

**In a tween:** pass the result of `distribute(config)` as the property value; GSAP calls the function for each target with `(index, target, targets)`.

```javascript
// Scale: middle elements 0.5, outer edges 3 (amount 2.5 distributed from center)
gsap.to(".class", {
  scale: gsap.utils.distribute({
    base: 0.5,
    amount: 2.5,
    from: "center"
  })
});
```

**Manual use:** call the returned function with `(index, target, targets)` to get the value for that index.

```javascript
const distributor = gsap.utils.distribute({
  base: 50,
  amount: 100,
  from: "center",
  ease: "power1.inOut"
});
const targets = gsap.utils.toArray(".box");
const valueForIndex2 = distributor(2, targets[2], targets);
```

See [distribute()](https://gsap.com/docs/v3/GSAP/UtilityMethods/distribute/) for more.

## Units and Parsing

### getUnit(value)

Returns the unit string of a value (e.g. `"px"`, `"%"`, `"deg"`). Use when normalizing or converting values.

```javascript
gsap.utils.getUnit("100px");   // "px"
gsap.utils.getUnit("50%");     // "%"
gsap.utils.getUnit(42);        // "" (unitless)
```

### unitize(value, unit)

Appends a unit to a number, or returns the value as-is if it already has a unit. Use when building CSS values or tween end values.

```javascript
gsap.utils.unitize(100, "px");  // "100px"
gsap.utils.unitize("2rem", "px"); // "2rem" (unchanged)
```

### splitColor(color, returnHSL?)

Converts a color string into an array: **[red, green, blue]** (0–255), or **[red, green, blue, alpha]** (4 elements for RGBA when alpha is present or required). Pass **true** as the second argument (**returnHSL**) to get **[hue, saturation, lightness]** or **[hue, saturation, lightness, alpha]** (HSL/HSLA) instead. Works with `"rgb()"`, `"rgba()"`, `"hsl()"`, `"hsla()"`, hex, and named colors (e.g. `"red"`). Use when animating color components or building gradients. See [splitColor()](https://gsap.com/docs/v3/GSAP/UtilityMethods/splitColor/).

```javascript
gsap.utils.splitColor("red");                    // [255, 0, 0]
gsap.utils.splitColor("#6fb936");                // [111, 185, 54]
gsap.utils.splitColor("rgba(204, 153, 51, 0.5)"); // [204, 153, 51, 0.5] (4 elements)
gsap.utils.splitColor("#6fb936", true);          // [94, 55, 47] (HSL: hue, saturation, lightness)
```

## Arrays and Collections

### selector(scope)

Returns a scoped selector function that finds elements only within the given element (or ref). Use in components so selectors like `".box"` match only descendants of that component, not the whole document. Accepts a DOM element or a ref (e.g. React ref; handles `.current`).

```javascript
const q = gsap.utils.selector(containerRef);
q(".box");        // array of .box elements inside container
gsap.to(q(".circle"), { x: 100 });
```

### toArray(value, scope?)

Converts a value to an array: selector string (scoped to element), NodeList, HTMLCollection, single element, or array. Use when passing mixed inputs to GSAP (e.g. targets) and a true array is needed.

```javascript
gsap.utils.toArray(".item");           // array of elements
gsap.utils.toArray(".item", container); // scoped to container
gsap.utils.toArray(nodeList);          // [ ... ] from NodeList
```

### pipe(...functions)

Composes functions: **pipe(f1, f2, f3)(value)** returns f3(f2(f1(value))). Use when applying a chain of transforms (e.g. normalize → mapRange → snap) in a tween or callback.

```javascript
const fn = gsap.utils.pipe(
  (v) => gsap.utils.normalize(0, 100, v),
  (v) => gsap.utils.snap(0.1, v)
);
fn(50); // normalized then snapped
```

### wrap(min, max, value?)

Wraps a value into the range min–max (inclusive min, exclusive max). Use for infinite scroll or cyclic values. Omit **value** to get a function: `wrap(min, max)(value)`.

```javascript
gsap.utils.wrap(0, 360, 370);  // 10
gsap.utils.wrap(0, 360, -10);   // 350

let wrapFn = gsap.utils.wrap(0, 360);
wrapFn(370); // 10
```

### wrapYoyo(min, max, value?)

Wraps value in range with a yoyo (bounces at ends). Use for back-and-forth within a range. Omit **value** to get a function: `wrapYoyo(min, max)(value)`.

```javascript
gsap.utils.wrapYoyo(0, 100, 150); // 50 (bounces back)

let wrapY = gsap.utils.wrapYoyo(0, 100);
wrapY(150); // 50
```

## Best practices

- ✅ Omit the value argument to get a reusable function when the same range/config is used many times (e.g. scroll handler, tween callback): `let mapFn = gsap.utils.mapRange(0, 1, 0, 360); mapFn(progress)`.
- ✅ Use **snap** for grid-aligned or step-based values; use **toArray** when GSAP or your code needs a real array from a selector or NodeList.
- ✅ Use **gsap.utils.selector(scope)** in components so selectors are scoped to a container or ref.

## Do Not

- ❌ Assume **mapRange** / **normalize** handle units; they work on numbers. Use **getUnit** / **unitize** when units matter.
- ❌ Override or rely on undocumented behavior; stick to the documented API.

### Learn More

https://gsap.com/docs/v3/HelperFunctions
