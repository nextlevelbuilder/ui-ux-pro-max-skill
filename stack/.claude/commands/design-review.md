---
description: Run the 7-phase design review (WCAG AA, responsive, interaction) on a page or URL
argument-hint: [url-or-file] [optional focus, e.g. "mobile nav" or "checkout flow"]
---

Use the **design-review** subagent to audit the target below. Drive a real browser via the
Playwright MCP, screenshot each viewport tier, and return ranked findings (Blockers → Nitpicks).

Target: $1
Focus (optional): $2

If no target was given, ask for the running dev-server URL (or a file path). If a browser
cannot be opened, fall back to `node scripts/design-audit.mjs` and report only the heuristic
findings, clearly labeled as such. Fix Blockers and High-severity findings before reporting the
work as complete.
