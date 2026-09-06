#!/usr/bin/env bash
# setup.sh — install the website design stack.
# Safe to re-run. Installs the audit deps + Chromium and the ui-ux-pro-max skill,
# then prints the two in-Claude steps (plugins are installed from inside Claude Code).
set -euo pipefail

cyan() { printf '\033[36m%s\033[0m\n' "$1"; }
green() { printf '\033[32m%s\033[0m\n' "$1"; }

cyan "==> Installing audit dependencies (Playwright)…"
npm install

cyan "==> Installing the Chromium browser for Playwright…"
# Skipped automatically in images that preinstall browsers; harmless to run.
npx playwright install chromium || echo "  (Chromium already present or managed by the environment — continuing.)"

cyan "==> Installing the ui-ux-pro-max skill (knowledge layer)…"
npx --yes ui-ux-pro-max-cli init --ai claude || {
  echo "  Could not auto-install ui-ux-pro-max-cli. Install it later with:"
  echo "    npx ui-ux-pro-max-cli init --ai claude"
}

green "==> CLI setup done."
echo
cyan "Two steps to finish inside Claude Code (plugins install from the app):"
echo "  1. Enable plugins, then run:"
echo "       /plugin install frontend-design@anthropics/claude-code"
echo "  2. Start Claude Code in this folder — .mcp.json (Playwright + Chrome DevTools + shadcn)"
echo "     and CLAUDE.md load automatically. Approve the MCP servers when prompted."
echo
echo "Optional add-ons: see docs/SETUP.md (Figma Dev Mode MCP, 21st.dev Magic MCP)."
