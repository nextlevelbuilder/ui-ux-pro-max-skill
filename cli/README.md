# uipro-cli

CLI to install UI/UX Pro Max skill for AI coding assistants.

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
uipro init --ai opencode    # OpenCode
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
