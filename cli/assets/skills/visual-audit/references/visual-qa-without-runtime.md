# Visual QA Without a Runtime

When the target application cannot be run (no Flutter toolchain on the QA machine, Unity project without the editor, a web app whose dev server needs secrets, or simply a CI container), visual contract compliance can still be verified **statically**: the generated or hand-written UI code is compared against the design contract (`design-system/<slug>/tokens.json`, `style-profile.json`, `pages/*.md`). What static review proves, what it cannot prove, and how to label it is fixed here so no report claims more than it saw.

## 1. Verification levels and labels

Every visual-QA row in a report carries exactly one of these labels in its Evidence column, before the evidence itself:

| Label | Meaning | What it can establish | What it cannot |
|---|---|---|---|
| `RUNTIME-VERIFIED` | the app was built and run; screenshots exist; `visual_qa.py diff` or a human looked at the screen | actual rendering, layout at a given viewport, motion, state styles | — |
| `STATIC-VERIFIED` | source code was read/scanned against the contract; nothing was rendered | which literals, tokens, classes, theme entries the code uses; drift from the token set; obvious structural rule breaks | how it looks, overlapping/overflow, real contrast after anti-aliasing, font fallback, runtime theme overrides, platform scaling |
| `TOOL-ANALYZED` | a platform analyzer ran without executing the app (`flutter analyze`, `dart format --set-exit-if-changed`, `tsc --noEmit`, USS parse) | the code compiles/parses and the theme wiring type-checks | anything visual |
| `NOT RUN` | none of the above | nothing | — |

A row that is `STATIC-VERIFIED` may be `PASS`, but its Observed column must say what was checked ("0 off-palette literals in 14 files"), never "looks correct". Reports summarise with two counts: `visual rows RUNTIME-VERIFIED: n/m`, `STATIC-VERIFIED: k/m`. The report's known-limitation row ("real Flutter/Unity app screenshot QA = NOT RUN unless executed") stays `NOT RUN` even when every static row passes.

## 2. Procedure A — generated code vs tokens (all stacks)

Inputs: `design-system/<slug>/tokens.json`, `style-profile.json`, the code tree.

1. **Machine pass first.** `python3 scripts/audit.py scan <code-root> --contract design-system/<slug>/tokens.json --profile design-system/<slug>/style-profile.json --out qa-logs/static-audit.json --md qa-logs/static-audit.md`. The findings file *is* the evidence for colour/radius/font-size/spacing/duration/family/icon/shadow/touch-target/contrast drift. Label: `STATIC-VERIFIED (audit.py scan, N findings)`. For web projects `node ../design-system/scripts/validate-tokens.cjs --dir src/` (the `design-system` skill) can add a second, coarser `STATIC-VERIFIED` row. It is a web-only complement, not a replacement: it scans `.css .scss .ts .tsx .js .jsx .vue .svelte` only — **not `.html`** (inline `<style>` blocks and markup colours go unseen; it reports "no violations" on an HTML-only app) — skips `globals.css`, and flags every hex/px literal rather than only off-contract ones. Label its row with the extensions it covered.
2. **Resolution table.** Build the "allowed literal" table once from `tokens.json` (resolve `{primitive…}` refs): colours (hex upper-case), radii, font sizes, spacing steps, durations, families, icon sizes, min touch target, z-index, opacity. Keep it in `qa-logs/allowed-literals.md`; every later grep cites it.
3. **Manual pass for what the scanner cannot see** (one row each, `STATIC-VERIFIED (manual read)`):
   - component rules in `profile.components` (e.g. `button.primary: pill, 3px outline, double shadow`): open the primary button implementation, quote the lines that set radius/outline/shadow, compare to the rule; cite `file:line`;
   - `anti_patterns`: grep for each named pattern (e.g. "drop shadow on text", "gradient on flat style") using a pattern you write down in the row;
   - `intentional_exceptions`: each must have a matching override in `pages/<scope>.md`; an exception with no page override is a FAIL;
   - hierarchy/layout rules from `component-catalog.md` (HUD position, safe-area padding): cite the layout widget/stylesheet lines.
4. **Page overrides.** For each `pages/<page>.md`, confirm the screen's code uses the override values and not the master values (grep both; cite).

## 3. Procedure B — Tailwind class audit (web)

Goal: every utility that sets colour, radius, shadow, font size, spacing or duration is either a **configured** token class or an explicit, documented exception. Arbitrary values and default-palette classes are drift.

