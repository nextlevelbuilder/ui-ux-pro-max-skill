# drift-project — STATIC AUDIT FIXTURE (not a runnable app)

This folder is a synthetic test fixture for `audit.py scan`. It is NOT a real
Flutter, Unity or web project: nothing here compiles or runs. Every file is
hand-written to contain a known set of intentional design-drift defects that
the scanner must detect when audited against `tokens.json` in this folder.

Layout
- `pubspec.yaml` + `lib/`            Flutter-style sources (detected: flutter)
- `web/package.json` + `web/`        React/Tailwind + CSS sources (detected: web)
- `unity/Assets/`, `unity/ProjectSettings/`  Unity UI Toolkit USS + C# (detected: unity)
- `build/`, `web/node_modules/`      decoys: MUST be skipped by the scanner
- `tokens.json`                      the design contract the fixture is audited against
- `../expected-findings.md`          the oracle: every intentional defect, rule id, severity

Root contains markers for three platforms, so platform = `mixed`.
Clean files (`lib/theme/app_theme.dart`, `lib/screens/home.dart`, `web/styles.css`,
`unity/Assets/UI/Theme.uss`) must produce zero findings.
