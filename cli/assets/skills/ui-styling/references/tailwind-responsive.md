# Tailwind CSS Responsive Design

Mobile-first breakpoints, responsive utilities, and adaptive layouts.

## Mobile-First Approach

Tailwind uses mobile-first responsive design. Base styles apply to all screen sizes, then use breakpoint prefixes to override at larger sizes.

```html
<!-- Base: 1 column (mobile)
     sm: 2 columns (tablet)
     lg: 4 columns (desktop) -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
  <div>Item 4</div>
</div>
```

## Breakpoint System

**Default breakpoints:**

| Prefix | Min Width | CSS Media Query |
|--------|-----------|-----------------|
| `sm:` | 640px | `@media (min-width: 640px)` |
| `md:` | 768px | `@media (min-width: 768px)` |
| `lg:` | 1024px | `@media (min-width: 1024px)` |
| `xl:` | 1280px | `@media (min-width: 1280px)` |
| `2xl:` | 1536px | `@media (min-width: 1536px)` |

## Responsive Patterns

### Layout Changes

```html
<!-- Vertical on mobile, horizontal on desktop -->
<div class="flex flex-col lg:flex-row gap-4">
  <div>Left</div>
  <div>Right</div>
</div>

<!-- 1 column -> 2 columns -> 3 columns -->
<div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
</div>
```

### Visibility

```html
<!-- Hide on mobile, show on desktop -->
<div class="hidden lg:block">
  Desktop only content
</div>

<!-- Show on mobile, hide on desktop -->
<div class="block lg:hidden">
  Mobile only content
</div>

<!-- Different content per breakpoint -->
<div class="lg:hidden">Mobile menu</div>
<div class="hidden lg:flex">Desktop navigation</div>
```

### Typography

```html
<!-- Responsive text sizes -->
<h1 class="text-2xl md:text-4xl lg:text-6xl font-bold">
  Heading scales with screen size
</h1>

<p class="text-sm md:text-base lg:text-lg">
  Body text scales appropriately
</p>
```

### Spacing

```html
<!-- Responsive padding -->
<div class="p-4 md:p-6 lg:p-8">
  More padding on larger screens
</div>

<!-- Responsive gap -->
<div class="flex gap-2 md:gap-4 lg:gap-6">
  <div>Item 1</div>
  <div>Item 2</div>
</div>
```

### Width

```html
<!-- Full width on mobile, constrained on desktop -->
<div class="w-full lg:w-1/2 xl:w-1/3">
  Responsive width
</div>

<!-- Responsive max-width -->
<div class="max-w-sm md:max-w-2xl lg:max-w-4xl mx-auto">
  Centered with responsive max width
</div>
```

## Common Responsive Layouts

### Sidebar Layout

```html
<div class="flex flex-col lg:flex-row min-h-screen">
  <!-- Sidebar: Full width on mobile, fixed on desktop -->
  <aside class="w-full lg:w-64 bg-gray-100 p-4">
    Sidebar
  </aside>

  <!-- Main content -->
  <main class="flex-1 p-4 md:p-8">
    Main content
  </main>
</div>
```

### Card Grid

```html
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
  <div class="bg-white rounded-lg shadow p-6">Card 1</div>
  <div class="bg-white rounded-lg shadow p-6">Card 2</div>
  <div class="bg-white rounded-lg shadow p-6">Card 3</div>
  <div class="bg-white rounded-lg shadow p-6">Card 4</div>
</div>
```

### Hero Section

```html
<section class="py-12 md:py-20 lg:py-32">
  <div class="container mx-auto px-4">
    <div class="flex flex-col lg:flex-row items-center gap-8 lg:gap-12">
      <div class="flex-1 text-center lg:text-left">
        <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold mb-4">
          Hero Title
        </h1>
        <p class="text-lg md:text-xl mb-6">
          Hero description
        </p>
        <button class="px-6 py-3 md:px-8 md:py-4">
          CTA Button
        </button>
      </div>
      <div class="flex-1">
        <img src="hero.jpg" class="w-full rounded-lg" />
      </div>
    </div>
  </div>
</section>
```

### Navigation

```html
<nav class="bg-white shadow">
  <div class="container mx-auto px-4">
    <div class="flex items-center justify-between h-16">
      <div class="text-xl font-bold">Logo</div>

      <!-- Desktop navigation -->
      <div class="hidden md:flex gap-6">
        <a href="#">Home</a>
        <a href="#">About</a>
        <a href="#">Services</a>
        <a href="#">Contact</a>
      </div>

      <!-- Mobile menu button -->
      <button class="md:hidden">
        <svg class="w-6 h-6">...</svg>
      </button>
    </div>
  </div>
</nav>
```

