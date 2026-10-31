# contract-conformant — STATIC AUDIT FIXTURE (not a runnable app)

Regression fixture for QA finding N3-1: code that copies the generated contract's own
`component.*` / `semantic.*` literals must scan clean.

- `tokens.json` — snapshot of Example A's contract
  (`docs/examples/visual-design-pro-max/example-a-japanese-cute-animal-puzzle/project/design-system/onet-garden/tokens.json`,
  taken 2026-10-16). It emits literal component values that are not in `primitive.*`:
  `component.button.{primary,secondary,icon}.pressDuration = 90ms` and tinted hard shadows such as
  `0 4px 0 #972743, 0 8px 12px rgba(46, 42, 50, 0.14)`.
- `flutter/` — the QA reproduction verbatim: three widgets with `const Duration(milliseconds: 90)`.
- `web/` — the QA reproduction verbatim: CSS whose values are copied from `component.*`.

Expected: `audit.py scan flutter --contract tokens.json` and `audit.py scan web --contract tokens.json`
report zero findings and exit 0. Before the fix: 3 × duration.off-scale high (Flutter) and
2 × duration.off-scale + 3 × shadow.unlisted (web).
