# Tailwind CSS Utility Reference

Core utility classes for layout, spacing, typography, colors, borders, and shadows.

## Layout Utilities

### Display

```html
<div class="block">Block</div>
<div class="inline-block">Inline Block</div>
<div class="inline">Inline</div>
<div class="flex">Flexbox</div>
<div class="inline-flex">Inline Flex</div>
<div class="grid">Grid</div>
<div class="inline-grid">Inline Grid</div>
<div class="hidden">Hidden</div>
```

### Flexbox

**Container:**
```html
<div class="flex flex-row">Row (default)</div>
<div class="flex flex-col">Column</div>
<div class="flex flex-row-reverse">Reverse row</div>
<div class="flex flex-col-reverse">Reverse column</div>
```

**Justify (main axis):**
```html
<div class="flex justify-start">Start</div>
<div class="flex justify-center">Center</div>
<div class="flex justify-end">End</div>
<div class="flex justify-between">Space between</div>
<div class="flex justify-around">Space around</div>
<div class="flex justify-evenly">Space evenly</div>
```

**Align (cross axis):**
```html
<div class="flex items-start">Start</div>
<div class="flex items-center">Center</div>
<div class="flex items-end">End</div>
<div class="flex items-baseline">Baseline</div>
<div class="flex items-stretch">Stretch</div>
```

**Gap:**
```html
<div class="flex gap-4">All sides</div>
<div class="flex gap-x-6 gap-y-2">X and Y</div>
```

**Wrap:**
```html
<div class="flex flex-wrap">Wrap</div>
<div class="flex flex-nowrap">No wrap</div>
```

### Grid

**Columns:**
```html
<div class="grid grid-cols-1">1 column</div>
<div class="grid grid-cols-2">2 columns</div>
<div class="grid grid-cols-3">3 columns</div>
<div class="grid grid-cols-4">4 columns</div>
<div class="grid grid-cols-12">12 columns</div>
<div class="grid grid-cols-[1fr_500px_2fr]">Custom</div>
```

**Rows:**
```html
<div class="grid grid-rows-3">3 rows</div>
<div class="grid grid-rows-[auto_1fr_auto]">Custom</div>
```

**Span:**
```html
<div class="col-span-2">Span 2 columns</div>
<div class="row-span-3">Span 3 rows</div>
```

**Gap:**
```html
<div class="grid gap-4">All sides</div>
<div class="grid gap-x-8 gap-y-4">X and Y</div>
```

### Positioning

```html
<div class="static">Static (default)</div>
<div class="relative">Relative</div>
<div class="absolute">Absolute</div>
<div class="fixed">Fixed</div>
<div class="sticky">Sticky</div>

<!-- Position values -->
<div class="absolute top-0 right-0">Top right</div>
<div class="absolute inset-0">All sides 0</div>
<div class="absolute inset-x-4">Left/right 4</div>
<div class="absolute inset-y-8">Top/bottom 8</div>
```

### Z-Index

```html
<div class="z-0">z-index: 0</div>
<div class="z-10">z-index: 10</div>
<div class="z-20">z-index: 20</div>
<div class="z-50">z-index: 50</div>
```

## Spacing Utilities

### Padding

```html
<div class="p-4">All sides</div>
<div class="px-6">Left and right</div>
<div class="py-3">Top and bottom</div>
<div class="pt-8">Top</div>
<div class="pr-4">Right</div>
<div class="pb-2">Bottom</div>
<div class="pl-6">Left</div>
```

### Margin

```html
<div class="m-4">All sides</div>
<div class="mx-auto">Center horizontally</div>
<div class="my-6">Top and bottom</div>
<div class="mt-8">Top</div>
<div class="-mt-4">Negative top</div>
<div class="ml-auto">Push to right</div>
```

### Space Between

```html
<div class="space-x-4">Horizontal spacing</div>
<div class="space-y-6">Vertical spacing</div>
```

### Spacing Scale

