# Brand Guidelines Template

Use this template to create comprehensive brand guidelines for any project.

## Document Structure

```markdown
# Brand Guidelines v{X.Y}

## Quick Reference
- **Primary Color:** #XXXXXX
- **Secondary Color:** #XXXXXX
- **Primary Font:** {font-family}
- **Voice:** {3 key traits}

## 1. Color Palette

### Primary Colors
| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| {Name} | #{hex} | rgb({r},{g},{b}) | Primary brand color, CTAs, headers |
| {Name} | #{hex} | rgb({r},{g},{b}) | Supporting accent |

### Secondary Colors
| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| {Name} | #{hex} | rgb({r},{g},{b}) | Secondary elements |
| {Name} | #{hex} | rgb({r},{g},{b}) | Highlights |

### Neutral Palette
| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| Background | #{hex} | rgb({r},{g},{b}) | Page backgrounds |
| Text Primary | #{hex} | rgb({r},{g},{b}) | Body text |
| Text Secondary | #{hex} | rgb({r},{g},{b}) | Captions, muted text |
| Border | #{hex} | rgb({r},{g},{b}) | Dividers, borders |

### Accessibility
- Text/Background Contrast: {ratio}:1 (WCAG {level})
- CTA Contrast: {ratio}:1
- All interactive elements meet WCAG 2.1 AA

## 2. Typography

### Font Stack
```css
--font-heading: '{Font}', sans-serif;
--font-body: '{Font}', sans-serif;
--font-mono: '{Font}', monospace;
```

### Type Scale
| Element | Font | Weight | Size (Desktop/Mobile) | Line Height |
|---------|------|--------|----------------------|-------------|
| H1 | {font} | 700 | 48px / 32px | 1.2 |
| H2 | {font} | 600 | 36px / 28px | 1.25 |
| H3 | {font} | 600 | 28px / 24px | 1.3 |
| H4 | {font} | 600 | 24px / 20px | 1.35 |
| Body | {font} | 400 | 16px / 16px | 1.5 |
| Small | {font} | 400 | 14px / 14px | 1.5 |
| Caption | {font} | 400 | 12px / 12px | 1.4 |

## 3. Logo Usage

### Variants
- **Primary:** Full horizontal logo with wordmark
- **Stacked:** Vertical arrangement for square spaces
- **Icon:** Symbol only for favicons, app icons
- **Monochrome:** Single color for limited palettes

### Clear Space
Minimum clear space = height of logo mark

### Minimum Size
- Digital: 80px width minimum
- Print: 25mm width minimum

### Don'ts
- Don't rotate or skew
- Don't change colors outside approved palette
- Don't add effects (shadows, gradients)
- Don't crop or modify proportions
- Don't place on busy backgrounds

## 4. Voice & Tone

### Brand Personality
{Trait 1}: {Description}
{Trait 2}: {Description}
{Trait 3}: {Description}

### Voice Chart
| Trait | We Are | We Are Not |
|-------|--------|------------|
| {Trait} | {Description} | {Anti-description} |

### Tone by Context
| Context | Tone | Example |
|---------|------|---------|
| Marketing | {tone} | "{example}" |
| Support | {tone} | "{example}" |
| Error Messages | {tone} | "{example}" |
| Success | {tone} | "{example}" |

### Prohibited Terms
- {term 1} (reason)
- {term 2} (reason)

## 5. Imagery Guidelines

### Photography Style
- {Lighting preference}
- {Subject guidelines}
- {Color treatment}

### Illustrations
- Style: {description}
- Colors: Brand palette only
- Stroke: {weight}px

### Icons
- Style: {outlined/filled/duotone}
- Size: 24px base grid
- Corner radius: {value}px
```

## Usage

1. Copy template above
2. Fill in brand-specific values
3. Save as `docs/brand-guidelines.md`
4. Reference in content workflows

## Extractable Fields

Scripts can extract:
- `colors.primary`, `colors.secondary`, `colors.neutral`
- `typography.heading`, `typography.body`
- `voice.traits`, `voice.prohibited`
- `logo.variants`, `logo.minSize`
