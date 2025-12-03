---
name: build-landing
description: Build a professional landing page with optimized structure, colors, and typography
argument-hint: Describe the product/service (e.g., "SaaS for project management", "skincare service")
tools:
  - execute/runInTerminal
---

# Build Landing Page

Create a professional landing page with optimized design.

## Task: ${input:description:Describe your product or service}

## Step 1: Search Design Database

```bash
# Product type recommendations
python3 .shared/ui-ux-pro-max/scripts/search.py "${input:description}" --domain product

# Landing page structure
python3 .shared/ui-ux-pro-max/scripts/search.py "hero pricing testimonial" --domain landing

# Color palette
python3 .shared/ui-ux-pro-max/scripts/search.py "${input:industry:saas}" --domain color

# Typography
python3 .shared/ui-ux-pro-max/scripts/search.py "professional modern" --domain typography

# Style guide
python3 .shared/ui-ux-pro-max/scripts/search.py "minimal modern" --domain style

# UX guidelines
python3 .shared/ui-ux-pro-max/scripts/search.py "animation cta" --domain ux
```

## Step 2: Implement Landing Page

Based on search results, create a landing page with:

### Structure (from landing search)
- Hero section with clear value proposition
- Features/benefits section
- Social proof (testimonials, logos)
- Pricing (if applicable)
- CTA sections
- Footer

### Design System (from search results)
- Apply color palette (Primary, Secondary, CTA, Background, Text, Border)
- Apply typography (Google Fonts import, heading/body fonts)
- Apply style effects (shadows, gradients, animations)

### Technical Requirements
- Semantic HTML5 structure
- Tailwind CSS for styling
- Mobile-first responsive design
- Accessible (WCAG 2.1 AA)
- SVG icons (no emojis)
