# The Stack — why each tool is here

AI design fails in three predictable ways. Each layer of this stack fixes one.

| Failure mode | Fix | Tool |
|--------------|-----|------|
| Generic, templated look ("AI slop") | Force an aesthetic commitment | `frontend-design` |
| Vague, inconsistent tokens & patterns | Ground decisions in a real database | `ui-ux-pro-max` |
| Never sees the result → ships broken UI | Give the agent eyes | Playwright / Chrome DevTools MCP |
| Reinventing primitives | Pull proven components | shadcn MCP |
| "Looks fine to me" self-assessment | Independent, rigorous review | `design-review` subagent |

## 🧠 Knowledge — `ui-ux-pro-max`

A searchable design-intelligence toolkit: **84 UI styles, 192 color palettes, 73 font
pairings, 99 UX guidelines, 25 chart types, a Core Web Vitals dataset, and 22 tech stacks**,
plus a design-system generator that turns a product brief into concrete tokens. It's the
answer to "what should this actually look like, and what are the anti-patterns?"

- Repo: <https://github.com/nextlevelbuilder/ui-ux-pro-max-skill> · License: MIT
- Install: `npx ui-ux-pro-max-cli init --ai claude`
- Use: `python3 <skill>/scripts/search.py "<brief>" --design-system` and `--domain <domain>`

## 🎨 Taste — `frontend-design` (official Anthropic)

~50 lines of markdown that stop Claude from sampling the safe center of its training data. It
forces four decisions — *purpose, tone, constraints, differentiation* — before any CSS, names
three "AI-slop" defaults to avoid, and pushes boldness into a single signature element.

- Repo: <https://github.com/anthropics/claude-code/tree/main/plugins/frontend-design>
- Install: `/plugin install frontend-design@anthropics/claude-code`

`ui-ux-pro-max` decides *what's correct*; `frontend-design` decides *what's distinctive*. Use both.

## 🧩 Components — shadcn MCP

Browse, search, and install shadcn/ui components (and other registries) by natural language,
instead of hand-rolling accessible primitives. Best for React/Next/Vue/Svelte projects.

- Docs: <https://ui.shadcn.com/docs/mcp> · Command: `npx shadcn@latest mcp`

## 👁️ Visual feedback — Playwright MCP + Chrome DevTools MCP

The single biggest lever. Claude connects to a **real Chromium**, navigates, clicks, resizes,
screenshots, reads the console, and takes an accessibility snapshot — so it can catch and fix
its own z-index bugs, animation-timing errors, overflow, and layout shift. Chrome DevTools MCP
adds deep performance/network/CLS profiling.

- Playwright MCP: <https://github.com/microsoft/playwright-mcp> — `npx @playwright/mcp@latest`
- Chrome DevTools MCP: <https://github.com/ChromeDevTools/chrome-devtools-mcp> — `npx chrome-devtools-mcp@latest`

## ✅ Automated review — `design-review` subagent

A senior-reviewer subagent (`.claude/agents/design-review.md`) that runs a 7-phase audit over a
live page: interaction states, responsiveness across 6 viewport tiers, visual polish, WCAG 2.1
AA, edge cases, and console health. Invoke with `/design-review <url>`. The heuristic subset
also runs headless in CI via `scripts/design-audit.mjs`.

## Optional add-ons (not in default `.mcp.json`)

- **Figma Dev Mode MCP** — read a frame's tokens/layout to generate matching code, and push
  Claude-built UI back to the canvas as editable layers. Needs the Figma desktop app + Dev Mode.
  <https://help.figma.com/hc/en-us/articles/39888612464151-Claude-Code-and-Figma-Set-up-the-MCP-server>
- **21st.dev Magic MCP** — generate React components from a prompt ("v0 in your editor"). Needs
  an API key. <https://github.com/21st-dev/magic-mcp>

Both are opt-in (see `docs/SETUP.md`) so the base stack runs with zero secrets.
