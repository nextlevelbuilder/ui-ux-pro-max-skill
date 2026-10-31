# Primitive Tokens — Andritz Precision

Raw design values for industrial precision design system with dark/light themes.

## Color Scales

### Andritz Blue Scale

```css
:root {
  --andritz-blue-900: #001c38;
  --andritz-blue-800: #003258;
  --andritz-blue-700: #004a77;
  --andritz-blue-600: #005c97;
  --andritz-blue-500: #0075be;
  --andritz-blue-400: #4d9fd4;
  --andritz-blue-300: #9bcaff;
  --andritz-blue-200: #c6dfff;
  --andritz-blue-100: #e0efff;
  --andritz-blue-50:  #f0f7ff;
}
```

### Surface Scale (Light Theme)

```css
:root {
  --surface-lowest:  #ffffff;
  --surface-low:     #f8fafb;
  --surface-base:    #f2f4f5;
  --surface-mid:     #eceeef;
  --surface-high:    #e6e8e9;
  --surface-highest: #e1e3e4;
}
```

### Surface Scale (Dark Theme)

```css
:root {
  --surface-dark-lowest:  #0a0e14;
  --surface-dark-low:     #10141a;
  --surface-dark-base:    #181c22;
  --surface-dark-mid:     #1c2026;
  --surface-dark-high:    #262a31;
  --surface-dark-highest: #31353c;
}
```

### Neutral Scale

```css
:root {
  --neutral-950: #001c38;  /* deepest black — replaces pure #000000 */
  --neutral-900: #191c1d;
  --neutral-700: #404751;
  --neutral-600: #49607f;
  --neutral-500: #4b5a69;
  --neutral-300: #c0c7d2;
  --neutral-200: #dfe2eb;
  --neutral-100: #eef1f6;
  --neutral-50:  #f5f7fa;
}
```

### Status Colors

```css
:root {
  /* Error */
  --color-error-600: #ba1a1a;
  --color-error-400: #ff6b6b;
  --color-error-300: #ffb4ab;
  --color-error-100: #ffdad6;
  --color-on-error: #ffffff;

  /* Warning / Tertiary (Caution Tape) */
  --color-tertiary-500: #ffb781;
  --color-tertiary-400: #ffc9a0;
  --color-tertiary-200: #ffe4cc;

  /* Success */
  --color-success-600: #1a8a4a;
  --color-success-400: #4ade80;
  --color-success-100: #dcfce7;

  /* Info */
  --color-info: var(--andritz-blue-300);
}
```

## Spacing Scale

8px grid base, extreme whitespace philosophy.

```css
:root {
  --space-0:   0;
  --space-px:  1px;
  --space-0-5: 0.125rem;  /* 2px */
  --space-1:   0.25rem;   /* 4px */
  --space-1-5: 0.375rem;  /* 6px */
  --space-2:   0.5rem;    /* 8px - base unit */
  --space-3:   0.75rem;   /* 12px */
  --space-4:   1rem;      /* 16px */
  --space-5:   1.25rem;   /* 20px */
  --space-6:   1.5rem;    /* 24px - component gap */
  --space-8:   2rem;      /* 32px - zone separation */
  --space-10:  2.5rem;    /* 40px */
  --space-12:  3rem;      /* 48px - section gap */
  --space-16:  4rem;      /* 64px */
  --space-20:  5rem;      /* 80px - extreme whitespace */
  --space-24:  6rem;      /* 96px */
  --space-32:  8rem;      /* 128px - hero spacing */
}
```

## Typography Scale

Blueprint Scale — engineered type hierarchy for industrial dashboards.

```css
:root {
  /* Font Families */
  --font-family-primary: 'Inter', system-ui, -apple-system, sans-serif;
  --font-family-premium: 'Gilroy', 'Inter', system-ui, sans-serif;

  /* Display — "stamped metal" KPIs */
  --font-size-display-lg: 3.5rem;   /* 56px */
  --font-size-display-md: 2.75rem;  /* 44px */
  --font-size-display-sm: 2.25rem;  /* 36px */

  /* Headline — structural beams */
  --font-size-headline-lg: 2rem;     /* 32px */
  --font-size-headline-md: 1.75rem;  /* 28px */
  --font-size-headline-sm: 1.5rem;   /* 24px */

  /* Title — navigation/card headers */
  --font-size-title-lg: 1.375rem;  /* 22px */
  --font-size-title-md: 1.125rem;  /* 18px */
  --font-size-title-sm: 1rem;      /* 16px */

  /* Body — high-density data */
  --font-size-body-lg: 1rem;      /* 16px */
  --font-size-body-md: 0.875rem;  /* 14px */
  --font-size-body-sm: 0.75rem;   /* 12px */

  /* Label — ALL CAPS machined look */
  --font-size-label-md: 0.75rem;   /* 12px */
  --font-size-label-sm: 0.6875rem; /* 11px */

  /* Line Heights */
  --leading-none:    1;
  --leading-tight:   1.2;
  --leading-snug:    1.35;
  --leading-normal:  1.5;
  --leading-relaxed: 1.625;

  /* Font Weights */
  --font-weight-regular:  400;
  --font-weight-medium:   500;
  --font-weight-semibold: 600;
  --font-weight-bold:     700;

  /* Letter Spacing */
  --tracking-tight:    -0.02em;  /* headlines — "technical manual" */
  --tracking-normal:   0;
  --tracking-wide:     0.05em;   /* labels — "machined" look */
  --tracking-wider:    0.1em;    /* display pairs — engineering drawing */
}
```

## Border Radius

Industrial Precision — 0px is the rule.

```css
:root {
  --radius-none: 0;      /* DEFAULT — used everywhere */
  --radius-full: 9999px; /* Only for status indicators/avatars */
  /* NO other radius values — 0px is the rule */
}
```

## Shadows

Ambient only — no drop shadows, no layered elevation.

```css
:root {
  --shadow-none: none;
  --shadow-ambient-light: 0px 12px 32px 0px rgba(0, 28, 56, 0.06);
  --shadow-ambient-dark:  0px 12px 32px 0px rgba(0, 28, 56, 0.4);
  --shadow-glow-primary:  0px 0px 8px var(--andritz-blue-300); /* dark theme pulse line */
  /* Ghost border fallback (not a shadow, but listed here for elevation) */
  --ghost-border-light: 1px solid rgba(192, 199, 210, 0.15);  /* outline-variant 15% */
  --ghost-border-dark:  1px solid rgba(64, 71, 81, 0.20);     /* outline-variant 20% */
}
```

## Motion / Duration

```css
:root {
  --duration-75:  75ms;
  --duration-100: 100ms;
  --duration-150: 150ms;
  --duration-200: 200ms;
  --duration-300: 300ms;
  --duration-500: 500ms;

  /* Semantic durations */
  --duration-fast:   var(--duration-150);
  --duration-normal: var(--duration-200);
  --duration-slow:   var(--duration-300);

  /* Easing */
  --ease-standard: ease-in-out;
  --ease-decelerate: ease-out;
}
```

## Z-Index Scale

```css
:root {
  --z-auto:     auto;
  --z-0:        0;
  --z-10:       10;
  --z-20:       20;
  --z-30:       30;
  --z-40:       40;
  --z-50:       50;
  --z-dropdown: 1000;
  --z-sticky:   1100;
  --z-modal:    1200;
  --z-popover:  1300;
  --z-tooltip:  1400;
}
```