```bash
# 1. the configured token names (from the generated config)
node ../design-system/scripts/generate-tokens.cjs --config design-system/<slug>/tokens.json -o qa-logs/tokens.css   # token names the classes must map to
# or read the project's tailwind.config.{js,ts} theme.extend keys
# 2. every class attribute in the code (JSX/TSX/HTML/Vue/Svelte)
grep -rhoE '(class|className)=["'"'"'][^"'"'"']*' src | tr ' ' '\n' | sed -E 's/^(class|className)=["'"'"']//' | sort | uniq -c | sort -rn > qa-logs/classes.txt
# 3. arbitrary values (always drift unless listed as exception)
grep -E '\[(#|[0-9.]+(px|rem|ms))' qa-logs/classes.txt
# 4. default-palette colours not in the config (bg-blue-500, text-gray-700, border-red-300, ring-*, from-*/to-*)
grep -E '^(bg|text|border|ring|from|to|via|fill|stroke|shadow)-(slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-[0-9]{2,3}' qa-logs/classes.txt
# 5. radius / shadow / duration scale usage
grep -E '^(rounded|shadow|duration|ease|text|p|m|gap|space)-' qa-logs/classes.txt
```

Report rows: `TW-01 arbitrary values: n occurrences in k files` (list top 10 with `file:line` via `grep -rn`), `TW-02 default-palette colours: n`, `TW-03 radius classes used ⊆ configured scale: yes/no (set difference)`, `TW-04 shadow variants: n distinct (threshold from profile)`, `TW-05 duration classes ⊆ {fast,base,slow} tokens`. Also check `tailwind.config` `theme` (not `theme.extend`) does not **replace** the default scale in a way that silently maps `rounded-lg` to a non-token value — quote the config lines. Label all rows `STATIC-VERIFIED (class audit)`. A `tsc --noEmit` / `npm run build` success is an additional `TOOL-ANALYZED` row, not a visual one.

## 4. Procedure C — Flutter theme audit

Precondition check: `flutter --version` (record). If absent → the analyzer rows are `BLOCKED (flutter not installed)`; the grep rows below still run.

1. `TOOL-ANALYZED` rows (only if Flutter is present; never run the app):
   - `flutter pub get` (may need network → BLOCKED if offline, say so);
   - `flutter analyze --no-pub` → rc 0 means the theme wiring compiles; paste the summary line;
   - `dart format --output=none --set-exit-if-changed lib` optional, cosmetic;
   - `flutter test` **only** for existing widget tests that assert theme values (`expect(theme.colorScheme.primary, Color(0xFF…))`); a golden test that renders is still `TOOL-ANALYZED` because the QA agent does not view the output unless it opens the PNGs (then it becomes `RUNTIME-VERIFIED (golden)`).
2. `STATIC-VERIFIED` rows:
   - the `ThemeData` / `ColorScheme` / `TextTheme` definition file: every colour, radius, text style maps to a token (table token → Dart constant → `file:line`);
   - `Theme.of(context)` / `context.theme` usage vs hard-coded `Color(0x…)`, `TextStyle(fontSize:)`, `BorderRadius.circular(n)` outside the theme file (`scripts/audit.py scan` output + `grep -rn 'Color(0x' lib | grep -v theme`);
   - Flame/HUD components (`PositionComponent`, `TextPaint`, `Paint()..color`) — the scanner's Dart patterns cover `Paint..color = Color(0x…)`; quote the lines for the HUD rule rows;
   - `MediaQuery.textScaler`/`textScaleFactor` handling, safe-area padding (`SafeArea`, `MediaQuery.padding`) for the layout rules;
   - min touch target: `GestureDetector`/`InkWell` children smaller than `$extensions.vdp.minTouchTarget` (scanner rule `touch.target-too-small`, see `references/drift-rules.md`), cite.
3. Simulator/device screenshots are **not** part of this procedure; if someone later runs the app, rows are re-labelled `RUNTIME-VERIFIED` with the capture command.

## 5. Procedure D — Unity (uGUI / UI Toolkit) audit

No Unity editor is launched. (`Unity -batchmode -quit -executeMethod …` is possible when the editor exists, but it is `TOOL-ANALYZED` at best and is out of the default scope: default row `NOT RUN (Unity editor not launched)`.)

