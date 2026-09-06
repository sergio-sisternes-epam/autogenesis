from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ci_output import write_github_outputs
from command_runner import CommandError, run_command


class HelperTests(unittest.TestCase):
    def test_multiline_github_output_is_delimited(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "output"
            write_github_outputs(path, {"value": "one\ntwo"})
            content = path.read_text(encoding="utf-8")
        self.assertRegex(content, r"^value<<ghadelimiter_[0-9a-f]+\n")
        self.assertIn("\none\ntwo\n", content)

    def test_command_failure_has_bounded_diagnostic(self) -> None:
        with self.assertRaisesRegex(CommandError, "failed with exit code 7"):
            run_command(
                ["python3", "-c", "import sys; print('bad'); sys.exit(7)"],
                cwd=Path.cwd(),
                timeout=10,
                label="fixture",
            )


if __name__ == "__main__":
    unittest.main()
