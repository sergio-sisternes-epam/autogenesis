from __future__ import annotations

import unittest

import dependency_contract


class DependencyContractTests(unittest.TestCase):
    def test_repository_manifest_and_lock_are_exact(self) -> None:
        self.assertEqual(dependency_contract.validate_manifest(), [])
        self.assertEqual(dependency_contract.validate_lock(), [])
        self.assertEqual(dependency_contract.validate_direct_okf_usage(), [])

    def test_all_direct_refs_are_released_tags(self) -> None:
        for dependency in dependency_contract.EXPECTED_DEPENDENCIES:
            self.assertEqual(
                dependency.source,
                f"{dependency.name}@{dependency_contract.MARKETPLACE}",
            )
            self.assertRegex(dependency.version, r"^[0-9]+\.[0-9]+\.[0-9]+$")
            self.assertRegex(dependency.commit, r"^[0-9a-f]{40}$")
            self.assertEqual(dependency.ref, dependency.commit)

    def test_lock_commit_drift_is_rejected(self) -> None:
        content = (dependency_contract.ROOT / "apm.lock.yaml").read_text(
            encoding="utf-8"
        )
        content = content.replace(
            dependency_contract.EXPECTED_DEPENDENCIES[0].commit,
            "0" * 40,
            1,
        )
        errors = dependency_contract.validate_lock_text(content)
        self.assertTrue(any("atlas.resolved_commit" in error for error in errors))

    def test_known_anchor_warnings_are_exact_and_documented(self) -> None:
        self.assertEqual(
            {item[0] for item in dependency_contract.KNOWN_ANCHOR_DIVERGENCES},
            {"atlas-okf-anchor", "discuss-atlas-anchor"},
        )
        readme = (dependency_contract.ROOT / "README.md").read_text(encoding="utf-8")
        for anchor in (
            "9088a99a613d9ccc53ec2a15341714139291633f",
            "5246f7b193b58a32ac8a15fc76aedf37c42b042c",
            "v0.8.15",
            "v0.9.0",
        ):
            self.assertIn(anchor, readme)
        self.assertIn("expected and reviewed, not suppressed", readme)


if __name__ == "__main__":
    unittest.main()
