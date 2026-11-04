# fixed/ — PARTIALLY corrected copy of the drift-project fixture (STATIC, NOT RUNNABLE)

Copy of `.claude/skills/visual-audit/scripts/tests/fixtures/drift-project/` made for Example C.
Only `lib/` (Flutter) and `web/` were corrected; `unity/` is left exactly as in the fixture on
purpose, so the re-scan shows a partially fixed project (Unity findings stay "unchanged").
`build/` and `web/node_modules/` decoys are copied unchanged and must still be skipped.
Nothing here compiles or runs: it is a mixed Flutter / web / Unity text fixture.

Corrections (all literals replaced by the project's own token references):
- lib/screens/shop.dart   — AppColors / AppRadius / AppText / AppShadows / AppMotion instead of literals; Material icon only; 48x48 icon button
- lib/screens/rewards.dart — MainButton deleted, PrimaryButton reused
- web/shop.css            — var(--color-*), var(--radius-md), var(--font-body), var(--duration-base), var(--shadow-card); 44px icon button; readable promo text
- web/components/CtaButton.tsx — deleted (Button.tsx is canonical); @heroicons/react removed from web/package.json
