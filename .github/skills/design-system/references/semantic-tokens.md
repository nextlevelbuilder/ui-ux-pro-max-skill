# Semantic Tokens

Purpose-based aliases referencing primitive tokens.

## Color Semantics

### Background & Foreground

```css
:root {
  /* Page background */
  --color-background: var(--color-gray-50);
  --color-foreground: var(--color-gray-900);

  /* Card/surface background */
  --color-card: white;
  --color-card-foreground: var(--color-gray-900);

  /* Popover/dropdown */
  --color-popover: white;
  --color-popover-foreground: var(--color-gray-900);
}
```

### Primary

```css
:root {
  --color-primary: var(--color-blue-600);
  --color-primary-hover: var(--color-blue-700);
  --color-primary-active: var(--color-blue-800);
  --color-primary-foreground: white;
}
```

### Secondary

```css
:root {
  --color-secondary: var(--color-gray-100);
  --color-secondary-hover: var(--color-gray-200);
  --color-secondary-foreground: var(--color-gray-900);
}
```

### Muted

```css
:root {
  --color-muted: var(--color-gray-100);
  --color-muted-foreground: var(--color-gray-500);
}
```

### Accent

```css
:root {
  --color-accent: var(--color-gray-100);
  --color-accent-foreground: var(--color-gray-900);
}
```

### Destructive

```css
:root {
  --color-destructive: var(--color-red-600);
  --color-destructive-hover: var(--color-red-700);
  --color-destructive-foreground: white;
}
```

### Status Colors

```css
:root {
  --color-success: var(--color-green-600);
  --color-success-foreground: white;

  --color-warning: var(--color-yellow-500);
  --color-warning-foreground: var(--color-gray-900);

  --color-error: var(--color-red-600);
  --color-error-foreground: white;

  --color-info: var(--color-blue-500);
  --color-info-foreground: white;
}
```

### Border & Ring

```css
:root {
  --color-border: var(--color-gray-200);
  --color-input: var(--color-gray-200);
  --color-ring: var(--color-blue-500);
}
```

## Spacing Semantics

```css
:root {
  /* Component internal spacing */
  --spacing-component-xs: var(--space-1);
  --spacing-component-sm: var(--space-2);
  --spacing-component: var(--space-3);
  --spacing-component-lg: var(--space-4);

  /* Section spacing */
  --spacing-section-sm: var(--space-8);
  --spacing-section: var(--space-12);
  --spacing-section-lg: var(--space-16);

  /* Page margins */
  --spacing-page-x: var(--space-4);
  --spacing-page-y: var(--space-6);
}
```

## Typography Semantics

```css
:root {
  /* Headings */
  --font-heading: var(--font-size-2xl);
  --font-heading-lg: var(--font-size-3xl);
  --font-heading-xl: var(--font-size-4xl);

  /* Body */
  --font-body: var(--font-size-base);
  --font-body-sm: var(--font-size-sm);
  --font-body-lg: var(--font-size-lg);

  /* Labels & Captions */
  --font-label: var(--font-size-sm);
  --font-caption: var(--font-size-xs);
}
```

## Interactive States

```css
:root {
  /* Focus ring */
  --ring-width: 2px;
  --ring-offset: 2px;
  --ring-color: var(--color-ring);

  /* Opacity for disabled */
  --opacity-disabled: 0.5;

  /* Transitions */
  --transition-colors: color, background-color, border-color;
  --transition-transform: transform;
  --transition-all: all;
}
```

## Dark Mode Overrides

```css
.dark {
  --color-background: var(--color-gray-950);
  --color-foreground: var(--color-gray-50);

  --color-card: var(--color-gray-900);
  --color-card-foreground: var(--color-gray-50);

  --color-popover: var(--color-gray-900);
  --color-popover-foreground: var(--color-gray-50);

  --color-muted: var(--color-gray-800);
  --color-muted-foreground: var(--color-gray-400);

  --color-secondary: var(--color-gray-800);
  --color-secondary-foreground: var(--color-gray-50);

  --color-accent: var(--color-gray-800);
  --color-accent-foreground: var(--color-gray-50);

  --color-border: var(--color-gray-800);
  --color-input: var(--color-gray-800);
}
```

## Usage Patterns

### Applying Semantic Tokens

```css
/* Good - uses semantic tokens */
.card {
  background: var(--color-card);
  color: var(--color-card-foreground);
  border: 1px solid var(--color-border);
}

/* Bad - uses primitive tokens directly */
.card {
  background: var(--color-gray-50);
  color: var(--color-gray-900);
}
```

### Theme Switching

Semantic tokens enable instant theme switching:

```js
// Toggle dark mode
document.documentElement.classList.toggle('dark');
```
