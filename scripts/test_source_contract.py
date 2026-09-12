from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path

import store_contract


ROOT = Path(__file__).resolve().parents[1]
MODULE_RESOURCE_REFERENCE = re.compile(
    r"(?<![/\w])(?P<skill_root><skill_root>/)?"
    r"(?P<prefix>(?:\./|\.\./)*)"
    r"(?P<path>references/[A-Za-z0-9_./-]*"
    r"\.[A-Za-z0-9_.-]+)"
    r"(?:#[A-Za-z0-9_.-]+)?"
    r"(?![A-Za-z0-9_./-])"
)
PARENT_RELATIVE_RESOURCE_REFERENCE = re.compile(
    r"(?<![/\w])(?P<prefix>(?:\./)*)"
    r"(?P<path>(?:\.\./)+[A-Za-z0-9_./-]*"
    r"\.[A-Za-z0-9_.-]+)"
    r"(?:#[A-Za-z0-9_.-]+)?"
    r"(?![A-Za-z0-9_./-])"
)
SKILL_ROOT_TRAVERSAL_REFERENCE = re.compile(
    r"<skill_root>/(?P<path>(?:\./)*(?:\.\./)+"
    r"[A-Za-z0-9_./-]*\.[A-Za-z0-9_.-]+)"
    r"(?:#[A-Za-z0-9_.-]+)?"
    r"(?![A-Za-z0-9_./-])"
)
WORKFLOW_ENTRYPOINT = Path(
    "references/modules/workflow-discipline/SKILL.md"
)


