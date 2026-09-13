from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path

import store_contract


ROOT = Path(__file__).resolve().parents[1]
RESOURCE_REFERENCE_TOKEN = re.compile(
    r"(?<![A-Za-z0-9_./<>-])(?P<token>"
    r"(?:\./)*<skill_root>/[A-Za-z0-9_./<>-]+"
    r"|(?:\./|\.\./)*references/[A-Za-z0-9_./<>-]+"
    r"|(?:\./)*(?:\.\./)+[A-Za-z0-9_./<>-]+"
    r"|/+[A-Za-z0-9_.-]+(?:/+[A-Za-z0-9_.-]+)*"
    r")(?![A-Za-z0-9_./<>-])"
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

    for match in RESOURCE_REFERENCE_TOKEN.finditer(content):
        path_token = match.group("token").rstrip(".,;:")
        if "/" not in path_token:
            continue

        if "<skill_root>" in path_token:
            if not path_token.startswith("<skill_root>/"):
                errors.append(
                    f"{entrypoint.relative_to(ROOT)}: non-canonical resource "
                    f"path {path_token} must start at <skill_root>"
                )
                continue
            raw_path = path_token.removeprefix("<skill_root>/")
            if (
                raw_path.startswith(("./", "../", "/"))
                or "//" in raw_path
            ):
                errors.append(
                    f"{entrypoint.relative_to(ROOT)}: non-canonical "
                    f"package-shared resource {path_token}"
                )
                continue
            relative = Path(raw_path)
            if any(part in {".", ".."} for part in relative.parts):
                errors.append(
                    f"{entrypoint.relative_to(ROOT)}: non-canonical resource "
                    f"path {path_token} contains a traversal segment"
                )
                continue
            if "<" in raw_path or ">" in raw_path:
                continue

            resource = (ROOT / relative).resolve()
            try:
                resource.relative_to(ROOT.resolve())
            except ValueError:
                errors.append(
                    f"{entrypoint.relative_to(ROOT)}: package-shared resource "
                    f"{path_token} escapes the skill root"
                )
                continue
            if not resource.exists():
                errors.append(
                    f"{entrypoint.relative_to(ROOT)}: missing package-shared "
                    f"resource {path_token}"
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

        if path_token.startswith("/"):
            errors.append(
                f"{entrypoint.relative_to(ROOT)}: absolute resource "
                f"{path_token} must use a declared resolution root"
            )
            continue
        if path_token.startswith("./"):
            errors.append(
                f"{entrypoint.relative_to(ROOT)}: non-canonical resource "
                f"path {path_token} uses a relative prefix"
            )
            continue
        if path_token.startswith("../"):
            errors.append(
                f"{entrypoint.relative_to(ROOT)}: parent-relative resource "
                f"{path_token} escapes the module root"
            )
            continue
        if "<" in path_token or ">" in path_token:
            continue
        if not path_token.startswith("references/"):
            continue

        relative = Path(path_token)
        if "//" in path_token:
            errors.append(
                f"{entrypoint.relative_to(ROOT)}: non-canonical resource "
                f"path {path_token} contains a repeated separator"
            )
            continue
        if any(part in {".", ".."} for part in relative.parts):
            errors.append(
                f"{entrypoint.relative_to(ROOT)}: non-canonical resource "
                f"path {relative} contains a traversal segment"
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
        if module_resource.exists():
            continue
        shared_resource = (ROOT / relative).resolve()
        if shared_resource.exists():
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
        self.assertIn("version: 0.8.0\n", manifest)
        self.assertIn("license: Apache-2.0\n", manifest)
        self.assertIn(
            "repository: https://github.com/sergio-sisternes-epam/autogenesis\n",
            manifest,
        )
        self.assertIn("name: autogenesis\n", skill)
        self.assertIn("version: 0.8.0\n", skill)
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

    def test_discuss_is_an_explicit_external_integration(self) -> None:
        manifest = (ROOT / "apm.yml").read_text(encoding="utf-8")
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        discipline = (
            ROOT / "references/modules/workflow-discipline/SKILL.md"
        ).read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("- name: discuss\n      marketplace: atlas", manifest)
        self.assertFalse((ROOT / "references/modules/discuss/SKILL.md").exists())
        self.assertFalse((ROOT / "references/paths/discuss.md").exists())
        self.assertNotIn("path: discuss", skill)
        self.assertNotIn("references/modules/discuss/SKILL.md", skill)
        self.assertNotIn("path: discuss", discipline)
        self.assertIn("Activate the\ncatalog **discuss** package directly", skill)
        self.assertIn("activate the catalog Discuss package directly", readme)

    def test_think_wrappers_nest_load_catalog_think(self) -> None:
        manifest = (ROOT / "apm.yml").read_text(encoding="utf-8")
        lock = (ROOT / "apm.lock.yaml").read_text(encoding="utf-8")
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        challenge = (
            ROOT / "references/modules/think-challenge/SKILL.md"
        ).read_text(encoding="utf-8")
        grill = (
            ROOT / "references/modules/think-grill/SKILL.md"
        ).read_text(encoding="utf-8")
        ramble = (
            ROOT / "references/modules/think-ramble/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("- name: think\n      marketplace: atlas", manifest)
        self.assertIn(
            "resolved_commit: 874613a67018c74ee95f857416fb315d2f80b92b",
            lock,
        )
        self.assertEqual(
            len(list((ROOT / "references/modules").glob("*/SKILL.md"))),
            22,
        )
        self.assertIn("external catalog skill", challenge)
        self.assertIn(
            "named `think-challenge` from package `think`",
            challenge,
        )
        self.assertIn("named `think-grill` from package `think`", grill)
        self.assertIn("named `think-ramble` from package `think`", ramble)
        self.assertIn(
            "do not treat the catalog skill name as a re-entry",
            challenge,
        )
        self.assertIn("must not re-enter the", skill)
        self.assertIn("named theories and model knowledge", challenge)
        self.assertIn(
            "Do not invoke while catalog Discuss is active",
            grill,
        )
        self.assertIn(
            "Do not invoke while catalog Discuss is active",
            ramble,
        )
        self.assertIn(
            "Conversation-only catalog fallback is not legal",
            challenge,
        )
        self.assertIn("nest-loads catalog `think@atlas`", skill)
        self.assertIn(
            "Map this wrapper's arguments onto that catalog",
            challenge,
        )
        self.assertIn("`design_target` is the claim to challenge", challenge)
        self.assertIn("`topic` is the idea to grill", grill)
        self.assertIn("`thoughts` is the free-form text to capture", ramble)
        self.assertIn(
            "Fail closed before loading if the catalog procedure cannot honor",
            ramble,
        )
        self.assertIn(
            "Fail closed before loading if the catalog procedure cannot honor",
            challenge,
        )
        self.assertIn(
            "Fail closed before loading if the catalog procedure cannot honor",
            grill,
        )

    def test_store_constants_are_exact(self) -> None:
        self.assertEqual(
            store_contract.STORE_COMMIT,
            "110cab3deb3a87695003c6276ad92426e6262521",
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

        self.assertEqual(len(module_entrypoints), 22)
        self.assertEqual(len(registry_rows), 22)
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
        self.assertEqual(len(indexed_scenarios), 35)
        self.assertEqual(len(indexed_scenarios), len(set(indexed_scenarios)))
        for scenario in indexed_scenarios:
            self.assertTrue((ROOT / "references/scenarios" / scenario).is_file())

    def test_help_and_getting_started_are_explanatory_operations(self) -> None:
        contract = json.loads(
            (
                ROOT
                / "references/modules/workflow-discipline/references"
                / "invocation-contract.json"
            ).read_text(encoding="utf-8")
        )
        help_skill = (ROOT / "references/modules/help/SKILL.md").read_text(
            encoding="utf-8"
        )
        getting_started = (
            ROOT / "references/modules/getting-started/SKILL.md"
        ).read_text(encoding="utf-8")
        catalog = (
            ROOT / "references/modules/help/references/capability-catalog.md"
        ).read_text(encoding="utf-8")
        journey = (
            ROOT
            / "references/modules/getting-started/references/first-journey.md"
        ).read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        notice = (ROOT / "NOTICE").read_text(encoding="utf-8")

        self.assertEqual(contract["modules"]["help"], "operation")
        self.assertEqual(contract["modules"]["getting-started"], "operation")
        self.assertEqual(len(contract["modules"]), 22)
        self.assertEqual(
            set(contract["modules"]),
            set(contract["module_arguments"]),
        )
        self.assertEqual(contract["module_arguments"]["help"]["required"], [])
        self.assertEqual(
            contract["module_arguments"]["help"]["optional"],
            ["target"],
        )
        self.assertTrue(
            (ROOT / "references/modules/help/references/topics.md").is_file()
        )
        self.assertIn("intent:", help_skill)
        self.assertIn("atlas_used:", help_skill)
        self.assertIn("Do not auto-mount Atlas", help_skill)
        self.assertIn("references/topics.md", help_skill)
        self.assertIn("inherited parent atlas_id", help_skill)
        self.assertIn("context_summary:", help_skill)
        self.assertIn("live parent registry", help_skill)
        self.assertIn("parent-registry **operation** name", help_skill)
        self.assertIn("context_summary:", getting_started)
        self.assertNotIn("atlas_status: not-queried", help_skill)
        self.assertIn("inherited parent atlas_id", getting_started)
        self.assertIn("help_status: pending", getting_started)
        self.assertNotIn("atlas_id: none", getting_started)
        enrich = (
            ROOT / "references/modules/help/references/enrichment.md"
        ).read_text(encoding="utf-8")
        self.assertIn("atlas resolve <atlas_id>", enrich)
        self.assertIn("Use only the path that command returns", enrich)
        self.assertIn("external `atlas` skill", enrich)
        self.assertIn("Never implement from discussion", journey)
        self.assertIn("initialise -> explicit", journey)
        self.assertIn("Do not design, implement, wire", help_skill)
        self.assertIn("Unknown target", help_skill)
        self.assertNotIn("validate-okf-conformance", catalog)
        self.assertIn("| getting-started |", catalog)
        self.assertIn("Never implement from discussion", journey)
        self.assertIn("| help |", readme)
        self.assertIn("| getting-started |", readme)
        self.assertIn("## Modules", readme)
        self.assertNotIn("activation path", readme.lower())
        self.assertNotIn("visualise", help_skill.lower())
        self.assertNotIn("visualise", getting_started.lower())
        self.assertIn("https://github.com/danielmeppiel/genesis", notice)

    def test_shared_skill_design_principles_are_linked(self) -> None:
        authority = ROOT / "references/skill-design-principles.md"
        self.assertTrue(authority.is_file())

        expected_references = {
            ROOT / "SKILL.md":
                "](references/skill-design-principles.md)",
            ROOT / "references/modules/design/SKILL.md":
                "`<skill_root>/references/skill-design-principles.md`",
            ROOT / "references/modules/initialise/SKILL.md":
                "`<skill_root>/references/skill-design-principles.md`",
            ROOT / "references/modules/review-package/SKILL.md":
                "`<skill_root>/references/skill-design-principles.md`",
            ROOT / (
                "references/modules/patterns/references/"
                "parent-routed-skill-module.md"
            ): "](../../../skill-design-principles.md)",
        }
        for path, reference in expected_references.items():
            with self.subTest(path=path.relative_to(ROOT)):
                content = path.read_text(encoding="utf-8")
                self.assertIn(reference, content)

    def test_actual_root_version_surface_is_v0_8_0(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        manifest = (ROOT / "apm.yml").read_text(encoding="utf-8")

        self.assertRegex(skill, r"(?m)^name: autogenesis$")
        self.assertRegex(skill, r'(?m)^version: "?0\.8\.0"?$')
        self.assertRegex(skill, r"(?m)^activation_card: on$")
        self.assertIn("name: autogenesis\n", manifest)
        self.assertIn("version: 0.8.0\n", manifest)

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
            "prefixed skill-root placeholder":
                "`./<skill_root>/references/aware-hook-template.md`",
            "skill-root repeated separator before traversal":
                "`<skill_root>//../outside.md`",
            "absolute package resource":
                "`/references/aware-hook-template.md`",
            "absolute external resource":
                "`/tmp/template.md`",
            "absolute single-component resource":
                "`/tmp`",
            "absolute repeated-separator resource":
                "`/tmp//outside.md`",
            "extensionless missing module resource":
                "`references/missing-reference`",
            "extensionless direct sibling module":
                "`<skill_root>/references/modules/patterns`",
            "plain bare package-shared resource":
                "Load references/aware-hook-template.md before continuing.",
            "templated skill-root traversal":
                "`<skill_root>/../<outside>.md`",
            "nested templated skill-root traversal":
                "`<skill_root>/references/modules/<module>/../../outside.md`",
            "templated parent-relative sibling":
                "`../<module>/SKILL.md`",
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
