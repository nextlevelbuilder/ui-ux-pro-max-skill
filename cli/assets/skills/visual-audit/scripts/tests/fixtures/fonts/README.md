# fonts — STATIC AUDIT FIXTURE (not a runnable app)

Two tiny inputs for the font-family extractors of `audit.py scan`, audited against
`../drift-project/tokens.json` (contract families: Fredoka, Nunito).

- `tailwind-page/index.html` — Google Fonts `<link>` (css2 + `&amp;`), inline `tailwind.config = {...}`
  with a `fontFamily` block, a `<style>` with `@import url(...css?family=A|B)` followed by a rule,
  an inline `style="..."` attribute and a Vue-style `:style` binding that must be ignored.
- `tailwind-config/tailwind.config.js` — a Tailwind config file with `fontFamily` entries in array,
  string, `var()` and generic-only forms.

Expected findings are asserted line by line in `test_audit.py` (`test_au_n1_*`).
