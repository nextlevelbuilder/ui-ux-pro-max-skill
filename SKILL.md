---
name: ui-ux-pro-max
description: Professional UI/UX design intelligence skill. Generates complete design systems with industry-specific reasoning (192 product types across Tech/SaaS, Finance, Healthcare, E-commerce, Creative, Lifestyle). Provides 79 searchable UI styles (Glassmorphism, Bento Grid, Brutalism, Neumorphism, AI-Native, etc.), 192 color palettes, 74 font pairings, 25 chart types, 119 UX guidelines, and 22 tech stack implementations (React, Next.js, Vue, Svelte, SwiftUI, Flutter, shadcn/ui, Tailwind, Laravel, and more). Use when designing dashboards, landing pages, mobile apps, SaaS interfaces, fintech, healthcare, e-commerce, or any product UI. Triggers on keywords like "design system", "dashboard UI", "landing page", "color palette", "typography pairing", "UX best practices", "component design".
---

# UI/UX Pro Max

A comprehensive AI design intelligence skill that produces professional, production-ready UI/UX across web, mobile, and desktop platforms. Built and maintained as an open standard, this skill combines a curated design system generator with searchable catalogs for styles, palettes, typography, charts, and UX guidelines.

## When to Use This Skill

Trigger this skill automatically when the user asks for any of the following:

- "Build a landing page for my SaaS product"
- "Create a dashboard for healthcare analytics"
- "Design a portfolio website with dark mode"
- "Make a mobile app UI for e-commerce"
- "Build a fintech banking app with dark theme"
- "Generate a design system for my project"
- "Recommend a color palette for a wellness app"
- "Suggest font pairings for an editorial site"
- "What UI style fits a B2B SaaS dashboard?"
- Any request involving UI design, design tokens, design systems, color theory, typography selection, chart visualization, or UX best practices

## How This Skill Works

This skill ships four core capabilities:

1. **Design System Generator (flagship, v2.0+)** - An AI reasoning engine that analyzes the project's industry (out of 192 product types) and emits a complete design system: color palette with semantic tokens, typography scale with font pairings, spacing scale, elevation/shadow tokens, border radius scale, motion tokens, and component-level recommendations.

2. **Searchable Catalogs** - Five domains you can search by keyword:
   - **Style** - 79 UI styles (50 active, 29 supplemental), each with stable IDs and aliases (Glassmorphism, Claymorphism, Neumorphism, Bento Grid, Brutalism, Minimalism, Dark Mode, AI-Native UI, Editorial, etc.)
   - **Color** - 192 industry-specific palettes aligned 1:1 with the 192 product types
   - **Typography** - 74 curated font pairings with Google Fonts imports
   - **Chart** - 25 chart types with dashboard and analytics recommendations
   - **UX** - 119 guidelines covering best practices, anti-patterns, accessibility, resilient text layout, compact labels, and cancellable interactions

3. **Stack-Specific Guidelines** - Implementation guidance for 22 tech stacks, so recommendations translate directly to idiomatic code in the user's chosen framework.

4. **Industry Reasoning Rules** - 192 industry-specific rules across Tech & SaaS, Finance, Healthcare, E-commerce, Services, Creative, Lifestyle, and Emerging Tech.

## Supported Tech Stacks

| Category | Stacks |
|----------|--------|
| Web (HTML) | HTML + Tailwind (default) |
| React Ecosystem | React, Next.js, shadcn/ui |
| Vue Ecosystem | Vue, Nuxt.js, Nuxt UI |
| Angular | Angular |
| PHP | Laravel (Blade, Livewire, Inertia.js) |
| Other Web | Svelte, Astro, Three.js |
| Desktop | JavaFX, WPF, WinUI 3, Avalonia, Uno Platform, UWP |
| iOS | SwiftUI |
| Android | Jetpack Compose |
| Cross-Platform | React Native, Flutter |

## Using the Search Script (CLI)

# When invoked, this skill can run the bundled Python search script to query the catalogs. The script uses only the Python 3 standard library - no extra dependencies.

```bash
# Generate a full design system for a project
python3 src/ui-ux-pro-max/scripts/search.py "beauty spa wellness" --design-system -p "Serenity Spa"
python3 src/ui-ux-pro-max/scripts/search.py "fintech banking" --design-system -f markdown

# Domain-specific keyword search
python3 src/ui-ux-pro-max/scripts/search.py "glassmorphism" --domain style
python3 src/ui-ux-pro-max/scripts/search.py "elegant serif" --domain typography
python3 src/ui-ux-pro-max/scripts/search.py "dashboard" --domain chart
python3 src/ui-ux-pro-max/scripts/search.py "error summary validation" --domain ux

# Stack-specific guidelines
python3 src/ui-ux-pro-max/scripts/search.py "form validation" --stack react
python3 src/ui-ux-pro-max/scripts/search.py "responsive layout" --stack html-tailwind
python3 src/ui-ux-pro-max/scripts/search.py "tableview binding" --stack javafx
```