- `0`: 0px
- `px`: 1px
- `0.5`: 0.125rem (2px)
- `1`: 0.25rem (4px)
- `2`: 0.5rem (8px)
- `3`: 0.75rem (12px)
- `4`: 1rem (16px)
- `6`: 1.5rem (24px)
- `8`: 2rem (32px)
- `12`: 3rem (48px)
- `16`: 4rem (64px)
- `24`: 6rem (96px)

## Typography

### Font Size

```html
<p class="text-xs">Extra small (12px)</p>
<p class="text-sm">Small (14px)</p>
<p class="text-base">Base (16px)</p>
<p class="text-lg">Large (18px)</p>
<p class="text-xl">XL (20px)</p>
<p class="text-2xl">2XL (24px)</p>
<p class="text-3xl">3XL (30px)</p>
<p class="text-4xl">4XL (36px)</p>
<p class="text-5xl">5XL (48px)</p>
```

### Font Weight

```html
<p class="font-thin">Thin (100)</p>
<p class="font-light">Light (300)</p>
<p class="font-normal">Normal (400)</p>
<p class="font-medium">Medium (500)</p>
<p class="font-semibold">Semibold (600)</p>
<p class="font-bold">Bold (700)</p>
<p class="font-black">Black (900)</p>
```

### Text Alignment

```html
<p class="text-left">Left</p>
<p class="text-center">Center</p>
<p class="text-right">Right</p>
<p class="text-justify">Justify</p>
```

### Line Height

```html
<p class="leading-none">1</p>
<p class="leading-tight">1.25</p>
<p class="leading-normal">1.5</p>
<p class="leading-relaxed">1.75</p>
<p class="leading-loose">2</p>
```

### Combined Font Utilities

```html
<h1 class="text-4xl/tight font-bold">
  Font size 4xl with tight line height
</h1>
```

### Text Transform

```html
<p class="uppercase">UPPERCASE</p>
<p class="lowercase">lowercase</p>
<p class="capitalize">Capitalize</p>
<p class="normal-case">Normal</p>
```

### Text Decoration

```html
<p class="underline">Underline</p>
<p class="line-through">Line through</p>
<p class="no-underline">No underline</p>
```

### Text Overflow

```html
<p class="truncate">Truncate with ellipsis...</p>
<p class="line-clamp-3">Clamp to 3 lines...</p>
<p class="text-ellipsis overflow-hidden">Ellipsis</p>
```

## Colors

### Text Colors

```html
<p class="text-black">Black</p>
<p class="text-white">White</p>
<p class="text-gray-500">Gray 500</p>
<p class="text-red-600">Red 600</p>
<p class="text-blue-500">Blue 500</p>
<p class="text-green-600">Green 600</p>
```

### Background Colors

```html
<div class="bg-white">White</div>
<div class="bg-gray-100">Gray 100</div>
<div class="bg-blue-500">Blue 500</div>
<div class="bg-red-600">Red 600</div>
```

### Color Scale

Each color has 11 shades (50-950):
- `50`: Lightest
- `100-400`: Light variations
- `500`: Base color
- `600-800`: Dark variations
- `950`: Darkest

### Opacity Modifiers

```html
<div class="bg-black/75">75% opacity</div>
<div class="text-blue-500/30">30% opacity</div>
<div class="bg-purple-500/[0.87]">87% opacity</div>
```

### Gradients

```html
<div class="bg-gradient-to-r from-blue-500 to-purple-600">
  Left to right gradient
</div>
<div class="bg-gradient-to-br from-pink-500 via-red-500 to-yellow-500">
  With via color
</div>
```

Directions: `to-t | to-tr | to-r | to-br | to-b | to-bl | to-l | to-tl`

## Borders

### Border Width

```html
<div class="border">1px all sides</div>
<div class="border-2">2px all sides</div>
<div class="border-t">Top only</div>
<div class="border-r-4">Right 4px</div>
<div class="border-b-2">Bottom 2px</div>
<div class="border-l">Left only</div>
<div class="border-0">No border</div>
```

