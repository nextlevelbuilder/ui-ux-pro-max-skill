# UI/UX Pro Max - Design Intelligence for GitHub Copilot

You have access to a comprehensive UI/UX design database with 57+ styles, 95+ color palettes, 56+ font pairings, 24+ chart types, and 98+ UX guidelines.

## Prerequisites

Ensure Python 3.x is installed for the search script.

## How to Use This Skill

When working on UI/UX tasks (design, build, create, implement, review, fix, improve), follow this workflow:

### Step 1: Analyze Requirements

Extract from user request:
- **Product type**: SaaS, e-commerce, portfolio, dashboard, landing page, etc.
- **Style keywords**: minimal, playful, professional, elegant, dark mode, etc.
- **Industry**: healthcare, fintech, gaming, education, etc.
- **Stack**: React, Vue, Next.js, or default to `html-tailwind`

### Step 2: Search Design Database

Use the search script to gather comprehensive design information:

```bash
python3 .shared/ui-ux-pro-max/scripts/search.py "<keyword>" --domain <domain> [-n <max_results>]
```

**Available Domains:**

| Domain | Use For | Example Keywords |
|--------|---------|------------------|
| `product` | Product type recommendations | SaaS, e-commerce, portfolio, healthcare |
| `style` | UI styles, colors, effects | glassmorphism, minimalism, dark mode, brutalism |
| `typography` | Font pairings, Google Fonts | elegant, playful, professional, modern |
| `color` | Color palettes by product type | saas, ecommerce, healthcare, beauty, fintech |
| `landing` | Page structure, CTA strategies | hero, testimonial, pricing, social-proof |
| `chart` | Chart types, library recommendations | trend, comparison, timeline, funnel, pie |
| `ux` | Best practices, anti-patterns | animation, accessibility, z-index, loading |
| `prompt` | AI prompts, CSS keywords | (style name) |

**Stack-Specific Search:**

```bash
python3 .shared/ui-ux-pro-max/scripts/search.py "<keyword>" --stack <stack>
```

Available stacks: `html-tailwind` (default), `react`, `nextjs`, `vue`, `svelte`, `swiftui`, `react-native`, `flutter`

### Step 3: Recommended Search Order

1. **Product** - Get style recommendations for product type
2. **Style** - Get detailed style guide (colors, effects, frameworks)
3. **Typography** - Get font pairings with Google Fonts imports
4. **Color** - Get color palette (Primary, Secondary, CTA, Background, Text, Border)
5. **Landing** - Get page structure (if landing page)
6. **Chart** - Get chart recommendations (if dashboard/analytics)
7. **UX** - Get best practices and anti-patterns
8. **Stack** - Get stack-specific guidelines

## Example Workflow

For request: "Build a landing page for my SaaS product"

```bash
# 1. Search product type
python3 .shared/ui-ux-pro-max/scripts/search.py "saas software" --domain product

# 2. Search style
python3 .shared/ui-ux-pro-max/scripts/search.py "modern minimal professional" --domain style

# 3. Search typography
python3 .shared/ui-ux-pro-max/scripts/search.py "professional modern" --domain typography

# 4. Search color palette
python3 .shared/ui-ux-pro-max/scripts/search.py "saas software" --domain color

# 5. Search landing structure
python3 .shared/ui-ux-pro-max/scripts/search.py "hero pricing" --domain landing

# 6. Search UX guidelines
python3 .shared/ui-ux-pro-max/scripts/search.py "animation accessibility" --domain ux

# 7. Search stack (default html-tailwind)
python3 .shared/ui-ux-pro-max/scripts/search.py "layout responsive" --stack html-tailwind
```

## Common UI Rules

### Icons & Visual Elements
- Use SVG icons (Heroicons, Lucide, Simple Icons), NOT emojis
- Use color/opacity transitions on hover, NOT scale transforms
- Use fixed viewBox (24x24) with consistent sizing (w-6 h-6)

### Interaction & Cursor
- Add `cursor-pointer` to all clickable elements
- Use `transition-colors duration-200` for smooth feedback
- Provide clear hover feedback (color, shadow, border)

### Light/Dark Mode Contrast
- Light mode glass cards: `bg-white/80` (not bg-white/10)
- Light mode text: `#0F172A` (slate-900) for body text
- Light mode muted: `#475569` (slate-600) minimum
- Light mode borders: `border-gray-200` (visible)

### Layout & Spacing
- Floating navbar: add `top-4 left-4 right-4` spacing
- Account for fixed navbar height with content padding
- Use consistent max-width (`max-w-6xl` or `max-w-7xl`)

## Pre-Delivery Checklist

### Visual Quality
- [ ] No emojis as icons (use SVG)
- [ ] Consistent icon set (Heroicons/Lucide)
- [ ] Correct brand logos (Simple Icons)
- [ ] Hover states don't cause layout shift

### Interaction
- [ ] All clickable elements have `cursor-pointer`
- [ ] Smooth transitions (150-300ms)
- [ ] Visible focus states for keyboard navigation

### Accessibility
- [ ] All images have alt text
- [ ] Form inputs have labels
- [ ] Color is not the only indicator
- [ ] `prefers-reduced-motion` respected

### Responsive
- [ ] Test at 320px, 768px, 1024px, 1440px
- [ ] No horizontal scroll on mobile
