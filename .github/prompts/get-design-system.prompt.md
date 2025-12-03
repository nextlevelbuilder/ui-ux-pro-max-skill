---
name: get-design-system
description: Generate a complete design system with colors, typography, and components
argument-hint: Describe the product type and industry (e.g., "fintech SaaS", "beauty e-commerce")
tools:
  - execute/runInTerminal
---

# Generate Design System

Create a complete design system for your project.

## Project: ${input:project:Describe your project}

## Step 1: Search All Design Elements

```bash
# Product recommendations
python3 .shared/ui-ux-pro-max/scripts/search.py "${input:project}" --domain product

# Style guide
python3 .shared/ui-ux-pro-max/scripts/search.py "${input:style:modern professional}" --domain style

# Color palette
python3 .shared/ui-ux-pro-max/scripts/search.py "${input:project}" --domain color

# Typography
python3 .shared/ui-ux-pro-max/scripts/search.py "${input:mood:professional}" --domain typography

# CSS/Tailwind keywords
python3 .shared/ui-ux-pro-max/scripts/search.py "${input:style:modern}" --domain prompt
```

## Step 2: Generate Design System

Based on search results, create a design system document with:

### Color Palette
```css
:root {
  --color-primary: /* from color search */;
  --color-secondary: /* from color search */;
  --color-cta: /* from color search */;
  --color-background: /* from color search */;
  --color-text: /* from color search */;
  --color-border: /* from color search */;
}
```

### Typography
```css
/* Google Fonts import from typography search */
:root {
  --font-heading: /* from typography search */;
  --font-body: /* from typography search */;
}
```

### Tailwind Config
```javascript
// tailwind.config.js extension
module.exports = {
  theme: {
    extend: {
      colors: { /* from color search */ },
      fontFamily: { /* from typography search */ },
    }
  }
}
```

### Component Tokens
- Border radius
- Shadow levels
- Spacing scale
- Transition timing

### Usage Examples
- Button variants
- Card styles
- Form elements
- Navigation patterns