## Max-Width Queries

Apply styles only below certain breakpoint using `max-*:` prefix:

```html
<!-- Only on mobile and tablet (below 1024px) -->
<div class="max-lg:text-center">
  Centered on mobile/tablet, left-aligned on desktop
</div>

<!-- Only on mobile (below 640px) -->
<div class="max-sm:hidden">
  Hidden only on mobile
</div>
```

Available: `max-sm:` `max-md:` `max-lg:` `max-xl:` `max-2xl:`

## Range Queries

Apply styles between breakpoints:

```html
<!-- Only on tablets (between md and lg) -->
<div class="md:block lg:hidden">
  Visible only on tablets
</div>

<!-- Between sm and xl -->
<div class="sm:grid-cols-2 xl:grid-cols-4">
  2 columns on tablet, 4 on extra large
</div>
```

## Container Queries

Style elements based on parent container width:

```html
<div class="@container">
  <div class="@md:grid-cols-2 @lg:grid-cols-3">
    Responds to parent width, not viewport
  </div>
</div>
```

Container query breakpoints: `@sm:` `@md:` `@lg:` `@xl:` `@2xl:`

## Custom Breakpoints

Define custom breakpoints in theme:

```css
@theme {
  --breakpoint-3xl: 120rem;  /* 1920px */
  --breakpoint-tablet: 48rem;  /* 768px */
}
```

```html
<div class="tablet:grid-cols-2 3xl:grid-cols-6">
  Uses custom breakpoints
</div>
```

## Responsive State Variants

Combine responsive with hover/focus:

```html
<!-- Hover effect only on desktop -->
<button class="lg:hover:scale-105">
  Scale on hover (desktop only)
</button>

<!-- Different hover colors per breakpoint -->
<a class="hover:text-blue-600 lg:hover:text-purple-600">
  Link
</a>
```

## Best Practices

### 1. Mobile-First Design

Start with mobile styles, add complexity at larger breakpoints:

```html
<!-- Good: Mobile first -->
<div class="text-base md:text-lg lg:text-xl">

<!-- Avoid: Desktop first -->
<div class="text-xl lg:text-base">
```

### 2. Consistent Breakpoint Usage

Use same breakpoints across related elements:

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6 lg:gap-8">
  Spacing scales with layout
</div>
```

### 3. Test at Breakpoint Boundaries

Test at exact breakpoint widths (640px, 768px, 1024px, etc.) to catch edge cases.

### 4. Use Container for Content Width

```html
<div class="container mx-auto px-4 sm:px-6 lg:px-8">
  <div class="max-w-7xl">
    Content with consistent max width
  </div>
</div>
```

### 5. Progressive Enhancement

Ensure core functionality works on mobile, enhance for larger screens:

```html
<!-- Core layout works on mobile -->
<div class="p-4">
  <!-- Enhanced spacing on desktop -->
  <div class="lg:p-8">
    Content
  </div>
</div>
```

### 6. Avoid Too Many Breakpoints

Use 2-3 breakpoints per element for maintainability:

```html
<!-- Good: 2 breakpoints -->
<div class="grid-cols-1 md:grid-cols-2 lg:grid-cols-4">

<!-- Avoid: Too many breakpoints -->
<div class="grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6">
```

## Common Responsive Utilities

### Responsive Display

```html
<div class="block md:flex lg:grid">
  Changes display type per breakpoint
</div>
```

### Responsive Position

```html
<div class="relative lg:absolute">
  Positioned differently per breakpoint
</div>
```

### Responsive Order

```html
<div class="flex flex-col">
  <div class="order-2 lg:order-1">First on desktop</div>
  <div class="order-1 lg:order-2">First on mobile</div>
</div>
```

### Responsive Overflow

```html
<div class="overflow-auto lg:overflow-visible">
  Scrollable on mobile, expanded on desktop
</div>
```

## Testing Checklist

- [ ] Test at 320px (small mobile)
- [ ] Test at 640px (mobile breakpoint)
- [ ] Test at 768px (tablet breakpoint)
- [ ] Test at 1024px (desktop breakpoint)
- [ ] Test at 1280px (large desktop breakpoint)
- [ ] Test landscape orientation
- [ ] Verify touch targets (min 44x44px)
- [ ] Check text readability at all sizes
- [ ] Verify navigation works on mobile
- [ ] Test with browser zoom
