# Intelligent Page Override Generation

## Summary
Enhances the `--page` flag to generate **intelligent, filled-in override content** based on detected page types, instead of empty templates.

## Problem
Previously, using `--page "dashboard"` created a template file with placeholder comments like:

```markdown
### Layout Overrides
- No overrides — use Master layout
```

This required manual work to fill in page-specific rules.

## Solution
Added `_generate_intelligent_overrides()` function that:
1. **Detects page type** from page name AND/OR query keywords
2. **Generates filled-in content** with specific rules for each type

### Supported Page Types

| Type | Keywords | Generated Rules |
|------|----------|-----------------|
| **Dashboard / Data View** | dashboard, admin, analytics, data, metrics, stats | Compact spacing (24px), data tables, 12-column grid, 14px body text, sidebar |
| **Checkout / Payment** | checkout, payment, cart, purchase, order | 800px narrow flow, step indicators, large form inputs, trust badges |
| **Settings / Profile** | settings, profile, account, preferences | Tabbed sections, toggles, danger zone for destructive actions |
| **Landing / Marketing** | landing, marketing, homepage, hero | Full-width hero, 80-120px section padding, feature grids |
| **Authentication** | login, signin, signup, register, auth | 400px centered card, social login buttons, minimal form |

## Example Output

```bash
python3 search.py "e-commerce" --design-system --persist -p "Shop" --page "checkout"
python3 search.py "SaaS analytics" --design-system --persist -p "DataApp" --page "dashboard"
```

**Output Structure (project-based):**
```
design-system/
├── shop/
│   ├── MASTER.md
│   └── pages/
│       └── checkout.md
└── dataapp/
    ├── MASTER.md
    └── pages/
        └── dashboard.md
```

**Before (Template):**
```markdown
### Layout Overrides
- No overrides — use Master layout
```

**After (Intelligent):**
```markdown
### Layout Overrides
- **Max Width:** 800px (narrow, focused flow)
- **Layout:** Single column, centered
- **Progress:** Step indicator at top

### Component Overrides
- Form inputs: Large touch targets (48px height minimum)
- CTA Button: Full-width, prominent, sticky on mobile
- Trust badges: Payment icons, security seals
```

## Files Changed
- `.shared/ui-ux-pro-max/scripts/design_system.py` — Added `_generate_intelligent_overrides()`
- All AI assistant folders synced

## Testing
```bash
# Dashboard detection
python3 search.py "SaaS app" --design-system --persist -p "Test" --page "dashboard"
# → Page Type: Dashboard / Data View ✅

# Checkout detection  
python3 search.py "store" --design-system --persist -p "Shop" --page "checkout"
# → Page Type: Checkout / Payment ✅

# Settings detection
python3 search.py "app" --design-system --persist -p "App" --page "user settings"
# → Page Type: Settings / Profile ✅
```

## Backward Compatibility
- No breaking changes
- Pages without detected keywords still get "General" type with basic template
