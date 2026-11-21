"""Retrieve the form error-handling guidelines and keep generic queries on generic rows."""

import csv
from pathlib import Path
import sys
import unittest

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
from core import search  # noqa: E402

DATA = SCRIPTS.parent / "data"

FORM_QUERIES = {
    "error message clears after correction": "Clear Errors After Correction",
    "premature validation": "Premature Validation",
    "form cleared after failed submit": "Preserve Input After Failed Submit",
    "disabled submit button until valid": "Submit Button Not Pre-Disabled",
    "unsaved changes warning": "Unsaved Changes Warning",
    "reject valid phone number with spaces": "Forgiving Input Formats",
    "block paste password": "Never Block Paste",
    "error toast disappears": "Persistent Error Messages",
    "invalid input error code": "Actionable Error Messages",
    "undo instead of confirmation": "Undo for Reversible Actions",
    "modal focus trap return focus": "Modal Dialog Focus",
}

# Generic questions must keep returning the general guideline first.
GENERIC_QUERIES = {
    "inline validation": "Inline Validation",
    "error placement": "Error Placement",
    "error messages": "Error Messages",
    "confirmation dialogs": "Confirmation Dialogs",
    "loading buttons": "Loading Buttons",
    "toast notifications": "Toast Notifications",
    "focus states": "Focus States",
    "disabled states": "Disabled States",
}


def ux_rows():
    with (DATA / "ux-guidelines.csv").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class TestFormErrorHandling(unittest.TestCase):
    def test_form_queries_retrieve_the_new_row_first(self):
        for query, issue in FORM_QUERIES.items():
            with self.subTest(query=query):
                result = search(query, domain="ux", max_results=3)
                self.assertEqual(issue, result["results"][0]["Issue"])

    def test_generic_queries_keep_the_generic_row_first(self):
        for query, issue in GENERIC_QUERIES.items():
            with self.subTest(query=query):
                result = search(query, domain="ux", max_results=3)
                self.assertEqual(issue, result["results"][0]["Issue"])

    def test_form_rows_are_complete(self):
        rows = {row["Issue"]: row for row in ux_rows()}
        for issue in FORM_QUERIES.values():
            with self.subTest(issue=issue):
                row = rows[issue]
                self.assertIn(row["Platform"], {"All", "Web"})
                self.assertIn(row["Severity"], {"Critical", "High", "Medium"})
                for field in ("Description", "Do", "Don't",
                              "Code Example Good", "Code Example Bad"):
                    self.assertTrue(row[field].strip(), field)

    def test_confirmation_example_names_the_outcome(self):
        row, = [row for row in ux_rows() if row["Issue"] == "Confirmation Dialogs"]
        self.assertNotIn("are you sure", row["Code Example Good"].casefold())

    def test_quick_references_include_the_form_rules(self):
        repo = next((parent for parent in SCRIPTS.parents
                     if (parent / "src/ui-ux-pro-max/templates/base").is_dir()), None)
        if not repo:
            self.skipTest("Repository quick references are not installed with scripts")
        for relative in (
            Path("src/ui-ux-pro-max/templates/base/quick-reference.md"),
            Path("cli/assets/templates/base/quick-reference.md"),
            Path(".claude", "skills", "ui-ux-pro-max", "references", "quick-reference.md"),
        ):
            with self.subTest(path=relative):
                text = (repo / relative).read_text(encoding="utf-8")
                for rule_id in ("`error-clears-on-fix`", "`keep-input-on-error`",
                                "`unsaved-changes-guard`", "`dialog-focus`"):
                    self.assertTrue(rule_id in text, f"{rule_id} missing from {relative}")


if __name__ == "__main__":
    unittest.main()
