from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import dependency_contract


class DependencyContractTests(unittest.TestCase):
    def test_repository_manifest_and_lock_are_exact(self) -> None:
        self.assertEqual(dependency_contract.validate_manifest(), [])
        self.assertEqual(dependency_contract.validate_lock(), [])

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
        self.assertEqual(dependency_contract.KNOWN_ANCHOR_DIVERGENCES, ())
        contributing = (dependency_contract.ROOT / "CONTRIBUTING.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("579e8090273ce991ea0717abed0775dc03f28de2", contributing)
        self.assertIn("c1c0936d9a0346dce7d877646046c918de335d69", contributing)
        self.assertNotIn("9088a99a613d9ccc53ec2a15341714139291633f", contributing)
        self.assertNotIn("expected and reviewed, not suppressed", contributing)

    def test_direct_okf_usage_requires_new_module_skill_paths(self) -> None:
        self.assertEqual(
            dependency_contract.validate_direct_okf_usage(
                dependency_contract.ROOT
            ),
            [],
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative_path in dependency_contract.DIRECT_OKF_CALLERS:
                path = root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    "Load skill named `okf` before continuing.\n",
                    encoding="utf-8",
                )
            self.assertEqual(dependency_contract.validate_direct_okf_usage(root), [])

    def test_old_direct_okf_paths_no_longer_satisfy_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            legacy = root / "references/modules/workflow-discipline.md"
            legacy.parent.mkdir(parents=True, exist_ok=True)
            legacy.write_text("skill named `okf`\n", encoding="utf-8")

            errors = dependency_contract.validate_direct_okf_usage(root)

            self.assertTrue(
                any("references/modules/workflow-discipline/SKILL.md" in error for error in errors)
            )
            self.assertTrue(
                any(
                    "references/modules/validate-okf-conformance/SKILL.md" in error
                    for error in errors
                )
            )


if __name__ == "__main__":
    unittest.main()
