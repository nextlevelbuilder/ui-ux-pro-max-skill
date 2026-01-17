# Intelligent Page Override Generation (Data-Driven)

## Summary
Enhances the `--page` flag to generate **intelligent, filled-in override content** using the existing layered search infrastructure, instead of empty templates.

## Problem
Previously, using `--page "dashboard"` created a template file with placeholder comments like:

```markdown
### Layout Overrides
<!-- Example: This page uses a different max-width -->
```

This required manual work to fill in page-specific rules.

## Solution
Added `_generate_intelligent_overrides()` function that:
1. **Uses existing layered search** across style, UX, and landing CSVs
2. **Detects page type** from page name AND/OR query keywords
3. **Extracts relevant rules** from search results (layout, spacing, effects, etc.)

### How It Works

```python
# Uses existing search infrastructure - NO hardcoded rules
style_results = search(context, "style")      # From styles.csv
ux_results = search(context, "ux")            # From ux-guidelines.csv  
landing_results = search(context, "landing")  # From landing.csv

# Extracts layout, colors, recommendations from search results
layout["Sections"] = landing_results["Section Order"]
colors["Strategy"] = landing_results["Color Strategy"]
recommendations.append(f"Effects: {style_results['Effects & Animation']}")
```

### Supported Page Types (Auto-Detected)

| Type | Keywords |
|------|----------|
| Dashboard / Data View | dashboard, admin, analytics, data, metrics, stats |
| Checkout / Payment | checkout, payment, cart, purchase, order |
| Settings / Profile | settings, profile, account, preferences |
| Landing / Marketing | landing, marketing, homepage, hero |
| Authentication | login, signin, signup, register, auth |
| Pricing / Plans | pricing, plans, subscription, tiers |
| Blog / Article | blog, article, post, news, content |
| Product Detail | product, item, detail, pdp, shop |
| Search Results | search, results, browse, filter, catalog |

## Example Output

```bash
python3 search.py "e-commerce landing" --design-system --persist -p "Marketing Website" --page "homepage"
python3 search.py "SaaS analytics" --design-system --persist -p "SaaS App" --page "dashboard"
```

**Output Structure (project-based):**
```
design-system/
├── marketing-website/
│   ├── MASTER.md
│   └── pages/
│       └── homepage.md
└── saas-app/
    ├── MASTER.md
    └── pages/
        └── dashboard.md
```

**Generated Content (from CSV data):**
```markdown
### Layout Overrides
- **Max Width:** 1200px (standard)
- **Layout:** Full-width sections, centered content
- **Sections:** 1. Dynamic hero, 2. Features, 3. Testimonials, 4. CTA

### Color Overrides
- **Strategy:** Adaptive based on user data. A/B test color variations.

## Recommendations
- Effects: Number animations, trend indicators, percentage change animations
- CTA Placement: Context-aware placement based on user segment
```

## Key Design Decisions

1. **No new CSV files** - Leverages existing data (styles.csv, ux-guidelines.csv, landing.csv)
2. **Core unchanged** - `DesignSystemGenerator` class and `generate()` method untouched
3. **Additive only** - New optional parameters (`persist`, `page`, `output_dir`)
4. **Project folders** - Each project gets its own directory (`design-system/<project>/`)

## Files Changed
- `.shared/ui-ux-pro-max/scripts/design_system.py`
  - Added `persist`, `page`, `output_dir` params to `generate_design_system()`
  - Added `persist_design_system()` function
  - Added `format_master_md()` function  
  - Enhanced `format_page_override_md()` with intelligent content
  - Added `_generate_intelligent_overrides()` using layered search
  - Added `_detect_page_type()` helper
- All AI assistant folders synced

## Testing
```bash
# Dashboard detection (uses style + landing search)
python3 search.py "SaaS analytics" --design-system --persist -p "SaaS App" --page "dashboard"
# → Extracts: Effects, Section Order, Color Strategy from CSVs ✅

# Landing page detection
python3 search.py "marketing website" --design-system --persist -p "Marketing Website" --page "homepage"
# → Page Type: Landing / Marketing ✅
```

## Backward Compatibility
- No breaking changes - all new params are optional
- Without `--persist`, behavior is identical to original
- Core generation logic completely unchanged

---

**@nextlevelbuilder** — Ready for review! This uses the existing layered search (no hardcoded rules) to generate intelligent page overrides. Would appreciate an expedited merge. Thank you!
