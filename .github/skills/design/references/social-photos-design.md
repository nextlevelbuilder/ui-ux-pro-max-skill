# Social Photos Design Guide

Design social media images via HTML/CSS rendering + screenshot export. Orchestrates `ui-ux-pro-max`, `brand`, `design-system`, and `chrome-devtools` skills.

## Platform Sizes

| Platform | Type | Size (px) | Aspect |
|----------|------|-----------|--------|
| Instagram | Post | 1080 x 1080 | 1:1 |
| Instagram | Story/Reel | 1080 x 1920 | 9:16 |
| Instagram | Carousel | 1080 x 1350 | 4:5 |
| Facebook | Post | 1200 x 630 | ~1.9:1 |
| Facebook | Story | 1080 x 1920 | 9:16 |
| Twitter/X | Post | 1200 x 675 | 16:9 |
| Twitter/X | Card | 800 x 418 | ~1.91:1 |
| LinkedIn | Post | 1200 x 627 | ~1.91:1 |
| LinkedIn | Article | 1200 x 644 | ~1.86:1 |
| Pinterest | Pin | 1000 x 1500 | 2:3 |
| YouTube | Thumbnail | 1280 x 720 | 16:9 |
| TikTok | Cover | 1080 x 1920 | 9:16 |
| Threads | Post | 1080 x 1080 | 1:1 |

## Workflow

### Step 1: Activate Project Management

Invoke `project-management` skill to create persistent TODO tasks via Claude's native task orchestration. Break down into:
- Requirement analysis task
- Idea generation task(s)
- HTML design task(s) — can parallelize per size/variant
- Screenshot export task(s) — can parallelize per file
- Report generation task

Spawn parallel subagents for independent tasks (e.g., multiple HTML files for different sizes).

### Step 2: Analyze Requirements

Parse user input for:
- **Subject/topic** — what the social photo represents
- **Target platforms** — which sizes needed (default: Instagram Post 1:1 + Story 9:16)
- **Visual style** — minimalist, bold, gradient, photo-based, etc.
- **Brand context** — read from `docs/brand-guidelines.md` if exists
- **Content elements** — headline, subtext, CTA, images, icons
- **Quantity** — how many variations (default: 3)

### Step 3: Generate Ideas

Create 3-5 concept ideas that:
- Match the input prompt/requirements
- Consider platform-specific best practices
- Vary in composition, color, typography approach
- Align with brand guidelines if available

Present ideas to user via `AskUserQuestion` for approval before designing.

### Step 4: Design HTML Files

Activate these skills in sequence:

1. **`/ckm:brand`** — Extract brand colors, fonts, voice from user's project
2. **`/ckm:design-system`** — Get design tokens (spacing, typography scale, color palette)
3. **Randomly invoke ONE of:** `/ck:ui-ux-pro-max` OR `/ck:frontend-design` — for layout, hierarchy, visual balance. Pick one at random each run for design variety.

For each approved idea + each target size, create an HTML file:

```
output/social-photos/
├── idea-1-instagram-post-1080x1080.html
├── idea-1-instagram-story-1080x1920.html
├── idea-2-instagram-post-1080x1080.html
├── idea-2-instagram-story-1080x1920.html
└── ...
```

#### HTML Design Rules

- **Viewport** — Set exact pixel dimensions matching target size
- **Self-contained** — Inline all CSS, embed fonts via Google Fonts CDN
- **No scrolling** — Everything fits in one viewport
- **High contrast** — Text readable at thumbnail size
- **Brand-aligned** — Use extracted brand colors/fonts
- **Safe zones** — Critical content within central 80% area
- **Typography** — Min 24px for headlines, min 16px for body at 1080px width
- **Visual hierarchy** — One focal point, clear reading flow

