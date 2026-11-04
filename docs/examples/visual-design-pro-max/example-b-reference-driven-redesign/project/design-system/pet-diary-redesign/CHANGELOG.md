# Changelog

Append-only. `vd.py` writes `[tool]` entries; humans write `[manual]` entries (format: `## <ISO UTC> · <actor> · [manual]`).

## 2026-10-16T12:33:59Z · vd.py init · [tool]
- profile: style-profile.json (sha256 73c0e76468b6) · style: reference-derived-custom · derivation: token-derivation.md v1
- created: style-profile.json, tokens.json, component-catalog.md, asset-guidelines.md, interaction-guidelines.md, visual-qa-checklist.md, pages/README.md, MASTER.md
- skipped (exists): —
- master: created
- tokens: 25 semantic colours, 14 primitive groups, 6 components · unit logical · touch min 48

## 2026-10-16T12:33:59Z · vd.py page home · [tool]
- profile: style-profile.json (sha256 73c0e76468b6)
- created: pages/home.md
- reason: quick-action tiles use the two secondary tints (blue, mint) that the global palette rule reserves for category tiles only (reference rule-8, context:home)

## 2026-10-16T12:33:59Z · vd.py page diary · [tool]
- profile: style-profile.json (sha256 73c0e76468b6)
- created: pages/diary.md
- reason: the log is a dense chronological list: rows drop the card elevation and use a 1 px border divider so eight entries fit above the fold

## 2026-10-16T12:33:59Z · vd.py page profile · [tool]
- profile: style-profile.json (sha256 73c0e76468b6)
- created: pages/profile.md
- reason: settings rows are grouped lists: the destructive sign-out row uses semantic.color.danger instead of the brand orange that carries every other emphasis
