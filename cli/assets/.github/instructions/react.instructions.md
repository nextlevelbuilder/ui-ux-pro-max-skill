---
applyTo: "**/*.tsx,**/*.jsx"
---

# React/JSX UI/UX Design Guidelines

When working with React/JSX files for UI/UX design, follow these guidelines:

## Search Design Database First

Before implementing UI components, search for relevant styles:

```bash
# Get product-specific recommendations
python3 .shared/ui-ux-pro-max/scripts/search.py "<product-type>" --domain product

# Get style guide
python3 .shared/ui-ux-pro-max/scripts/search.py "<style-keywords>" --domain style

# Get color palette
python3 .shared/ui-ux-pro-max/scripts/search.py "<industry>" --domain color

# Get React-specific best practices
python3 .shared/ui-ux-pro-max/scripts/search.py "<topic>" --stack react

# For Next.js projects
python3 .shared/ui-ux-pro-max/scripts/search.py "<topic>" --stack nextjs
```

## React Component Best Practices

### Component Structure
- Use functional components with hooks
- Extract reusable UI elements into separate components
- Use TypeScript for type safety (`interface Props {}`)

### Styling
- Prefer Tailwind CSS or CSS Modules
- Use `cn()` or `clsx()` for conditional classes
- Define consistent spacing tokens

### Icons
- Import from `lucide-react` or `@heroicons/react`
- Pass `className` for sizing: `<Icon className="w-6 h-6" />`
- Never use emoji as icons in production UI

### State & Interactivity
- Use `useState` for local UI state
- Add `cursor-pointer` to clickable elements
- Use `transition-colors duration-200` for hover effects

### Accessibility
- Use semantic elements (`<button>`, `<a>`, `<nav>`)
- Add `aria-label` for icon-only buttons
- Implement keyboard navigation (`onKeyDown`)
- Use `role` attributes when semantic HTML isn't available

### Performance
- Lazy load heavy components with `React.lazy()`
- Memoize expensive components with `React.memo()`
- Use `useMemo` and `useCallback` appropriately
