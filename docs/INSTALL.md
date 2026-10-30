# Installing UI/UX Pro Max in AutoClaw

UI/UX Pro Max installs into AutoClaw through the `ui-ux-pro-max-cli` package. The CLI generates the skill from the same canonical templates used for every other supported platform, so the installed copy always matches the current release.

AutoClaw loads skills from these locations (highest precedence first):

- `<workspace>/skills` - per-workspace skills (used by a local install)
- `~/.openclaw-autoclaw/skills` - shared skills for every agent on the machine (used by `--global`)
- `<workspace>/.agents/skills` and `~/.agents/skills`

The `autoclaw` platform config targets the first two paths, so an installed skill is discovered without any extra configuration.

## Prerequisites

- AutoClaw installed (download from <https://autoclaw.z.ai/?channel=zai>)
- Node.js 18+ and npm (for the CLI installer)
- Python 3.x on your system (the bundled search script uses only the standard library)

---

## Install the CLI

```bash
npm install -g ui-ux-pro-max-cli
```

This installs the `uipro` command.

---

## Method 1: Local Install (Per Workspace)

Run the installer from the AutoClaw workspace root (the project folder your agent uses):

```bash
uipro init --ai autoclaw
```

The CLI writes the skill to `skills/` inside that workspace:

```text
skills/
├── ui-ux-pro-max/          # orchestrator skill
│   ├── SKILL.md
│   ├── data/
│   └── scripts/
│       └── search.py
├── banner-design/
├── brand/
├── design/
├── design-system/
├── slides/
└── ui-styling/
```

The one `uipro init` call installs the orchestrator plus its six sibling sub-skills.

Useful flags:

```bash
uipro init --ai autoclaw --dry-run   # Preview every path the install would write
uipro init --ai autoclaw --force     # Overwrite an existing installation
```

You can also omit `--ai` and let the CLI detect the platform from an existing installation:

```bash
uipro init
```

---

## Method 2: Global Install (All Agents)

Run the installer with `--global`:

```bash
uipro init --ai autoclaw --global
```

The CLI writes the skill to `~/.openclaw-autoclaw/skills/` instead of the current workspace. In the generated `SKILL.md`, script commands are anchored at the home directory (`~/.openclaw-autoclaw/skills/ui-ux-pro-max/scripts/search.py`) so they resolve from any project.

---

## Activate the Skill in AutoClaw

1. Open AutoClaw
2. Go to **Settings → Skills**
3. Click **Refresh**
4. Confirm `ui-ux-pro-max` appears with the toggle enabled
5. Start a chat with a design prompt (e.g., "Build a dashboard for healthcare analytics") - the skill triggers automatically

---

## Verify the Installation

### Check the generated files

Local install (run from the workspace root):

```bash
ls skills/ui-ux-pro-max/SKILL.md
ls skills/ui-ux-pro-max/scripts/search.py
```

Global install:

```bash
ls ~/.openclaw-autoclaw/skills/ui-ux-pro-max/SKILL.md
ls ~/.openclaw-autoclaw/skills/ui-ux-pro-max/scripts/search.py
```

The generated `SKILL.md` should reference the installed location, not a source checkout. For a local install, its commands start with `skills/ui-ux-pro-max/scripts/search.py`; for a global install, with `~/.openclaw-autoclaw/skills/ui-ux-pro-max/scripts/search.py`.

### Run the search script

```bash
# Local install (from the workspace root)
python3 skills/ui-ux-pro-max/scripts/search.py "saas dashboard" --design-system

# Global install
python3 ~/.openclaw-autoclaw/skills/ui-ux-pro-max/scripts/search.py "saas dashboard" --design-system
```

On Windows, use `python` instead of `python3`.

If the script prints a design-system report, the skill and its data catalogs are installed correctly.

---

## Update

```bash
# Update a local installation
uipro update --ai autoclaw

# Update a global installation
uipro update --ai autoclaw --global
```

`uipro update` checks the latest CLI release. If the installed CLI is current, it regenerates the skill files with `--force`. If a newer CLI exists, it installs that version first and then asks you to rerun the command above.

---

## Uninstall

```bash
# Remove the workspace-local installation
uipro uninstall --ai autoclaw

# Remove the global installation
uipro uninstall --ai autoclaw --global
```

The CLI prompts for confirmation before removing the orchestrator and the six sibling sub-skills. Afterwards, click **Refresh** in AutoClaw's Skills page.

---

## Troubleshooting

### Skill doesn't appear in Settings → Skills

- Confirm the files are under a scanned root: `skills/ui-ux-pro-max/SKILL.md` (workspace) or `~/.openclaw-autoclaw/skills/ui-ux-pro-max/SKILL.md` (global).
- Make sure you ran the installer from the workspace root that AutoClaw uses, not from an unrelated folder.
- Confirm the directory name matches the `name` field in the frontmatter (both should be `ui-ux-pro-max`).
- Click **Refresh** in the Skills page.
- Check the diagnostics panel for any error messages.

### Skill appears but never triggers automatically

Common causes:

1. **Too many skills enabled** - AutoClaw injects metadata for every enabled skill into the model context. If you've blown past the budget, descriptions get dropped and the model can't decide when to trigger. Disable skills you don't actively use.
2. **Vague description** - The skill's `description` already spells out triggers, but if you've customized it, make sure your version includes concrete trigger phrases.
3. **Inside a subagent with a custom `tools` allowlist** - If you've defined a subagent that restricts tools, the skill tool may not be on the allowlist. Remove the `tools` field or add the skill tool explicitly.

### Search script fails to run

```bash
# Verify Python 3 is on PATH
python3 --version

# Run the script directly to see the error
python3 skills/ui-ux-pro-max/scripts/search.py "saas dashboard" --design-system
```

The script uses only the Python 3 standard library, so there should be no missing-module errors. If you see import errors, your Python install may be non-standard.

### Wrong paths in the generated SKILL.md

Reinstall with `--force` so the file is regenerated from the current templates:

```bash
uipro init --ai autoclaw --force
```

Or, for a global installation:

```bash
uipro init --ai autoclaw --global --force
```

---

## License

Same as upstream: MIT.
