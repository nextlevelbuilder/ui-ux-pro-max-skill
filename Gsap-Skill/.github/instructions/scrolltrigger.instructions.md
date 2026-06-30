---
applyTo: ["**/*scroll*", "**/*ScrollTrigger*", "**/scroll*"]
---

# ScrollTrigger — path-specific instructions

When writing or suggesting scroll-linked GSAP code (ScrollTrigger):

- Register the plugin once: `gsap.registerPlugin(ScrollTrigger)`.
- Use **scrub: true** (or a number) for scroll-driven progress; use **toggleActions** for discrete play/reverse. Do not use both on the same trigger.
- Put ScrollTrigger on the **timeline** or a **top-level tween**, not on a tween that is a child of a timeline (wrong: `tl.to(..., { scrollTrigger: {... } })`; right: `gsap.timeline({ scrollTrigger: {... } }).to(...)`).
- When **pinning**, do not animate the pinned element itself; animate its children. Use **pinSpacing: true** (default) so layout does not collapse.
- Prefer **transform** properties (`x`, `y`, `scale`, `rotation`) for the animated element; avoid animating layout properties when possible.
- For “fake” horizontal scroll (pin a section, content moves horizontally while scrolling vertically), use **containerAnimation** and set **ease: "none"** on the horizontal tween so scroll and position stay in sync.
- **start** / **end** format: `"triggerPosition viewportPosition"` (e.g. `"top center"`, `"bottom top"`). Use `endTrigger` if the end is based on a different element.
- Call **ScrollTrigger.refresh()** after DOM or layout changes that affect trigger positions (e.g. new content, fonts loaded). Viewport resize is handled automatically.
- Create ScrollTriggers in **top-to-bottom** page order, or set **refreshPriority** so they refresh in that order when creation order differs.
- When removing elements or changing routes (SPAs), **kill** ScrollTrigger instances: `ScrollTrigger.getAll().forEach(t => t.kill())` or kill by id. 
