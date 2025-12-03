---
name: ui-ux-pro-max
description: Build professional UI/UX with design intelligence - styles, colors, typography, and best practices
argument-hint: Describe your UI/UX task (e.g., "landing page for SaaS", "dashboard for healthcare")
tools:
  - execute/runInTerminal
---

# UI/UX Pro Max - Design Intelligence

You have access to a comprehensive UI/UX design database. Follow this workflow to build professional UI.

## Step 1: Analyze Requirements

From the user request, identify:
- **Product type**: SaaS, e-commerce, portfolio, dashboard, landing page
- **Style keywords**: minimal, playful, professional, elegant, dark mode
- **Industry**: healthcare, fintech, gaming, education
- **Stack**: React, Vue, Next.js, or default to HTML + Tailwind

## Step 2: Search Design Database

Run these searches to gather design information:

```bash
# 1. Product recommendations
python3 .shared/ui-ux-pro-max/scripts/search.py "${input:productType:saas}" --domain product

# 2. Style guide
python3 .shared/ui-ux-pro-max/scripts/search.py "${input:styleKeywords:modern minimal}" --domain style

# 3. Typography
python3 .shared/ui-ux-pro-max/scripts/search.py "${input:mood:professional}" --domain typography

# 4. Color palette
python3 .shared/ui-ux-pro-max/scripts/search.py "${input:industry:software}" --domain color

# 5. UX guidelines
python3 .shared/ui-ux-pro-max/scripts/search.py "animation accessibility" --domain ux

# 6. Stack guidelines (default: html-tailwind)
python3 .shared/ui-ux-pro-max/scripts/search.py "layout responsive" --stack html-tailwind
```

## Step 3: Implement with Best Practices

### Icons
- Use SVG icons (Heroicons, Lucide), NOT emojis
- Standard sizing: `w-6 h-6` with `viewBox="0 0 24 24"`

### Interactions
- Add `cursor-pointer` to all clickable elements
- Use `transition-colors duration-200` for smooth feedback

### Light/Dark Mode
- Light mode glass cards: `bg-white/80` (not bg-white/10)
- Light mode text: `#0F172A` (slate-900) for body text

### Accessibility
- All images have alt text
- Form inputs have labels
- Color is not the only indicator

## Step 4: Deliver

Apply search results to create professional UI following the design system.
