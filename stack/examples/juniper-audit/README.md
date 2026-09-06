# Worked example — auditing a production marketing site

This is a **real run** of `scripts/design-audit.mjs` against a live single-page marketing site
(a financial-services firm's homepage), captured to show what the heuristic layer of the stack
produces before you wire it into your own project.

## How it was produced

```bash
# serve the site, then audit it over HTTP (not file://, so asset/CORS noise is realistic)
python3 -m http.server 8099          # in the site directory
node scripts/design-audit.mjs --url http://localhost:8099/ --out examples/juniper-audit
```

## What's here

- [`report.md`](./report.md) — ranked findings + console health
- [`report.json`](./report.json) — the same, machine-readable (what CI consumes)
- [`screenshots/`](./screenshots) — full-page capture at all six viewport tiers (360 → 1920 px)

## Reading the results

The site is genuinely well-built (design tokens, self-hosted fonts, `prefers-reduced-motion`,
scroll-reveal). The audit still surfaced three actionable items — exactly the kind a human
misses on a quick look:

| Finding | Severity | Why it matters |
|---------|----------|----------------|
| 2–3 sampled interactive elements show no visible focus indicator | High | Keyboard users can't see where they are — WCAG 2.4.7 |
| 14 tap targets < 44×44 px on mobile | Medium | Small touch targets → mis-taps on phones |
| ~1 text node below AA contrast (approximate) | Medium | Lead to verify by hand; contrast is estimated from the nearest opaque background |

The single console error is a `404` for one asset — worth chasing, but not a layout defect.

## Two things this example teaches about the tooling

1. **Serve over HTTP, not `file://`.** Opening via `file://` produces a wall of font-CORS
   errors that are pure artifacts (browsers block cross-origin font fetches from `null` origin).
   The numbers above are from a real HTTP serve, so the console is clean.

2. **Full-page capture + aggressive scroll-reveal don't fully mix.** The script auto-scrolls to
   trigger `IntersectionObserver` reveals before shooting, which recovers most content — but a
   page that reveals sections only on fine-grained scroll can still show a blank band in a
   single full-page screenshot. That's both a tooling limit **and** a real robustness signal
   (the same content is invisible to some crawlers, print, and any non-interactive capture).
   For those pages, the interactive **`/design-review`** subagent — which scrolls naturally,
   waits, and interacts — is the more reliable check. Heuristics catch the mechanical defects;
   the subagent judges the experience.

## The point

This is the *fast, automatic* half of the stack (also runs in CI). The *full* review —
interaction flows, visual taste, edge cases — is the `design-review` subagent invoked with
`/design-review <url>`. Use both: heuristics to gate merges, the subagent to raise the bar.
