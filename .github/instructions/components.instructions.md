---
applyTo: "**/components/**,**/pages/**,**/views/**,**/screens/**"
---

# UI Component Design Guidelines

When working on UI components in any framework, follow these design principles:

## Search Design Database First

Always search for relevant design information before implementing:

```bash
# Search by product type
python3 .shared/ui-ux-pro-max/scripts/search.py "<product-type>" --domain product

# Search by style
python3 .shared/ui-ux-pro-max/scripts/search.py "<style-keywords>" --domain style

# Search for colors
python3 .shared/ui-ux-pro-max/scripts/search.py "<industry>" --domain color

# Search UX guidelines
python3 .shared/ui-ux-pro-max/scripts/search.py "<topic>" --domain ux
```

## Universal Design Principles

### Visual Hierarchy
- Clear heading structure (H1 → H2 → H3)
- Consistent spacing (8px grid system)
- Visual weight guides attention

### Color Usage
- Primary: Main actions, key UI elements
- Secondary: Supporting elements
- CTA: Call-to-action buttons
- Background: Page/card backgrounds
- Text: Body text, headings
- Border: Dividers, input borders

### Typography
- Maximum 2 font families
- Heading font: Display/serif for personality
- Body font: Sans-serif for readability
- Line height: 1.5-1.75 for body text

### Icons
- SVG icons only (Heroicons, Lucide, SF Symbols)
- Consistent sizing within context
- Never use emoji as icons

### Interaction States
- Hover: Subtle color/shadow change
- Active: Pressed state feedback
- Focus: Visible outline for keyboard navigation
- Disabled: Reduced opacity (0.5-0.6)

### Responsive Design
- Mobile-first approach
- Breakpoints: 640px, 768px, 1024px, 1280px
- Touch targets: minimum 44x44px on mobile

### Accessibility (WCAG 2.1 AA)
- Color contrast: 4.5:1 for text, 3:1 for large text
- All interactive elements keyboard accessible
- Screen reader compatible
- Support reduced motion preference
