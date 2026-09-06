# Color Palette Management

Guidelines for defining, extracting, and enforcing brand colors.

## Color System Structure

### Hierarchy
```
Primary Colors (1-2)
├── Main brand color - Used for CTAs, headers, key elements
└── Supporting primary - Secondary emphasis

Secondary Colors (2-3)
├── Accent colors - Highlights, interactive states
└── Supporting visuals - Icons, illustrations

Neutral Palette (3-5)
├── Background colors - Page, card, modal backgrounds
├── Text colors - Headings, body, muted text
└── UI elements - Borders, dividers, shadows

Semantic Colors (4)
├── Success - #22C55E (green)
├── Warning - #F59E0B (amber)
├── Error - #EF4444 (red)
└── Info - #3B82F6 (blue)
```

## Color Documentation Format

### Markdown Table
```markdown
| Name | Hex | RGB | HSL | Usage |
|------|-----|-----|-----|-------|
| Primary Blue | #2563EB | rgb(37,99,235) | hsl(217,91%,53%) | CTAs, links |
```

### CSS Variables
```css
:root {
  /* Primary */
  --color-primary: #2563EB;
  --color-primary-light: #3B82F6;
  --color-primary-dark: #1D4ED8;

  /* Secondary */
  --color-secondary: #8B5CF6;
  --color-accent: #F59E0B;

  /* Neutral */
  --color-background: #FFFFFF;
  --color-surface: #F9FAFB;
  --color-text-primary: #111827;
  --color-text-secondary: #6B7280;
  --color-border: #E5E7EB;
}
```

### Tailwind Config
```javascript
colors: {
  primary: {
    DEFAULT: '#2563EB',
    50: '#EFF6FF',
    100: '#DBEAFE',
    500: '#3B82F6',
    600: '#2563EB',
    700: '#1D4ED8',
  }
}
```

## Accessibility Requirements

### Contrast Ratios (WCAG 2.1)
| Level | Normal Text | Large Text | UI Components |
|-------|-------------|------------|---------------|
| AA | 4.5:1 | 3:1 | 3:1 |
| AAA | 7:1 | 4.5:1 | 4.5:1 |

### Checking Contrast
```javascript
// Formula for relative luminance
function luminance(r, g, b) {
  const [rs, gs, bs] = [r, g, b].map(v => {
    v /= 255;
    return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

function contrastRatio(l1, l2) {
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}
```

## Color Extraction

### From Images
Use `extract-colors.cjs` script to:
1. Load image file
2. Extract dominant colors using k-means clustering
3. Map to nearest brand colors
4. Report compliance percentage

### From Brand Guidelines
Parse markdown to extract:
- Hex values from tables
- CSS variable definitions
- Color names and usage descriptions

## Brand Compliance Validation

### Rules
1. **Primary color ratio**: 60-70% of design
2. **Secondary color ratio**: 20-30% of design
3. **Accent color ratio**: 5-10% of design
4. **Off-brand tolerance**: Max 20% non-palette colors

### Validation Output
```json
{
  "compliance": 85,
  "colors": {
    "brand": ["#2563EB", "#8B5CF6", "#FFFFFF"],
    "offBrand": ["#FF5500"],
    "dominant": "#2563EB"
  },
  "issues": [
    "Off-brand color #FF5500 detected (15% coverage)",
    "Primary color underused (45% vs 60% target)"
  ]
}
```

## Color Usage Guidelines

### Do's
- Use primary for main CTAs and key elements
- Maintain consistent hover/active states
- Test all combinations for accessibility
- Document color decisions

### Don'ts
- Use more than 2-3 colors in single component
- Mix warm and cool tones without intent
- Use pure black (#000) for text (use #111 or similar)
- Rely solely on color for meaning (use icons/text too)

## Color Palette Examples

### Tech/SaaS
```
Primary: #2563EB (Blue)
Secondary: #8B5CF6 (Purple)
Accent: #10B981 (Emerald)
Background: #F9FAFB
Text: #111827
```

### Marketing/Creative
```
Primary: #F97316 (Orange)
Secondary: #EC4899 (Pink)
Accent: #14B8A6 (Teal)
Background: #FFFFFF
Text: #1F2937
```

### Professional/Corporate
```
Primary: #1E40AF (Navy)
Secondary: #475569 (Slate)
Accent: #0EA5E9 (Sky)
Background: #F8FAFC
Text: #0F172A
```

## Tools & Resources

- [Coolors](https://coolors.co) - Palette generation
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Tailwind Color Reference](https://tailwindcss.com/docs/customizing-colors)
- [Color Hunt](https://colorhunt.co) - Curated palettes
