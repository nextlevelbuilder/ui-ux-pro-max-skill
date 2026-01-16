# uipro-cli

CLI to install UI/UX Pro Max skill for AI coding assistants.

**Version 2.0.0** includes Advanced Customization Architecture with 47 AI chat patterns, 24 architecture patterns, external configuration support, brand integration, and A2UI cross-platform export.

## Installation

```bash
npm install -g uipro-cli
```

## Usage

```bash
# Install for specific AI assistant
uipro init --ai claude      # Claude Code
uipro init --ai cursor      # Cursor
uipro init --ai windsurf    # Windsurf
uipro init --ai antigravity # Antigravity
uipro init --ai copilot     # GitHub Copilot
uipro init --ai kiro        # Kiro
uipro init --ai codex       # Codex (Skills)
uipro init --ai roocode     # Roo Code
uipro init --ai qoder       # Qoder
uipro init --ai gemini      # Gemini CLI
uipro init --ai trae        # Trae
uipro init --ai all         # All assistants

# Options
uipro init --offline        # Skip GitHub download, use bundled assets only
uipro init --force          # Overwrite existing files

# Other commands
uipro versions              # List available versions
uipro update                # Update to latest version
```

## How It Works

By default, `uipro init` tries to download the latest release from GitHub to ensure you get the most up-to-date version. If the download fails (network error, rate limit), it automatically falls back to the bundled assets included in the CLI package.

Use `--offline` to skip the GitHub download and use bundled assets directly.

## New in v2.0.0 - Advanced Features

The installed skill includes advanced customization capabilities:

### External Configuration Support
Customize with your own brand colors and guidelines:
```bash
# Create external configuration directory
mkdir .ui-ux-pro-max-config

# Use with brand integration
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "dashboard design" --apply-brand --config-path .ui-ux-pro-max-config/
```

### A2UI Cross-Platform Export
Export designs for multiple platforms:
```bash
# Export as A2UI protocol
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "button design" --export-a2ui

# Export for specific targets
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "dashboard layout" --export-a2ui --export-targets react vue flutter
```

### AI Chat Interface Patterns
Access 47 specialized patterns for building conversational UIs:
```bash
# Search AI chat patterns
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "thinking bubble" --domain prompt
```

### Architecture Patterns
24 clean architecture patterns including hexagonal, DDD, and CQRS:
```bash
# Search architecture patterns
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "clean architecture" --domain ux
```

## Development

```bash
# Install dependencies
bun install

# Run locally
bun run src/index.ts --help

# Build
bun run build

# Link for local testing
bun link
```

## License

CC-BY-NC-4.0
