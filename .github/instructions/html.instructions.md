---
applyTo: "**/*.html,**/*.htm"
---

# HTML UI/UX Design Guidelines

When working with HTML files for UI/UX design, follow these guidelines:

## Search Design Database First

Before implementing UI, search for relevant styles and guidelines:

```bash
# Get product-specific recommendations
python3 .shared/ui-ux-pro-max/scripts/search.py "<product-type>" --domain product

# Get style guide
python3 .shared/ui-ux-pro-max/scripts/search.py "<style-keywords>" --domain style

# Get color palette
python3 .shared/ui-ux-pro-max/scripts/search.py "<industry>" --domain color

# Get typography
python3 .shared/ui-ux-pro-max/scripts/search.py "<mood>" --domain typography

# Get HTML/Tailwind best practices
python3 .shared/ui-ux-pro-max/scripts/search.py "<topic>" --stack html-tailwind
```

## HTML + Tailwind Best Practices

### Structure
- Use semantic HTML5 elements (`<header>`, `<nav>`, `<main>`, `<section>`, `<footer>`)
- Apply Tailwind utilities directly in class attributes
- Use `max-w-6xl mx-auto` for centered containers

### Icons
- Use inline SVG with Heroicons or Lucide icons
- Standard sizing: `w-6 h-6` with `viewBox="0 0 24 24"`
- Never use emojis as icons

### Responsive Design
- Use Tailwind responsive prefixes: `sm:`, `md:`, `lg:`, `xl:`
- Mobile-first approach (default styles for mobile)
- Use `flex` and `grid` for layouts

### Accessibility
- Always include `alt` attributes on images
- Use proper heading hierarchy (h1 → h2 → h3)
- Ensure color contrast meets WCAG 2.1 AA standards
- Add `aria-label` for interactive elements without visible text

### Performance
- Lazy load images below the fold: `loading="lazy"`
- Use CDN links for Tailwind and fonts
- Minimize inline scripts
