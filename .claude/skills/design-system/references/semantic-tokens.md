# Semantic Tokens — Andritz Precision

Purpose-based aliases referencing primitive tokens. Material Design surface hierarchy with Andritz industrial identity.

## Color Semantics

### Surface Hierarchy (Light — `:root`)

```css
:root {
  /* Surface Hierarchy — "Machined Plates" */
  --color-surface:                    var(--surface-low);        /* #f8fafb — application floor */
  --color-surface-container:          var(--surface-mid);        /* #eceeef — primary content */
  --color-surface-container-low:      var(--surface-base);       /* #f2f4f5 — sidebar/secondary */
  --color-surface-container-high:     var(--surface-high);       /* #e6e8e9 — interactive surfaces */
  --color-surface-container-highest:  var(--surface-highest);    /* #e1e3e4 — prominent highlights */
  --color-surface-container-lowest:   var(--surface-lowest);     /* #ffffff — cards for "pop" */

  /* Text & Content */
  --color-on-surface:          var(--neutral-900);   /* #191c1d — primary text */
  --color-on-surface-variant:  var(--neutral-700);   /* #404751 — secondary data */

  /* Primary (Andritz Blue) */
  --color-primary:             var(--andritz-blue-500);  /* #0075be — action containers */
  --color-primary-text:        var(--andritz-blue-600);  /* #005c97 — text/iconography */
  --color-primary-container:   var(--andritz-blue-500);  /* #0075be — CTA containers */
  --color-on-primary:          #ffffff;
  --color-primary-fixed-dim:   var(--andritz-blue-300);  /* #9bcaff — light blue text/icons */

  /* Secondary */
  --color-secondary:           var(--neutral-600);   /* #49607f */
  --color-secondary-container: var(--surface-high);  /* #e6e8e9 */

  /* Tertiary */
  --color-tertiary:            var(--neutral-500);   /* #4b5a69 */

  /* Error */
  --color-error:               var(--color-error-600);   /* #ba1a1a */
  --color-error-container:     var(--color-error-100);   /* #ffdad6 */
  --color-on-error:            #ffffff;
  --color-on-error-container:  var(--color-error-600);   /* #ba1a1a */

  /* Outline (Ghost Border) */
  --color-outline-variant:     var(--neutral-300);  /* #c0c7d2 at 15% opacity */
  --ghost-border-opacity:      0.15;

  /* Card / Popover */
  --color-card:                var(--color-surface-container-lowest);
  --color-card-foreground:     var(--color-on-surface);
  --color-popover:             var(--color-surface-container-lowest);
  --color-popover-foreground:  var(--color-on-surface);

  /* Muted */
  --color-muted:               var(--surface-mid);     /* #eceeef */
  --color-muted-foreground:    var(--neutral-700);     /* #404751 */

  /* Border & Ring */
  --color-border:    transparent;  /* No-Line Rule: no visible borders */
  --color-input:     var(--color-surface-container-highest);
  --color-ring:      var(--color-primary);

  /* Destructive */
  --color-destructive:            var(--color-error-600);
  --color-destructive-foreground: #ffffff;
}
```

### Dark Theme (`.dark`)

