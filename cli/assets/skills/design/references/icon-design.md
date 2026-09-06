# Icon Design Reference

AI-powered SVG icon generation using Gemini 3.1 Pro Preview. 15 styles, 12 categories, multi-size export.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/icon/generate.py` | Generate SVG icons with Gemini 3.1 Pro Preview |

## Commands

### Generate Single Icon

```bash
python3 scripts/icon/generate.py --prompt "settings gear" --style outlined
python3 scripts/icon/generate.py --prompt "shopping cart" --style filled --color "#6366F1"
python3 scripts/icon/generate.py --name "dashboard" --category navigation --style duotone
```

### Generate Batch Variations

```bash
python3 scripts/icon/generate.py --prompt "cloud upload" --batch 4 --output-dir ./icons
python3 scripts/icon/generate.py --prompt "notification bell" --batch 6 --style outlined --output-dir ./icons
```

### Generate Multiple Sizes

```bash
python3 scripts/icon/generate.py --prompt "user profile" --sizes "16,24,32,48" --output-dir ./icons
```

### List Styles/Categories

```bash
python3 scripts/icon/generate.py --list-styles
python3 scripts/icon/generate.py --list-categories
```

## CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--prompt, -p` | Icon description | required |
| `--name, -n` | Icon name (for filename) | - |
| `--style, -s` | Icon style (15 options) | - |
| `--category, -c` | Icon category for context | - |
| `--color` | Primary hex color | currentColor |
| `--size` | Display size in px | 24 |
| `--viewbox` | SVG viewBox size | 24 |
| `--output, -o` | Output file path | auto |
| `--output-dir` | Output directory (batch) | ./icons |
| `--batch` | Number of variations | - |
| `--sizes` | Comma-separated sizes | - |

## Available Styles

| Style | Stroke | Fill | Best For |
|-------|--------|------|----------|
| outlined | 2px | none | UI interfaces, web apps |
| filled | 0 | solid | Mobile apps, nav bars |
| duotone | 0 | dual | Marketing, landing pages |
| thin | 1-1.5px | none | Luxury brands, editorial |
| bold | 3px | none | Headers, hero sections |
| rounded | 2px | none | Friendly apps, health |
| sharp | 2px | none | Tech, fintech, enterprise |
| flat | 0 | solid | Material design, Google-style |
| gradient | 0 | gradient | Modern brands, SaaS |
| glassmorphism | 1px | semi | Modern UI, overlays |
| pixel | 0 | solid | Gaming, retro |
| hand-drawn | varies | none | Artisan, creative |
| isometric | 1-2px | partial | Tech docs, infographics |
| glyph | 0 | solid | System UI, compact |
| animated-ready | 2px | varies | Interactive UI, onboarding |

## Icon Categories

| Category | Icons |
|----------|-------|
| navigation | arrows, menus, home, chevrons |
| action | edit, delete, save, download, upload |
| communication | email, chat, phone, notification |
| media | play, pause, volume, camera |
| file | document, folder, archive, cloud |
| user | person, group, profile, settings |
| commerce | cart, bag, wallet, credit card |
| data | chart, graph, analytics, dashboard |
| development | code, terminal, bug, git, API |
| social | heart, star, bookmark, trophy |
| weather | sun, moon, cloud, rain |
| map | pin, location, compass, globe |

## SVG Best Practices

- **ViewBox**: Use `0 0 24 24` (standard) or `0 0 16 16` (compact)
- **Colors**: Use `currentColor` for CSS inheritance, avoid hardcoded colors
- **Accessibility**: Always include `<title>` element
- **Optimization**: Minimal path nodes, no embedded fonts or raster images
- **Sizing**: Design at 24px, test at 16px and 48px for clarity
- **Stroke**: Use `stroke-linecap="round"` and `stroke-linejoin="round"` for outlined styles

## Model

- **gemini-3.1-pro-preview**: Best thinking, token efficiency, factual consistency
- Text-only output (SVG is XML text) — no image generation API needed
- Supports structured output for consistent SVG formatting

## Workflow

1. Describe icon → `--prompt "settings gear"`
2. Choose style → `--style outlined`
3. Generate → script outputs .svg file
4. Optionally batch → `--batch 4` for variations
5. Multi-size export → `--sizes "16,24,32,48"`

## Setup

```bash
export GEMINI_API_KEY="your-key"
pip install google-genai
```
