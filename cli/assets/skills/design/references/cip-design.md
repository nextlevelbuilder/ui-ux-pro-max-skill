# CIP Design Reference

Corporate Identity Program design with 50+ deliverables, 20 styles, 20 industries. Generate mockups with Gemini Nano Banana (Flash/Pro).

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/cip/search.py` | Search deliverables, styles, industries; generate CIP briefs |
| `scripts/cip/generate.py` | Generate CIP mockups with Gemini (Flash/Pro) |
| `scripts/cip/render-html.py` | Render HTML presentation from CIP mockups |
| `scripts/cip/core.py` | BM25 search engine for CIP data |

## Commands

### CIP Brief (Start Here)

```bash
python3 scripts/cip/search.py "tech startup" --cip-brief -b "BrandName"
```

### Search Domains

```bash
# Deliverables
python3 scripts/cip/search.py "business card letterhead" --domain deliverable

# Design styles
python3 scripts/cip/search.py "luxury premium elegant" --domain style

# Industry guidelines
python3 scripts/cip/search.py "hospitality hotel" --domain industry

# Mockup contexts
python3 scripts/cip/search.py "office reception" --domain mockup
```

### Generate Mockups

```bash
# With logo (RECOMMENDED - uses image editing)
python3 scripts/cip/generate.py --brand "TopGroup" --logo /path/to/logo.png --deliverable "business card" --industry "consulting"

# Full CIP set with logo
python3 scripts/cip/generate.py --brand "TopGroup" --logo /path/to/logo.png --industry "consulting" --set

# Pro model for 4K text rendering
python3 scripts/cip/generate.py --brand "TopGroup" --logo logo.png --deliverable "business card" --model pro

# Custom deliverables with aspect ratio
python3 scripts/cip/generate.py --brand "GreenLeaf" --logo logo.png --industry "organic food" --deliverables "letterhead,packaging,vehicle" --ratio 16:9

# Without logo (AI generates interpretation)
python3 scripts/cip/generate.py --brand "TechFlow" --deliverable "business card" --no-logo-prompt
```

### Render HTML Presentation

```bash
python3 scripts/cip/render-html.py --brand "TopGroup" --industry "consulting" --images /path/to/cip-output
python3 scripts/cip/render-html.py --brand "TopGroup" --industry "consulting" --images ./topgroup-cip --output presentation.html
```

## Models

- `flash` (default): `gemini-2.5-flash-image` - Fast, cost-effective
- `pro`: `gemini-3-pro-image-preview` - Quality, 4K text rendering

## Deliverable Categories

| Category | Items |
|----------|-------|
| Core Identity | Logo, Logo Variations |
| Stationery | Business Card, Letterhead, Envelope, Folder, Notebook, Pen |
| Security/Access | ID Badge, Lanyard, Access Card |
| Office Environment | Reception Signage, Wayfinding, Meeting Room Signs, Wall Graphics |
| Apparel | Polo Shirt, T-Shirt, Cap, Jacket, Apron |
| Promotional | Tote Bag, Gift Box, USB Drive, Water Bottle, Mug, Umbrella |
| Vehicle | Car Sedan, Van, Truck |
| Digital | Social Media, Email Signature, PowerPoint, Document Templates |
| Product | Packaging Box, Labels, Tags, Retail Display |
| Events | Trade Show Booth, Banner Stand, Table Cover, Backdrop |

## Design Styles

| Style | Colors | Best For |
|-------|--------|----------|
| Corporate Minimal | Navy, White, Blue | Finance, Legal, Consulting |
| Modern Tech | Purple, Cyan, Green | Tech, Startups, SaaS |
| Luxury Premium | Black, Gold, White | Fashion, Jewelry, Hotels |
| Warm Organic | Brown, Green, Cream | Food, Organic, Artisan |
| Bold Dynamic | Red, Orange, Black | Sports, Entertainment |

## HTML Presentation Features

- Hero section with brand name, industry, style, mood
- Deliverable cards with mockup images
- Descriptions: concept, purpose, specifications
- Responsive desktop/mobile, dark theme
- Images embedded as base64 (single-file portable)

## Workflow

1. Generate CIP brief → `scripts/cip/search.py --cip-brief`
2. Generate mockups with logo → `scripts/cip/generate.py --brand --logo --industry --set`
3. Render HTML presentation → `scripts/cip/render-html.py --brand --industry --images`

**Tip:** If no logo exists, use Logo Design (built-in) to generate one first.

## Detailed References

- `references/cip-deliverable-guide.md` - Deliverable specifications
- `references/cip-style-guide.md` - Design style descriptions
- `references/cip-prompt-engineering.md` - AI generation prompts

## Setup

```bash
export GEMINI_API_KEY="your-key"
pip install google-genai pillow
```
