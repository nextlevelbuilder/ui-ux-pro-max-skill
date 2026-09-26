# Brand Guidelines v1.0

> Last updated: {DATE}
> Status: Draft

## Quick Reference

| Element | Value |
|---------|-------|
| Primary Color | #2563EB |
| Secondary Color | #8B5CF6 |
| Primary Font | Inter |
| Voice | Professional, Helpful, Clear |

---

## 1. Color Palette

### Primary Colors

| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| Primary Blue | #2563EB | rgb(37,99,235) | CTAs, headers, links |
| Primary Dark | #1D4ED8 | rgb(29,78,216) | Hover states, emphasis |

### Secondary Colors

| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| Secondary Purple | #8B5CF6 | rgb(139,92,246) | Accents, highlights |
| Accent Green | #10B981 | rgb(16,185,129) | Success, positive states |

### Neutral Palette

| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| Background | #FFFFFF | rgb(255,255,255) | Page backgrounds |
| Surface | #F9FAFB | rgb(249,250,251) | Cards, sections |
| Text Primary | #111827 | rgb(17,24,39) | Headings, body text |
| Text Secondary | #6B7280 | rgb(107,114,128) | Captions, muted text |
| Border | #E5E7EB | rgb(229,231,235) | Dividers, borders |

### Semantic Colors

| State | Hex | Usage |
|-------|-----|-------|
| Success | #22C55E | Positive actions, confirmations |
| Warning | #F59E0B | Cautions, pending states |
| Error | #EF4444 | Errors, destructive actions |
| Info | #3B82F6 | Informational messages |

### Accessibility

- Text on white background: 7.2:1 contrast ratio (AAA)
- Primary on white: 4.6:1 contrast ratio (AA)
- All interactive elements meet WCAG 2.1 AA standards

---

## 2. Typography

### Font Stack

```css
--font-heading: 'Inter', system-ui, -apple-system, sans-serif;
--font-body: 'Inter', system-ui, -apple-system, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
```

### Type Scale

| Element | Size (Desktop) | Size (Mobile) | Weight | Line Height |
|---------|----------------|---------------|--------|-------------|
| H1 | 48px | 32px | 700 | 1.2 |
| H2 | 36px | 28px | 600 | 1.25 |
| H3 | 28px | 24px | 600 | 1.3 |
| H4 | 24px | 20px | 600 | 1.35 |
| Body | 16px | 16px | 400 | 1.5 |
| Body Large | 18px | 18px | 400 | 1.6 |
| Small | 14px | 14px | 400 | 1.5 |
| Caption | 12px | 12px | 400 | 1.4 |

### Font Loading

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

---

## 3. Logo Usage

### Variants

| Variant | File | Use Case |
|---------|------|----------|
| Full Horizontal | logo-full-horizontal.svg | Headers, documents |
| Stacked | logo-stacked.svg | Square spaces |
| Icon Only | logo-icon.svg | Favicons, small spaces |
| Monochrome | logo-mono.svg | Limited color contexts |

### Clear Space

Minimum clear space = height of the logo icon (mark)

### Minimum Size

| Context | Minimum Width |
|---------|---------------|
| Digital - Full Logo | 120px |
| Digital - Icon | 24px |
| Print - Full Logo | 35mm |
| Print - Icon | 10mm |

### Don'ts

- Don't rotate or skew the logo
- Don't change colors outside approved palette
- Don't add shadows or effects
- Don't crop or modify proportions
- Don't place on busy backgrounds without sufficient contrast

---

## 4. Voice & Tone

### Brand Personality

| Trait | Description |
|-------|-------------|
| **Professional** | Expert knowledge, authoritative yet approachable |
| **Helpful** | Solution-focused, actionable guidance |
| **Clear** | Direct communication, jargon-free |
| **Confident** | Assured without being arrogant |

### Voice Chart

| Trait | We Are | We Are Not |
|-------|--------|------------|
| Professional | Expert, knowledgeable | Stuffy, corporate |
| Helpful | Supportive, empowering | Patronizing |
| Clear | Direct, concise | Vague, wordy |
| Confident | Assured, trustworthy | Arrogant, overselling |

### Tone by Context

| Context | Tone | Example |
|---------|------|---------|
| Marketing | Engaging, benefit-focused | "Create campaigns that convert." |
| Documentation | Clear, instructional | "Run the command to start." |
| Error messages | Calm, solution-focused | "Try refreshing the page." |
| Success | Brief, celebratory | "Campaign published!" |

### Prohibited Terms

| Avoid | Reason |
|-------|--------|
| Revolutionary | Overused |
| Best-in-class | Vague claim |
| Seamless | Overused |
| Synergy | Corporate jargon |
| Leverage | Use "use" instead |

---

## 5. Imagery Guidelines

### Photography Style

- **Lighting:** Natural, soft lighting preferred
- **Subjects:** Real people, authentic scenarios
- **Color treatment:** Maintain brand colors in post
- **Composition:** Clean, focused subjects

### Illustrations

- Style: Modern, flat design with subtle gradients
- Colors: Brand palette only
- Line weight: 2px consistent stroke
- Corners: 4px rounded

### Icons

- Style: Outlined, 24px base grid
- Stroke: 1.5px consistent
- Corner radius: 2px
- Fill: None (outline only)

---

## 6. Design Components

### Buttons

| Type | Background | Text | Border Radius |
|------|------------|------|---------------|
| Primary | #2563EB | #FFFFFF | 8px |
| Secondary | Transparent | #2563EB | 8px |
| Tertiary | Transparent | #6B7280 | 8px |

### Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Tight spacing |
| sm | 8px | Compact elements |
| md | 16px | Standard spacing |
| lg | 24px | Section spacing |
| xl | 32px | Large gaps |
| 2xl | 48px | Section dividers |

### Border Radius

| Element | Radius |
|---------|--------|
| Buttons | 8px |
| Cards | 12px |
| Inputs | 8px |
| Modals | 16px |
| Pills/Tags | 9999px |

---

## AI Image Generation

### Base Prompt Template

Always prepend to image generation prompts:

```
{DESCRIBE YOUR VISUAL STYLE HERE - mood, colors with hex codes, lighting, atmosphere}
```

### Style Keywords

| Category | Keywords |
|----------|----------|
| **Lighting** | {e.g., soft lighting, dramatic, natural} |
| **Mood** | {e.g., professional, energetic, calm} |
| **Composition** | {e.g., centered, rule of thirds, minimal} |
| **Treatment** | {e.g., high contrast, muted, vibrant} |
| **Aesthetic** | {e.g., modern, vintage, minimalist} |

### Visual Mood Descriptors

- {Mood descriptor 1}
- {Mood descriptor 2}
- {Mood descriptor 3}

### Visual Don'ts

| Avoid | Reason |
|-------|--------|
| {Item to avoid} | {Why to avoid it} |

### Example Prompts

**Hero Banner:**
```
{Example prompt for hero banners}
```

**Social Media Post:**
```
{Example prompt for social graphics}
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | {DATE} | Initial guidelines |