def module_resource_reference_errors(
    entrypoint: Path,
    content: str,
) -> list[str]:
    errors: list[str] = []
    module_root = entrypoint.parent

    for match in SKILL_ROOT_TRAVERSAL_REFERENCE.finditer(content):
        errors.append(
            f"{entrypoint.relative_to(ROOT)}: package-shared resource "
            f"<skill_root>/{match.group('path')} escapes the skill root"
        )

    for match in PARENT_RELATIVE_RESOURCE_REFERENCE.finditer(content):
        errors.append(
            f"{entrypoint.relative_to(ROOT)}: parent-relative resource "
            f"{match.group('prefix')}{match.group('path')} escapes the "
            "module root"
        )

    for match in MODULE_RESOURCE_REFERENCE.finditer(content):
        raw_path = match.group("path")
        relative = Path(raw_path)
        if match.group("prefix"):
            errors.append(
                f"{entrypoint.relative_to(ROOT)}: non-canonical resource "
                f"path {match.group('prefix')}{relative} uses a relative "
                "prefix"
            )
            continue
        if "//" in raw_path:
            errors.append(
                f"{entrypoint.relative_to(ROOT)}: non-canonical resource "
                f"path {raw_path} contains a repeated separator"
            )
            continue
        if any(part in {".", ".."} for part in relative.parts):
            errors.append(
                f"{entrypoint.relative_to(ROOT)}: non-canonical resource "
                f"path {relative} contains a traversal segment"
            )
            continue

        if match.group("skill_root"):
            resource = (ROOT / relative).resolve()
            try:
                resource.relative_to(ROOT.resolve())
            except ValueError:
                errors.append(
                    f"{entrypoint.relative_to(ROOT)}: package-shared resource "
                    f"<skill_root>/{relative} escapes the skill root"
                )
                continue
            if not resource.is_file():
                errors.append(
                    f"{entrypoint.relative_to(ROOT)}: missing package-shared "
                    f"resource <skill_root>/{relative}"
                )
            module_entrypoints = (ROOT / "references/modules").resolve()
            workflow_entrypoint = (ROOT / WORKFLOW_ENTRYPOINT).resolve()
            if (
                resource.is_relative_to(module_entrypoints)
                and resource != workflow_entrypoint
            ):
                errors.append(
                    f"{entrypoint.relative_to(ROOT)}: sibling module "
                    f"{relative} must resolve through the parent registry"
                )
            continue

        module_resource = (module_root / relative).resolve()
        try:
            module_resource.relative_to(module_root.resolve())
        except ValueError:
            errors.append(
                f"{entrypoint.relative_to(ROOT)}: module-local resource "
                f"{relative} escapes the module root"
            )
            continue
        if module_resource.is_file():
            continue
        shared_resource = (ROOT / relative).resolve()
        if shared_resource.is_file():
            errors.append(
                f"{entrypoint.relative_to(ROOT)}: package-shared resource "
                f"{relative} must use <skill_root>/{relative}"
            )
        else:
            errors.append(
                f"{entrypoint.relative_to(ROOT)}: unresolved bare resource "
                f"{relative}; module-local paths resolve from {module_root}"
            )

    return errors


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

    def test_license_and_notice_contract(self) -> None:
        license_bytes = (ROOT / "LICENSE").read_bytes()
        notice = (ROOT / "NOTICE").read_text(encoding="utf-8")
        self.assertEqual(
            hashlib.sha256(license_bytes).hexdigest(),
            "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
        )
        self.assertIn("Copyright 2026 Sergio Sisternes", notice)
        self.assertIn("Copyright 2025 Daniel Meppiel", notice)
        self.assertIn("https://github.com/danielmeppiel/genesis", notice)
        self.assertIn("repository code is licensed under the Apache License", notice)
        self.assertIn("CC BY-NC 4.0", notice)

    def test_store_constants_are_exact(self) -> None:
        self.assertEqual(
            store_contract.STORE_COMMIT,
            "73b97db21b8155a7a95ed10259524110d070facc",
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

    def test_module_layout_and_scenario_inventory(self) -> None:
        module_root = ROOT / "references/modules"
        module_entrypoints = sorted(module_root.glob("*/SKILL.md"))
        root_skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        scenario_index = json.loads(
            (ROOT / "references/scenarios/suite-index.json").read_text(
                encoding="utf-8"
            )
        )
        registry_rows = re.findall(
            r"(?m)^\| ([a-z0-9-]+) \| (?:operation|support) \| .* "
            r"\| `([^`]+)` \|$",
            root_skill,
        )

        self.assertEqual(len(module_entrypoints), 21)
        self.assertEqual(len(registry_rows), 21)
        self.assertEqual(
            len(registry_rows),
            len({module for module, _ in registry_rows}),
        )
        registry = dict(registry_rows)
        for entrypoint in module_entrypoints:
            module = entrypoint.parent.name
            self.assertEqual(
                registry.get(module),
                f"references/modules/{module}/SKILL.md",
            )
        indexed_scenarios = (
            scenario_index["current"] + scenario_index["historical"]
        )
        self.assertEqual(len(indexed_scenarios), 27)
        self.assertEqual(len(indexed_scenarios), len(set(indexed_scenarios)))
        for scenario in indexed_scenarios:
            self.assertTrue((ROOT / "references/scenarios" / scenario).is_file())

    def test_actual_root_version_surface_is_v0_5_0(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        manifest = (ROOT / "apm.yml").read_text(encoding="utf-8")

        self.assertRegex(skill, r"(?m)^name: autogenesis$")
        self.assertRegex(skill, r'(?m)^version: "?0\.5\.0"?$')
        self.assertRegex(skill, r"(?m)^activation_card: on$")
        self.assertIn("name: autogenesis\n", manifest)
        self.assertIn("version: 0.5.0\n", manifest)

    def test_optional_module_template_is_instruction_only(self) -> None:
        template = (
            ROOT / "references/modules/patterns/references/skill-module-template.md"
        ).read_text(encoding="utf-8")
        example = template.split("```markdown\n", 1)[1].split("```", 1)[0]
        frontmatter = example.split("---\n", 2)[1]
        fields = {
            line.split(":", 1)[0]
            for line in frontmatter.splitlines()
            if ":" in line
        }

        self.assertEqual(fields, {"name", "description"})
        self.assertNotIn("autogenesis.invocation-", example)
        self.assertNotIn("workflow-discipline", example)
        self.assertNotIn(".py", example)
        self.assertIn("## Inputs and boundaries", example)
        self.assertIn("## Procedure", example)
        self.assertIn("## Outcome", example)

    def test_implement_plan_is_bound_to_approved_design_receipt(self) -> None:
        contract_root = ROOT / "references/modules/workflow-discipline/references"
        contract = json.loads(
            (contract_root / "invocation-contract.json").read_text(
                encoding="utf-8"
            )
        )
        prose = (contract_root / "invocation-contract.md").read_text(
            encoding="utf-8"
        )
        implement = (ROOT / "references/modules/implement/SKILL.md").read_text(
            encoding="utf-8"
        )

        self.assertEqual(
            contract["approval_binding"],
            {
                "implement_plan_ref_source":
                    "parent_design_receipt.result.artifact",
                "required_design_disposition": "approved",
                "required_context_matches": ["approval_ref", "work_id"],
                "mismatch_disposition": "blocked-before-effects",
            },
        )
        self.assertIn("`arguments.plan_ref`", prose)
        self.assertRegex(
            prose,
            r"accepted only when it exactly\s+equals",
        )
        self.assertIn("`result.artifact`", prose)
        self.assertIn("`context.work_id`", prose)
        self.assertIn("blocks before procedure effects", prose)
        self.assertIn("exactly match", implement)
        self.assertIn("approved parent design receipt", implement)
        self.assertIn("Reject before effects", implement)

    def test_module_resource_references_resolve_from_declared_roots(self) -> None:
        module_root = ROOT / "references/modules"
        entrypoints = sorted(module_root.glob("*/SKILL.md"))
        authority = " ".join(
            (module_root / "workflow-discipline/SKILL.md")
            .read_text(encoding="utf-8")
            .split()
        )
        for rule in (
            "Normal references resolve from this module root.",
            "Shared package resources resolve from `<skill_root>`.",
            "Siblings resolve through the active parent registry.",
            "Never use cwd as the base.",
        ):
            self.assertIn(rule, authority)

        errors = []
        for entrypoint in entrypoints:
            errors.extend(
                module_resource_reference_errors(
                    entrypoint,
                    entrypoint.read_text(encoding="utf-8"),
                )
            )
        self.assertEqual([], errors)

        expected_shared_resources = {
            "aware-runtime": "references/aware-hook-template.md",
            "reflect-challenge":
                "references/behaviour-challenge-template.md",
        }
        for module, relative in expected_shared_resources.items():
            with self.subTest(module=module):
                content = (
                    module_root / module / "SKILL.md"
                ).read_text(encoding="utf-8")
                self.assertIn(f"<skill_root>/{relative}", content)
                self.assertTrue((ROOT / relative).is_file())

        mutation_cases = {
            "bare package-shared resource":
                "`references/aware-hook-template.md`",
            "missing package-shared resource":
                "`<skill_root>/references/missing-template.md`",
            "missing module-local resource":
                "`references/missing-reference.md`",
            "direct sibling module":
                "`<skill_root>/references/modules/patterns/SKILL.md`",
            "normalized direct sibling module":
                "`<skill_root>/references/./modules/patterns/SKILL.md`",
            "skill-root traversal":
                "`<skill_root>/references/../../outside.md`",
            "parent-relative sibling module":
                "`../patterns/SKILL.md`",
            "dot-relative package-shared resource":
                "`./references/aware-hook-template.md`",
            "dot-parent-relative sibling module":
                "`./../patterns/SKILL.md`",
            "skill-root dot-relative package-shared resource":
                "`<skill_root>/./references/aware-hook-template.md`",
            "skill-root parent traversal":
                "`<skill_root>/../outside.md`",
            "skill-root dot-parent traversal":
                "`<skill_root>/./../outside.md`",
            "skill-root repeated-separator traversal":
                "`<skill_root>/references//../../outside.md`",
            "complete malformed path token":
                "`<skill_root>/references/aware-hook-template.md-extra`",
        }
        entrypoint = module_root / "aware-runtime/SKILL.md"
        for case, content in mutation_cases.items():
            with self.subTest(case=case):
                self.assertTrue(
                    module_resource_reference_errors(entrypoint, content)
                )

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