```css
.dark {
  /* Surface Hierarchy — "The Void" */
  --color-surface:                    #10141a;  /* application void */
  --color-surface-container:          #1c2026;  /* primary content */
  --color-surface-container-low:      #181c22;  /* secondary sections */
  --color-surface-container-high:     #262a31;  /* interactive surfaces */
  --color-surface-container-highest:  #31353c;  /* prominent highlights */
  --color-surface-container-lowest:   #0a0e14;  /* deepest recesses */

  /* Text & Content */
  --color-on-surface:          #dfe2eb;  /* primary text */
  --color-on-surface-variant:  #c0c7d2;  /* secondary data */

  /* Primary (Andritz Blue — inverted for dark) */
  --color-primary:             #0075be;  /* action containers */
  --color-primary-text:        #9bcaff;  /* text/iconography */
  --color-primary-container:   #0075be;
  --color-on-primary:          #ffffff;
  --color-primary-fixed-dim:   #9bcaff;

  /* Tertiary (Warning/Caution — "caution tape" high-contrast) */
  --color-tertiary:            #ffb781;

  /* Error */
  --color-error:               #ffb4ab;
  --color-error-container:     #93000a;
  --color-on-error-container:  #ffdad6;

  /* Outline (Ghost Border — 20% in dark) */
  --color-outline-variant:     #404751;
  --ghost-border-opacity:      0.20;

  /* Card / Popover */
  --color-card:                var(--color-surface-container);
  --color-card-foreground:     var(--color-on-surface);

  /* Muted */
  --color-muted:               #262a31;
  --color-muted-foreground:    #c0c7d2;

  /* Border & Ring */
  --color-border:    transparent;
  --color-input:     #0a0e14;  /* inset look */
  --color-ring:      #9bcaff;

  /* Deepest Black (NEVER use pure #000000) */
  --color-deepest-black:       #001c38;  /* on-secondary-fixed */
}
```

## Spacing Semantics

```css
:root {
  /* Component internal spacing — "Extreme Whitespace" */
  --spacing-component-xs: var(--space-1);   /* 4px */
  --spacing-component-sm: var(--space-2);   /* 8px */
  --spacing-component:    var(--space-4);   /* 16px */
  --spacing-component-lg: var(--space-6);   /* 24px */

  /* Zone & section spacing */
  --spacing-zone-gap:     var(--space-8);   /* 32px — zone separation */
  --spacing-section:      var(--space-12);  /* 48px — section gap */
  --spacing-section-lg:   var(--space-16);  /* 64px */
  --spacing-hero:         var(--space-32);  /* 128px — hero breathing room */

  /* Page margins */
  --spacing-page-x: var(--space-6);   /* 24px */
  --spacing-page-y: var(--space-8);   /* 32px */
}
```

## Typography Semantics

```css
:root {
  /* Font family */
  --font-heading:  var(--font-family-primary);  /* Inter */
  --font-body:     var(--font-family-primary);  /* Inter */
  --font-label:    var(--font-family-primary);  /* Inter */

  /* Display — bold only, "stamped metal" */
  --font-display-lg: var(--font-weight-bold) var(--font-size-display-lg) / var(--leading-tight) var(--font-heading);
  --font-display-md: var(--font-weight-bold) var(--font-size-display-md) / var(--leading-tight) var(--font-heading);
  --font-display-sm: var(--font-weight-bold) var(--font-size-display-sm) / var(--leading-tight) var(--font-heading);

  /* Headline — tight tracking, "technical manual" */
  --font-headline-tracking: var(--tracking-tight);  /* -0.02em */

  /* Label — ALL CAPS, wide tracking, "machined" */
  --font-label-transform: uppercase;
  --font-label-tracking: var(--tracking-wide);  /* +0.05em */
}
```

## Interactive States

```css
:root {
  --ring-width: 2px;
  --ring-offset: 0px;  /* No offset — industrial precision */
  --ring-color: var(--color-ring);

  --opacity-disabled: 0.5;

  --transition-colors: color, background-color, border-color;
  --transition-transform: transform;
  --transition-all: all;
}
```

## Usage Patterns

### Applying Semantic Tokens

```css
/* Good — uses Andritz semantic tokens */
.card {
  background: var(--color-surface-container-lowest);
  color: var(--color-on-surface);
  /* No border — No-Line Rule */
}

/* Bad — uses primitive tokens directly */
.card {
  background: #ffffff;
  color: #191c1d;
  border: 1px solid #c0c7d2;  /* violates No-Line Rule */
}
```

### Theme Switching

Semantic tokens enable instant theme switching — surfaces shift automatically:

```js
// Toggle dark mode — surfaces shift automatically
document.documentElement.classList.toggle('dark');
```
