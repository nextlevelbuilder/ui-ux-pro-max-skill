---
applyTo: ["**/*.tsx", "**/*.jsx", "**/components/**"]
---

# GSAP in React — path-specific instructions

When writing or suggesting GSAP code in React/JSX/TSX files:

- Prefer **useGSAP()** from `@gsap/react` over raw `useEffect` for GSAP setup. Register the hook once: `gsap.registerPlugin(useGSAP)` (and any other plugins used).
- Pass a **scope** (ref to container) so selectors are scoped: `useGSAP(() => { ... }, { scope: containerRef })`. This avoids animating elements outside the component.
- When targeting by ref, pass the **DOM element** (e.g. `ref.current`), not the ref object. Wrong: `gsap.to(myRef, ...)`. Right: `gsap.to(myRef.current, ...)`. With useGSAP, the scope ref limits selectors to that subtree.
- Rely on useGSAP’s automatic **cleanup** on unmount (reverts animations and kills ScrollTriggers). Do not leave ScrollTriggers or timelines running after unmount.
- Use **contextSafe** (returned from useGSAP) to wrap callbacks like `onComplete` so they no-op after unmount and avoid React state-update warnings.
- By default useGSAP runs once (empty dependency array). To re-run when deps change, pass `{ dependencies: [dep1, dep2] }` or `{ revertOnUpdate: true }` as the second argument. Put animation logic in the callback, not in a separate effect.
- If not using useGSAP, use **gsap.context()** in useEffect and return a cleanup that calls `ctx.revert()`.
