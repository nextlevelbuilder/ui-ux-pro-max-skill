# Claude Website Design Stack

A ready-to-clone Claude Code project that makes the agent **genuinely good at website
design** — not by hoping for better output, but by wiring in the three things generic AI
design is missing: a **knowledge** layer, a **taste** layer, and a **visual feedback** layer.

> Most AI design fails because the model never *sees* what it built and has no opinionated
> point of view. This repo fixes both: Claude plans with a real design database, commits to
> a distinctive aesthetic, then opens the page in a browser and iterates on what it sees —
> and self-reviews against WCAG AA before finishing.

## The stack

| Layer | Tool | What it adds |
|-------|------|--------------|
| 🧠 **Knowledge** | [`ui-ux-pro-max`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | 84 UI styles, 192 color palettes, 73 font pairings, 99 UX rules, Core Web Vitals, 22 stacks — searchable, turned into a concrete design system |
| 🎨 **Taste** | [`frontend-design`](https://github.com/anthropics/claude-code/tree/main/plugins/frontend-design) (official Anthropic) | Forces a real aesthetic commitment before any CSS; kills "AI slop" defaults |
| 🧩 **Components** | [`shadcn` MCP](https://ui.shadcn.com/docs/mcp) | Search/add production components by natural language |
| 👁️ **Visual feedback** | [`@playwright/mcp`](https://github.com/microsoft/playwright-mcp) + [`chrome-devtools-mcp`](https://github.com/ChromeDevTools/chrome-devtools-mcp) | Claude opens a real browser, screenshots, reads the console, exercises states, and fixes what it sees |
| ✅ **Automated review** | `design-review` subagent + `/design-review` | 7-phase audit across viewports: WCAG AA, responsive, interaction states |

## Quickstart

```bash
# 1. Clone and enter
git clone https://github.com/YMungerDev/claude-website-design-stack
cd claude-website-design-stack

# 2. Install the skills/plugins + Playwright browser
./scripts/setup.sh

# 3. Open Claude Code — the MCP servers and CLAUDE.md workflow load automatically
claude
```

Then just ask for UI work. Claude will plan → commit to a look → build → **screenshot and
iterate** → run `/design-review`. See `docs/WORKFLOW.md` for a full walkthrough.

## Try it in 30 seconds

```
> Build a pricing section for a developer tool. Plan it with ui-ux-pro-max,
> commit to a distinctive look, then screenshot it at mobile and desktop and fix any issues.
```

## What's in here

```
.
├── .mcp.json                     # Playwright + Chrome DevTools + shadcn MCP servers
├── CLAUDE.md                     # The design loop Claude follows (the "brain")
├── .claude/
│   ├── settings.json             # Enables the MCP servers + safe permissions
│   ├── agents/design-review.md   # 7-phase design-review subagent
│   └── commands/
│       ├── design-review.md      # /design-review — audit a URL/page
│       └── design-plan.md        # /design-plan — generate a design system first
├── scripts/
│   ├── setup.sh                  # Installs skills/plugins + Playwright chromium
│   └── design-audit.mjs          # Standalone multi-viewport screenshot + heuristic audit
├── .github/workflows/
│   └── design-review.yml         # Runs the audit on every PR that touches UI
├── docs/
│   ├── STACK.md                  # Why each tool is in the stack
│   ├── SETUP.md                  # Install details + optional add-ons (Figma, Magic)
│   └── WORKFLOW.md               # End-to-end worked example
└── examples/juniper-audit/       # Real audit run against a production site
```

## Standalone audit (no MCP needed)

The same checks are available as a plain script for local runs and CI:

```bash
node scripts/design-audit.mjs --url http://localhost:3000 --out audit-output
# or audit a static file
node scripts/design-audit.mjs --file ./index.html
```

It screenshots 7 viewport tiers (360 → 1920 px) and reports heuristic findings
(horizontal overflow, missing focus styles, unsized media, contrast risks, tap-target size).
See `examples/juniper-audit/` for a real report.

## Requirements

- Node 18+ and Python 3.x
- Claude Code with plugins enabled (`/plugin`)

## License

MIT. The bundled tools keep their own licenses — see `docs/STACK.md` for links.

---

Built as a starter for teams who want Claude Code to ship distinctive, accessible,
production-grade web UI instead of generic AI output.
