# Antigravity Instructions: UI/UX Pro Max

These workspace instructions guide Antigravity and Agentic AI assistants when designing, styling, building, reviewing, or refactoring user interfaces in this workspace.

For Antigravity documentation on skills, rules, and customization, see:
- [Antigravity Documentation](https://antigravity.google)
- [Agent Skills & Rules Specification](https://docs.agentic.org)

---

## Skill Architecture & Locations

Antigravity automatically discovers and activates skills configured for the workspace or user:

1. **Project Skills (installed via `uipro init --ai antigravity`):**
   - Located at `.agents/skills/<skill-name>/SKILL.md`
   - Data and search scripts are collocated within `.agents/skills/<skill-name>/`
2. **Personal / Global Skills (installed via `uipro init --ai antigravity --global`):**
   - Located at `~/.agents/skills/<skill-name>/SKILL.md` (or `~/.gemini/antigravity/skills/`)
3. **Repository Development (working inside this repository):**
   - Source-of-truth files reside in `src/ui-ux-pro-max/` and `.claude/skills/`

---

## Skill Routing Matrix

When addressing UI/UX requests, route to the relevant skill domain before generating code:

| Skill | Primary Focus | Triggers / Use Cases |
| :--- | :--- | :--- |
| **`ui-ux-pro-max`** | Core UI/UX intelligence & strategy | Full interface design, product styling, style recommendations (51 active styles), 194 product palettes, 74 font pairings, 141 UX guidelines, 22 technology stacks |
| **`ui-styling`** | Component styling & tokens | shadcn/ui component integration, Tailwind CSS customization, responsive layout rules, dark mode theming, and micro-interactions |
| **`design-system`** | Systematic design tokens & specs | Design tokens (primitive, semantic, component), CSS variables, token architecture, and design token validation |
| **`brand`** | Visual brand identity & consistency | Brand guideline creation, brand color palettes, typography specifications, logo rules, and tone/voice frameworks |
| **`slides`** | Presentation & slide design | Pitch decks, slide layouts, copywriting formulas, and data presentation strategies |
| **`banner-design`** | Marketing & ad creatives | Hero banners, promotional ad sizes, display banners, social graphics, and layout safe zones |
| **`design`** | Multi-domain creative generation | Logo design, CIP (Corporate Identity Pack), SVG icon design, and mockup contexts |

---

## Searching Design Data

When searching for recommendations, use the bundled search scripts:

```bash
# In projects initialized with `uipro init --ai antigravity`:
python3 .agents/skills/ui-ux-pro-max/scripts/search.py "<query>" --domain <domain> [-n <max_results>]

# In repository development checkout:
python3 src/ui-ux-pro-max/scripts/search.py "<query>" --domain <domain> [-n <max_results>]
```

Available domains:
- `product`: Product type recommendations (SaaS, e-commerce, mobile app, dashboard)
- `style`: Visual style guidelines (minimalism, glassmorphism, brutalism, bento-grid, etc.)
- `color`: Curated color palettes with semantic role definitions
- `typography`: Font pairings with Google Fonts import links
- `ux`: Interaction patterns, usability heuristics, and anti-patterns
- `chart`: Data visualization and charting recommendations
- `landing`: High-conversion page structures and CTA strategies

Stack-specific guidance:
```bash
python3 .agents/skills/ui-ux-pro-max/scripts/search.py "<query>" --stack <stack>
```
Supported stacks (22 total) include, e.g.: `html-tailwind`, `react`, `nextjs`, `astro`, `vue`, `nuxtjs`, `nuxt-ui`, `svelte`, `swiftui`, `react-native`, `flutter`, `shadcn`, `jetpack-compose`, `angular`, `laravel`, `wpf`, `winui`.

---

## UI/UX Quality Guidelines

1. **Accessibility by Default:**
   - Maintain WCAG AA minimum contrast ratio (4.5:1 for normal text, 3:1 for large text and UI components).
   - Ensure full keyboard navigation (`Tab`, `Shift+Tab`, `Enter`, `Space`, `Escape`) with visible, distinct `:focus-visible` outlines.
   - Handle IME composition gracefully for text inputs to avoid prematurely intercepting `Enter`.
   - Include ARIA attributes (`aria-label`, `aria-expanded`, `aria-hidden`) where semantic HTML elements alone are insufficient.

2. **Responsive & Mobile-First:**
   - Design fluid layouts using CSS Grid and Flexbox across mobile, tablet, and desktop breakpoints.
   - Avoid fixed-width elements that cause horizontal overflow.
   - Touch targets must be at least 44×44px on mobile viewports.

3. **Systematic Design Decisions:**
   - Prefer design tokens (colors, spacing scale, font sizes) over arbitrary ad-hoc hex codes or magic pixel values.
   - Maintain visual hierarchy: 1 primary CTA per viewport, clear heading progression (h1 → h2 → h3), and consistent spacing rhythms.
   - Provide concrete, production-ready code with clean file structure.
