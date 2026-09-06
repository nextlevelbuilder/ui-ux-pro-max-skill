# Typography Specifications

Guidelines for defining and implementing brand typography.

## Font Stack Structure

### Primary Fonts
```css
/* Headings - Display font for impact */
--font-heading: 'Inter', system-ui, -apple-system, sans-serif;

/* Body - Readable for long-form content */
--font-body: 'Inter', system-ui, -apple-system, sans-serif;

/* Monospace - Code, technical content */
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
```

### Font Loading
```html
<!-- Google Fonts (recommended) -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

## Type Scale

### Base System
- Base size: 16px (1rem)
- Scale ratio: 1.25 (Major Third)

### Scale Definition
| Element | Size (rem) | Size (px) | Weight | Line Height |
|---------|------------|-----------|--------|-------------|
| Display | 3.815rem | 61px | 700 | 1.1 |
| H1 | 3.052rem | 49px | 700 | 1.2 |
| H2 | 2.441rem | 39px | 600 | 1.25 |
| H3 | 1.953rem | 31px | 600 | 1.3 |
| H4 | 1.563rem | 25px | 600 | 1.35 |
| H5 | 1.25rem | 20px | 600 | 1.4 |
| Body Large | 1.125rem | 18px | 400 | 1.6 |
| Body | 1rem | 16px | 400 | 1.5 |
| Small | 0.875rem | 14px | 400 | 1.5 |
| Caption | 0.75rem | 12px | 400 | 1.4 |

### Responsive Adjustments
```css
/* Mobile (< 768px) */
h1 { font-size: 2rem; }    /* 32px */
h2 { font-size: 1.5rem; }  /* 24px */
h3 { font-size: 1.25rem; } /* 20px */
body { font-size: 1rem; }  /* 16px */

/* Desktop (>= 768px) */
h1 { font-size: 3rem; }    /* 48px */
h2 { font-size: 2.25rem; } /* 36px */
h3 { font-size: 1.75rem; } /* 28px */
body { font-size: 1rem; }  /* 16px */
```

## Font Weights

### Weight Scale
| Name | Value | Usage |
|------|-------|-------|
| Regular | 400 | Body text, paragraphs |
| Medium | 500 | Buttons, nav items |
| Semibold | 600 | Subheadings, emphasis |
| Bold | 700 | Headings, CTAs |

### Weight Pairing
- Headings: 600-700
- Body: 400
- Links: 500
- Buttons: 600

## Line Height Guidelines

### Rules
| Content Type | Line Height | Notes |
|--------------|-------------|-------|
| Headings | 1.1-1.3 | Tighter for visual impact |
| Body text | 1.5-1.6 | Optimal readability |
| Small text | 1.4-1.5 | Slightly tighter |
| Long-form | 1.6-1.75 | Extra comfortable |

## Letter Spacing

### Guidelines
| Element | Tracking | Value |
|---------|----------|-------|
| Display | Tighter | -0.02em |
| Headings | Normal | 0 |
| Body | Normal | 0 |
| All caps | Wider | 0.05em |
| Small caps | Wider | 0.1em |

## Paragraph Spacing

### Margins
```css
/* Heading spacing */
h1, h2 { margin-top: 2rem; margin-bottom: 1rem; }
h3, h4 { margin-top: 1.5rem; margin-bottom: 0.75rem; }

/* Paragraph spacing */
p { margin-bottom: 1rem; }
p + p { margin-top: 0; }
```

### Maximum Line Length
- Body text: 65-75 characters (optimal)
- Headings: Can be wider
- Code blocks: 80-100 characters

```css
.prose {
  max-width: 65ch;
}
```

## CSS Implementation

### Full Variables
```css
:root {
  /* Font Families */
  --font-heading: 'Inter', system-ui, sans-serif;
  --font-body: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  /* Font Sizes */
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.25rem;
  --text-5xl: 3rem;

  /* Font Weights */
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  /* Line Heights */
  --leading-none: 1;
  --leading-tight: 1.25;
  --leading-snug: 1.375;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
  --leading-loose: 2;
}
```

### Tailwind Config
```javascript
theme: {
  fontFamily: {
    heading: ['Inter', 'system-ui', 'sans-serif'],
    body: ['Inter', 'system-ui', 'sans-serif'],
    mono: ['JetBrains Mono', 'monospace'],
  },
  fontSize: {
    xs: ['0.75rem', { lineHeight: '1rem' }],
    sm: ['0.875rem', { lineHeight: '1.25rem' }],
    base: ['1rem', { lineHeight: '1.5rem' }],
    lg: ['1.125rem', { lineHeight: '1.75rem' }],
    xl: ['1.25rem', { lineHeight: '1.75rem' }],
    '2xl': ['1.5rem', { lineHeight: '2rem' }],
    '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
    '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
    '5xl': ['3rem', { lineHeight: '1.1' }],
  }
}
```

## Common Font Pairings

### Clean & Modern
- Heading: Inter
- Body: Inter

### Professional
- Heading: Playfair Display
- Body: Source Sans Pro

### Startup/Tech
- Heading: Poppins
- Body: Open Sans

### Editorial
- Heading: Merriweather
- Body: Lato

## Accessibility

### Minimum Sizes
- Body text: 16px minimum
- Small text: 14px minimum, not for long content
- Caption: 12px minimum, use sparingly

### Contrast Requirements
- Text on background: 4.5:1 minimum (AA)
- Large text (18px+): 3:1 minimum

### Best Practices
- Don't use all caps for long text
- Avoid justified text (use left-align)
- Ensure adequate line spacing
- Don't use thin weights (<400) at small sizes
