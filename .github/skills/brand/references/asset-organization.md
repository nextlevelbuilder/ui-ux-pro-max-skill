# Asset Organization Guide

Guidelines for organizing marketing assets in a structured, searchable system.

## Directory Structure

```
project-root/
├── .assets/                          # Git-tracked metadata
│   ├── manifest.json                 # Central asset registry
│   ├── tags.json                     # Tagging system
│   ├── versions/                     # Version history
│   │   └── {asset-id}/
│   │       └── v{n}.json
│   └── metadata/                     # Type-specific metadata
│       ├── designs.json
│       ├── banners.json
│       ├── logos.json
│       └── videos.json
├── assets/                           # Raw files
│   ├── designs/
│   │   ├── campaigns/                # Campaign-specific designs
│   │   ├── web/                      # Website graphics
│   │   └── print/                    # Print materials
│   ├── banners/
│   │   ├── social-media/             # Platform banners
│   │   ├── email-headers/            # Email template headers
│   │   └── landing-pages/            # Hero/section images
│   ├── logos/
│   │   ├── full-horizontal/          # Full logo with wordmark
│   │   ├── icon-only/                # Symbol only
│   │   ├── monochrome/               # Single color versions
│   │   └── variations/               # Special versions
│   ├── videos/
│   │   ├── ads/                      # Promotional videos
│   │   ├── tutorials/                # How-to content
│   │   └── testimonials/             # Customer videos
│   ├── infographics/                 # Data visualizations
│   └── generated/                    # AI-generated assets
│       └── {YYYYMMDD}/               # Date-organized
```

## Naming Convention

### Format
```
{type}_{campaign}_{description}_{timestamp}_{variant}.{ext}
```

### Components
| Component | Format | Required | Examples |
|-----------|--------|----------|----------|
| type | lowercase | Yes | banner, logo, design, video |
| campaign | kebab-case | Yes* | claude-launch, q1-promo, evergreen |
| description | kebab-case | Yes | hero-image, email-header |
| timestamp | YYYYMMDD | Yes | 20251209 |
| variant | kebab-case | No | dark-mode, 1x1, mobile |

*Use "evergreen" for non-campaign assets

### Examples
```
banner_claude-launch_hero-image_20251209_16-9.png
logo_brand-refresh_horizontal-full-color_20251209.svg
design_holiday-campaign_email-hero_20251209_dark-mode.psd
video_product-demo_feature-walkthrough_20251209.mp4
infographic_evergreen_pricing-comparison_20251209.png
```

## Metadata Schema

### Asset Entry (manifest.json)
```json
{
  "id": "uuid-v4",
  "name": "Campaign Hero Banner",
  "type": "banner",
  "path": "assets/banners/landing-pages/banner_claude-launch_hero-image_20251209.png",
  "dimensions": { "width": 1920, "height": 1080 },
  "fileSize": 245760,
  "mimeType": "image/png",
  "tags": ["campaign", "hero", "launch"],
  "status": "approved",
  "source": {
    "model": "imagen-4",
    "prompt": "...",
    "createdAt": "2025-12-09T10:30:00Z"
  },
  "version": 2,
  "createdBy": "agent:content-creator",
  "approvedBy": "user:john",
  "approvedAt": "2025-12-09T14:00:00Z"
}
```

### Version Entry (versions/{id}/v{n}.json)
```json
{
  "version": 2,
  "previousVersion": 1,
  "path": "assets/banners/landing-pages/banner_claude-launch_hero-image_20251209_v2.png",
  "changes": "Updated CTA button color to match brand refresh",
  "createdAt": "2025-12-09T12:00:00Z",
  "createdBy": "agent:ui-designer"
}
```

## Tagging System

### Standard Tags
| Category | Values |
|----------|--------|
| status | draft, review, approved, archived |
| platform | instagram, twitter, linkedin, facebook, youtube, email, web |
| content-type | promotional, educational, brand, product, testimonial |
| format | 1x1, 4x5, 9x16, 16x9, story, reel, banner |
| source | imagen-4, veo-3, user-upload, canva, figma |

### Tag Usage
- Each asset should have: status + platform + content-type
- Optional: format, source, campaign

## File Organization Best Practices

1. **One file per variant** - Don't combine dark/light in one file
2. **Source files separate** - Keep .psd/.fig in same structure
3. **AI assets timestamped** - Auto-organize by generation date
4. **Archive don't delete** - Move to `archived/` with date prefix
5. **Large files external** - Videos > 100MB use cloud storage links

## Search Patterns

### By Type
```bash
# Find all banners
ls assets/banners/**/*
```

### By Campaign
```bash
# Find all assets for specific campaign
grep -l "claude-launch" .assets/manifest.json
```

### By Status
```bash
# Find approved assets only
jq '.assets[] | select(.status == "approved")' .assets/manifest.json
```

## Cleanup Workflow

1. Run `extract-colors.cjs` on new assets
2. Validate against brand guidelines
3. Update manifest.json with new entries
4. Tag appropriately
5. Remove duplicates/outdated versions
