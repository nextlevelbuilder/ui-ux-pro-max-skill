# Primitive Tokens

Raw design values - foundation of the design system.

## Color Scales

### Gray Scale

```css
:root {
  --color-gray-50:  #F9FAFB;
  --color-gray-100: #F3F4F6;
  --color-gray-200: #E5E7EB;
  --color-gray-300: #D1D5DB;
  --color-gray-400: #9CA3AF;
  --color-gray-500: #6B7280;
  --color-gray-600: #4B5563;
  --color-gray-700: #374151;
  --color-gray-800: #1F2937;
  --color-gray-900: #111827;
  --color-gray-950: #030712;
}
```

### Primary Colors (Blue)

```css
:root {
  --color-blue-50:  #EFF6FF;
  --color-blue-100: #DBEAFE;
  --color-blue-200: #BFDBFE;
  --color-blue-300: #93C5FD;
  --color-blue-400: #60A5FA;
  --color-blue-500: #3B82F6;
  --color-blue-600: #2563EB;
  --color-blue-700: #1D4ED8;
  --color-blue-800: #1E40AF;
  --color-blue-900: #1E3A8A;
}
```

### Status Colors

```css
:root {
  /* Success - Green */
  --color-green-500: #22C55E;
  --color-green-600: #16A34A;

  /* Warning - Yellow */
  --color-yellow-500: #EAB308;
  --color-yellow-600: #CA8A04;

  /* Error - Red */
  --color-red-500: #EF4444;
  --color-red-600: #DC2626;

  /* Info - Blue */
  --color-info: var(--color-blue-500);
}
```

## Spacing Scale

4px base unit system.

```css
:root {
  --space-0:   0;
  --space-px:  1px;
  --space-0-5: 0.125rem;  /* 2px */
  --space-1:   0.25rem;   /* 4px */
  --space-1-5: 0.375rem;  /* 6px */
  --space-2:   0.5rem;    /* 8px */
  --space-2-5: 0.625rem;  /* 10px */
  --space-3:   0.75rem;   /* 12px */
  --space-3-5: 0.875rem;  /* 14px */
  --space-4:   1rem;      /* 16px */
  --space-5:   1.25rem;   /* 20px */
  --space-6:   1.5rem;    /* 24px */
  --space-7:   1.75rem;   /* 28px */
  --space-8:   2rem;      /* 32px */
  --space-9:   2.25rem;   /* 36px */
  --space-10:  2.5rem;    /* 40px */
  --space-12:  3rem;      /* 48px */
  --space-14:  3.5rem;    /* 56px */
  --space-16:  4rem;      /* 64px */
  --space-20:  5rem;      /* 80px */
  --space-24:  6rem;      /* 96px */
}
```

## Typography Scale

```css
:root {
  /* Font Sizes */
  --font-size-xs:   0.75rem;   /* 12px */
  --font-size-sm:   0.875rem;  /* 14px */
  --font-size-base: 1rem;      /* 16px */
  --font-size-lg:   1.125rem;  /* 18px */
  --font-size-xl:   1.25rem;   /* 20px */
  --font-size-2xl:  1.5rem;    /* 24px */
  --font-size-3xl:  1.875rem;  /* 30px */
  --font-size-4xl:  2.25rem;   /* 36px */
  --font-size-5xl:  3rem;      /* 48px */

  /* Line Heights */
  --leading-none:   1;
  --leading-tight:  1.25;
  --leading-snug:   1.375;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;
  --leading-loose:  2;

  /* Font Weights */
  --font-weight-normal:   400;
  --font-weight-medium:   500;
  --font-weight-semibold: 600;
  --font-weight-bold:     700;

  /* Letter Spacing */
  --tracking-tighter: -0.05em;
  --tracking-tight:   -0.025em;
  --tracking-normal:  0;
  --tracking-wide:    0.025em;
  --tracking-wider:   0.05em;
}
```

## Border Radius

```css
:root {
  --radius-none:    0;
  --radius-sm:      0.125rem;  /* 2px */
  --radius-default: 0.25rem;   /* 4px */
  --radius-md:      0.375rem;  /* 6px */
  --radius-lg:      0.5rem;    /* 8px */
  --radius-xl:      0.75rem;   /* 12px */
  --radius-2xl:     1rem;      /* 16px */
  --radius-3xl:     1.5rem;    /* 24px */
  --radius-full:    9999px;
}
```

## Shadows

```css
:root {
  --shadow-none: none;
  --shadow-sm:   0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-default: 0 1px 3px 0 rgb(0 0 0 / 0.1),
                    0 1px 2px -1px rgb(0 0 0 / 0.1);
  --shadow-md:   0 4px 6px -1px rgb(0 0 0 / 0.1),
                 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg:   0 10px 15px -3px rgb(0 0 0 / 0.1),
                 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-xl:   0 20px 25px -5px rgb(0 0 0 / 0.1),
                 0 8px 10px -6px rgb(0 0 0 / 0.1);
  --shadow-2xl:  0 25px 50px -12px rgb(0 0 0 / 0.25);
  --shadow-inner: inset 0 2px 4px 0 rgb(0 0 0 / 0.05);
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
  --duration-700: 700ms;
  --duration-1000: 1000ms;

  /* Semantic durations */
  --duration-fast:   var(--duration-150);
  --duration-normal: var(--duration-200);
  --duration-slow:   var(--duration-300);
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
