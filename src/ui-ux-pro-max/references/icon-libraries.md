# Icon & Animation Library Selection Guide

Free for commercial use, **no visible attribution required on the website**. Libraries requiring visible credit (Font Awesome Free CC BY 4.0, Lordicon free tier) are excluded.

## License Quick Reference

| License | Commercial | Website Attribution | Obligation |
|---------|-----------|-------------------|------------|
| MIT | ✅ | Not required | Keep LICENSE in source/dist |
| ISC | ✅ | Not required | Same as MIT, shorter text |
| Apache 2.0 | ✅ | Not required | Keep LICENSE; note modifications |

All three require only that the license text stays in source/distribution files — nothing on the front-end.

---

## 1. Static Icon Sets

| Library | License | Count | Notes |
|---------|---------|-------|-------|
| [Lucide](https://lucide.dev/) | ISC | 1 500+ | Feather fork, React/Vue/Svelte packages. **Default pick** |
| [Phosphor Icons](https://phosphoricons.com/) | MIT | 9 000+ | Six weights (thin → fill), high style consistency |
| [Tabler Icons](https://tabler.io/icons) | MIT | 5 900+ | Large set, strong for admin/dashboard UI |
| [Material Symbols](https://fonts.google.com/icons) | Apache 2.0 | 2 500+ | Variable font, continuous weight/fill axis; SVG download available |
| [Remix Icon](https://remixicon.com/) | Apache 2.0 | 3 000+ | Must note modifications per Apache 2.0 |
| [Bootstrap Icons](https://icons.getbootstrap.com/) | MIT | 2 000+ | Framework-agnostic pure SVG |
| [Iconoir](https://iconoir.com/) | MIT | 1 600+ | Official React/RN/Flutter/Figma exports |
| [Heroicons](https://heroicons.com/) | MIT | 300+ | Tailwind official, best fit for Tailwind projects |
| [Ionicons](https://ionic.io/ionicons) | MIT | 1 300+ | iOS + Android dual-style |

## 2. Hover Micro-Animation Icon Sets

Hover/focus triggers built-in — no animation engine needed.

| Library | License | Notes |
|---------|---------|-------|
| [lucide-animated](https://lucide-animated.com/) | MIT | 350+ React components, extends Lucide style |
| [AnimateIcons](https://animateicons.in/) | MIT | 542+, path-level animation, hover/focus/programmatic trigger |

## 3. Morph Engines (Icon A → Icon B)

Shape interpolation layer — different category from the above.

| Library | License | Size | Notes |
|---------|---------|------|-------|
| [morphicons](https://www.morphicons.com/) | MIT | 6.5 KB gzip | Stroke icons, spring physics. React/Vue/Svelte/RN/Astro/vanilla |
| [flubber](https://github.com/veltman/flubber) | MIT | ~10 KB | D3 ecosystem, arbitrary path morph with split/merge. BYO tween |
| [lottie-web](https://github.com/airbnb/lottie-web) | MIT | ~250 KB | After Effects export; morph designed in the editor. Needs art assets |
| [GSAP MorphSVGPlugin](https://gsap.com/docs/v3/Plugins/MorphSVGPlugin/) | GreenSock No-Charge | — | All plugins free since 2025. Only restriction: cannot resell in a GSAP-competing product |

## Decision Tree

1. **General web icons** → Lucide (ISC, best ecosystem)
2. **Hover micro-animation** → lucide-animated (matches Lucide style)
3. **Two-icon morph** (hamburger ↔ X, play ↔ pause) → morphicons (6.5 KB, lightest)
4. **Complex custom morph** → flubber, or GSAP MorphSVGPlugin
5. **Massive icon count needed** → Phosphor (9 000+) or Tabler (5 900+)

**Consistent combo:** `Lucide` + `lucide-animated` + `morphicons` — all on 24×24 grid.

## Existing Skill Default

This skill's `icons.csv` uses **Phosphor** as the primary library (9 000+ icons, six weights) and **Heroicons** as fallback. That pairing remains the default for projects already using Phosphor. For new projects, pick from the decision tree above based on actual needs.

## Office Documents (Word / PowerPoint)

Only static icon sets (§1) work — download SVG and insert directly. Hover animations (§2) and morph engines (§3) require a browser runtime.

- PowerPoint: Insert → Picture → select SVG → right-click "Convert to Shape" → recolor/decompose
- For slide transitions that morph between icons, use PowerPoint's built-in **Morph** transition instead of any JS library
