# States and Variants — Andritz Precision

Andritz industrial design system state definitions. Tonal shifts (not opacity) for hover, scale-[0.98] active press, bottom-border-only input focus, ghost borders.

## Interactive States

### State Definitions

| State | Trigger | Visual Change |
|-------|---------|---------------|
| default | None | Base appearance — tonal surface |
| hover | Mouse over | Tonal shift to next surface tier |
| focus | Tab/click | Ghost border OR bottom-border (inputs) |
| active | Mouse down | scale(0.98) press + tonal shift |
| disabled | disabled attr | Muted surface tier, reduced opacity |
| loading | Async action | Spinner + reduced opacity |

### State Priority (highest to lowest)

1. disabled
2. loading
3. active
4. focus
5. hover
6. default

### State Transitions (Industrial Precision)

```css
.interactive {
  transition-property: color, background-color, border-color, transform;
  transition-duration: var(--duration-fast);  /* 150ms */
  transition-timing-function: ease-in-out;
}
```

| Transition | Duration | Easing |
|------------|----------|--------|
| Color/background | 150ms | ease-in-out |
| Transform (scale) | 150ms | ease-out |
| Border-bottom | 150ms | ease-in-out |
| Opacity | 150ms | ease |
| Shadow | 200ms | ease-out |

## Focus States

### Input Focus (Bottom-Border Only — "Technical Ledger")

```css
/* Andritz input focus — bottom border only, NO ring */
.input:focus {
  outline: none;
  border-bottom: 2px solid var(--color-primary);  /* #005c97 light / #9bcaff dark */
  box-shadow: none;
}
```

### General Focus (Ghost Border)

```css
/* Non-input focus — ghost border appears */
.focusable:focus-visible {
  outline: none;
  box-shadow: 0 0 0 1px var(--color-outline-variant);  /* ghost border */
}
```

| Element | Focus Style |
|---------|-------------|
| Input/textarea | 2px primary bottom-border only |
| Button | Ghost border (outline-variant at 15%/20%) |
| Card (interactive) | Ambient shadow appears |
| Link | 2px primary bottom underline |

### Focus Within

```css
.container:focus-within {
  border-bottom-color: var(--color-primary);
}
```

## Hover States

### Tonal Shift Pattern

Hover uses surface tier shifts, not opacity changes:

```css
/* Button hover — tonal shift */
.button-secondary:hover {
  background: var(--color-surface-container-highest);
  /* shifts from surface-container-high to surface-container-highest */
}

/* Row hover — tonal shift */
.table-row:hover {
  background: var(--color-surface-container-low);
}

/* Tertiary button hover — bottom underline appears */
.button-tertiary:hover {
  text-decoration: none;
  border-bottom: 2px solid var(--color-primary);
}
```

## Active States

### Press Animation

```css
/* Primary button active — industrial press */
.button-primary:active {
  transform: scale(0.98);
  transition: transform var(--duration-fast) ease-out;
}

/* Card active (interactive) — subtle press */
.card-interactive:active {
  transform: scale(0.995);
}
```

| Component | Active Effect |
|-----------|---------------|
| Button (primary) | scale(0.98) + darker gradient |
| Button (secondary) | scale(0.98) + tonal shift |
| Card (interactive) | scale(0.995) |
| Nav item | Background shifts to surface-container-high |

## Disabled States

### Visual Treatment (Tonal, not just opacity)

```css
.disabled {
  opacity: 0.5;
  pointer-events: none;
  cursor: not-allowed;
  background: var(--color-surface-container);  /* muted surface tier */
  color: var(--color-on-surface-variant);
}
```

| Property | Disabled Value |
|----------|----------------|
| Opacity | 50% |
| Background | surface-container (muted tier) |
| Color | on-surface-variant |
| Pointer events | none |
| Cursor | not-allowed |
| Border | none (maintains No-Line Rule) |

### Accessibility

- Use `aria-disabled="true"` for semantic disabled
- Use `disabled` attribute for form elements
- Maintain 3:1 minimum contrast