#### HTML Template Structure

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width={WIDTH}, initial-scale=1.0">
  <link href="https://fonts.googleapis.com/css2?family={FONT}&display=swap" rel="stylesheet">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body {
      width: {WIDTH}px;
      height: {HEIGHT}px;
      overflow: hidden;
      font-family: '{FONT}', sans-serif;
    }
    .canvas {
      width: {WIDTH}px;
      height: {HEIGHT}px;
      position: relative;
      /* Background: gradient, solid, or image */
    }
    /* Design tokens from brand/design-system */
  </style>
</head>
<body>
  <div class="canvas">
    <!-- Content layers -->
  </div>
</body>
</html>
```

### Step 5: Screenshot Export

Use Chrome headless, `chrome-devtools` skill, or Playwright/Puppeteer to capture exact-size screenshots.

**IMPORTANT:** Always add a delay (3-5s) after page load for fonts/images to fully render before capture.

#### Option A: Chrome Headless CLI (Recommended — zero dependencies)

```bash
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
DELAY=5  # seconds for fonts/images to load

"$CHROME" \
  --headless \
  --disable-gpu \
  --no-sandbox \
  --hide-scrollbars \
  --window-size="${WIDTH},${HEIGHT}" \
  --virtual-time-budget=$((DELAY * 1000)) \
  --screenshot="output.png" \
  "file:///path/to/file.html"
```

Key flags:
- `--virtual-time-budget=5000` — waits 5s virtual time for assets (Google Fonts, images) to load
- `--hide-scrollbars` — prevents scrollbar artifacts in screenshots
- `--window-size=WxH` — sets exact pixel dimensions

#### Option B: chrome-devtools skill

Invoke `/chrome-devtools` with instructions to:
1. Open each HTML file in browser
2. Set viewport to exact target dimensions
3. Wait 3-5s for fonts/images to fully load
4. Screenshot full page to PNG
5. Save to `output/social-photos/exports/`

#### Option C: Playwright script

```javascript
const { chromium } = require('playwright');

async function captureScreenshots(htmlFiles) {
  const browser = await chromium.launch();

  for (const file of htmlFiles) {
    const [width, height] = file.match(/(\d+)x(\d+)/).slice(1).map(Number);

    const page = await browser.newPage();
    await page.setViewportSize({ width, height });
    await page.goto(`file://${file}`, { waitUntil: 'networkidle' });
    // Wait for fonts/images to fully render
    await page.waitForTimeout(3000);

    const outputPath = file.replace('.html', '.png').replace('social-photos/', 'social-photos/exports/');
    await page.screenshot({ path: outputPath, type: 'png' });
    await page.close();
  }

  await browser.close();
}
```

#### Option D: Puppeteer script

```javascript
const puppeteer = require('puppeteer');

async function captureScreenshots(htmlFiles) {
  const browser = await puppeteer.launch();

  for (const file of htmlFiles) {
    const [width, height] = file.match(/(\d+)x(\d+)/).slice(1).map(Number);

    const page = await browser.newPage();
    await page.setViewport({ width, height, deviceScaleFactor: 2 }); // 2x for retina
    await page.goto(`file://${file}`, { waitUntil: 'networkidle0' });
    // Wait for fonts/images to fully render
    await new Promise(r => setTimeout(r, 3000));

    const outputPath = file.replace('.html', '.png').replace('social-photos/', 'social-photos/exports/');
    await page.screenshot({ path: outputPath, type: 'png' });
    await page.close();
  }

  await browser.close();
}
```

**IMPORTANT:** Use `deviceScaleFactor: 2` for retina-quality output (Puppeteer only).

### Step 6: Verify & Fix Designs

Use Chrome MCP or `chrome-devtools` skill to visually inspect each exported PNG:

1. Open exported screenshots and check for layout/styling issues
2. Verify: fonts rendered correctly, colors match brand, text readable at thumbnail size
3. Check: no overflow, no cut-off content, safe zones respected, visual hierarchy clear
4. If issues found → fix HTML source → re-export screenshot → verify again
5. Repeat until all designs pass visual QA

**Common issues to check:**
- Fonts not loaded (fallback to system fonts)
- Text overflow or clipping
- Elements outside safe zone (central 80%)
- Low contrast text (below WCAG AA 4.5:1)
- Misaligned elements or broken layouts

### Step 7: Generate Summary Report

Save report to `plans/reports/` with naming pattern from session hooks.

Report structure:

```markdown
# Social Photos Design Report

