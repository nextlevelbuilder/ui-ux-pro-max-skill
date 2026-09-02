# Logo Design Reference

AI-powered logo design with 55+ styles, 30 color palettes, 25 industry guides. Gemini Nano Banana is the default provider; Atlas Cloud and MuAPI are also available as explicit opt-in providers.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/logo/search.py` | Search styles, colors, industries; generate design briefs |
| `scripts/logo/generate.py` | Generate logos with Gemini Nano Banana, Atlas Cloud, or MuAPI |
| `scripts/logo/core.py` | BM25 search engine for logo data |

## Commands

### Design Brief (Start Here)

```bash
python3 scripts/logo/search.py "tech startup modern" --design-brief -p "BrandName"
```

### Search Domains

```bash
# Styles
python3 scripts/logo/search.py "minimalist clean" --domain style

# Color palettes
python3 scripts/logo/search.py "tech professional" --domain color

# Industry guidelines
python3 scripts/logo/search.py "healthcare medical" --domain industry
```

### Generate Logo

**ALWAYS** use white background for output logos.

```bash
python3 scripts/logo/generate.py --brand "TechFlow" --style minimalist --industry tech
python3 scripts/logo/generate.py --prompt "coffee shop vintage badge" --style vintage
python3 scripts/logo/generate.py --brand "TechFlow" --provider atlas
python3 scripts/logo/generate.py --brand "TechFlow" --provider muapi
python3 scripts/logo/generate.py --brand "TechFlow" --provider muapi --muapi-model nano-banana-pro
```

Options: `--style`, `--industry`, `--prompt`, `--provider`, `--atlas-model`, `--muapi-model`

## Available Styles

| Category | Styles |
|----------|--------|
| General | Minimalist, Wordmark, Lettermark, Pictorial Mark, Abstract Mark, Mascot, Emblem, Combination Mark |
| Aesthetic | Vintage/Retro, Art Deco, Luxury, Playful, Corporate, Organic, Neon, Grunge, Watercolor |
| Modern | Gradient, Flat Design, 3D/Isometric, Geometric, Line Art, Duotone, Motion-Ready |
| Clever | Negative Space, Monoline, Split/Fragmented, Responsive/Adaptive |

## Color Psychology

| Color | Psychology | Best For |
|-------|------------|----------|
| Blue | Trust, stability | Finance, tech, healthcare |
| Green | Growth, natural | Eco, wellness, organic |
| Red | Energy, passion | Food, sports, entertainment |
| Gold | Luxury, premium | Fashion, jewelry, hotels |
| Purple | Creative, innovative | Beauty, creative, tech |

## Industry Defaults

| Industry | Style | Colors | Typography |
|----------|-------|--------|------------|
| Tech | Minimalist, Abstract | Blues, purples, gradients | Geometric sans |
| Healthcare | Professional, Line Art | Blues, greens, teals | Clean sans |
| Finance | Corporate, Emblem | Navy, gold | Serif or clean sans |
| Food | Vintage Badge, Mascot | Warm reds, oranges | Friendly, script |
| Fashion | Wordmark, Luxury | Black, gold, white | Elegant serif |

## Workflow

1. Generate design brief → `scripts/logo/search.py --design-brief`
2. Generate logo variations → `scripts/logo/generate.py --brand --style --industry`
3. Ask user about HTML preview → `AskUserQuestion` tool
4. If yes, invoke `/ui-ux-pro-max` for HTML gallery

## Detailed References

- `references/logo-style-guide.md` - Detailed style descriptions
- `references/logo-color-psychology.md` - Color meanings and combinations
- `references/logo-prompt-engineering.md` - AI generation prompts

## Setup

```bash
export GEMINI_API_KEY="your-key"
pip install google-genai

# Optional Atlas Cloud provider (no extra Python package required)
export ATLASCLOUD_API_KEY="your-key"

# Optional MuAPI provider (no extra Python package required)
export MUAPI_API_KEY="your-key"
```

MuAPI uses the asynchronous model endpoint and prediction result API. See the
[MuAPI API reference](https://muapi.ai/docs/api-reference) for authentication
and the [nano-banana model contract](https://api.muapi.ai/api/v1/models/nano-banana)
or [nano-banana-pro model contract](https://api.muapi.ai/api/v1/models/nano-banana-pro)
for the current model-specific schemas. The logo generator supports both documented
model slugs and sends their shared required `prompt` plus optional `aspect_ratio`
fields; the Pro model also accepts an optional `resolution` field that this focused
logo workflow leaves at the provider default.
