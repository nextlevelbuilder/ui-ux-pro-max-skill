# User Settings Page Overrides

> **PROJECT:** FinApp
> **Generated:** 2026-01-17 16:35:37
> **Page Type:** Settings / Profile

> ⚠️ **IMPORTANT:** Rules in this file **override** the Master file (`design-system/MASTER.md`).
> Only deviations from the Master are documented here. For all other rules, refer to the Master.

---

## Page-Specific Rules

### Layout Overrides

- **Max Width:** 800px (narrow for readability)
- **Layout:** Left nav + content area, or tabbed sections
- **Sections:** Group related settings together

### Spacing Overrides

- **Section Padding:** 32px between setting groups
- **Form Field Gap:** 20px between fields
- **Setting Item:** 16px padding

### Typography Overrides

- **H1 (Settings Title):** 24px
- **Section Headers:** 18px, semi-bold
- **Setting Labels:** 14px
- **Helper Text:** 12px, muted color

### Color Overrides

- **Background:** White or very light gray
- **Danger Actions:** Red for destructive actions (delete account)
- **Success Feedback:** Green for saved/updated confirmations

### Component Overrides

- Toggle switches for on/off settings
- Form inputs with clear labels
- Save button: Fixed at bottom or per-section
- Danger zone: Separated, red-accented section for destructive actions

---

## Page-Specific Components

- Avatar upload with preview
- Password change form
- Notification preferences toggles
- Connected accounts/integrations
- Danger zone (delete account)

---

## Recommendations

- Auto-save where possible, or clear save indicators
- Confirm destructive actions with modal
- Group related settings logically
- Show success feedback after saving
