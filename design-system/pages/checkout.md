# Checkout Page Overrides

> **PROJECT:** ShopApp
> **Generated:** 2026-01-17 16:35:26
> **Page Type:** Checkout / Payment

> ⚠️ **IMPORTANT:** Rules in this file **override** the Master file (`design-system/MASTER.md`).
> Only deviations from the Master are documented here. For all other rules, refer to the Master.

---

## Page-Specific Rules

### Layout Overrides

- **Max Width:** 800px (narrow, focused flow)
- **Layout:** Single column, centered
- **Progress:** Step indicator at top

### Spacing Overrides

- **Section Padding:** 32px (generous for clarity)
- **Form Field Gap:** 24px between fields
- **Step Separation:** 48px between checkout steps

### Typography Overrides

- **H1 (Checkout Title):** 28px
- **Form Labels:** 14px, semi-bold
- **Price/Total:** 24px, bold, prominent

### Color Overrides

- **Background:** Clean white (#FFFFFF)
- **CTA Button:** High contrast, full-width on mobile
- **Trust Indicators:** Green for security, muted for secondary info

### Component Overrides

- Form inputs: Large touch targets (48px height minimum)
- CTA Button: Full-width, prominent, sticky on mobile
- Order summary: Collapsible on mobile, visible on desktop
- Trust badges: Payment icons, security seals

---

## Page-Specific Components

- Step progress indicator
- Order summary sidebar/panel
- Payment method selector
- Shipping address form
- Promo code input

---

## Recommendations

- Minimize distractions — no sidebar, minimal navigation
- Show trust signals (SSL, payment icons)
- Enable autofill for address fields
- Show clear error messages inline