## Loading States

### Spinner Placement

| Component | Spinner Position |
|-----------|------------------|
| Button | Center, replaces label |
| Input | Trailing position |
| Card | Center overlay with surface backdrop |
| Page | Center of viewport on surface |

### Loading Treatment

```css
.loading {
  position: relative;
  pointer-events: none;
}

.loading::after {
  content: '';
  /* Spinner using primary color */
  border: 2px solid var(--color-surface-container-high);
  border-top: 2px solid var(--color-primary);
  border-radius: var(--radius-full);  /* only exception to 0px rule */
  animation: spin 0.8s linear infinite;
}

.loading > * {
  opacity: 0.7;
}
```

## Error States

### Visual Treatment

```css
.error {
  background: var(--color-error-container);  /* #ffdad6 */
  color: var(--color-on-error-container);     /* #ba1a1a */
  border-bottom: 2px solid var(--color-error);
}

.error:focus {
  border-bottom: 2px solid var(--color-error);
  box-shadow: none;
}
```

| Element | Error Treatment |
|---------|-----------------|
| Input bg | error-container (#ffdad6) |
| Input bottom-border | 2px solid error (#ba1a1a) |
| Helper text | error color, body-sm |
| Icon | error color (functional, not decorative) |

## Dark Theme Specific States

### Pulse Line Glow (Data Visualization)

```css
.dark .chart-line {
  stroke: var(--color-primary-text);  /* #9bcaff */
  filter: drop-shadow(0px 0px 8px var(--color-primary-text));
}
```

### Caution/Warning State

```css
.dark .status-warning {
  color: var(--color-tertiary);  /* #ffb781 — "caution tape" effect */
  /* High contrast against navy base for immediate visibility */
}
```

### Ghost Border (Dark — 20% opacity)

```css
.dark .ghost-border {
  border: 1px solid rgba(64, 71, 81, 0.20);  /* outline-variant at 20% */
}
```

## Variant Patterns

### Color Variants

```css
.component {
  --component-bg: var(--color-primary);
  --component-fg: var(--color-on-primary);
  background: var(--component-bg);
  color: var(--component-fg);
}

.component.secondary {
  --component-bg: var(--color-surface-container-high);
  --component-fg: var(--color-primary-text);
}

.component.destructive {
  --component-bg: var(--color-error);
  --component-fg: var(--color-on-error);
}

.component.warning {
  --component-bg: rgba(255, 183, 129, 0.15);
  --component-fg: var(--color-tertiary);
}
```

### Size Variants

```css
.component {
  --component-height: 40px;
  --component-padding: var(--space-6);  /* 24px — industrial weight */
  --component-font: var(--font-size-label-md);
}

.component.sm {
  --component-height: 32px;
  --component-padding: var(--space-4);
  --component-font: var(--font-size-label-sm);
}

.component.lg {
  --component-height: 48px;
  --component-padding: var(--space-8);
  --component-font: var(--font-size-body-md);
}
```

## Accessibility Requirements

### Color Contrast

| Element | Minimum Ratio |
|---------|---------------|
| Primary text (on-surface) | 4.5:1 |
| Large text (display/headline) | 3:1 |
| UI components | 3:1 |
| Focus indicator (ghost border) | 3:1 |

### State Indicators

- Never rely on color alone — use icons (functional) + text
- Ghost borders must be "felt, not seen" but meet 3:1 contrast
- Focus must be visible in both light and dark themes
- Loading states: provide aria-busy announcements

### ARIA States

```html
<!-- Disabled -->
<button disabled aria-disabled="true">SUBMIT</button>

<!-- Loading -->
<button aria-busy="true" aria-describedby="loading-text">
  <span id="loading-text" class="sr-only">Loading...</span>
</button>

<!-- Error input -->
<input aria-invalid="true" aria-describedby="error-msg"
       style="background: var(--color-error-container);
              border-bottom: 2px solid var(--color-error);">
<span id="error-msg" role="alert">Error message</span>
```
