---
applyTo: "**/*.css,**/*.scss,**/*.sass,**/*.less,**/tailwind.config.*"
---

# CSS/Styling Guidelines

When working with CSS or styling files, follow these guidelines:

## Search Design Database First

```bash
# Get style guide
python3 .shared/ui-ux-pro-max/scripts/search.py "<style-name>" --domain style

# Get CSS keywords and variables
python3 .shared/ui-ux-pro-max/scripts/search.py "<style-name>" --domain prompt

# Get color palette
python3 .shared/ui-ux-pro-max/scripts/search.py "<industry>" --domain color

# Get typography
python3 .shared/ui-ux-pro-max/scripts/search.py "<mood>" --domain typography
```

## CSS Best Practices

### Custom Properties (CSS Variables)
```css
:root {
  --color-primary: #3B82F6;
  --color-secondary: #6366F1;
  --color-cta: #10B981;
  --color-background: #FFFFFF;
  --color-text: #0F172A;
  --color-border: #E2E8F0;
  
  --font-heading: 'Inter', sans-serif;
  --font-body: 'Inter', sans-serif;
  
  --spacing-unit: 8px;
  --border-radius: 8px;
  --transition-fast: 150ms ease;
  --transition-normal: 300ms ease;
}
```

### Transitions
- Duration: 150-300ms for UI elements
- Easing: `ease` or `ease-in-out`
- Properties: specify explicitly (`transition-colors`, not `transition-all`)

### Hover States
- Use color/opacity changes, not scale transforms
- Maintain layout stability (no shift)
- Subtle shadow changes for elevation

### Dark Mode
```css
@media (prefers-color-scheme: dark) {
  :root {
    --color-background: #0F172A;
    --color-text: #F8FAFC;
    --color-border: #334155;
  }
}
```

### Reduced Motion
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Tailwind Config
When working with `tailwind.config.js`, extend theme with design tokens:
- Colors from color palette search
- Fonts from typography search
- Custom spacing if needed
