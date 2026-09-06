# Component Specifications

Detailed specs for core components with states and variants.

## Button

### Variants

| Variant | Background | Text | Border | Use Case |
|---------|------------|------|--------|----------|
| default | primary | white | none | Primary actions |
| secondary | gray-100 | gray-900 | none | Secondary actions |
| outline | transparent | foreground | border | Tertiary actions |
| ghost | transparent | foreground | none | Subtle actions |
| link | transparent | primary | none | Navigation |
| destructive | red-600 | white | none | Dangerous actions |

### Sizes

| Size | Height | Padding X | Padding Y | Font Size | Icon Size |
|------|--------|-----------|-----------|-----------|-----------|
| sm | 32px | 12px | 6px | 14px | 16px |
| default | 40px | 16px | 8px | 14px | 18px |
| lg | 48px | 24px | 12px | 16px | 20px |
| icon | 40px | 0 | 0 | - | 18px |

### States

| State | Background | Text | Opacity | Cursor |
|-------|------------|------|---------|--------|
| default | token | token | 1 | pointer |
| hover | darker | token | 1 | pointer |
| active | darkest | token | 1 | pointer |
| focus | token | token | 1 | pointer |
| disabled | muted | muted-fg | 0.5 | not-allowed |
| loading | token | token | 0.7 | wait |

### Anatomy

```
┌─────────────────────────────────────┐
│  [icon]  Label Text  [icon]         │
└─────────────────────────────────────┘
     ↑                      ↑
  leading icon         trailing icon
```

---

## Input

### Variants

| Variant | Description |
|---------|-------------|
| default | Standard text input |
| textarea | Multi-line text |
| select | Dropdown selection |
| checkbox | Boolean toggle |
| radio | Single selection |
| switch | Toggle switch |

### Sizes

| Size | Height | Padding | Font Size |
|------|--------|---------|-----------|
| sm | 32px | 8px 12px | 14px |
| default | 40px | 8px 12px | 14px |
| lg | 48px | 12px 16px | 16px |

### States

| State | Border | Background | Ring |
|-------|--------|------------|------|
| default | gray-300 | white | none |
| hover | gray-400 | white | none |
| focus | primary | white | primary/20% |
| error | red-500 | white | red/20% |
| disabled | gray-200 | gray-100 | none |

### Anatomy

```
Label (optional)
┌─────────────────────────────────────┐
│ [icon] Placeholder/Value   [action] │
└─────────────────────────────────────┘
Helper text or error message
```

---

## Card

### Variants

| Variant | Shadow | Border | Use Case |
|---------|--------|--------|----------|
| default | sm | 1px | Standard card |
| elevated | lg | none | Prominent content |
| outline | none | 1px | Subtle container |
| interactive | sm→md | 1px | Clickable card |

### Anatomy

```
┌─────────────────────────────────────┐
│ Card Header                         │
│   Title                             │
│   Description                       │
├─────────────────────────────────────┤
│ Card Content                        │
│   Main content area                 │
│                                     │
├─────────────────────────────────────┤
│ Card Footer                         │
│   Actions                           │
└─────────────────────────────────────┘
```

### Spacing

| Area | Padding |
|------|---------|
| header | 24px 24px 0 |
| content | 24px |
| footer | 0 24px 24px |
| gap | 16px |

---

## Badge

### Variants

| Variant | Background | Text |
|---------|------------|------|
| default | primary | white |
| secondary | gray-100 | gray-900 |
| outline | transparent | foreground |
| destructive | red-600 | white |
| success | green-600 | white |
| warning | yellow-500 | gray-900 |

### Sizes

| Size | Padding | Font Size | Height |
|------|---------|-----------|--------|
| sm | 4px 8px | 11px | 20px |
| default | 4px 10px | 12px | 24px |
| lg | 6px 12px | 14px | 28px |

---

## Alert

### Variants

| Variant | Icon | Background | Border |
|---------|------|------------|--------|
| default | info | gray-50 | gray-200 |
| destructive | alert | red-50 | red-200 |
| success | check | green-50 | green-200 |
| warning | warning | yellow-50 | yellow-200 |

### Anatomy

```
┌─────────────────────────────────────┐
│ [icon]  Title                    [×]│
│         Description text            │
└─────────────────────────────────────┘
```

---

## Dialog

### Sizes

| Size | Max Width | Use Case |
|------|-----------|----------|
| sm | 384px | Simple confirmations |
| default | 512px | Standard dialogs |
| lg | 640px | Complex forms |
| xl | 768px | Data-heavy dialogs |
| full | 100% - 32px | Full-screen on mobile |

### Anatomy

```
┌───────────────────────────────────────┐
│ Dialog Header                      [×]│
│   Title                               │
│   Description                         │
├───────────────────────────────────────┤
│ Dialog Content                        │
│   Scrollable if needed                │
│                                       │
├───────────────────────────────────────┤
│ Dialog Footer                         │
│                     [Cancel] [Confirm]│
└───────────────────────────────────────┘
```

---

## Table

### Row States

| State | Background | Use Case |
|-------|------------|----------|
| default | white | Normal row |
| hover | gray-50 | Mouse over |
| selected | primary/10% | Selected row |
| striped | gray-50/white | Alternating |

### Cell Alignment

| Content Type | Alignment |
|--------------|-----------|
| Text | Left |
| Numbers | Right |
| Status/Badge | Center |
| Actions | Right |

### Spacing

| Element | Value |
|---------|-------|
| cell padding | 12px 16px |
| header padding | 12px 16px |
| row height (compact) | 40px |
| row height (default) | 48px |
| row height (comfortable) | 56px |
