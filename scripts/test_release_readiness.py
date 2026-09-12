from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

import release_readiness


ROOT = Path(__file__).resolve().parents[1]


class ReleaseReadinessTests(unittest.TestCase):
    def copy_surfaces(self, destination: Path) -> None:
        for surface in release_readiness.SURFACES:
            target = destination / surface.path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / surface.path, target)
        shutil.copy2(ROOT / "CHANGELOG.md", destination / "CHANGELOG.md")

    def test_repository_version_surfaces_match(self) -> None:
        version, errors = release_readiness.validate_versions()
        self.assertEqual(version, "0.5.0")
        self.assertEqual(errors, [])
        self.assertFalse(release_readiness.is_prerelease(version))

    def test_mismatched_skill_version_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_surfaces(root)
            skill = root / "SKILL.md"
            skill.write_text(
                skill.read_text(encoding="utf-8").replace(
                    "version: 0.5.0", "version: 0.5.1", 1
                ),
                encoding="utf-8",
            )
            version, errors = release_readiness.validate_versions(root)
        self.assertEqual(version, "0.5.0")
        self.assertTrue(any("skill frontmatter version 0.5.1" in item for item in errors))

    def test_changelog_links_are_required(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.copy_surfaces(root)
            changelog = root / "CHANGELOG.md"
            changelog.write_text(
                changelog.read_text(encoding="utf-8").replace(
                    "[0.5.0]: https://github.com/sergio-sisternes-epam/"
                    "autogenesis/releases/tag/v0.5.0\n",
                    "",
                ),
                encoding="utf-8",
            )
            _, errors = release_readiness.validate_versions(root)
        self.assertTrue(any("changelog release link" in item for item in errors))

    def test_invalid_semver_and_tag_are_rejected(self) -> None:
        self.assertTrue(release_readiness.validate_tag("v0.4.0", "0.4.1"))
        self.assertTrue(release_readiness.is_prerelease("0.4.2-rc.1"))
        self.assertTrue(release_readiness.validate_commit("main"))


if __name__ == "__main__":
    unittest.main()