If the search script is not available in the user's environment, fall back to using the catalog knowledge directly from the `data/` directory in this skill folder.

## Output Format

When this skill is invoked, the agent should:

1. **Identify the industry / product type** from the user's request. If ambiguous, ask one clarifying question (e.g., "Is this for a B2B SaaS dashboard or a consumer mobile app?").

2. **Emit a Design System block** containing:
   - Color palette (primary, secondary, accent, neutral, semantic states) with hex values and semantic token names
   - Typography scale (display, heading, body, caption, mono) with font family, size, weight, line height
   - Spacing scale (4pt base, e.g., 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64)
   - Border radius scale (sm, md, lg, xl, full)
   - Elevation / shadow scale
   - Motion tokens (duration, easing)

3. **Recommend a UI style** from the catalog with rationale (e.g., "Bento Grid for the dashboard because the analytics surface benefits from modular cards").

4. **Recommend a chart type** for any data visualization needs.

5. **Provide stack-specific implementation hints** matched to the user's tech stack.

6. **Surface relevant UX guidelines** from the catalog (e.g., resilient text layout for variable content, accessible icon buttons with aria-label, cancellable rapid chip animations).

7. **Output as clean Markdown** with fenced code blocks for any code, token tables for the design system, and a "Why these choices" section explaining the rationale.

## Industry Coverage (192 product types)

The reasoning engine understands the following industries, grouped by domain:

- **Tech & SaaS**: SaaS, Micro SaaS, B2B Service, Developer Tool / IDE, AI/Chatbot Platform, Cybersecurity Platform
- **Finance**: Fintech/Crypto, Banking, Insurance, Personal Finance Tracker, Invoice & Billing Tool
- **Healthcare**: Medical Clinic, Pharmacy, Dental, Veterinary, Mental Health, Medication Reminder
- **E-commerce**: General, Luxury, Marketplace (P2P), Subscription Box, Food Delivery
- **Services**: Beauty/Spa, Restaurant, Hotel, Legal, Home Services, Booking & Appointment
- **Creative**: Portfolio, Agency, Photography, Gaming, Music Streaming, Photo/Video Editor
- **Lifestyle**: Habit Tracker, Recipe & Cooking, Meditation, Weather, Diary, Mood Tracker
- **Emerging Tech**: Web3/NFT, Spatial Computing, Quantum Computing, Autonomous Drone Fleet

If the user's industry is not in this list, pick the closest match and note the assumption.

## Example Session

> **User**: "Build a dashboard for healthcare analytics"

**Agent (using this skill)**:
1. Identify industry: Healthcare Analytics (reasoning rule: clinical data density, accessibility for medical professionals, WCAG AA mandatory, calm color palette to reduce decision fatigue).
2. Emit design system: Slate primary (#0F172A), Teal accent (#14B8A6), semantic states for patient status, Inter for body + IBM Plex Mono for vitals.
3. Recommend UI style: Bento Grid (modular cards for KPI tiles).
4. Recommend charts: Time-series line for trend, heatmap for distribution, donut for composition.
5. Recommend stack: Next.js + shadcn/ui + Tailwind (assumed default web stack).
6. Surface UX guidelines: Resilient text layout for variable patient names, accessible color contrast for status badges, tooltip + detail drawer pattern for drill-down.
7. Output as Markdown with token tables and rationale.

## Folder Layout

```
src/ui-ux-pro-max/
├── data/                <- Catalog data (styles, palettes, fonts, charts, UX, reasoning rules)
├── scripts/
│   └── search.py        <- Python 3 stdlib search script
└── templates/           <- Output templates for design system generation
```

## AutoClaw / ZCode Compatibility

This skill follows the standard `SKILL.md` format compatible with:
- AutoClaw (`~/.autoclaw/skills/ui-ux-pro-max/SKILL.md`)
- ZCode (`~/.zcode/skills/ui-ux-pro-max/SKILL.md`)
- OpenClaw (`.agents/skills/`)
- Any agent supporting the open SKILL.md standard

The frontmatter includes `name` and `description` as required by the standard. The `description` is under 1024 characters. The body is under 100KB.

## License

MIT - same as the upstream repository.

## Source

Forked from [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) with AutoClaw compatibility added.
