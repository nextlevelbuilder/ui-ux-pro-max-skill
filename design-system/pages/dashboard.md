# Dashboard Page Overrides

> **PROJECT:** TestApp2
> **Generated:** 2026-01-17 16:33:33
> **Page Type:** Dashboard / Data View

> ⚠️ **IMPORTANT:** Rules in this file **override** the Master file (`design-system/MASTER.md`).
> Only deviations from the Master are documented here. For all other rules, refer to the Master.

---

## Page-Specific Rules

### Layout Overrides

- **Max Width:** 1400px or full-width (wider than landing pages)
- **Grid:** 12-column grid for data flexibility
- **Sidebar:** Fixed 240px sidebar for navigation

### Spacing Overrides

- **Section Padding:** 24px (reduced from 48px for density)
- **Card Padding:** 16px (reduced from 24px)
- **Gap Between Cards:** 16px (reduced from 24px)
- **Content Density:** High — optimize for information display

### Typography Overrides

- **H1 (Page Title):** 24px (reduced from 48-64px)
- **H2 (Section Header):** 18px (reduced from 32px)
- **H3 (Card Title):** 16px (reduced from 24px)
- **Body:** 14px (reduced from 16px for data tables)
- **Monospace:** Use for numbers, IDs, timestamps

### Color Overrides

- **Background:** Neutral gray (#F8FAFC or #F1F5F9) for reduced eye strain
- **Primary Color Usage:** Actions only (buttons, links) — not for backgrounds
- **Status Colors:** Green (#22C55E) success, Yellow (#EAB308) warning, Red (#EF4444) error

### Component Overrides

- Cards: Compact padding (16px), subtle border, minimal shadow
- Tables: Alternating row colors, sticky headers, sortable columns
- Sidebar: Collapsible, icon + text navigation items
- Stat Cards: Number prominent, label secondary, trend indicator

---

## Page-Specific Components

- Data Tables with pagination and sorting
- Stat/Metric Cards with trends
- Charts (line, bar, pie) — use consistent chart library
- Filters and search bar
- Breadcrumb navigation

---

## Recommendations

- Prioritize data readability over visual impact
- Use consistent icon set for all actions
- Implement loading skeletons for async data
- Add keyboard shortcuts for power users
