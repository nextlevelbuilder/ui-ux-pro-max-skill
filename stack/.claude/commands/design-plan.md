---
description: Generate a concrete design system (tokens, style, type, UX) before building UI
argument-hint: <product/industry + keywords>, e.g. "fintech dashboard trustworthy data-dense"
---

Before writing any markup, produce a design system for: **$ARGUMENTS**

1. Run the `ui-ux-pro-max` design-system generator to get style + color tokens + typography +
   UX anti-patterns:
   ```bash
   python3 <ui-ux-pro-max-skill-path>/scripts/search.py "$ARGUMENTS" --design-system -p "Project"
   ```
   (Resolve `<ui-ux-pro-max-skill-path>` from the installed skill — see CLAUDE.md.)

2. Pull anything the brief needs specifically, e.g.:
   - `--domain color "<industry> <mood>"` for the palette / semantic tokens
   - `--domain typography "<mood>"` for font pairing + imports
   - `--domain web-vitals "<page type>"` for the performance budget
   - `--domain ux "<pattern>"` for do/don't guidance

3. Then apply the **frontend-design** lens: state purpose / tone / constraints / differentiation,
   pick ONE tone, choose a single signature element, and reject any choice that reads like a
   generic AI default.

Output a compact token block (4–6 named colors, 2–3 type roles, spacing scale, one signature
element) and a one-paragraph rationale. Do **not** start building until the tokens are decided.
