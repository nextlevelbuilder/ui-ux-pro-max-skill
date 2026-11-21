# Layout Patterns

25 slide layouts with CSS structures and animation classes.

## Layout Selection by Use Case

| Layout | Use Case | Animation |
|--------|----------|-----------|
| Title Slide | Opening/first impression | `animate-fade-up` |
| Problem Statement | Establish pain point | `animate-stagger` |
| Solution Overview | Introduce solution | `animate-scale` |
| Feature Grid | Show capabilities (3-6 cards) | `animate-stagger` |
| Metrics Dashboard | Display KPIs (3-4 metrics) | `animate-stagger-scale` |
| Comparison Table | Compare options | `animate-fade-up` |
| Timeline Flow | Show progression | `animate-stagger` |
| Team Grid | Introduce people | `animate-stagger` |
| Quote Testimonial | Customer endorsement | `animate-fade-up` |
| Two Column Split | Compare/contrast | `animate-fade-up` |
| Big Number Hero | Single powerful metric | `animate-count` |
| Product Screenshot | Show product UI | `animate-scale` |
| Pricing Cards | Present tiers | `animate-stagger` |
| CTA Closing | Drive action | `animate-pulse` |

## CSS Structures

### Title Slide
```css
.slide-title {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
}
```

### Two Column Split
```css
.slide-split {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 48px;
    align-items: center;
}
@media (max-width: 768px) {
    .slide-split { grid-template-columns: 1fr; gap: 24px; }
}
```

### Feature Grid (3 columns)
```css
.slide-features {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
}
@media (max-width: 768px) {
    .slide-features { grid-template-columns: repeat(2, 1fr); gap: 16px; }
}
@media (max-width: 480px) {
    .slide-features { grid-template-columns: 1fr; }
}
```

### Metrics Dashboard (4 columns)
```css
.slide-metrics {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
}
@media (max-width: 768px) {
    .slide-metrics { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 480px) {
    .slide-metrics { grid-template-columns: 1fr; }
}
```

## Component Variants

### Card Styles
| Style | CSS Class | Use For |
|-------|-----------|---------|
| Icon Left | `.card-icon-left` | Features with icons |
| Accent Bar | `.card-accent-bar` | Highlighted features |
| Metric Card | `.card-metric` | Numbers/stats |
| Avatar Card | `.card-avatar` | Team members |
| Pricing Card | `.card-pricing` | Price tiers |

### Metric Styles
| Style | Effect |
|-------|--------|
| `gradient-number` | Gradient text on numbers |
| `oversized` | Extra large (120px+) |
| `sparkline` | Small inline chart |
| `funnel-numbers` | Conversion stages |

## Visual Treatments

| Treatment | When to Use |
|-----------|-------------|
| `gradient-glow` | Title slides, CTAs |
| `subtle-border` | Problem statements |
| `icon-top` | Feature grids |
| `screenshot-shadow` | Product screenshots |
| `popular-highlight` | Pricing (scale 1.05) |
| `bg-overlay` | Background images |
| `contrast-pair` | Before/after |
| `logo-grayscale` | Client logos |

## Search Commands

```bash
# Find layout for specific use
python .github/skills/design-system/scripts/search-slides.py "metrics dashboard" -d layout

# Contextual recommendation
python .github/skills/design-system/scripts/search-slides.py "traction slide" \
  --context --position 4 --total 10
```

## Layout Decision Flow

```
1. What's the slide goal?
   └─> Search layout-logic.csv

2. What emotion should it trigger?
   └─> Search color-logic.csv

3. What's the content type?
   └─> Search typography.csv

4. Should it break pattern?
   └─> Check position (1/3, 2/3) → Use full-bleed
```
