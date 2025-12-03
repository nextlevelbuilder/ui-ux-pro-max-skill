---
name: review-ui
description: Review UI code for design quality, accessibility, and best practices
argument-hint: Provide the file or code to review
tools:
  - execute/runInTerminal
---

# UI/UX Code Review

Review the UI code for design quality and best practices.

## File to Review: ${file}

## Step 1: Search UX Guidelines

```bash
# Get UX best practices
python3 .shared/ui-ux-pro-max/scripts/search.py "accessibility" --domain ux
python3 .shared/ui-ux-pro-max/scripts/search.py "animation" --domain ux
python3 .shared/ui-ux-pro-max/scripts/search.py "color contrast" --domain ux
```

## Step 2: Review Checklist

### Visual Quality
- [ ] No emojis used as icons (should use SVG)
- [ ] Icons from consistent set (Heroicons/Lucide)
- [ ] Hover states don't cause layout shift
- [ ] Consistent spacing and typography

### Interaction
- [ ] All clickable elements have `cursor-pointer`
- [ ] Hover states provide visual feedback
- [ ] Transitions are smooth (150-300ms)
- [ ] Focus states visible for keyboard navigation

### Light/Dark Mode
- [ ] Light mode text has sufficient contrast (4.5:1)
- [ ] Glass/transparent elements visible in light mode
- [ ] Borders visible in both modes

### Accessibility
- [ ] All images have alt text
- [ ] Form inputs have labels
- [ ] Color is not the only indicator
- [ ] `prefers-reduced-motion` respected

### Responsive
- [ ] Works at 320px, 768px, 1024px, 1440px
- [ ] No horizontal scroll on mobile
- [ ] Touch targets are minimum 44x44px

## Step 3: Report Issues

For each issue found, provide:
1. **Issue**: What's wrong
2. **Location**: Where in the code
3. **Fix**: How to fix it
4. **Severity**: Critical / Major / Minor
