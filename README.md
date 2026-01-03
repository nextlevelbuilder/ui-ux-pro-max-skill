# UI UX Pro Max

An AI skill that provides design intelligence for building professional UI/UX across multiple platforms and frameworks.

<p align="center">
  <img src="screenshots/website.png" alt="UI UX Pro Max" width="800">
</p>

## Overview

UI UX Pro Max is a searchable database of UI styles, color palettes, font pairings, chart types, product recommendations, UX guidelines, and stack-specific best practices. It works as a skill/workflow for AI coding assistants (Claude Code, Cursor, Windsurf, etc.).

## Features

- **57 UI Styles** - Glassmorphism, Claymorphism, Minimalism, Brutalism, Neumorphism, Bento Grid, Dark Mode, and more
- **95 Color Palettes** - Industry-specific palettes for SaaS, E-commerce, Healthcare, Fintech, Beauty, etc.
- **56 Font Pairings** - Curated typography combinations with Google Fonts imports
- **24 Chart Types** - Recommendations for dashboards and analytics
- **9 Tech Stacks** - React, Next.js, Vue, Nuxt UI, Svelte, SwiftUI, React Native, Flutter, HTML+Tailwind
- **98 UX Guidelines** - Best practices, anti-patterns, and accessibility rules

## Installation

### Using CLI (Recommended)

```bash
# Install CLI globally
npm install -g uipro-cli

# Go to your project
cd /path/to/your/project

# Install for your AI assistant
uipro init --ai claude      # Claude Code
uipro init --ai cursor      # Cursor
uipro init --ai windsurf    # Windsurf
uipro init --ai antigravity # Antigravity (.agent + .shared)
uipro init --ai copilot     # GitHub Copilot
uipro init --ai kiro        # Kiro
uipro init --ai all         # All assistants
```

### Other CLI Commands

```bash
uipro versions              # List available versions
uipro update                # Update to latest version
uipro init --version v1.0.0 # Install specific version
```

### Manual Installation

Copy the appropriate folders to your project:

| AI Assistant   | Folders to Copy                                                     |
| -------------- | ------------------------------------------------------------------- |
| Claude Code    | `.claude/skills/ui-ux-pro-max/`                                     |
| Cursor         | `.cursor/commands/ui-ux-pro-max.md` + `.shared/ui-ux-pro-max/`      |
| Windsurf       | `.windsurf/workflows/ui-ux-pro-max.md` + `.shared/ui-ux-pro-max/`   |
| Antigravity    | `.agent/workflows/ui-ux-pro-max.md` + `.shared/ui-ux-pro-max/`      |
| GitHub Copilot | `.github/prompts/ui-ux-pro-max.prompt.md` + `.shared/ui-ux-pro-max/`|
| Kiro           | `.kiro/steering/ui-ux-pro-max.md` + `.shared/ui-ux-pro-max/`        |

## Prerequisites

Python 3.x is required for the search script.

```bash
# Check if Python is installed
python3 --version

# macOS
brew install python3

# Ubuntu/Debian
sudo apt update && sudo apt install python3

# Windows
winget install Python.Python.3.12
```

## Usage

### Claude Code

The skill activates automatically when you request UI/UX work. Just chat naturally:

```
Build a landing page for my SaaS product
```

### Cursor / Windsurf / Antigravity

Use the slash command to invoke the skill:

```
/ui-ux-pro-max Build a landing page for my SaaS product
```

### Kiro

Type `/` in chat to see available commands, then select `ui-ux-pro-max`:

```
/ui-ux-pro-max Build a landing page for my SaaS product
```

### GitHub Copilot

In VS Code with Copilot, type `/` in chat to see available prompts, then select `ui-ux-pro-max`:

```
/ui-ux-pro-max Build a landing page for my SaaS product
```

### Example Prompts

```
Build a landing page for my SaaS product

Create a dashboard for healthcare analytics

Design a portfolio website with dark mode

Make a mobile app UI for e-commerce
```

### How It Works

1. **You ask** - Request any UI/UX task (build, design, create, implement, review, fix, improve)
2. **Skill activates** - The AI automatically searches the design database for relevant styles, colors, typography, and guidelines
3. **Smart recommendations** - Based on your product type and requirements, it finds the best matching design system
4. **Code generation** - Implements the UI with proper colors, fonts, spacing, and best practices

### Supported Stacks

The skill provides stack-specific guidelines for:

- **HTML + Tailwind** (default)
- **React** / **Next.js**
- **Vue** / **Nuxt UI** / **Svelte**
- **SwiftUI** / **React Native** / **Flutter**

Just mention your preferred stack in the prompt, or let it default to HTML + Tailwind.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=nextlevelbuilder/ui-ux-pro-max-skill&type=Date)](https://star-history.com/#nextlevelbuilder/ui-ux-pro-max-skill&Date)

## License

This project is licensed under the [MIT License](LICENSE).