## Overview
- Prompt/requirements: {original input}
- Platforms: {target platforms}
- Variations: {count}
- Style: {chosen style}

## Ideas Generated
1. **{Idea name}** — {brief description, rationale}
2. ...

## Design Decisions
- Color palette: {colors used, why}
- Typography: {fonts, sizes, why}
- Layout: {composition approach, why}
- Brand alignment: {how brand guidelines influenced design}

## Output Files
| File | Size | Platform | Preview |
|------|------|----------|---------|
| exports/{filename}.png | {WxH} | {platform} | {description} |

## Why This Works
- {Platform-specific reasoning}
- {Brand alignment reasoning}
- {Visual hierarchy reasoning}
- {Engagement potential reasoning}

## Recommendations
- {A/B test suggestions}
- {Platform-specific tips}
- {Iteration opportunities}
```

### Step 8: Organize Output

Invoke `assets-organizing` skill to organize all output files and reports:
- Move/copy exported PNGs to proper asset directories
- Ensure reports are in `plans/reports/` with correct naming
- Clean up intermediate HTML files if requested
- Tag outputs with metadata (platform, size, concept name)

## Design Best Practices

### Platform-Specific Tips

- **Instagram** — Visual-first, minimal text (<20%), strong colors, lifestyle feel
- **Facebook** — Informative, can have more text, eye-catching in feed
- **Twitter/X** — Bold headlines, contrast for dark/light mode, clear message
- **LinkedIn** — Professional, clean, data-driven visuals, thought leadership
- **Pinterest** — Vertical format, text overlay on images, how-to style
- **YouTube** — Face close-ups perform best, bright colors, readable at small size
- **TikTok** — Trendy, energetic, bold typography, youth-oriented

### Art Direction Styles (Reuse from Banner)

| Style | Best For | Key Elements |
|-------|----------|--------------|
| Minimalist | SaaS, tech, luxury | Whitespace, single accent color, clean type |
| Bold Typography | Announcements, quotes | Large type, high contrast, minimal imagery |
| Gradient Mesh | Modern brands, apps | Fluid color transitions, floating elements |
| Photo-Based | Lifestyle, e-commerce | Hero image, subtle overlay, text on image |
| Geometric | Tech, fintech | Shapes, patterns, structured layouts |
| Glassmorphism | SaaS, modern apps | Frosted glass, blur effects, transparency |
| Flat Illustration | Education, health | Custom illustrations, friendly, approachable |
| Duotone | Creative, editorial | Two-color treatment on photos |
| Collage | Fashion, culture | Mixed media, overlapping elements |
| 3D/Isometric | Tech, product | Depth, shadows, modern perspective |

### Color & Contrast

- Ensure WCAG AA contrast ratio (4.5:1 min) for all text
- Test designs at 50% size to verify readability
- Consider platform dark/light mode compatibility
- Use brand primary color as dominant, secondary as accent

### Typography Hierarchy

| Element | Min Size (at 1080px) | Weight |
|---------|---------------------|--------|
| Headline | 48px | Bold/Black |
| Subheadline | 32px | Semibold |
| Body | 24px | Regular |
| Caption | 18px | Regular/Light |
| CTA | 28px | Bold |

## Security & Scope

This sub-skill handles social media image design only. Does NOT handle:
- Video content creation
- Animation/motion graphics
- Print production files (CMYK, bleed)
- Direct social media posting/scheduling
- AI image generation (use `ai-artist` skill for that)
