"""Retrieve IME guidance and exercise the actual CSV JavaScript example."""

import csv
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
from core import search  # noqa: E402


class TestImeGuidance(unittest.TestCase):
    def test_quick_references_include_the_rule(self):
        repo = next((parent for parent in SCRIPTS.parents
                     if (parent / "docs/ime-composition.md").is_file()), None)
        if not repo:
            self.skipTest("Repository quick references are not installed with scripts")
        for relative in ("src/ui-ux-pro-max/templates/base/quick-reference.md",
                         "cli/assets/templates/base/quick-reference.md",
                         ".claude/skills/ui-ux-pro-max/references/quick-reference.md"):
            with self.subTest(path=relative):
                text = (repo / relative).read_text(encoding="utf-8")
                self.assertIn("`ime-composition-enter`", text)

    def test_composition_queries_retrieve_the_rule_first(self):
        for query in ("IME composition Enter", "Korean input Enter submit",
                      "Japanese Chinese composition", "한글 IME Enter"):
            with self.subTest(query=query):
                result = search(query, domain="ux", max_results=3)
                self.assertEqual("IME Composition Enter", result["results"][0]["Issue"])

    def test_csv_example_preserves_ime_and_submission_paths(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is required to execute the JavaScript example")
        with (SCRIPTS.parent / "data/ux-guidelines.csv").open(
                encoding="utf-8", newline="") as handle:
            row, = [row for row in csv.DictReader(handle)
                    if row["Issue"] == "IME Composition Enter"]
        # Evaluate the published snippet rather than a copied implementation.
        repo = next((parent for parent in SCRIPTS.parents
                     if (parent / "docs/ime-composition.md").is_file()), None)
        examples = {"csv": row["Code Example Good"]}
        if repo:
            guide = (repo / "docs/ime-composition.md").read_text(encoding="utf-8")
            block, = re.findall(r"```js\n(.*?)```", guide, re.S)
            examples["docs"] = block
        # Installed CLI/plugin copies do not ship repository-level docs.
        runner = r"""
const vm = require('node:vm');
const assert = require('node:assert/strict');
const examples = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
for (const [name, example] of Object.entries(examples)) {
let handler, sent = 0;
const textarea = { addEventListener(type, fn) {
  assert.equal(type, 'keydown'); handler = fn;
} };
const form = { requestSubmit() { sent++; } };
vm.runInNewContext(example, {
  textarea, form,
  document: { querySelector(selector) {
    if (selector === '#message') return textarea;
    assert.equal(selector, '#message-form'); return form;
  } }
});
function key(overrides, expectedSent, expectedPrevented) {
  let prevented = false;
  const event = { key: 'Enter', shiftKey: false, ctrlKey: false, metaKey: false,
    altKey: false, repeat: false, isComposing: false, keyCode: 13,
    preventDefault() { prevented = true; }, ...overrides };
  const composing = event.isComposing, code = event.keyCode;
  Object.defineProperty(event, 'isComposing', { get() {
    assert.equal(prevented, true, 'Cancel handled Enter before the IME guard');
    return composing;
  } });
  Object.defineProperty(event, 'keyCode', { get() {
    assert.equal(prevented, true, 'Cancel handled Enter before the 229 guard');
    return code;
  } });
  handler(event);
  assert.equal(sent, expectedSent);
  assert.equal(prevented, expectedPrevented);
}
key({isComposing: true}, 0, true);
key({isComposing: false, keyCode: 229}, 0, true);
key({key: 'Process', keyCode: 229}, 0, false);
key({key: 'a', keyCode: 65}, 0, false);
key({shiftKey: true}, 0, false);
key({ctrlKey: true}, 0, false);
key({metaKey: true}, 0, false);
key({altKey: true}, 0, false);
key({}, 1, true); // A separate Enter after confirmation submits once.
key({repeat: true}, 1, true);
console.log(`${name}: 10 IME/keyboard handler cases passed`);
}
"""
        completed = subprocess.run(
            [node, "-e", runner], input=json.dumps(examples),
            text=True, capture_output=True, check=True,
        )
        for name in examples:
            self.assertIn(f"{name}: 10 IME/keyboard handler cases passed", completed.stdout)


if __name__ == "__main__":
    unittest.main()
