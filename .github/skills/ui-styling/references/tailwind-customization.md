# Tailwind CSS Customization

Config file structure, custom utilities, plugins, and theme extensions.

## @theme Directive

Modern approach to customize Tailwind using CSS:

```css
@import "tailwindcss";

@theme {
  /* Custom colors */
  --color-brand-50: oklch(0.97 0.02 264);
  --color-brand-500: oklch(0.55 0.22 264);
  --color-brand-900: oklch(0.25 0.15 264);

  /* Custom fonts */
  --font-display: "Satoshi", "Inter", sans-serif;
  --font-body: "Inter", system-ui, sans-serif;

  /* Custom spacing */
  --spacing-18: calc(var(--spacing) * 18);
  --spacing-navbar: 4.5rem;

  /* Custom breakpoints */
  --breakpoint-3xl: 120rem;
  --breakpoint-tablet: 48rem;

  /* Custom shadows */
  --shadow-glow: 0 0 20px rgba(139, 92, 246, 0.3);

  /* Custom radius */
  --radius-large: 1.5rem;
}
```

**Usage:**
```html
<div class="bg-brand-500 font-display shadow-glow rounded-large">
  Custom themed element
</div>

<div class="tablet:grid-cols-2 3xl:grid-cols-6">
  Custom breakpoints
</div>
```

## Color Customization

### Custom Color Palette

```css
@theme {
  /* Full color scale */
  --color-primary-50: oklch(0.98 0.02 250);
  --color-primary-100: oklch(0.95 0.05 250);
  --color-primary-200: oklch(0.90 0.10 250);
  --color-primary-300: oklch(0.85 0.15 250);
  --color-primary-400: oklch(0.75 0.18 250);
  --color-primary-500: oklch(0.65 0.22 250);
  --color-primary-600: oklch(0.55 0.22 250);
  --color-primary-700: oklch(0.45 0.20 250);
  --color-primary-800: oklch(0.35 0.18 250);
  --color-primary-900: oklch(0.25 0.15 250);
  --color-primary-950: oklch(0.15 0.10 250);
}
```

### Semantic Colors

```css
@theme {
  --color-success: oklch(0.65 0.18 145);
  --color-warning: oklch(0.75 0.15 85);
  --color-error: oklch(0.60 0.22 25);
  --color-info: oklch(0.65 0.18 240);
}
```

```html
<div class="bg-success text-white">Success message</div>
<div class="border-error">Error state</div>
```

## Typography Customization

### Custom Fonts

```css
@theme {
  --font-sans: "Inter", system-ui, sans-serif;
  --font-serif: "Merriweather", Georgia, serif;
  --font-mono: "JetBrains Mono", Consolas, monospace;
  --font-display: "Playfair Display", serif;
}
```

```html
<h1 class="font-display">Display heading</h1>
<p class="font-sans">Body text</p>
<code class="font-mono">Code block</code>
```

### Custom Font Sizes

```css
@theme {
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;
  --font-size-3xl: 1.875rem;
  --font-size-4xl: 2.25rem;
  --font-size-5xl: 3rem;
  --font-size-jumbo: 4rem;
}
```

## Spacing Customization

```css
@theme {
  /* Add custom spacing values */
  --spacing-13: calc(var(--spacing) * 13);
  --spacing-15: calc(var(--spacing) * 15);
  --spacing-18: calc(var(--spacing) * 18);

  /* Named spacing */
  --spacing-header: 4rem;
  --spacing-footer: 3rem;
  --spacing-section: 6rem;
}
```

```html
<div class="p-18">Custom padding</div>
<section class="py-section">Section spacing</section>
```

## Custom Utilities

Create reusable utility classes:

```css
@utility content-auto {
  content-visibility: auto;
}

@utility tab-* {
  tab-size: var(--tab-size-*);
}

@utility glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}
```

**Usage:**
```html
<div class="content-auto">Optimized rendering</div>
<pre class="tab-4">Code with 4-space tabs</pre>
<div class="glass">Glassmorphism effect</div>
```

## Custom Variants

Create custom state variants:

```css
@custom-variant theme-midnight (&:where([data-theme="midnight"] *));
@custom-variant aria-checked (&[aria-checked="true"]);
@custom-variant required (&:required);
```

**Usage:**
```html
<div data-theme="midnight">
  <div class="theme-midnight:bg-navy-900">
    Applies in midnight theme
  </div>
</div>

<input class="required:border-red-500" required />
```

## Layer Organization

Organize CSS into layers:

```css
@layer base {
  h1 {
    @apply text-4xl font-bold tracking-tight;
  }

  h2 {
    @apply text-3xl font-semibold;
  }

  a {
    @apply text-blue-600 hover:text-blue-700 underline-offset-4 hover:underline;
  }

  body {
    @apply bg-background text-foreground antialiased;
  }
}

@layer components {
  .btn {
    @apply px-4 py-2 rounded-lg font-medium transition-colors;
  }

  .btn-primary {
    @apply bg-blue-600 text-white hover:bg-blue-700;
  }

  .btn-secondary {
    @apply bg-gray-200 text-gray-900 hover:bg-gray-300;
  }

  .card {
    @apply bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow;
  }

  .input {
    @apply w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent;
  }
}

@layer utilities {
  .text-balance {
    text-wrap: balance;
  }

  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }
}
```

## @apply Directive

Extract repeated utility patterns:

```css
.btn-primary {
  @apply bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-semibold px-6 py-3 rounded-lg shadow-md hover:shadow-lg transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-blue-300;
}

.input-field {
  @apply w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed;
}

.section-container {
  @apply container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl;
}
```

**Usage:**
```html
<button class="btn-primary">Click me</button>
<input class="input-field" />
<div class="section-container">Content</div>
```

## Plugins

### Official Plugins

```bash
npm install -D @tailwindcss/typography @tailwindcss/forms @tailwindcss/container-queries
```

```javascript
// tailwind.config.js
export default {
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/container-queries'),
  ],
}
```

**Typography plugin:**
```html
<article class="prose lg:prose-xl">
  <h1>Styled article</h1>
  <p>Automatically styled prose content</p>
</article>
```

**Forms plugin:**
```html
<!-- Automatically styled form elements -->
<input type="text" />
<select></select>
<textarea></textarea>
```

### Custom Plugin

```javascript
// tailwind.config.js
const plugin = require('tailwindcss/plugin')

export default {
  plugins: [
    plugin(function({ addUtilities, addComponents, theme }) {
      // Add utilities
      addUtilities({
        '.text-shadow': {
          textShadow: '2px 2px 4px rgba(0, 0, 0, 0.1)',
        },
        '.text-shadow-lg': {
          textShadow: '4px 4px 8px rgba(0, 0, 0, 0.2)',
        },
      })

      // Add components
      addComponents({
        '.card-custom': {
          backgroundColor: theme('colors.white'),
          borderRadius: theme('borderRadius.lg'),
          padding: theme('spacing.6'),
          boxShadow: theme('boxShadow.md'),
        },
      })
    }),
  ],
}
```

## Configuration Examples

### Complete Tailwind Config

```javascript
// tailwind.config.ts
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        brand: {
          50: '#f0f9ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Playfair Display', 'serif'],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "slide-in": {
          "0%": { transform: "translateX(-100%)" },
          "100%": { transform: "translateX(0)" },
        },
      },
      animation: {
        "slide-in": "slide-in 0.5s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}

export default config
```

## Dark Mode Configuration

```javascript
// tailwind.config.js
export default {
  darkMode: ["class"],  // or "media" for automatic
  // ...
}
```

**Usage:**
```html
<!-- Class-based -->
<html class="dark">
  <div class="bg-white dark:bg-gray-900">
    Responds to .dark class
  </div>
</html>

<!-- Media query-based -->
<div class="bg-white dark:bg-gray-900">
  Responds to system preference automatically
</div>
```

## Content Configuration

Specify files to scan for classes:

```javascript
// tailwind.config.js
export default {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./app/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}",
    "./pages/**/*.{js,jsx,ts,tsx}",
  ],
  // ...
}
```

### Safelist

Preserve dynamic classes:

```javascript
export default {
  safelist: [
    'bg-red-500',
    'bg-green-500',
    'bg-blue-500',
    {
      pattern: /bg-(red|green|blue)-(100|500|900)/,
    },
  ],
}
```

## Best Practices

1. **Use @theme for simple customizations**: Prefer CSS-based customization
2. **Extract components sparingly**: Use @apply only for truly repeated patterns
3. **Leverage design tokens**: Define custom tokens in @theme
4. **Layer organization**: Keep base, components, and utilities separate
5. **Plugin for complex logic**: Use plugins for advanced customizations
6. **Test dark mode**: Ensure custom colors work in both themes
7. **Document custom utilities**: Add comments explaining custom classes
8. **Semantic naming**: Use descriptive names (primary not blue)
