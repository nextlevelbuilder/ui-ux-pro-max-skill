---
applyTo: "**/*.svelte"
---

# Svelte UI/UX Design Guidelines

When working with Svelte files for UI/UX design, follow these guidelines:

## Search Design Database First

Before implementing UI components, search for relevant styles:

```bash
# Get product-specific recommendations
python3 .shared/ui-ux-pro-max/scripts/search.py "<product-type>" --domain product

# Get style guide
python3 .shared/ui-ux-pro-max/scripts/search.py "<style-keywords>" --domain style

# Get color palette
python3 .shared/ui-ux-pro-max/scripts/search.py "<industry>" --domain color

# Get Svelte-specific best practices
python3 .shared/ui-ux-pro-max/scripts/search.py "<topic>" --stack svelte
```

## Svelte Component Best Practices

### Component Structure
- Use Svelte 5 runes: `$state`, `$derived`, `$effect`
- Order: `<script>`, HTML, `<style>`
- TypeScript with `<script lang="ts">`

### Styling
- Prefer Tailwind CSS or scoped styles
- Styles are scoped by default in Svelte
- Use CSS variables for theming

### Icons
- Use `lucide-svelte` or inline SVG
- Pass size via props: `<Icon size={24} />`
- Never use emoji icons

### State & Interactivity
- Use `$state()` rune for reactive state (Svelte 5)
- Use `$derived()` for computed values
- Add `cursor-pointer` to clickable elements
- Use Svelte transitions: `transition:fade`

### Accessibility
- Use semantic HTML elements
- Add `aria-` attributes
- Handle keyboard events with `on:keydown`
- Use `<svelte:element>` for dynamic elements

### Performance
- Svelte compiles away framework overhead
- Use `{#key}` blocks for forced re-renders
- Lazy load components with dynamic imports