1. **USS parse** (UI Toolkit). USS is a CSS subset; a stdlib parse is enough:
   ```bash
   python3 - <<'EOF'
   import re, sys, pathlib
   bad = 0
   for p in pathlib.Path("Assets").rglob("*.uss"):
       s = p.read_text(encoding="utf-8", errors="replace")
       s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
       if s.count("{") != s.count("}"): print(f"{p}: unbalanced braces"); bad = 1
       for m in re.finditer(r"\{([^}]*)\}", s):
           for decl in filter(None, (d.strip() for d in m.group(1).split(";"))):
               if ":" not in decl: print(f"{p}: bad declaration '{decl}'"); bad = 1
       for v in re.findall(r"var\((--[a-zA-Z0-9-]+)\)", s):
           print(f"{p}: uses {v}")
   sys.exit(bad)
   EOF
   ```
   Rows: `USS-01 all .uss parse (n files)`, `USS-02 every var(--x) is defined in a theme .tss/.uss` (grep `--x:` across `Assets/**/*.{uss,tss}`), `USS-03 literals vs tokens` (from `python3 scripts/audit.py scan Assets --platform unity --contract …`, which reads `#hex`, `px`, `ms` in USS and `Color32(...)`/`Color(...)` in C#).
2. **C# / uGUI**: `grep -rn "new Color(" Assets --include='*.cs'`, `Color32(`, `.fontSize =`, `cornerRadius`, DOTween/`LeanTween` durations → compare with the allowed-literal table; ScriptableObject theme assets (`.asset` YAML): grep `m_Color`/`r: g: b:` floats and convert (×255, round) to hex for the comparison, cite the asset path and the line.
3. **Prefabs/UXML**: `grep -rn 'style="' Assets --include='*.uxml'` inline styles are drift unless whitelisted; prefab `.prefab` YAML `m_Color:` blocks likewise.
4. Label: `STATIC-VERIFIED (USS parse + grep)`; the limitation "Unity scanner = fixture-tested only" is quoted in the report unless a real project was scanned.

## 6. Procedure E — checklist walk (`visual_qa.py checklist`)

`python3 scripts/visual_qa.py checklist --profile design-system/<slug>/style-profile.json --screen <screen> --format md` produces one item per `qa_criteria` plus generic items (`<screen>` is one of `home gameplay level-select pause win lose settings shop rewards profile tutorial` or a `pages/<name>.md` in the same contract folder). For each item decide and record which label it can reach without a runtime:

| Item kind | Reachable label | Evidence |
|---|---|---|
| "all CTAs use the primary token", "radius class xl on cards" | STATIC-VERIFIED | grep/scan result, `file:line` |
| "text contrast ≥ 4.5:1 on surface" | STATIC-VERIFIED (computed from token pairs) with the caveat "outline/anti-aliasing not included" | ratio from `scripts/audit.py` `text.contrast-risk` or a one-line WCAG computation |
| "HUD readable over gameplay", "reward animation feels bouncy", "no overlap at 320 pt width" | RUNTIME only → `NOT RUN` | reason: needs rendering |
| "reduced-motion respected" | STATIC-VERIFIED partially: code reads the OS setting (`MediaQuery.disableAnimations`, `prefers-reduced-motion`) — cite; behaviour unverified | |

The checklist file with the filled status column is attached as `qa-logs/checklist-<screen>.md`; the manifest output (`python3 scripts/visual_qa.py manifest --stack <stack> --screens …`) is attached unchanged to show what *would* be captured, with every entry still `NOT RUN`.

## 7. Evidence format for static rows

```
| VQ-S-07 | button.primary rule: pill, 3px outline | STATIC-VERIFIED (manual read) | lib/widgets/primary_button.dart:31 BorderRadius.circular(999); :34 Border.all(width: 3, color: tokens.outline) | PASS |
| VQ-S-12 | contrast text/surface ≥ 4.5 | STATIC-VERIFIED (computed) | #3B2A1E on #FFF6E9 = 11.9:1 (tokens.semantic.color.text / surface); AA ok; anti-aliasing not modelled | PASS |
| VQ-R-01 | home screen matches reference look | NOT RUN | needs a build; manifest entry screens.json#home | NOT RUN |
```

## 8. Limits to state verbatim in every report that uses this procedure

- Static review cannot see layout overflow, clipping, z-order, font fallback, DPI scaling, animation timing, or platform theme overrides (dark mode, dynamic type, Android system fonts).
- Computed contrast uses token colours only; real contrast differs with outlines, gradients, images, and anti-aliasing.
- A passing `flutter analyze` / `tsc` / USS parse proves the code is well-formed, not that it looks right.
- Unity findings come from text patterns over USS/C#/YAML; serialized prefabs and material colours are only partially covered.
- The scanner's rule set is the one in `references/drift-rules.md`; anything outside it was checked by hand only where a row says `manual read`.