### Border Color

```html
<div class="border border-gray-300">Gray</div>
<div class="border-2 border-blue-500">Blue</div>
<div class="border border-red-600/50">Red with opacity</div>
```

### Border Radius

```html
<div class="rounded">0.25rem</div>
<div class="rounded-md">0.375rem</div>
<div class="rounded-lg">0.5rem</div>
<div class="rounded-xl">0.75rem</div>
<div class="rounded-2xl">1rem</div>
<div class="rounded-full">9999px</div>

<!-- Individual corners -->
<div class="rounded-t-lg">Top corners</div>
<div class="rounded-br-xl">Bottom right</div>
```

### Border Style

```html
<div class="border border-solid">Solid</div>
<div class="border-2 border-dashed">Dashed</div>
<div class="border border-dotted">Dotted</div>
```

## Shadows

```html
<div class="shadow-sm">Small</div>
<div class="shadow">Default</div>
<div class="shadow-md">Medium</div>
<div class="shadow-lg">Large</div>
<div class="shadow-xl">Extra large</div>
<div class="shadow-2xl">2XL</div>
<div class="shadow-none">No shadow</div>
```

### Colored Shadows

```html
<div class="shadow-lg shadow-blue-500/50">Blue shadow</div>
```

## Width & Height

### Width

```html
<div class="w-full">100%</div>
<div class="w-1/2">50%</div>
<div class="w-1/3">33.333%</div>
<div class="w-64">16rem</div>
<div class="w-[500px]">500px</div>
<div class="w-screen">100vw</div>

<!-- Min/Max width -->
<div class="min-w-0">min-width: 0</div>
<div class="max-w-md">max-width: 28rem</div>
<div class="max-w-screen-xl">max-width: 1280px</div>
```

### Height

```html
<div class="h-full">100%</div>
<div class="h-screen">100vh</div>
<div class="h-64">16rem</div>
<div class="h-[500px]">500px</div>

<!-- Min/Max height -->
<div class="min-h-screen">min-height: 100vh</div>
<div class="max-h-96">max-height: 24rem</div>
```

## Arbitrary Values

Use square brackets for custom values:

```html
<!-- Spacing -->
<div class="p-[17px]">Custom padding</div>
<div class="top-[117px]">Custom position</div>

<!-- Colors -->
<div class="bg-[#bada55]">Hex color</div>
<div class="text-[rgb(123,45,67)]">RGB</div>

<!-- Sizes -->
<div class="w-[500px]">Custom width</div>
<div class="text-[22px]">Custom font size</div>

<!-- CSS variables -->
<div class="bg-[var(--brand-color)]">CSS var</div>

<!-- Complex values -->
<div class="grid-cols-[1fr_500px_2fr]">Custom grid</div>
```

## Aspect Ratio

```html
<div class="aspect-square">1:1</div>
<div class="aspect-video">16:9</div>
<div class="aspect-[4/3]">4:3</div>
```

## Overflow

```html
<div class="overflow-auto">Auto scroll</div>
<div class="overflow-hidden">Hidden</div>
<div class="overflow-scroll">Always scroll</div>
<div class="overflow-x-auto">Horizontal scroll</div>
<div class="overflow-y-hidden">No vertical scroll</div>
```

## Opacity

```html
<div class="opacity-0">0%</div>
<div class="opacity-50">50%</div>
<div class="opacity-75">75%</div>
<div class="opacity-100">100%</div>
```

## Cursor

```html
<div class="cursor-pointer">Pointer</div>
<div class="cursor-wait">Wait</div>
<div class="cursor-not-allowed">Not allowed</div>
<div class="cursor-default">Default</div>
```

## User Select

```html
<div class="select-none">No select</div>
<div class="select-text">Text selectable</div>
<div class="select-all">Select all</div>
```
