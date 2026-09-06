from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

import release_tag


class ReleaseTagTests(unittest.TestCase):
    def git(self, root: Path, *args: str) -> str:
        return subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        ).stdout.strip()

    def create_remote(self, root: Path) -> tuple[Path, Path, str]:
        remote = root / "remote.git"
        source = root / "source"
        self.git(root, "init", "--bare", str(remote))
        self.git(root, "init", "-b", "main", str(source))
        self.git(source, "config", "user.name", "Release Test")
        self.git(source, "config", "user.email", "release@example.com")
        (source / "package.txt").write_text("candidate\n", encoding="utf-8")
        self.git(source, "add", "package.txt")
        self.git(source, "commit", "-m", "Release candidate")
        commit = self.git(source, "rev-parse", "HEAD")
        self.git(source, "remote", "add", "origin", str(remote))
        self.git(source, "push", "origin", "main")
        return remote, source, commit

    def clone(self, root: Path, remote: Path, commit: str) -> Path:
        checkout = root / "checkout"
        self.git(root, "clone", "--no-tags", str(remote), str(checkout))
        self.git(checkout, "checkout", "--detach", commit)
        return checkout

    def test_remote_annotated_tag_uses_isolated_namespace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            remote, source, commit = self.create_remote(root)
            self.git(source, "tag", "-a", "v0.4.1", "-m", "Autogenesis v0.4.1")
            self.git(source, "push", "origin", "refs/tags/v0.4.1")
            checkout = self.clone(root, remote, commit)
            self.git(
                checkout,
                "fetch",
                "--no-tags",
                "origin",
                f"{commit}:refs/tags/v0.4.1",
            )
            verified = release_tag.verify_remote_tag("v0.4.1", checkout)
            self.assertEqual(verified.tag_ref, "refs/release-tags/v0.4.1")
            self.assertEqual(verified.candidate_revision, commit)
            self.assertEqual(
                self.git(checkout, "cat-file", "-t", verified.tag_ref),
                "tag",
            )
            self.assertEqual(
                self.git(checkout, "cat-file", "-t", "refs/tags/v0.4.1"),
                "commit",
            )

    def test_lightweight_tag_and_non_main_tag_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            remote, source, commit = self.create_remote(root)
            self.git(source, "tag", "v0.4.1")
            self.git(source, "push", "origin", "refs/tags/v0.4.1")
            checkout = self.clone(root, remote, commit)
            with self.assertRaisesRegex(release_tag.ReleaseTagError, "not an annotated"):
                release_tag.verify_remote_tag("v0.4.1", checkout)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            remote, source, commit = self.create_remote(root)
            self.git(source, "tag", "-a", "v0.4.1", "-m", "Autogenesis v0.4.1")
            (source / "package.txt").write_text("advanced\n", encoding="utf-8")
            self.git(source, "commit", "-am", "Advance main")
            self.git(source, "push", "origin", "main", "refs/tags/v0.4.1")
            checkout = self.clone(root, remote, commit)
            with self.assertRaisesRegex(release_tag.ReleaseTagError, "not exact current main"):
                release_tag.verify_remote_tag("v0.4.1", checkout)


if __name__ == "__main__":
    unittest.main()
