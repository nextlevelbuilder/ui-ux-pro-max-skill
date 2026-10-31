<!-- generated-by: visual-direction vd.py 1.0.0; profile-hash: 73c0e76468b6 -->
# Visual QA Checklist — Pet Diary Redesign

Tick every item per screen before sign-off. Items come from `style-profile.json#qa_criteria` plus generic per-screen checks. Automated checks: `audit.py scan --contract tokens.json` (code) and `visual_qa.py checklist --profile style-profile.json` (screenshots) from the `visual-audit` skill.

## Profile criteria (every screen)

- [ ] palette: One brand orange carries all emphasis (brand mark, key numbers, active state, status dots); secondary tints are reserved for category tiles only.
- [ ] radius: Radius ladder: cards 20–28px, tiles 12–14px, controls circular/pill; nothing below 12px except text.
- [ ] outline: All surfaces use a 2px peach outline (light tint of brand), never grey/black; outline is the primary separation device, shadow is secondary.
- [ ] typography: Two-family system: rounded display family for headings/numbers (bold), neutral sans for body; captions one step smaller and muted.
- [ ] icon: Filled rounded glyphs, single colour, same optical size across the app bar, tiles and nav.
- [ ] button.icon: Circular 44px white button with 2px peach outline and orange glyph.
- [ ] nav: Bottom nav active state = peach pill + orange icon/label; max 4–5 items.
- [ ] Every rule in style-profile.json cites an observation id
- [ ] Fields with no observation are marked not-derivable or inherited from a named catalog style
- [ ] Palette seeds match palette_observed roles
- [ ] Text contrast at least 4.5:1 after extraction (adjust text, not background)
- [ ] Enum fields hold valid catalog values, never free text
- [ ] Every `onX` text passes 4.5:1 on its `X`
- [ ] All interactive targets ≥ 48 logical px
- [ ] No colour, font family, radius, spacing or duration outside `tokens.json` without an intentional exception

## Screen: home

- [ ] One primary action per view
- [ ] Hierarchy by weight and spacing, not boxes
- [ ] Navigation inside the thumb zone on mobile

## Screen: list

- [ ] Row height from tokens; dividers use `semantic.color.border`
- [ ] Empty, loading and error states present
- [ ] Tap target ≥ touch minimum per row

## Screen: detail

- [ ] Title uses `semantic.typography.title`; body uses `.body`
- [ ] Secondary actions subordinate to the primary
- [ ] Back navigation consistent with the platform

## Screen: form

- [ ] Inputs use `component.*` tokens; focus ring visible
- [ ] Validation messages use `semantic.color.danger` + icon/text
- [ ] Disabled state readable (opacity token), not focusable

## Screen: settings

- [ ] Grouped lists with consistent spacing tokens
- [ ] Destructive actions styled with `button.destructive` + confirm
- [ ] Theme switch keeps contrast ≥ 4.5:1 in both modes
