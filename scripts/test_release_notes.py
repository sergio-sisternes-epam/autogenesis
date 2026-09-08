from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import release_notes


class ReleaseNotesTests(unittest.TestCase):
    def test_current_release_has_curated_notes(self) -> None:
        notes = release_notes.release_notes("0.4.2")
        self.assertTrue(notes.startswith("### Changed"))
        self.assertIn("marketplace objects", notes)
        self.assertNotIn("## [0.4.1]", notes)

    def test_missing_release_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "release notes not found"):
            release_notes.release_notes("9.9.9")

    def test_empty_release_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "CHANGELOG.md").write_text(
                "# Changelog\n\n## [1.0.0]\n\n[1.0.0]: https://example.test\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "release notes are empty"):
                release_notes.release_notes("1.0.0", root)


if __name__ == "__main__":
    unittest.main()
