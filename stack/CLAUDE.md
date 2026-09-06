# CLAUDE.md — Website Design Stack

This repository is a **ready-to-use environment that makes Claude Code good at website
design**. When you (Claude) do any UI, web page, landing page, component, or visual-polish
work in a project that uses this stack, follow the workflow below. It combines a *knowledge*
layer (what to build), a *taste* layer (making it distinctive), and a *feedback* layer
(actually seeing the rendered result and fixing it).

## The design loop (follow in order)

1. **PLAN with data — `ui-ux-pro-max`.** Before writing markup, get a concrete design
   system. Run the generator, then pull specifics per surface:
   ```bash
   python3 <skill>/scripts/search.py "<product> <industry> <keywords>" --design-system -p "Project"
   python3 <skill>/scripts/search.py "<query>" --domain style|color|typography|ux|landing|web-vitals
   ```
   Use it for: product-type patterns, color tokens, font pairings, UX anti-patterns,
   landing structure, and Core Web Vitals budgets. Treat its output as the source of truth
   for tokens (color, type, spacing).

2. **COMMIT to an aesthetic — `frontend-design`.** Do not sample the safe center of the
   training distribution. Answer four questions first — *purpose, tone, constraints,
   differentiation* — pick ONE tone and execute it precisely. Avoid the three AI-slop
   defaults (cream + serif + terracotta; near-black + acid accent; hairline broadsheet)
   unless the brief explicitly asks. Spend boldness in **one** signature element; keep the
   rest quiet.

3. **BUILD.** Implement with the chosen tokens. Match the surrounding code's conventions.
   For component-driven stacks, use the **shadcn** MCP to search/add components instead of
   hand-rolling primitives.

4. **SEE IT — Playwright / Chrome DevTools MCP.** You are not done when the code compiles.
   Open the page in a real browser, screenshot it, read the console, exercise interactive
   states (hover, focus, open menus, submit forms), and resize the viewport. Fix what you
   see — z-index, animation timing, layout shift, overflow. This feedback loop is the whole
   point of the stack; a change you have not looked at is not finished.

5. **REVIEW — `/design-review` (the `design-review` subagent).** Before you call a UI change
   complete, run the design-review subagent. It drives Playwright across mobile→ultrawide
   viewports, checks WCAG 2.1 AA (contrast, focus order, keyboard traps), responsive
   integrity, and interaction states, and returns ranked findings. Fix Blocker/High
   findings before finishing.

## Quality floor (never ship below this)

- **Responsive:** no horizontal scroll at 375 / 768 / 1024 / 1440 px; content reflows, not shrinks.
- **Accessible:** visible `:focus-visible` on every interactive element; WCAG AA contrast
  (4.5:1 text, 3:1 large text / UI); semantic landmarks; labelled controls; `prefers-reduced-motion` respected.
- **Performant:** stable layout (no CLS from unsized media/fonts), lazy-load below-fold
  images, `font-display: swap`, avoid render-blocking. Check against the `web-vitals` domain.
- **Intentional copy:** active voice, sentence case, name things by what users recognize.

## What's wired in this repo

| Layer | Tool | Where |
|-------|------|-------|
| Knowledge | `ui-ux-pro-max` skill | installed via `scripts/setup.sh` (plugin) |
| Taste | `frontend-design` skill | installed via `scripts/setup.sh` (plugin) |
| Component gen | `shadcn` MCP | `.mcp.json` |
| Visual feedback | `@playwright/mcp` + `chrome-devtools-mcp` | `.mcp.json` |
| Automated review | `design-review` subagent + `/design-review` command | `.claude/agents`, `.claude/commands` |
| Standalone audit | `scripts/design-audit.mjs` (multi-viewport screenshots) | `scripts/`, CI in `.github/workflows` |

See `docs/STACK.md` for why each tool is here, `docs/SETUP.md` to install, and
`docs/WORKFLOW.md` for a worked end-to-end example.

## Notes

- `<skill>` above resolves to the installed skill path (e.g. `.claude/skills/ui-ux-pro-max`
  or the plugin location). The skill's own `SKILL.md` tells you the exact command form.
- Optional: 21st.dev **Magic** MCP (`@21st-dev/magic`) generates React components from a
  prompt but needs an API key — see `docs/SETUP.md`. It is intentionally left out of the
  default `.mcp.json` so the stack works with zero secrets.
