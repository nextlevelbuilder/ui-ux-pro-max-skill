#!/usr/bin/env python3
"""The catalog snapshot must not depend on the checkout's line endings.

Regression test for bd19ab9 (#462), where catalog-summary.json was regenerated
on a CRLF checkout. Every recorded sha256 was the CRLF hash of the source file,
so `verify:data` failed on every LF platform, including CI.
"""

import hashlib
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

REPO = next(
    parent for parent in Path(__file__).resolve().parents
    if (parent / "scripts" / "generate-catalog-summary.py").is_file()
)
DATA = REPO / "src/ui-ux-pro-max/data"
SNAPSHOT_FILES = (
    "google-fonts.csv",
    "google-font-licenses.json",
    "icons.csv",
    "phosphor-icons-upstream.json",
)


def _load_generator():
    path = REPO / "scripts" / "generate-catalog-summary.py"
    spec = importlib.util.spec_from_file_location("generate_catalog_summary", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CatalogSummaryLineEndingsTest(unittest.TestCase):
    def test_digest_is_identical_for_lf_and_crlf(self):
        digest = _load_generator().digest
        with tempfile.TemporaryDirectory() as tmp:
            lf = Path(tmp) / "lf.csv"
            crlf = Path(tmp) / "crlf.csv"
            lf.write_bytes(b"id,name\n1,alpha\n2,beta\n")
            crlf.write_bytes(b"id,name\r\n1,alpha\r\n2,beta\r\n")
            self.assertEqual(
                digest(lf), digest(crlf),
                "snapshot hashes must not change with the checkout's line endings",
            )

    def test_committed_snapshot_matches_normalized_sources(self):
        summary = json.loads((DATA / "catalog-summary.json").read_text(encoding="utf-8"))
        for name in SNAPSHOT_FILES:
            expected = hashlib.sha256(
                (DATA / name).read_bytes().replace(b"\r\n", b"\n")
            ).hexdigest()
            self.assertEqual(
                summary["snapshots"][name]["sha256"], expected,
                f"{name}: committed snapshot hash does not match the LF-normalized source",
            )

    def test_crlf_checkout_produces_the_committed_hashes(self):
        """Simulate a Windows checkout: the recorded hashes must still validate."""
        digest = _load_generator().digest
        summary = json.loads((DATA / "catalog-summary.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            for name in SNAPSHOT_FILES:
                crlf_copy = Path(tmp) / name
                raw = (DATA / name).read_bytes().replace(b"\r\n", b"\n")
                crlf_copy.write_bytes(raw.replace(b"\n", b"\r\n"))
                self.assertEqual(
                    digest(crlf_copy), summary["snapshots"][name]["sha256"],
                    f"{name}: a CRLF checkout would record a different hash",
                )


if __name__ == "__main__":
    unittest.main()
