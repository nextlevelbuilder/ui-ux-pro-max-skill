---
applyTo: "**/*.vue"
---

# Vue UI/UX Design Guidelines

When working with Vue files for UI/UX design, follow these guidelines:

## Search Design Database First

Before implementing UI components, search for relevant styles:

```bash
# Get product-specific recommendations
python3 .shared/ui-ux-pro-max/scripts/search.py "<product-type>" --domain product

# Get style guide
python3 .shared/ui-ux-pro-max/scripts/search.py "<style-keywords>" --domain style

# Get color palette
python3 .shared/ui-ux-pro-max/scripts/search.py "<industry>" --domain color

# Get Vue-specific best practices
python3 .shared/ui-ux-pro-max/scripts/search.py "<topic>" --stack vue
```

## Vue Component Best Practices

### Component Structure
- Use Composition API with `<script setup>`
- Organize: `<script>`, `<template>`, `<style>`
- Use TypeScript with `defineProps<{}>()` and `defineEmits<{}>()`

### Styling
- Prefer Tailwind CSS or scoped styles
- Use `<style scoped>` to prevent style leaking
- Define CSS variables in `:root` for theming

### Icons
- Use `lucide-vue-next` or `@heroicons/vue`
- Pass size via props or class
- Avoid emoji icons in UI

### State & Interactivity
- Use `ref()` and `reactive()` for state
- Add `cursor-pointer` class to clickable elements
- Use `transition` component for animations

### Accessibility
- Use semantic elements
- Add `aria-` attributes where needed
- Implement keyboard handlers (`@keydown`)
- Test with screen readers

### Performance
- Use `defineAsyncComponent()` for lazy loading
- Use `v-memo` for expensive list items
- Avoid reactivity on large static data
