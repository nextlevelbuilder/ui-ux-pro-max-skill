<!-- generated-by: visual-direction vd.py 1.0.0; profile-hash: d350c253757e -->
# Visual QA Checklist — Onet Garden

Tick every item per screen before sign-off. Items come from `style-profile.json#qa_criteria` plus generic per-screen checks. Automated checks: `audit.py scan --contract tokens.json` (code) and `visual_qa.py checklist --profile style-profile.json` (screenshots) from the `visual-audit` skill.

## Profile criteria (every screen)

- [ ] All outlines are darker shades of their own fill, never #000
- [ ] Corner radius within the xl class on every panel and button
- [ ] Text contrast at least 4.5:1 on the cream background
- [ ] Tile silhouettes identical size and radius across the grid
- [ ] Reward screen uses the same character style as home
- [ ] Pressed state visible within 100ms
- [ ] Every `onX` text passes 4.5:1 on its `X`
- [ ] All interactive targets ≥ 48 logical px
- [ ] No colour, font family, radius, spacing or duration outside `tokens.json` without an intentional exception

## Screen: home

- [ ] Primary CTA is the single most saturated element
- [ ] HUD chips readable over the hero art
- [ ] Bottom navigation inside the thumb zone

## Screen: gameplay

- [ ] Board owns ≥ 60 % of the height; HUD ≤ 12 %
- [ ] Tiles ≥ touch minimum; selection feedback within 1 frame
- [ ] Timer/moves readable during motion; no shadows on HUD plates

## Screen: popup

- [ ] Scrim uses `semantic.color.overlay`; panel uses `component.popup.*`
- [ ] Close control ≥ touch minimum, top-right
- [ ] Entrance uses `primitive.duration.base` + `primitive.easing.enter`

## Screen: shop

- [ ] Price tags share one component; currency icons from one set
- [ ] Offer cards never louder than the primary CTA
- [ ] Purchase confirmation uses the confirm popup, not a toast

## Screen: reward

- [ ] Reward colour is `semantic.color.reward` only
- [ ] Beat length within `primitive.duration.reward` ± 20 %
- [ ] Skippable at 1.2 s; reduced-motion swap exists
