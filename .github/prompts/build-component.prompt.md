---
name: build-component
description: Build a UI component with proper styling, accessibility, and interactions
argument-hint: Describe the component (e.g., "navbar with dropdown", "pricing cards")
tools:
  - execute/runInTerminal
---

# Build UI Component

Create a professional UI component.

## Component: ${input:component:Describe your component}

## Step 1: Search Design Database

```bash
# Style guide
python3 .shared/ui-ux-pro-max/scripts/search.py "${input:style:modern}" --domain style

# Color palette
python3 .shared/ui-ux-pro-max/scripts/search.py "${input:industry:software}" --domain color

# UX guidelines for the component type
python3 .shared/ui-ux-pro-max/scripts/search.py "${input:component}" --domain ux

# Stack-specific best practices
python3 .shared/ui-ux-pro-max/scripts/search.py "component ${input:component}" --stack ${input:stack:html-tailwind}
```

## Step 2: Implement Component

Based on search results, create the component with:

### Visual Design
- Apply color palette (Primary, Secondary, CTA colors)
- Consistent with overall design system
- Proper spacing and typography

### Interaction States
- Default state
- Hover state (`transition-colors duration-200`)
- Active/pressed state
- Focus state (visible outline)
- Disabled state (reduced opacity)

### Accessibility
- Semantic HTML elements
- ARIA labels where needed
- Keyboard navigation support
- Color contrast (4.5:1 minimum)

### Technical
- Clean, maintainable code
- Responsive design
- No emojis as icons (use SVG)
- `cursor-pointer` on clickable elements
