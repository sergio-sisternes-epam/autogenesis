from __future__ import annotations

import re
import unittest
from pathlib import Path

import module_contract
import store_contract


ROOT = Path(__file__).resolve().parents[1]


class SourceContractTests(unittest.TestCase):
    def test_root_skill_package_and_generated_state_contract(self) -> None:
        manifest = (ROOT / "apm.yml").read_text(encoding="utf-8")
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("name: autogenesis\n", manifest)
        self.assertIn("version: 0.5.0\n", manifest)
        self.assertIn("license: Apache-2.0\n", manifest)
        self.assertIn(
            "repository: https://github.com/sergio-sisternes-epam/autogenesis\n",
            manifest,
        )
        self.assertIn("name: autogenesis\n", skill)
        self.assertIn("version: 0.5.0\n", skill)
        self.assertTrue((ROOT / "apm.lock.yaml").is_file())
        self.assertIn("apm_modules/", ignore)
        self.assertIn("Commit `apm.lock.yaml`", agents)
        self.assertIn("Never commit `apm_modules/`", agents)

    def test_store_constants_are_exact(self) -> None:
        self.assertEqual(
            store_contract.STORE_COMMIT,
            "1ba15358a3157e3c946436ee60e73b87f3c77a0f",
        )
        self.assertEqual(store_contract.STORE_REF, "main")
        self.assertEqual(store_contract.ATLAS_VERSION, "0.9.0")
        self.assertEqual(
            store_contract.ATLAS_COMMIT,
            "2b6659e5440886c7abbd9ad10686fa3a0100813b",
        )

    def test_external_actions_are_commit_pinned(self) -> None:
        for relative in (".github/workflows/ci.yml", ".github/workflows/release.yml"):
            content = (ROOT / relative).read_text(encoding="utf-8")
            external_uses = re.findall(
                r"(?m)^\s*-\s+uses:\s+([^./][^@\s]*)@(\S+)",
                content,
            )
            self.assertTrue(external_uses, relative)
            for action, revision in external_uses:
                self.assertRegex(revision, r"^[0-9a-f]{40}$", action)

    def test_workflows_never_use_pull_request_target(self) -> None:
        workflows = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (ROOT / ".github/workflows").glob("*.yml")
        )
        self.assertNotIn("pull_request_target", workflows)
        self.assertIn("pull_request:", workflows)
        self.assertIn("persist-credentials: false", workflows)

    def test_setup_action_verifies_checksum_before_execution(self) -> None:
        action = (ROOT / ".github/actions/setup-apm/action.yml").read_text(
            encoding="utf-8"
        )
        ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("0.30.0", action)
        self.assertIn("8c2e0d9", action)
        self.assertIn(
            "8b84bebf19c350faf36d21aebb350dc656d04c0b7a1c2bf8ea35c0caa0e44bb9",
            ci,
        )
        self.assertLess(action.index("sha256sum"), action.index("tar -xzf"))
        self.assertLess(action.index("tar -xzf"), action.index('"$binary_dir/apm" --version'))
        self.assertIn('expected_identity="version $APM_VERSION"', action)

    def test_release_uses_isolated_authoritative_tag_and_inherited_secret(self) -> None:
        release = (ROOT / ".github/workflows/release.yml").read_text(
            encoding="utf-8"
        )
        helper = (ROOT / "scripts/release_tag.py").read_text(encoding="utf-8")
        self.assertIn("refs/release-tags/", helper)
        self.assertIn("secrets: inherit", release)
        self.assertIn(
            "package_source: sergio-sisternes-epam/autogenesis#"
            "${{ github.ref_name }}",
            release,
        )
        self.assertIn("EXPECTED_TAG_OBJECT", release)
        self.assertIn("REVERIFIED_TAG_OBJECT", release)
        self.assertIn("--generate-notes", release)
        self.assertIn('--notes-file "$notes_file"', release)
        self.assertNotIn('release_notes="$(<"$notes_file")"', release)

    def test_private_reads_are_explicitly_credentialed(self) -> None:
        ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("APM_READ_TOKEN", ci)
        self.assertGreaterEqual(ci.count("Missing private read token"), 3)
        self.assertIn("GITHUB_APM_PAT_SERGIO_SISTERNES_EPAM", ci)
        self.assertGreaterEqual(
            ci.count('Authorization: Bearer $APM_READ_TOKEN'),
            3,
        )
        self.assertNotIn("Authorization: " + "*" * 6, ci)
        self.assertIn("Mutable package source", ci)

    def test_pull_request_jobs_validate_exact_head(self) -> None:
        ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")

        candidate = (
            "${{ inputs.candidate_revision || "
            "github.event.pull_request.head.sha || github.sha }}"
        )
        self.assertEqual(ci.count(candidate), 9)
        self.assertNotIn(
            "${{ inputs.candidate_revision || github.sha }}",
            ci,
        )

    def test_actual_source_validator_passes_complete_current_source(self) -> None:
        report = module_contract.validate_source_tree(ROOT)

        self.assertEqual(report.command, "source")
        self.assertEqual(report.details.get("module_count"), 21)
        self.assertEqual(report.details.get("registry_rows"), 21)
        self.assertEqual(report.details.get("module_entrypoints"), 21)
        self.assertEqual(report.details.get("scenario_files"), 27)
        self.assertTrue(report.ok, report.as_dict())
        self.assertEqual(report.errors, [])

    def test_actual_root_version_surface_is_v0_5_0(self) -> None:
        root_frontmatter = module_contract.parse_frontmatter(
            (ROOT / "SKILL.md").read_text(encoding="utf-8"),
            "SKILL.md",
        )
        manifest = (ROOT / "apm.yml").read_text(encoding="utf-8")

        self.assertEqual(root_frontmatter.fields["name"], "autogenesis")
        self.assertEqual(root_frontmatter.fields["version"], "0.5.0")
        self.assertEqual(root_frontmatter.fields["activation_card"], "on")
        self.assertIn("name: autogenesis\n", manifest)
        self.assertIn("version: 0.5.0\n", manifest)

    def test_optional_module_template_is_instruction_only(self) -> None:
        template = (
            ROOT / "references/modules/patterns/references/skill-module-template.md"
        ).read_text(encoding="utf-8")
        example = template.split("```markdown\n", 1)[1].split("```", 1)[0]
        module = module_contract.parse_frontmatter(example, "template example")

        self.assertEqual(set(module.fields), {"name", "description"})
        self.assertNotIn("autogenesis.invocation-", example)
        self.assertNotIn("workflow-discipline", example)
        self.assertNotIn(".py", example)
        self.assertIn("## Inputs and boundaries", module.body)
        self.assertIn("## Procedure", module.body)
        self.assertIn("## Outcome", module.body)

    def test_live_workflow_has_no_construct_binding(self) -> None:
        live_paths = [
            ROOT / "SKILL.md",
            *sorted((ROOT / "references/modules").glob("*/SKILL.md")),
            *sorted((ROOT / "references/templates").glob("*.md")),
        ]
        binding = re.compile(
            r"(?i)\bconstruct\b|construct_(?:eval|report|scenario)"
        )
        for path in live_paths:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertIsNone(binding.search(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
