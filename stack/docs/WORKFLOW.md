# Workflow — the design loop, end to end

The stack is built around one loop: **plan → commit → build → see → review**. Skipping the
"see" and "review" steps is exactly what makes AI design look like AI design. Here's the loop
on a real task.

## Example: "Build a pricing section for a developer tool"

### 1. Plan with data (`/design-plan` → `ui-ux-pro-max`)

```
> /design-plan developer tool pricing section, technical audience, trustworthy, high-contrast
```

Claude runs the design-system generator and pulls the palette, a font pairing, and the relevant
UX anti-patterns (e.g. "don't hide the total", "make the recommended plan obvious"). Output is a
compact token set — 4–6 colors, 2 type roles, spacing scale.

### 2. Commit to a look (`frontend-design`)

Claude answers *purpose / tone / constraints / differentiation*, picks ONE tone (say
"precise, engineered, monospace-accented"), and chooses a single signature element (a subtle
grid-paper background behind the recommended plan). It explicitly rejects the cream+serif and
acid-on-black defaults.

### 3. Build

Implements with the chosen tokens. On a React project it uses the **shadcn MCP** to add a
`card`, `toggle`, and `badge` rather than hand-rolling them.

### 4. See it (Playwright MCP) — the step that matters

```
> Open it at http://localhost:3000/pricing. Screenshot mobile (375) and desktop (1440).
> Toggle monthly/annual and check the focus states.
```

Claude opens the real page and catches what code review can't: the annual/monthly toggle has no
visible focus ring, the "Most popular" badge overlaps the card border at 375px, and a price
number animates in before the card scrolls into view. It fixes each and re-screenshots.

### 5. Review (`/design-review`)

```
> /design-review http://localhost:3000/pricing
```

The subagent drives all six viewport tiers, tabs through the whole section, checks contrast on
the muted "per month" text, and returns:

```
Verdict: Ship with fixes
Blockers: none
High: "per user / month" text is 3.9:1 on the card background (fails AA for body text)
Medium: CTA tap target is 40px tall on mobile (<44)
What's working: type scale is consistent; recommended-plan emphasis is clear
```

Claude fixes the High + Medium and the section is done — distinctive, responsive, accessible,
and actually verified.

## The same loop for an existing site

Point the tools at what's already deployed:

```
> npm run audit -- --url https://your-site.com        # fast heuristic pass + screenshots
> /design-review https://your-site.com/pricing         # full review with taste + flows
```

## A worked audit on a production site

`examples/juniper-audit/` contains a real run of `scripts/design-audit.mjs` against a live
marketing site — the generated `report.md`, the per-viewport screenshots, and notes on how to
read the output. It's the fastest way to see what the heuristic layer catches before you wire
the stack into your own project.

## Rules of thumb

- **Never report UI work "done" without step 4.** If you didn't look at it, it isn't finished.
- **Let `ui-ux-pro-max` set tokens, `frontend-design` set attitude.** Data for correctness,
  taste for distinctiveness.
- **Blockers/High gate merging; Medium/Nit don't.** Keep momentum; don't bikeshed nitpicks.
- **Re-screenshot after every fix.** The loop is cheap; regressions are not.
