---
name: sync-assets
description: Mirror src/ui-ux-pro-max/ into cli/assets/ and .claude/skills/ui-ux-pro-max/ and verify the mirrors match. Run after editing data/, scripts/ or templates/.
disable-model-invocation: true
---

Run from the `cli/` directory:

1. `npm run sync:assets` mirrors `src/ui-ux-pro-max/` into `cli/assets/` and `.claude/skills/ui-ux-pro-max/{data,scripts}`.
2. `npm run check:assets` must print "Assets are in sync." (this is what the "Check asset sync" CI job runs).
3. Run `git status --short`. The sync writes LF line endings, so on Windows with `core.autocrlf=true` unchanged mirrors can show as modified. `git add --renormalize .` clears that; only files with real content changes should remain.
4. Run the Python tests: `python -m unittest discover -s src/ui-ux-pro-max/scripts/tests -p "test_*.py"`.

Never edit the mirrored copies directly; a PreToolUse hook blocks it.
