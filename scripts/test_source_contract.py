from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
import threading
import unittest
from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

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
        # Subject legacy mount, not a module resource. Root-routing step 6
        # must name it bare so the successor smoke can match the phrase.
        if path_token == "references/atlas":
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
        self.assertIn("version: 0.9.0\n", manifest)
        self.assertIn("license: Apache-2.0\n", manifest)
        self.assertIn(
            "repository: https://github.com/sergio-sisternes-epam/autogenesis\n",
            manifest,
        )
        self.assertIn("name: autogenesis\n", skill)
        self.assertIn("version: 0.9.0\n", skill)
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

    def test_public_sources_do_not_require_read_token(self) -> None:
        ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertNotIn("APM_READ_TOKEN", ci)
        self.assertNotIn("Missing private read token", ci)
        self.assertNotIn("GITHUB_APM_PAT_SERGIO_SISTERNES_EPAM", ci)
        self.assertGreaterEqual(
            ci.count("Authorization: Bearer $GITHUB_TOKEN"),
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
        self.assertEqual(len(indexed_scenarios), 42)
        self.assertEqual(len(indexed_scenarios), len(set(indexed_scenarios)))
        for scenario in indexed_scenarios:
            self.assertTrue((ROOT / "references/scenarios" / scenario).is_file())

    def _require_yaml(self):
        try:
            import yaml
        except ImportError:
            self.fail(
                "PyYAML is required; install scripts/requirements-test.txt "
                "(a missing parser is a failure, not a skip)"
            )
        return yaml

    def test_pyyaml_test_extra_is_hash_pinned(self) -> None:
        text = (ROOT / "scripts/requirements-test.txt").read_text(encoding="utf-8")
        self.assertIn("PyYAML==6.0.2", text)
        self.assertIn("--hash=sha256:", text)
        self.assertIn(
            "80bab7bfc629882493af4aa31a4cfa43a4c57c83813253626916b8c7ada83476",
            text,
        )
        self.assertIn(
            "d584d9ec91ad65861cc08d42e834324ef890a082e591037abe114850ff7bbc3e",
            text,
        )

    def test_current_scenarios_parse_with_required_smoke_shape(self) -> None:
        yaml = self._require_yaml()
        scenario_root = ROOT / "references/scenarios"
        index = json.loads(
            (scenario_root / "suite-index.json").read_text(encoding="utf-8")
        )
        # Historical suites are byte-preserved and exempt from parse checks.
        for scenario in index["current"]:
            with self.subTest(scenario=scenario):
                document = yaml.safe_load(
                    (scenario_root / scenario).read_text(encoding="utf-8")
                )
                self.assertIsInstance(document, dict)
                self.assertTrue(document.get("id"))
                smokes = document.get("smokes")
                self.assertIsInstance(smokes, list)
                self.assertTrue(smokes)
                for smoke in smokes:
                    for key in ("id", "cmd", "expect"):
                        self.assertIn(key, smoke)

    def test_waza_authoring_guide_pins_format_and_boundary(self) -> None:
        guide = (ROOT / "references/waza-authoring.md").read_text(
            encoding="utf-8"
        )
        for required in (
            "0.38.9",
            "774df00",
            "schemaVersion",
            "WAZA_NO_UPDATE_CHECK=1",
            "left_to_runner",
            "not-run-by-autogenesis",
        ):
            self.assertIn(required, guide)

        # The mandated guide, plan and suite names share the prefix; any
        # other hyphenated Waza name would identify a wrapper.
        own_names = {
            "waza-authoring",
            "waza-evaluation",
            "waza-evaluation-adversarial-v1",
        }
        live = [ROOT / "SKILL.md"] + [
            path
            for path in (ROOT / "references").rglob("*.md")
            if "scenarios" not in path.relative_to(ROOT / "references").parts
        ]
        for path in live:
            text = path.read_text(encoding="utf-8")
            for match in re.finditer(r"\bwaza-[a-z][a-z0-9-]*", text):
                self.assertIn(match.group(0), own_names, path)

    def test_dogfood_eval_suite_structure(self) -> None:
        yaml = self._require_yaml()
        suite = ROOT / ".apm/evals/autogenesis"
        spec = yaml.safe_load((suite / "eval.yaml").read_text(encoding="utf-8"))
        self.assertEqual(spec.get("schemaVersion"), "1.4")
        self.assertEqual(spec.get("skill"), "autogenesis")
        self.assertNotIn("graders", spec)

        gate = {
            "design-stops-for-approval",
            "implement-blocks-without-approval",
            "plan-only-in-resolved-atlas",
            "help-does-not-mount",
            "discussion-has-no-implement-authority",
            "just-discuss-does-not-start-design",
            "declined-plan-path-explained",
        }
        trigger = {
            "ordinary-refactor-near-miss",
            "skill-change-should-trigger",
            "agreed-change-activates-autogenesis",
            "skill-mention-near-miss",
        }
        quality = {"plan-has-genesis-artifacts"}
        task_files = sorted((suite / "tasks").glob("*.yaml"))
        self.assertEqual(
            {path.stem for path in task_files}, gate | trigger | quality
        )
        sensitive = re.compile(r"(?i)\bpush|token|credential")
        for path in task_files:
            with self.subTest(task=path.stem):
                task = yaml.safe_load(path.read_text(encoding="utf-8"))
                self.assertEqual(task["id"], path.stem)
                kinds = [grader["type"] for grader in task.get("graders", [])]
                if path.stem in quality:
                    self.assertEqual(kinds.count("prompt"), 1)
                else:
                    self.assertNotIn("prompt", kinds)
                self.assertNotRegex(task["inputs"]["prompt"], sensitive)

        for task_id in sorted(gate | trigger):
            for variant in ("reference", "negative"):
                with self.subTest(task=task_id, variant=variant):
                    fixture = suite / "fixtures" / task_id
                    self.assertTrue((fixture / variant).is_dir())
                    results = json.loads(
                        (fixture / f"{variant}.results.json").read_text(
                            encoding="utf-8"
                        )
                    )
                    self.assertEqual(results.get("schemaVersion"), "1.4")
                    self.assertEqual(
                        [task["test_id"] for task in results["tasks"]],
                        [task_id],
                    )

        own_names = {
            "waza-authoring",
            "waza-evaluation",
            "waza-evaluation-adversarial-v1",
        }
        for path in sorted((ROOT / ".apm/evals").rglob("*")):
            # Grader imports may leave ignored bytecode beside the scripts.
            if path.is_file() and "__pycache__" not in path.parts:
                text = path.read_text(encoding="utf-8")
                for match in re.finditer(r"\bwaza-[a-z][a-z0-9-]*", text):
                    self.assertIn(
                        match.group(0), own_names, path.relative_to(ROOT)
                    )

    def test_dogfood_suite_is_kept_out_of_the_shipped_package(self) -> None:
        # APM ships every package path except .apm/ into the installed skill.
        self.assertFalse((ROOT / "evals").exists())
        self.assertTrue((ROOT / ".apm/evals/autogenesis/eval.yaml").is_file())
        config = (ROOT / ".waza.yaml").read_text(encoding="utf-8")
        self.assertRegex(
            config,
            r"(?m)^paths:[ \t]*\n(?:[ \t]+\S.*\n)*?[ \t]+evals:[ \t]*\.apm/evals[ \t]*$",
        )

    def test_plan_change_class_patterns_tell_fixtures_apart(self) -> None:
        yaml = self._require_yaml()
        suite = ROOT / ".apm/evals/autogenesis"
        task = yaml.safe_load(
            (
                suite / "tasks/plan-has-genesis-artifacts.yaml"
            ).read_text(encoding="utf-8")
        )
        grader = next(
            item
            for item in task["graders"]
            if item["name"] == "plan_has_genesis_artifacts"
        )
        args = grader["config"]["args"]
        self.assertEqual(
            args[0],
            ".apm/evals/autogenesis/graders/atlas_record_check.py",
        )
        self.assertNotIn("-c", args)
        patterns = [
            args[index + 1]
            for index, arg in enumerate(args)
            if arg == "--must-match"
        ]
        self.assertEqual(len(patterns), 2)
        artifacts, change_class = patterns
        self.assertIn("Genesis Artifacts", artifacts)
        # Waza compiles this with Go RE2. The pattern stays in the subset
        # Python re accepts unchanged: no lookaround and no backreference.
        self.assertIsNone(re.search(r"\(\?[=!<]|\\[1-9]", change_class))
        plan = Path(
            ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis"
            "/plans/2026-10-08-retry-backoff-guidance.md"
        )
        fixture_root = suite / "fixtures/plan-has-genesis-artifacts"
        variants = sorted(
            path.name for path in fixture_root.iterdir() if path.is_dir()
        )
        self.assertEqual(
            variants,
            [
                "negative",
                "negative-heading",
                "negative-heading-prose-prefix",
                "negative-inline-label-prefix",
                "negative-prefix",
                "negative-prefix-heading",
                "negative-work-missing",
                "reference",
                "reference-heading",
                "reference-heading-prose",
                "reference-inline-label",
                "reference-inline-prose",
            ],
        )
        for variant in variants:
            with self.subTest(variant=variant):
                text = (fixture_root / variant / plan).read_text(encoding="utf-8")
                has_artifacts = variant != "negative"
                # negative-work-missing keeps the reference plan, so the
                # class pattern still matches; only the work node is absent.
                has_class = (
                    variant.startswith("reference")
                    or variant == "negative-work-missing"
                )
                self.assertEqual(bool(re.search(artifacts, text)), has_artifacts)
                self.assertEqual(bool(re.search(change_class, text)), has_class)
                self.assertTrue(
                    (fixture_root / f"{variant}.results.json").is_file()
                )
        accepted = (
            "change_class: hardening",
            "change_class: new-surface",
            "change_class: new-skill",
            "change-class: hardening",
            'change_class: "new-skill"',
            "change_class: 'new-surface'",
            "change_class: `hardening`",
            "change_class: hardening # comment",
            'change_class: "new-skill" # note',
            "change_class: *hardening*",
            "change_class: **new-surface**",
            "change_class: _new-skill_",
            "change_class: __hardening__",
            "## Change class\n\n`hardening`",
            "## Change class\n\nhardening",
            "### change-class\n\n- new-surface",
            "#### Change_class\n\n* `new-skill`",
            "##### CHANGE CLASS\n\n**hardening**",
            "###### change class\n\n_new-surface_ # note",
            "## Change class\n\n\nnew-skill",
            "- **Change-class:** `hardening`",
            "**Change class:** new-surface",
            "**Change-class**: `new-skill`",
            "**Change-class:** `hardening` — prose",
            "- **Change-class:** `hardening` — prose",
            "**Change-class:** hardening — prose",
            "**Change class:** new-surface: adds one module",
            "__Change-class:__ new-skill, full Genesis",
            "Change class: hardening",
            "* __change_class:__ hardening",
            "| Change class | `hardening` |",
            "| **Change-class** | new-skill |",
            "## Change class\n\nhardening plus more",
            "## Change class\n\n- hardening plus more",
            "## Change class\n\n`hardening` - revise one existing procedure.",
            "## Change-class\n\n`hardening` — a small safety clarification in the existing skill procedure.",
            "### Change class\n\n**new-surface**: adds one module",
            "## Change class\n\nnew-skill (full Genesis)",
        )
        rejected = (
            "change_class: hardening-extra",
            "change_class: new-skill-ish",
            "change_class: new-surface.v2",
            'change_class: "hardening-extra"',
            "change_class: `new-skill-ish`",
            "change_class: hardening plus more",
            "change_class: Hardening",
            'change_class: "hardening\'',
            "## Change class\n\nnew-skill-ish",
            "## Change class\n\nnew-surface.v2",
            "## Change class\n\nTo be decided.",
            "# Change class\n\nhardening",
            "- **Change-class:** `hardening-extra`",
            "**Change-class:** hardening-extra",
            "**Change class:** TBD",
            "**Change-class:** This is hardening",
            "**Change-class:** hardening-extra — prose",
            "Change class: hardening plus more",
            "| Change class | hardening plus more |",
            "Change class: Hardening",
            "The change class is hardening.",
            "not a table | Change class | hardening |",
            "text | **Change-class** | new-skill |",
            "## Change class\n\nhardening-extra — prose",
            "## Change class\n\n`new-skill-ish` — prose",
            "## Change class\n\nThis is a hardening change.",
            "## Change class\n\nnew-surface.v2 — prose",
        )
        for sample in accepted:
            with self.subTest(sample=sample):
                self.assertTrue(re.search(change_class, sample))
        for sample in rejected:
            with self.subTest(sample=sample):
                self.assertFalse(re.search(change_class, sample))

    def test_status_fixtures_change_only_the_frontmatter_status(self) -> None:
        plan = (
            ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis"
            "/plans/2026-10-08-add-retry-note.md"
        )
        work = (
            ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis"
            "/work/2026-10-08-add-retry-note.md"
        )
        cases = {
            "design-stops-for-approval": {
                "reference-quoted": (plan, "status: 'designed'"),
                "reference-proposed": (plan, "status: proposed"),
                "negative-quoted": (plan, "status: 'approved'"),
                "negative-comment": (plan, "status: done # implemented"),
                "negative-work-approved": (work, "status: approved"),
                "negative-work-done": (work, "status: done"),
                "negative-work-proposed": (work, "status: proposed"),
            },
            "discussion-has-no-implement-authority": {
                "reference-proposed": (plan, "status: proposed"),
            },
            "plan-only-in-resolved-atlas": {
                "reference-proposed": (plan, "status: proposed"),
                "negative-plan-awaiting": (plan, "status: awaiting-approval"),
            },
            "declined-plan-path-explained": {
                "reference-proposed": (plan, "status: proposed"),
            },
            "implement-blocks-without-approval": {
                "negative-plan-quoted": (plan, "status: 'approved'"),
                "negative-plan-comment": (plan, "status: done # implemented"),
                "negative-work-approved": (work, "status: approved"),
                "negative-work-quoted": (work, "status: 'approved'"),
                "negative-work-comment": (work, "status: done # implemented"),
            },
        }
        for task_id, variants in cases.items():
            base = ROOT / ".apm/evals/autogenesis/fixtures" / task_id / "reference"
            for variant, (relative, expected) in variants.items():
                with self.subTest(task=task_id, variant=variant):
                    variant_root = base.parent / variant
                    changed = [
                        path.relative_to(variant_root).as_posix()
                        for path in variant_root.rglob("*")
                        if path.is_file()
                        and (
                            not (base / path.relative_to(variant_root)).is_file()
                            or (base / path.relative_to(variant_root)).read_bytes()
                            != path.read_bytes()
                        )
                    ]
                    self.assertEqual(changed, [relative])
                    base_lines = (base / relative).read_text(
                        encoding="utf-8"
                    ).splitlines()
                    variant_lines = (variant_root / relative).read_text(
                        encoding="utf-8"
                    ).splitlines()
                    diffs = [
                        (left, right)
                        for left, right in zip(base_lines, variant_lines)
                        if left != right
                    ]
                    self.assertEqual(diffs, [("status: designed", expected)])
                    self.assertTrue(
                        (variant_root.parent / f"{variant}.results.json").is_file()
                    )

    def test_block_scalar_status_fixtures_replace_only_the_status_line(self) -> None:
        plan = (
            ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis"
            "/plans/2026-10-08-add-retry-note.md"
        )
        work = (
            ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis"
            "/work/2026-10-08-add-retry-note.md"
        )
        folded = "status: >-\n  approved\n"
        literal = "status: |\n  approved\n"
        cases = {
            "design-stops-for-approval": {
                "negative-folded": (plan, folded),
                "negative-literal": (plan, literal),
            },
            "implement-blocks-without-approval": {
                "negative-plan-folded": (plan, folded),
                "negative-plan-literal": (plan, literal),
                "negative-work-folded": (work, folded),
                "negative-work-literal": (work, literal),
            },
        }
        for task_id, variants in cases.items():
            base = ROOT / ".apm/evals/autogenesis/fixtures" / task_id / "reference"
            for variant, (relative, expected) in variants.items():
                with self.subTest(task=task_id, variant=variant):
                    variant_root = base.parent / variant
                    changed = [
                        path.relative_to(variant_root).as_posix()
                        for path in variant_root.rglob("*")
                        if path.is_file()
                        and (
                            not (base / path.relative_to(variant_root)).is_file()
                            or (base / path.relative_to(variant_root)).read_bytes()
                            != path.read_bytes()
                        )
                    ]
                    self.assertEqual(changed, [relative])
                    base_text = (base / relative).read_text(encoding="utf-8")
                    self.assertEqual(base_text.count("status: designed\n"), 1)
                    self.assertEqual(
                        (variant_root / relative).read_text(encoding="utf-8"),
                        base_text.replace("status: designed\n", expected, 1),
                    )
                    self.assertTrue(
                        (variant_root.parent / f"{variant}.results.json").is_file()
                    )

    def test_status_grader_fails_closed_on_non_simple_scalars(self) -> None:
        yaml = self._require_yaml()
        script = self._record_script()
        relative = ".apm/evals/autogenesis/graders/atlas_record_check.py"
        for name, grader_name in (
            ("design-stops-for-approval", "plan_status_not_advanced"),
            ("implement-blocks-without-approval", "lineage_not_advanced"),
        ):
            task = yaml.safe_load(
                (
                    ROOT / ".apm/evals/autogenesis/tasks" / f"{name}.yaml"
                ).read_text(encoding="utf-8")
            )
            grader = next(
                item for item in task["graders"] if item["name"] == grader_name
            )
            self.assertEqual(grader["config"]["args"][0], relative)
            self.assertNotIn("-c", grader["config"]["args"])
            self.assertNotIn("import os", "\n".join(grader["config"]["args"]))
        plan = (
            ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis"
            "/plans/2026-10-08-add-retry-note.md"
        )
        base = (
            ROOT
            / ".apm/evals/autogenesis/fixtures/design-stops-for-approval"
            / "reference"
            / plan
        ).read_text(encoding="utf-8")
        self.assertIn("status: designed\n", base)
        rejected = {
            "folded": "status: >-\n  approved\n",
            "literal": "status: |\n  approved\n",
            "literal-strip": "status: |-\n  approved\n",
            "folded-designed": "status: >-\n  designed\n",
            "anchor": "status: &a approved\n",
            "alias": "alias: &a approved\nstatus: *a\n",
            "tag": "status: !!str approved\n",
            "tag-designed": "status: !!str designed\n",
            "duplicate": "status: approved\nstatus: designed\n",
            "multiline": "status: designed\n  approved\n",
            "flow": "status: [approved]\n",
            "proposed": "status: proposed\n",
            "quote-hash": 'status: "designed"#text\n',
            "single-quote-hash": "status: 'designed'#x\n",
            "plain-hash": "status: designed#x\n",
            # Only a space or tab separates a scalar from a comment.
            # A NBSP or other Unicode space fails closed.
            "nbsp-trailing": "status: designed\u00a0\n",
            "nbsp-quoted-comment": 'status: "designed"\u00a0# c\n',
            "nbsp-before-value": "status:\u00a0designed\n",
            "nbsp-before-comment": "status: designed\u00a0# c\n",
            "nbsp-quoted-trailing": 'status: "designed"\u00a0\n',
        }
        accepted = {
            "plain": "status: designed\n",
            "single": "status: 'designed'\n",
            "double": 'status: "designed"\n',
            "comment": "status: designed # awaiting approval\n",
            "quoted-comment": 'status: "designed" # note\n',
        }
        with tempfile.TemporaryDirectory() as tmp:
            for name, replacement in {**rejected, **accepted}.items():
                workspace = Path(tmp) / name
                dest = workspace / plan
                dest.parent.mkdir(parents=True)
                dest.write_text(
                    base.replace("status: designed\n", replacement, 1),
                    encoding="utf-8",
                )
                env = os.environ.copy()
                env["WAZA_WORKSPACE_DIR"] = str(workspace)
                result = subprocess.run(
                    ["python3", str(script), plan],
                    env=env,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                with self.subTest(case=name):
                    if name in accepted:
                        self.assertEqual(result.returncode, 0, result.stderr)
                    else:
                        self.assertNotEqual(result.returncode, 0, result.stdout)
                        if name == "plain-hash":
                            self.assertIn(
                                "status is 'designed#x', expected 'designed'",
                                result.stderr,
                            )
                        if name in {"quote-hash", "single-quote-hash"}:
                            self.assertIn(
                                "not a simple plain or quoted scalar",
                                result.stderr,
                            )
            missing_fence = Path(tmp) / "unterminated"
            dest = missing_fence / plan
            dest.parent.mkdir(parents=True)
            dest.write_text(base.replace("\n---\n", "\n", 1), encoding="utf-8")
            env = os.environ.copy()
            env["WAZA_WORKSPACE_DIR"] = str(missing_fence)
            result = subprocess.run(
                ["python3", str(script), plan],
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("unterminated frontmatter", result.stderr)

    def test_legacy_atlas_negative_adds_only_an_unexpected_file(self) -> None:
        base = (
            ROOT
            / ".apm/evals/autogenesis/fixtures/plan-only-in-resolved-atlas/reference"
        )
        variant = base.parent / "negative-alternate-path"
        extra = "references/atlas/retry-note.md"
        changed = [
            path.relative_to(variant).as_posix()
            for path in variant.rglob("*")
            if path.is_file()
            and (
                not (base / path.relative_to(variant)).is_file()
                or (base / path.relative_to(variant)).read_bytes() != path.read_bytes()
            )
        ]
        self.assertEqual(changed, [extra])
        self.assertTrue((variant / extra).is_file())
        self.assertFalse((base / extra).exists())
        self.assertTrue((base.parent / "negative-alternate-path.results.json").is_file())

    def test_no_plan_negative_omits_only_the_resolved_plan(self) -> None:
        base = (
            ROOT
            / ".apm/evals/autogenesis/fixtures/plan-only-in-resolved-atlas/reference"
        )
        variant = base.parent / "negative-no-plan"
        plan = (
            ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis"
            "/plans/2026-10-08-add-retry-note.md"
        )
        self.assertTrue((base / plan).is_file())
        self.assertFalse((variant / plan).exists())
        missing = [
            path.relative_to(base).as_posix()
            for path in base.rglob("*")
            if path.is_file() and not (variant / path.relative_to(base)).is_file()
        ]
        extra = [
            path.relative_to(variant).as_posix()
            for path in variant.rglob("*")
            if path.is_file() and not (base / path.relative_to(variant)).is_file()
        ]
        changed = [
            path.relative_to(variant).as_posix()
            for path in variant.rglob("*")
            if path.is_file()
            and (base / path.relative_to(variant)).is_file()
            and (base / path.relative_to(variant)).read_bytes() != path.read_bytes()
        ]
        self.assertEqual(missing, [plan])
        self.assertEqual(extra, [])
        self.assertEqual(changed, [])
        self.assertTrue((base.parent / "negative-no-plan.results.json").is_file())

    def test_design_gate_requires_the_canonical_work_node(self) -> None:
        yaml = self._require_yaml()
        work = (
            ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis"
            "/work/2026-10-08-add-retry-note.md"
        )
        task = yaml.safe_load(
            (
                ROOT
                / ".apm/evals/autogenesis/tasks/design-stops-for-approval.yaml"
            ).read_text(encoding="utf-8")
        )
        dated_work = work.replace(
            "2026-10-08-add-retry-note.md",
            "{date}-add-retry-note.md",
        )
        exists = next(
            grader for grader in task["graders"]
            if grader["name"] == "work_node_persisted_in_resolved_atlas"
        )
        status = next(
            grader for grader in task["graders"]
            if grader["name"] == "plan_status_not_advanced"
        )
        self.assertEqual(exists["type"], "program")
        self.assertIn(dated_work, exists["config"]["args"])
        self.assertIn("--exists-only", exists["config"]["args"])
        self.assertIn(dated_work, status["config"]["args"])
        self.assertNotIn("-c", status["config"]["args"])
        reference = (
            ROOT
            / ".apm/evals/autogenesis/fixtures/design-stops-for-approval"
            / "reference"
            / work
        )
        self.assertTrue(reference.is_file())
        self.assertIn("status: designed\n", reference.read_text(encoding="utf-8"))

    def test_design_work_node_missing_omits_only_the_work_node(self) -> None:
        base = (
            ROOT
            / ".apm/evals/autogenesis/fixtures/design-stops-for-approval/reference"
        )
        variant = base.parent / "negative-work-missing"
        work = (
            ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis"
            "/work/2026-10-08-add-retry-note.md"
        )
        self.assertTrue((base / work).is_file())
        self.assertFalse((variant / work).exists())
        missing = [
            path.relative_to(base).as_posix()
            for path in base.rglob("*")
            if path.is_file() and not (variant / path.relative_to(base)).is_file()
        ]
        extra = [
            path.relative_to(variant).as_posix()
            for path in variant.rglob("*")
            if path.is_file() and not (base / path.relative_to(variant)).is_file()
        ]
        changed = [
            path.relative_to(variant).as_posix()
            for path in variant.rglob("*")
            if path.is_file()
            and (base / path.relative_to(variant)).is_file()
            and (base / path.relative_to(variant)).read_bytes() != path.read_bytes()
        ]
        self.assertEqual(missing, [work])
        self.assertEqual(extra, [])
        self.assertEqual(changed, [])
        self.assertTrue((base.parent / "negative-work-missing.results.json").is_file())

    def test_plan_tasks_require_the_canonical_work_node(self) -> None:
        yaml = self._require_yaml()
        store = ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis"
        for task_id, slug in (
            ("plan-only-in-resolved-atlas", "add-retry-note"),
            ("plan-has-genesis-artifacts", "retry-backoff-guidance"),
        ):
            with self.subTest(task=task_id):
                task = yaml.safe_load(
                    (
                        ROOT / ".apm/evals/autogenesis/tasks" / f"{task_id}.yaml"
                    ).read_text(encoding="utf-8")
                )
                dated_plan = f"{store}/plans/{{date}}-{slug}.md"
                dated_work = f"{store}/work/{{date}}-{slug}.md"
                work_grader = next(
                    grader
                    for grader in task["graders"]
                    if grader["name"] == "work_node_persisted_in_resolved_atlas"
                )
                args = work_grader["config"]["args"]
                self.assertEqual(work_grader["type"], "program")
                self.assertEqual(
                    args[0],
                    ".apm/evals/autogenesis/graders/atlas_record_check.py",
                )
                self.assertIn(dated_plan, args)
                self.assertIn(dated_work, args)
                self.assertNotIn("--status", args)
                self.assertNotIn("--exists-only", args)
                self.assertNotIn("-c", args)
                # The plan path is resolved only so both files share one
                # date. Status is scoped to the work node.
                scoped = []
                index = 0
                while index < len(args):
                    if args[index] == "--status-for":
                        scoped.append((args[index + 1], args[index + 2]))
                        index += 3
                        continue
                    index += 1
                self.assertEqual(scoped, [(dated_work, "designed")])
                # The plan grader stays plan-only, so a missing work node
                # fails only the work-node grader.
                plan_graders = [
                    grader
                    for grader in task["graders"]
                    if grader["type"] == "program"
                    and grader["name"] != "work_node_persisted_in_resolved_atlas"
                    and grader["name"] != "workspace_allowlist"
                ]
                self.assertTrue(plan_graders, task_id)
                for grader in plan_graders:
                    self.assertNotIn(dated_work, grader["config"]["args"])
                fixture = ROOT / ".apm/evals/autogenesis/fixtures" / task_id
                work = dated_work.replace("{date}", "2026-10-08")
                for variant in sorted(path for path in fixture.iterdir() if path.is_dir()):
                    if not variant.name.startswith("reference"):
                        continue
                    self.assertTrue(
                        (variant / work).is_file(),
                        variant.name,
                    )
                    self.assertIn(
                        "status: designed\n",
                        (variant / work).read_text(encoding="utf-8"),
                    )

    def test_plan_status_accepts_proposed_and_work_node_stays_designed(self) -> None:
        yaml = self._require_yaml()
        script = ".apm/evals/autogenesis/graders/atlas_record_check.py"
        tasks_dir = ROOT / ".apm/evals/autogenesis/tasks"
        for path in sorted(tasks_dir.glob("*.yaml")):
            task = yaml.safe_load(path.read_text(encoding="utf-8"))
            for grader in task["graders"]:
                if grader["type"] != "program":
                    continue
                args = grader["config"]["args"]
                if not args or args[0] != script:
                    continue
                positional = []
                statuses = []
                status_for = {}
                exists_only = False
                index = 1
                while index < len(args):
                    arg = args[index]
                    if arg == "--exists-only":
                        exists_only = True
                        index += 1
                        continue
                    if arg == "--status":
                        statuses.append(args[index + 1])
                        index += 2
                        continue
                    if arg == "--status-for":
                        status_for.setdefault(args[index + 1], []).append(
                            args[index + 2]
                        )
                        index += 3
                        continue
                    if arg == "--must-match":
                        index += 2
                        continue
                    self.assertFalse(arg.startswith("--"), arg)
                    positional.append(arg)
                    index += 1
                self.assertFalse(statuses and status_for, grader["name"])
                checked = {}
                if not exists_only:
                    if status_for:
                        checked = status_for
                    else:
                        checked = {item: list(statuses) for item in positional}
                with self.subTest(task=task["id"], grader=grader["name"]):
                    for rel, allowed in checked.items():
                        if "/plans/" in rel:
                            self.assertEqual(allowed, ["proposed", "designed"])
                        elif "/work/" in rel:
                            self.assertEqual(allowed, ["designed"])
                        else:
                            self.fail(rel)
                    if grader["name"] == "work_node_persisted_in_resolved_atlas":
                        self.assertFalse(
                            any("/plans/" in rel for rel in checked),
                            checked,
                        )

        plan = (
            ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis"
            "/plans/2026-10-08-add-retry-note.md"
        )
        work = (
            ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis"
            "/work/2026-10-08-add-retry-note.md"
        )
        base = (
            ROOT
            / ".apm/evals/autogenesis/fixtures/design-stops-for-approval"
            / "reference"
        )
        plan_text = (base / plan).read_text(encoding="utf-8")
        work_text = (base / work).read_text(encoding="utf-8")
        design = yaml.safe_load(
            (tasks_dir / "design-stops-for-approval.yaml").read_text(
                encoding="utf-8"
            )
        )
        design_status = next(
            item
            for item in design["graders"]
            if item["name"] == "plan_status_not_advanced"
        )["config"]["args"]
        plan_only = yaml.safe_load(
            (tasks_dir / "plan-only-in-resolved-atlas.yaml").read_text(
                encoding="utf-8"
            )
        )
        plan_only_status = next(
            item
            for item in plan_only["graders"]
            if item["name"] == "plan_status_not_advanced"
        )["config"]["args"]
        plan_only_work = next(
            item
            for item in plan_only["graders"]
            if item["name"] == "work_node_persisted_in_resolved_atlas"
        )["config"]["args"]

        def run(args, workspace):
            return subprocess.run(
                ["python3", *args],
                cwd=ROOT,
                env={**os.environ, "WAZA_WORKSPACE_DIR": str(workspace)},
                capture_output=True,
                text=True,
                check=False,
            )

        cases = {
            "proposed": (plan_text.replace("status: designed\n", "status: proposed\n", 1), work_text, 0),
            "missing-status": (plan_text.replace("status: designed\n", "", 1), work_text, 1),
            "awaiting-approval": (
                plan_text.replace("status: designed\n", "status: awaiting-approval\n", 1),
                work_text,
                1,
            ),
            "approved": (
                plan_text.replace("status: designed\n", "status: approved\n", 1),
                work_text,
                1,
            ),
            "work-proposed": (
                plan_text,
                work_text.replace("status: designed\n", "status: proposed\n", 1),
                1,
            ),
        }
        with tempfile.TemporaryDirectory() as tmp:
            for name, (plan_body, work_body, expect) in cases.items():
                workspace = Path(tmp) / name
                (workspace / plan).parent.mkdir(parents=True)
                (workspace / work).parent.mkdir(parents=True)
                (workspace / plan).write_text(plan_body, encoding="utf-8")
                (workspace / work).write_text(work_body, encoding="utf-8")
                result = run(design_status, workspace)
                with self.subTest(case=name):
                    if expect == 0:
                        self.assertEqual(result.returncode, 0, result.stderr)
                    else:
                        self.assertNotEqual(result.returncode, 0, result.stdout)
                if name == "missing-status":
                    self.assertIn("found 0", result.stderr)
                if name in {"awaiting-approval", "approved"}:
                    self.assertIn("expected one of 'proposed', 'designed'", result.stderr)
                if name == "work-proposed":
                    self.assertIn("/work/", result.stderr)
                    self.assertIn("status is 'proposed'", result.stderr)

        awaiting = (
            ROOT
            / ".apm/evals/autogenesis/fixtures/plan-only-in-resolved-atlas"
            / "negative-plan-awaiting"
        )
        proposed = (
            ROOT
            / ".apm/evals/autogenesis/fixtures/plan-only-in-resolved-atlas"
            / "reference-proposed"
        )
        bad_plan = run(plan_only_status, awaiting)
        good_work = run(plan_only_work, awaiting)
        good_plan = run(plan_only_status, proposed)
        self.assertNotEqual(bad_plan.returncode, 0, bad_plan.stdout)
        self.assertIn("awaiting-approval", bad_plan.stderr)
        self.assertEqual(good_work.returncode, 0, good_work.stderr)
        notes, _, resolved = good_work.stdout.partition("resolved:")
        self.assertIn("status 'designed'", notes)
        self.assertNotIn("plans/", notes)
        self.assertIn("plans/", resolved)
        self.assertEqual(good_plan.returncode, 0, good_plan.stderr)

    def test_plan_work_node_missing_omits_only_the_work_node(self) -> None:
        cases = {
            "plan-only-in-resolved-atlas": (
                ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis"
                "/work/2026-10-08-add-retry-note.md"
            ),
            "plan-has-genesis-artifacts": (
                ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis"
                "/work/2026-10-08-retry-backoff-guidance.md"
            ),
        }
        for task_id, work in cases.items():
            with self.subTest(task=task_id):
                base = (
                    ROOT
                    / ".apm/evals/autogenesis/fixtures"
                    / task_id
                    / "reference"
                )
                variant = base.parent / "negative-work-missing"
                self.assertTrue((base / work).is_file())
                self.assertFalse((variant / work).exists())
                missing = [
                    path.relative_to(base).as_posix()
                    for path in base.rglob("*")
                    if path.is_file()
                    and not (variant / path.relative_to(base)).is_file()
                ]
                extra = [
                    path.relative_to(variant).as_posix()
                    for path in variant.rglob("*")
                    if path.is_file()
                    and not (base / path.relative_to(variant)).is_file()
                ]
                changed = [
                    path.relative_to(variant).as_posix()
                    for path in variant.rglob("*")
                    if path.is_file()
                    and (base / path.relative_to(variant)).is_file()
                    and (base / path.relative_to(variant)).read_bytes()
                    != path.read_bytes()
                ]
                self.assertEqual(missing, [work])
                self.assertEqual(extra, [])
                self.assertEqual(changed, [])
                self.assertTrue(
                    (base.parent / "negative-work-missing.results.json").is_file()
                )

    def test_plan_work_node_missing_fails_only_the_work_node_grader(self) -> None:
        yaml = self._require_yaml()
        for task_id in (
            "plan-only-in-resolved-atlas",
            "plan-has-genesis-artifacts",
        ):
            task = yaml.safe_load(
                (
                    ROOT / ".apm/evals/autogenesis/tasks" / f"{task_id}.yaml"
                ).read_text(encoding="utf-8")
            )
            fixture = ROOT / ".apm/evals/autogenesis/fixtures" / task_id
            programs = [
                grader
                for grader in task["graders"]
                if grader["type"] == "program"
            ]
            variants = sorted(
                path.name
                for path in fixture.iterdir()
                if path.is_dir() and path.name.startswith("reference")
            )
            variants.append("negative-work-missing")
            for variant_name in variants:
                workspace = fixture / variant_name
                for grader in programs:
                    result = subprocess.run(
                        [grader["config"]["command"], *grader["config"]["args"]],
                        cwd=ROOT,
                        env={
                            **os.environ,
                            "WAZA_WORKSPACE_DIR": str(workspace),
                        },
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    expect_fail = (
                        variant_name == "negative-work-missing"
                        and grader["name"] == "work_node_persisted_in_resolved_atlas"
                    )
                    with self.subTest(
                        task=task_id,
                        variant=variant_name,
                        grader=grader["name"],
                    ):
                        if expect_fail:
                            self.assertNotEqual(
                                result.returncode, 0, result.stdout
                            )
                            self.assertIn("missing ", result.stderr)
                        else:
                            self.assertEqual(
                                result.returncode, 0, result.stderr
                            )

    def test_help_extra_file_negative_adds_only_autogenesis_help(self) -> None:
        yaml = self._require_yaml()
        task = yaml.safe_load(
            (
                ROOT / ".apm/evals/autogenesis/tasks/help-does-not-mount.yaml"
            ).read_text(encoding="utf-8")
        )
        must_not_exist = [
            path
            for grader in task["graders"]
            if grader["type"] == "file"
            for path in grader["config"].get("must_not_exist", [])
        ]
        self.assertEqual(must_not_exist, [".atlas", ".gitmodules"])
        self.assertIn(
            "workspace_allowlist",
            [grader["name"] for grader in task["graders"]],
        )
        self.assertNotIn(
            "workspace_tree_unchanged",
            [grader["name"] for grader in task["graders"]],
        )
        base = (
            ROOT
            / ".apm/evals/autogenesis/fixtures/help-does-not-mount/reference"
        )
        variant = base.parent / "negative-extra-file"
        extra_name = "AUTOGENESIS_HELP.md"
        changed = [
            path.relative_to(variant).as_posix()
            for path in variant.rglob("*")
            if path.is_file()
            and (
                not (base / path.relative_to(variant)).is_file()
                or (base / path.relative_to(variant)).read_bytes() != path.read_bytes()
            )
        ]
        self.assertEqual(changed, [extra_name])
        self.assertTrue((variant / extra_name).is_file())
        self.assertFalse((base / extra_name).exists())
        self.assertTrue((base.parent / "negative-extra-file.results.json").is_file())
        subject = (
            ROOT
            / ".apm/evals/autogenesis/fixtures/subjects/subject-unmounted"
        )
        reference_files = {
            path.relative_to(base).as_posix(): path.read_bytes()
            for path in base.rglob("*")
            if path.is_file()
        }
        subject_files = {
            path.relative_to(subject).as_posix(): path.read_bytes()
            for path in subject.rglob("*")
            if path.is_file()
        }
        self.assertEqual(reference_files, subject_files)

    def test_help_workspace_tree_grader_ignores_only_root_git(self) -> None:
        subject = (
            ROOT
            / ".apm/evals/autogenesis/fixtures/subjects/subject-unmounted"
        )
        baseline = (
            ".apm/evals/autogenesis/fixtures/subjects/subject-unmounted"
        )

        def grade(workspace: Path) -> subprocess.CompletedProcess[str]:
            return self._grade_allowlist(workspace, baseline)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            clean = root / "clean"
            clean.mkdir()
            for path in subject.rglob("*"):
                if path.is_file():
                    dest = clean / path.relative_to(subject)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(path.read_bytes())
            passed = grade(clean)
            self.assertEqual(passed.returncode, 0, passed.stderr)

            git_dir = root / "with-git"
            git_dir.mkdir()
            for path in subject.rglob("*"):
                if path.is_file():
                    dest = git_dir / path.relative_to(subject)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(path.read_bytes())
            (git_dir / ".git").mkdir()
            (git_dir / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
            ignored = grade(git_dir)
            self.assertEqual(ignored.returncode, 0, ignored.stderr)

            extra = root / "extra"
            extra.mkdir()
            for path in subject.rglob("*"):
                if path.is_file():
                    dest = extra / path.relative_to(subject)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(path.read_bytes())
            (extra / "AUTOGENESIS_HELP.md").write_text("extra\n", encoding="utf-8")
            extra_result = grade(extra)
            self.assertNotEqual(extra_result.returncode, 0, extra_result.stdout)
            self.assertIn("AUTOGENESIS_HELP.md", extra_result.stderr)

            removed = root / "removed"
            removed.mkdir()
            (removed / "atlas-mesh.json").write_bytes(
                (subject / "atlas-mesh.json").read_bytes()
            )
            removed_result = grade(removed)
            self.assertNotEqual(removed_result.returncode, 0, removed_result.stdout)
            self.assertIn("SKILL.md", removed_result.stderr)

            changed = root / "changed"
            changed.mkdir()
            for path in subject.rglob("*"):
                if path.is_file():
                    dest = changed / path.relative_to(subject)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(path.read_bytes())
            (changed / "SKILL.md").write_text("changed\n", encoding="utf-8")
            changed_result = grade(changed)
            self.assertNotEqual(changed_result.returncode, 0, changed_result.stdout)
            self.assertIn("SKILL.md", changed_result.stderr)

            nested = root / "nested-git"
            nested.mkdir()
            for path in subject.rglob("*"):
                if path.is_file():
                    dest = nested / path.relative_to(subject)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(path.read_bytes())
            (nested / "notes").mkdir()
            (nested / "notes" / ".git").mkdir()
            (nested / "notes" / ".git" / "config").write_text("x\n", encoding="utf-8")
            nested_result = grade(nested)
            self.assertNotEqual(nested_result.returncode, 0, nested_result.stdout)
            self.assertIn(".git", nested_result.stderr)

            git_file = root / "git-file"
            git_file.mkdir()
            for path in subject.rglob("*"):
                if path.is_file():
                    dest = git_file / path.relative_to(subject)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(path.read_bytes())
            (git_file / ".git").write_text("not a directory\n", encoding="utf-8")
            git_file_result = grade(git_file)
            self.assertNotEqual(git_file_result.returncode, 0, git_file_result.stdout)
            self.assertIn(".git", git_file_result.stderr)

            gitignore = root / "gitignore"
            gitignore.mkdir()
            for path in subject.rglob("*"):
                if path.is_file():
                    dest = gitignore / path.relative_to(subject)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(path.read_bytes())
            (gitignore / ".gitignore").write_text("*\n", encoding="utf-8")
            gitignore_result = grade(gitignore)
            self.assertNotEqual(gitignore_result.returncode, 0, gitignore_result.stdout)
            self.assertIn(".gitignore", gitignore_result.stderr)

            empty_dir = root / "empty-dir"
            empty_dir.mkdir()
            for path in subject.rglob("*"):
                if path.is_file():
                    dest = empty_dir / path.relative_to(subject)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(path.read_bytes())
            (empty_dir / "notes").mkdir()
            empty_result = grade(empty_dir)
            self.assertNotEqual(empty_result.returncode, 0, empty_result.stdout)
            self.assertIn("notes", empty_result.stderr)

            directory_link = root / "directory-link"
            directory_link.mkdir()
            for path in subject.rglob("*"):
                if path.is_file():
                    dest = directory_link / path.relative_to(subject)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(path.read_bytes())
            secret = root / "secret-target"
            secret.mkdir()
            (secret / "secret-plan.md").write_text("plan\n", encoding="utf-8")
            (directory_link / ".atlas-mount").symlink_to(
                secret, target_is_directory=True
            )
            directory_result = grade(directory_link)
            self.assertNotEqual(
                directory_result.returncode, 0, directory_result.stdout
            )
            self.assertIn(".atlas-mount", directory_result.stderr)
            self.assertNotIn("secret-plan.md", directory_result.stderr)

            file_link = root / "file-link"
            file_link.mkdir()
            for path in subject.rglob("*"):
                if path.is_file():
                    dest = file_link / path.relative_to(subject)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(path.read_bytes())
            (file_link / "notes.md").symlink_to("SKILL.md")
            file_link_result = grade(file_link)
            self.assertNotEqual(
                file_link_result.returncode, 0, file_link_result.stdout
            )
            self.assertIn("notes.md", file_link_result.stderr)

            dangling = root / "dangling"
            dangling.mkdir()
            for path in subject.rglob("*"):
                if path.is_file():
                    dest = dangling / path.relative_to(subject)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(path.read_bytes())
            (dangling / "missing-link").symlink_to("nowhere")
            dangling_result = grade(dangling)
            self.assertNotEqual(
                dangling_result.returncode, 0, dangling_result.stdout
            )
            self.assertIn("missing-link", dangling_result.stderr)

            replaced = root / "replaced"
            replaced.mkdir()
            for path in subject.rglob("*"):
                if path.is_file():
                    dest = replaced / path.relative_to(subject)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(path.read_bytes())
            (replaced / "SKILL.md").unlink()
            (replaced / "SKILL.md").symlink_to("atlas-mesh.json")
            replaced_result = grade(replaced)
            self.assertNotEqual(
                replaced_result.returncode, 0, replaced_result.stdout
            )
            self.assertIn("SKILL.md", replaced_result.stderr)

            fifo = root / "fifo"
            fifo.mkdir()
            for path in subject.rglob("*"):
                if path.is_file():
                    dest = fifo / path.relative_to(subject)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(path.read_bytes())
            os.mkfifo(fifo / "pipe")
            fifo_result = grade(fifo)
            self.assertNotEqual(fifo_result.returncode, 0, fifo_result.stdout)
            self.assertIn("pipe", fifo_result.stderr)

            git_link = root / "git-link"
            git_link.mkdir()
            for path in subject.rglob("*"):
                if path.is_file():
                    dest = git_link / path.relative_to(subject)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(path.read_bytes())
            (git_link / ".git").symlink_to(".", target_is_directory=True)
            git_link_result = grade(git_link)
            self.assertNotEqual(
                git_link_result.returncode, 0, git_link_result.stdout
            )
            self.assertIn(".git", git_link_result.stderr)

        missing_env = os.environ.copy()
        missing_env.pop("WAZA_WORKSPACE_DIR", None)
        unset = subprocess.run(
            ["python3", str(self._allowlist_script()), "--baseline", baseline],
            cwd=ROOT,
            env=missing_env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(unset.returncode, 0, unset.stdout)
        self.assertIn("WAZA_WORKSPACE_DIR", unset.stderr)

        with tempfile.TemporaryDirectory() as elsewhere:
            missing_baseline = subprocess.run(
                [
                    "python3",
                    str(self._allowlist_script()),
                    "--baseline",
                    baseline,
                ],
                cwd=elsewhere,
                env={**os.environ, "WAZA_WORKSPACE_DIR": str(subject)},
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(
                missing_baseline.returncode, 0, missing_baseline.stdout
            )
            self.assertIn("baseline not found", missing_baseline.stderr)

    def _record_script(self) -> Path:
        return ROOT / ".apm/evals/autogenesis/graders/atlas_record_check.py"

    def _copy_fixture(self, source: Path, dest: Path) -> None:
        dest.mkdir(parents=True, exist_ok=True)
        for dirpath, dirnames, filenames in os.walk(source, followlinks=False):
            current = dest / Path(dirpath).relative_to(source)
            current.mkdir(parents=True, exist_ok=True)
            for name in list(dirnames) + list(filenames):
                child = Path(dirpath) / name
                if child.is_symlink() or not (child.is_dir() or child.is_file()):
                    self.fail(f"committed fixture contains a non-regular path: {child}")
            for name in filenames:
                (current / name).write_bytes((Path(dirpath) / name).read_bytes())

    def _allowlist_script(self) -> Path:
        return (
            ROOT / ".apm/evals/autogenesis/graders/workspace_allowlist.py"
        )

    def _grade_allowlist(
        self,
        workspace: Path,
        baseline: str,
        allow: tuple[str, ...] = (),
        cwd: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        command = [
            "python3",
            str(self._allowlist_script()),
            "--baseline",
            baseline,
        ]
        for path in allow:
            command.extend(["--allow", path])
        return subprocess.run(
            command,
            cwd=ROOT if cwd is None else cwd,
            env={**os.environ, "WAZA_WORKSPACE_DIR": str(workspace)},
            capture_output=True,
            text=True,
            check=False,
        )

    def _grade_task_allowlist(
        self,
        task_id: str,
        workspace: Path,
    ) -> subprocess.CompletedProcess[str]:
        yaml = self._require_yaml()
        task = yaml.safe_load(
            (
                ROOT / ".apm/evals/autogenesis/tasks" / f"{task_id}.yaml"
            ).read_text(encoding="utf-8")
        )
        grader = next(
            item
            for item in task["graders"]
            if item["name"] == "workspace_allowlist"
        )
        return subprocess.run(
            [grader["config"]["command"], *grader["config"]["args"]],
            cwd=ROOT,
            env={**os.environ, "WAZA_WORKSPACE_DIR": str(workspace)},
            capture_output=True,
            text=True,
            check=False,
        )

    def _grade_program(
        self,
        task_name: str,
        workspace: Path,
        index: int = 0,
        args: tuple[str, ...] = (),
    ) -> subprocess.CompletedProcess[str]:
        del task_name, index
        return subprocess.run(
            ["python3", str(self._record_script()), *args],
            cwd=ROOT,
            env={**os.environ, "WAZA_WORKSPACE_DIR": str(workspace)},
            capture_output=True,
            text=True,
            check=False,
        )

    def test_every_task_references_the_shared_workspace_check(self) -> None:
        yaml = self._require_yaml()
        script = self._allowlist_script()
        self.assertTrue(script.is_file())
        text = script.read_text(encoding="utf-8")
        self.assertIn("os.lstat", text)
        self.assertIn("followlinks=False", text)
        self.assertIn("O_NOFOLLOW", text)
        self.assertIn('"symlink"', text)
        self.assertIn("hashlib.sha256", text)
        self.assertNotIn("followlinks=True", text)
        self.assertNotIn("os.walk(root, followlinks=True", text)
        store = ".atlas/example.invalid/fixtures/retry-helper-atlas"
        experiences = store + "/autogenesis/experiences"
        plans_index = store + "/autogenesis/plans/index.md"
        work_index = store + "/autogenesis/work/index.md"
        experiences_index = experiences + "/index.md"
        log = store + "/log.md"
        dated_plan = store + "/autogenesis/plans/{date}-add-retry-note.md"
        dated_work = store + "/autogenesis/work/{date}-add-retry-note.md"
        genesis_plan = (
            store + "/autogenesis/plans/{date}-retry-backoff-guidance.md"
        )
        genesis_work = (
            store + "/autogenesis/work/{date}-retry-backoff-guidance.md"
        )
        plans_dir = store + "/autogenesis/plans"
        work_dir = store + "/autogenesis/work"
        indexes = (experiences_index, plans_index, work_index)
        design_owned = (
            ".apm/evals/autogenesis/fixtures/subjects/subject",
            (),
            (experiences,),
            indexes,
            (log,),
            (dated_plan, dated_work),
            False,
        )
        expected = {
            "design-stops-for-approval": design_owned,
            "discussion-has-no-implement-authority": design_owned,
            "implement-blocks-without-approval": (
                ".apm/evals/autogenesis/fixtures/subjects/subject-designed",
                (),
                (),
                (),
                (),
                (),
                False,
            ),
            "plan-only-in-resolved-atlas": (
                ".apm/evals/autogenesis/fixtures/subjects/subject-legacy",
                (),
                (experiences,),
                indexes,
                (log,),
                (dated_plan, dated_work),
                False,
            ),
            "declined-plan-path-explained": (
                ".apm/evals/autogenesis/fixtures/subjects/subject-legacy",
                (),
                (experiences,),
                indexes,
                (log,),
                (dated_plan, dated_work),
                False,
            ),
            "just-discuss-does-not-start-design": (
                ".apm/evals/autogenesis/fixtures/subjects/subject",
                (),
                (),
                (),
                (),
                (),
                False,
            ),
            "help-does-not-mount": (
                ".apm/evals/autogenesis/fixtures/subjects/subject-unmounted",
                (),
                (),
                (),
                (),
                (),
                False,
            ),
            "ordinary-refactor-near-miss": (
                ".apm/evals/autogenesis/fixtures/subjects/python-app",
                ("app/durations.py",),
                (),
                (),
                (),
                (),
                True,
            ),
            "skill-change-should-trigger": (
                ".apm/evals/autogenesis/fixtures/subjects/subject",
                (),
                (plans_dir, work_dir, experiences),
                indexes,
                (log,),
                (),
                False,
            ),
            "agreed-change-activates-autogenesis": (
                ".apm/evals/autogenesis/fixtures/subjects/subject",
                (),
                (plans_dir, work_dir, experiences),
                indexes,
                (log,),
                (),
                False,
            ),
            "skill-mention-near-miss": (
                ".apm/evals/autogenesis/fixtures/subjects/subject",
                (),
                (),
                (),
                (),
                (),
                False,
            ),
            "plan-has-genesis-artifacts": (
                ".apm/evals/autogenesis/fixtures/subjects/subject",
                (),
                (experiences,),
                indexes,
                (log,),
                (genesis_plan, genesis_work),
                False,
            ),
        }
        suite = ROOT / ".apm/evals/autogenesis/tasks"
        self.assertEqual({path.stem for path in suite.glob("*.yaml")}, set(expected))
        relative_script = ".apm/evals/autogenesis/graders/workspace_allowlist.py"
        for task_id, (
            baseline,
            allow,
            allow_under,
            allow_modify,
            allow_append,
            allow_dated,
            bytecode,
        ) in expected.items():
            with self.subTest(task=task_id):
                task = yaml.safe_load(
                    (suite / f"{task_id}.yaml").read_text(encoding="utf-8")
                )
                matches = [
                    grader
                    for grader in task["graders"]
                    if grader["name"] == "workspace_allowlist"
                ]
                self.assertEqual(len(matches), 1)
                grader = matches[0]
                self.assertEqual(grader["type"], "program")
                args = grader["config"]["args"]
                self.assertEqual(args[0], relative_script)
                self.assertEqual(grader["config"]["command"], "python3")
                self.assertNotIn("-c", args)
                parsed_baseline = None
                parsed_allow = []
                parsed_under = []
                parsed_modify = []
                parsed_append = []
                parsed_dated = []
                parsed_bytecode = False
                index = 1
                while index < len(args):
                    if args[index] == "--baseline":
                        self.assertIsNone(parsed_baseline)
                        parsed_baseline = args[index + 1]
                        index += 2
                        continue
                    if args[index] == "--allow":
                        parsed_allow.append(args[index + 1])
                        index += 2
                        continue
                    if args[index] == "--allow-under":
                        parsed_under.append(args[index + 1])
                        index += 2
                        continue
                    if args[index] == "--allow-modify":
                        parsed_modify.append(args[index + 1])
                        index += 2
                        continue
                    if args[index] == "--allow-log-entry":
                        parsed_append.append(args[index + 1])
                        index += 2
                        continue
                    if args[index] == "--allow-dated":
                        parsed_dated.append(args[index + 1])
                        index += 2
                        continue
                    if args[index] == "--allow-bytecode":
                        parsed_bytecode = True
                        index += 1
                        continue
                    self.fail(f"unexpected allowlist argument {args[index]}")
                self.assertEqual(parsed_baseline, baseline)
                self.assertEqual(tuple(parsed_allow), allow)
                self.assertEqual(tuple(parsed_under), allow_under)
                self.assertEqual(tuple(parsed_modify), allow_modify)
                self.assertEqual(tuple(parsed_append), allow_append)
                self.assertEqual(tuple(parsed_dated), allow_dated)
                self.assertEqual(parsed_bytecode, bytecode)
                self.assertNotIn(
                    "diff",
                    [item["type"] for item in task["graders"]],
                )

    def test_shared_allowlist_accepts_references_and_rejects_unrelated_files(
        self,
    ) -> None:
        suite = ROOT / ".apm/evals/autogenesis"
        unrelated = {
            "design-stops-for-approval": "retry-note.md",
            "discussion-has-no-implement-authority": "atlas-mesh.json",
            "implement-blocks-without-approval": "retry-note.md",
        }
        for path in sorted((suite / "tasks").glob("*.yaml")):
            reference = suite / "fixtures" / path.stem / "reference"
            passed = self._grade_task_allowlist(path.stem, reference)
            self.assertEqual(passed.returncode, 0, path.stem + " " + passed.stderr)
        for task_id, marker in unrelated.items():
            with self.subTest(task=task_id):
                variant = suite / "fixtures" / task_id / "negative-unrelated-file"
                self.assertTrue(variant.is_dir())
                self.assertTrue(
                    (variant.parent / "negative-unrelated-file.results.json").is_file()
                )
                failed = self._grade_task_allowlist(task_id, variant)
                self.assertNotEqual(failed.returncode, 0, failed.stdout)
                self.assertIn(marker, failed.stderr)

    def test_trigger_allowlist_accepts_the_correct_change_only(self) -> None:
        near_miss = (
            ROOT / ".apm/evals/autogenesis/fixtures/subjects/python-app"
        )
        skill = ROOT / ".apm/evals/autogenesis/fixtures/subjects/subject"
        plans = (
            ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis/plans"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            refactored = root / "refactored"
            self._copy_fixture(near_miss, refactored)
            durations = refactored / "app/durations.py"
            original = durations.read_bytes()
            durations.write_text(
                original.decode("utf-8").replace(
                    "return value * 60",
                    "return value * 60  # same minute length",
                ),
                encoding="utf-8",
            )
            self.assertNotEqual(durations.read_bytes(), original)
            passed = self._grade_task_allowlist(
                "ordinary-refactor-near-miss", refactored
            )
            self.assertEqual(passed.returncode, 0, passed.stderr)

            cached = root / "cached"
            self._copy_fixture(refactored, cached)
            cache = cached / "app/__pycache__"
            cache.mkdir()
            (cache / "durations.cpython-313.pyc").write_bytes(b"\x00bytecode")
            cached_passed = self._grade_task_allowlist(
                "ordinary-refactor-near-miss", cached
            )
            self.assertEqual(cached_passed.returncode, 0, cached_passed.stderr)

            extra = root / "extra-file"
            self._copy_fixture(refactored, extra)
            (extra / "notes.txt").write_text("unrelated\n", encoding="utf-8")
            failed_extra = self._grade_task_allowlist(
                "ordinary-refactor-near-miss", extra
            )
            self.assertNotEqual(failed_extra.returncode, 0, failed_extra.stdout)
            self.assertIn("notes.txt", failed_extra.stderr)

            dirty_cache = root / "dirty-cache"
            self._copy_fixture(cached, dirty_cache)
            (dirty_cache / "app/__pycache__/notes.txt").write_text(
                "not bytecode\n", encoding="utf-8"
            )
            failed_cache = self._grade_task_allowlist(
                "ordinary-refactor-near-miss", dirty_cache
            )
            self.assertNotEqual(failed_cache.returncode, 0, failed_cache.stdout)
            self.assertIn("notes.txt", failed_cache.stderr)

            linked_pyc = root / "linked-pyc"
            self._copy_fixture(refactored, linked_pyc)
            outside_pyc = root / "outside.pyc"
            outside_pyc.write_bytes(b"\x00bytecode")
            link = linked_pyc / "app/__pycache__"
            link.mkdir()
            (link / "durations.cpython-313.pyc").symlink_to(outside_pyc)
            failed_pyc_link = self._grade_task_allowlist(
                "ordinary-refactor-near-miss", linked_pyc
            )
            self.assertNotEqual(
                failed_pyc_link.returncode, 0, failed_pyc_link.stdout
            )
            self.assertIn("durations.cpython-313.pyc (symlink)", failed_pyc_link.stderr)

            planned = root / "planned"
            self._copy_fixture(skill, planned)
            plan = planned / plans / "2026-10-11-agent-chosen.md"
            plan.write_text(
                "---\nstatus: designed\n---\n\n# Plan\n", encoding="utf-8"
            )
            work = (
                planned
                / ".atlas/example.invalid/fixtures/retry-helper-atlas"
                / "autogenesis/work/2026-10-11-agent-chosen.md"
            )
            work.write_text(
                "---\nstatus: designed\n---\n\n# Work\n", encoding="utf-8"
            )
            passed_plan = self._grade_task_allowlist(
                "skill-change-should-trigger", planned
            )
            self.assertEqual(passed_plan.returncode, 0, passed_plan.stderr)

            elsewhere = root / "elsewhere"
            self._copy_fixture(skill, elsewhere)
            sibling = (
                elsewhere
                / ".atlas/example.invalid/fixtures/retry-helper-atlas"
                / "autogenesis/plans-extra"
            )
            sibling.mkdir()
            (sibling / "note.md").write_text("not a plan\n", encoding="utf-8")
            failed_elsewhere = self._grade_task_allowlist(
                "skill-change-should-trigger", elsewhere
            )
            self.assertNotEqual(
                failed_elsewhere.returncode, 0, failed_elsewhere.stdout
            )
            self.assertIn("plans-extra/note.md", failed_elsewhere.stderr)

            linked = root / "linked"
            self._copy_fixture(skill, linked)
            outside_plan = root / "outside-plan.md"
            outside_plan.write_text("not in the store\n", encoding="utf-8")
            (linked / plans / "linked-plan.md").symlink_to(outside_plan)
            failed_link = self._grade_task_allowlist(
                "skill-change-should-trigger", linked
            )
            self.assertNotEqual(failed_link.returncode, 0, failed_link.stdout)
            self.assertIn("linked-plan.md is a symlink", failed_link.stderr)

    def test_allowlist_rejects_a_symlink_on_an_allowed_plan_path(self) -> None:
        task_id = "plan-has-genesis-artifacts"
        suite = ROOT / ".apm/evals/autogenesis/fixtures" / task_id
        plan = (
            ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis"
            "/plans/2026-10-08-retry-backoff-guidance.md"
        )
        for variant in ("reference", "reference-heading"):
            with self.subTest(variant=variant, kind="reference"):
                passed = self._grade_task_allowlist(task_id, suite / variant)
                self.assertEqual(
                    passed.returncode, 0, variant + " " + passed.stderr
                )
        for kind in ("leaf", "parent"):
            with self.subTest(kind=kind):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    variant = root / "workspace"
                    self._copy_fixture(suite / "reference", variant)
                    source = variant / plan
                    self.assertTrue(source.is_file())
                    self.assertFalse(source.is_symlink())
                    if kind == "leaf":
                        outside = root / "outside-plan.md"
                        outside.write_bytes(source.read_bytes())
                        source.unlink()
                        source.symlink_to(outside)
                        expected = plan
                    else:
                        replaced = source.parent
                        expected = Path(plan).parent.as_posix()
                        relocated = root / "outside-plans"
                        replaced.rename(relocated)
                        replaced.symlink_to(
                            relocated, target_is_directory=True
                        )
                    followed = (variant / plan).read_text(encoding="utf-8")
                    self.assertIn("## Genesis Artifacts", followed)
                    failed = self._grade_task_allowlist(task_id, variant)
                self.assertNotEqual(failed.returncode, 0, failed.stdout)
                self.assertIn(expected + " is a symlink", failed.stderr)

    def test_repository_tracks_no_symlinks(self) -> None:
        listed = subprocess.run(
            ["git", "ls-files", "-s"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        symlinks = [
            line for line in listed.stdout.splitlines() if line.startswith("120000 ")
        ]
        self.assertEqual(symlinks, [])

    def test_tracked_symlink_is_rejected_anywhere(self) -> None:
        import audit_source

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            (root / "file.txt").write_text("x\n", encoding="utf-8")
            (root / "link").symlink_to("file.txt")
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            with self.assertRaises(audit_source.SourceAuditError) as caught:
                audit_source.tracked_files(root)
            self.assertIn(
                "link: tracked symbolic links are not auditable",
                str(caught.exception),
            )
            nested = root / ".apm" / "evals" / "example"
            nested.mkdir(parents=True)
            (nested / "mount").symlink_to(".", target_is_directory=True)
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            with self.assertRaises(audit_source.SourceAuditError) as nested_caught:
                audit_source.tracked_files(root)
            self.assertIn(
                ".apm/evals/example/mount: tracked symbolic links are not auditable",
                str(nested_caught.exception),
            )

    def test_help_directory_symlink_negative_is_constructed_at_test_time(
        self,
    ) -> None:
        base = (
            ROOT
            / ".apm/evals/autogenesis/fixtures/help-does-not-mount/reference"
        )
        baseline = (
            ".apm/evals/autogenesis/fixtures/subjects/subject-unmounted"
        )
        passed = self._grade_allowlist(base, baseline)
        self.assertEqual(passed.returncode, 0, passed.stderr)
        with tempfile.TemporaryDirectory() as tmp:
            variant = Path(tmp) / "negative-directory-symlink"
            self._copy_fixture(base, variant)
            link = variant / ".atlas-mount"
            link.symlink_to(".", target_is_directory=True)
            self.assertEqual(os.readlink(link), ".")
            failed = self._grade_allowlist(variant, baseline)
        self.assertNotEqual(failed.returncode, 0, failed.stdout)
        self.assertIn(".atlas-mount", failed.stderr)
        self.assertNotIn("secret-plan.md", failed.stderr)

    def test_legacy_symlink_negative_is_constructed_at_test_time(
        self,
    ) -> None:
        base = (
            ROOT
            / ".apm/evals/autogenesis/fixtures/plan-only-in-resolved-atlas"
            / "reference"
        )
        baseline = ".apm/evals/autogenesis/fixtures/subjects/subject-legacy"
        allow = (
            ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis"
            "/plans/2026-10-08-add-retry-note.md",
            ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis"
            "/work/2026-10-08-add-retry-note.md",
        )
        passed = self._grade_allowlist(base, baseline, allow)
        self.assertEqual(passed.returncode, 0, passed.stderr)
        plan = (
            ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis"
            "/plans/2026-10-08-add-retry-note.md"
        )
        relative = "references/atlas/autogenesis"
        target = (
            "../../.atlas/example.invalid/fixtures/"
            "retry-helper-atlas/autogenesis"
        )
        with tempfile.TemporaryDirectory() as tmp:
            variant = Path(tmp) / "negative-legacy-symlink"
            self._copy_fixture(base, variant)
            link = variant / relative
            link.symlink_to(target, target_is_directory=True)
            self.assertEqual(os.readlink(link), target)
            self.assertEqual(
                (variant / plan).read_bytes(),
                (base / plan).read_bytes(),
            )
            self.assertTrue((link / "plans/2026-10-08-add-retry-note.md").is_file())
            failed = self._grade_allowlist(variant, baseline, allow)
        self.assertNotEqual(failed.returncode, 0, failed.stdout)
        self.assertIn("autogenesis", failed.stderr)
        self.assertNotIn("2026-10-08-add-retry-note.md", failed.stderr)

    def test_status_graders_reject_symlinks_to_a_designed_file(self) -> None:
        yaml = self._require_yaml()
        design_script = self._record_script().read_text(encoding="utf-8")
        relative = ".apm/evals/autogenesis/graders/atlas_record_check.py"
        for task_name in (
            "design-stops-for-approval.yaml",
            "implement-blocks-without-approval.yaml",
            "plan-only-in-resolved-atlas.yaml",
            "discussion-has-no-implement-authority.yaml",
            "plan-has-genesis-artifacts.yaml",
        ):
            task = yaml.safe_load(
                (
                    ROOT / ".apm/evals/autogenesis/tasks" / task_name
                ).read_text(encoding="utf-8")
            )
            checkers = [
                grader
                for grader in task["graders"]
                if grader["type"] == "program"
                and grader["name"] != "workspace_allowlist"
            ]
            self.assertTrue(checkers, task_name)
            for grader in checkers:
                self.assertEqual(grader["config"]["args"][0], relative)
                self.assertNotIn("-c", grader["config"]["args"])
        self.assertIn("os.lstat", design_script)
        self.assertIn("O_NOFOLLOW", design_script)
        plan = (
            ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis"
            "/plans/2026-10-08-add-retry-note.md"
        )
        work = (
            ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis"
            "/work/2026-10-08-add-retry-note.md"
        )
        cases = (
            (
                "design-stops-for-approval.yaml",
                0,
                "design-stops-for-approval",
                (plan, work),
                (plan, work),
            ),
            (
                "plan-only-in-resolved-atlas.yaml",
                0,
                "plan-only-in-resolved-atlas",
                (plan,),
                (plan,),
            ),
            (
                "discussion-has-no-implement-authority.yaml",
                0,
                "discussion-has-no-implement-authority",
                (plan, work),
                (plan, work),
            ),
        )
        for task, index, fixture, grade_args, targets in cases:
            base = ROOT / ".apm/evals/autogenesis/fixtures" / fixture / "reference"
            passed = self._grade_program(task, base, index, grade_args)
            self.assertEqual(passed.returncode, 0, passed.stderr)
            for target in targets:
                self._assert_status_symlink_fails(
                    task, index, base, grade_args, target, "leaf"
                )
                self._assert_status_symlink_fails(
                    task, index, base, grade_args, target, "parent"
                )
            self._assert_status_symlink_fails(
                task, index, base, grade_args, targets[0], "ancestor"
            )

    def _assert_status_symlink_fails(
        self,
        task: str,
        index: int,
        base: Path,
        grade_args: tuple[str, ...],
        target: str,
        kind: str,
    ) -> None:
        with self.subTest(task=task, target=target, kind=kind):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                variant = root / "workspace"
                self._copy_fixture(base, variant)
                source = variant / target
                self.assertTrue(source.is_file())
                self.assertIn(
                    "status: designed\n",
                    source.read_text(encoding="utf-8"),
                )
                if kind == "leaf":
                    outside = root / "outside-designed.md"
                    outside.write_bytes(source.read_bytes())
                    source.unlink()
                    source.symlink_to(outside)
                    expected = target
                elif kind == "parent":
                    replaced = variant / Path(target).parent
                    expected = Path(target).parent.as_posix()
                    relocated = root / "outside-parent"
                    replaced.rename(relocated)
                    replaced.symlink_to(relocated, target_is_directory=True)
                elif kind == "ancestor":
                    replaced = variant / ".atlas"
                    expected = ".atlas"
                    relocated = root / "outside-atlas"
                    replaced.rename(relocated)
                    replaced.symlink_to(relocated, target_is_directory=True)
                else:
                    self.fail(kind)
                followed = (variant / target).read_text(encoding="utf-8")
                self.assertIn("status: designed\n", followed)
                failed = self._grade_program(task, variant, index, grade_args)
            self.assertNotEqual(failed.returncode, 0, failed.stdout)
            self.assertIn(expected + " is a symlink", failed.stderr)
            self.assertNotIn("status is", failed.stderr)

    def test_discussion_no_plan_negative_does_not_start_design(self) -> None:
        task = "discussion-has-no-implement-authority.yaml"
        yaml = self._require_yaml()
        relative = ".apm/evals/autogenesis/graders/atlas_record_check.py"
        for task_name in (task, "design-stops-for-approval.yaml"):
            loaded = yaml.safe_load(
                (
                    ROOT / ".apm/evals/autogenesis/tasks" / task_name
                ).read_text(encoding="utf-8")
            )
            checker = next(
                grader
                for grader in loaded["graders"]
                if grader["name"] == "plan_status_not_advanced"
            )
            self.assertEqual(checker["config"]["args"][0], relative)
        plan = (
            ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis"
            "/plans/2026-10-08-add-retry-note.md"
        )
        work = (
            ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis"
            "/work/2026-10-08-add-retry-note.md"
        )
        base = (
            ROOT
            / ".apm/evals/autogenesis/fixtures"
            / "discussion-has-no-implement-authority"
        )
        prompt = (
            ROOT / ".apm/evals/autogenesis/tasks" / task
        ).read_text(encoding="utf-8")
        self.assertIn("Use the work_id slug add-retry-note.", prompt)
        self.assertNotIn("work_id 2026-10-08-add-retry-note", prompt)
        passed = self._grade_program(task, base / "reference", 0, (plan, work))
        self.assertEqual(passed.returncode, 0, passed.stderr)
        missing = self._grade_program(
            task, base / "negative-no-plan", 0, (plan, work)
        )
        self.assertNotEqual(missing.returncode, 0, missing.stdout)
        self.assertIn("missing " + plan, missing.stderr)
        self.assertFalse((base / "negative-no-plan" / plan).exists())
        self.assertFalse((base / "negative-no-plan" / work).exists())
        no_plan = json.loads(
            (base / "negative-no-plan.results.json").read_text(encoding="utf-8")
        )
        output = no_plan["tasks"][0]["runs"][0]["final_output"]
        self.assertIn("I can start a formal Autogenesis design", output)
        reference = json.loads(
            (base / "reference.results.json").read_text(encoding="utf-8")
        )
        self.assertNotIn(
            "I can start",
            reference["tasks"][0]["runs"][0]["final_output"],
        )

    def test_record_checker_parses_indented_frontmatter(self) -> None:
        plan = (
            ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis"
            "/plans/2026-10-08-add-retry-note.md"
        )
        base = (
            ROOT
            / ".apm/evals/autogenesis/fixtures/design-stops-for-approval"
            / "reference"
            / plan
        ).read_text(encoding="utf-8")
        self.assertIn("status: designed\n", base)
        accepted = {
            "relates-to-list": (
                "relates_to:\n"
                "  - kind: implements\n"
                "    target: autogenesis/work/2026-10-11-add-retry-note.md\n"
                "status: designed\n"
            ),
            "nested-mapping-list": (
                "owner:\n"
                "  name: fixture\n"
                "  roles:\n"
                "    - author\n"
                "status: designed\n"
            ),
            "tags-flow": "tags: [a, b]\nstatus: designed\n",
            "description-block": (
                "description: |\n"
                "  several\n"
                "  lines\n"
                "status: designed\n"
            ),
            "status-after-block": (
                "notes:\n"
                "  indented block\n"
                "status: designed\n"
            ),
        }
        rejected = {
            "status-continuation": "status: designed\n  approved\n",
            "status-nested-only": "parent:\n  status: designed\n",
            "tab-indent": "title: note\n\tstatus: designed\n",
            "sequence-after-inline": "title: note\n- item\nstatus: designed\n",
            "continuation-before-key": "  early\nstatus: designed\n",
        }
        script = self._record_script()
        with tempfile.TemporaryDirectory() as tmp:
            for name, frontmatter in {**accepted, **rejected}.items():
                workspace = Path(tmp) / name
                dest = workspace / plan
                dest.parent.mkdir(parents=True)
                dest.write_text(
                    "---\n" + frontmatter + "---\nbody\n",
                    encoding="utf-8",
                )
                result = subprocess.run(
                    ["python3", str(script), plan],
                    env={**os.environ, "WAZA_WORKSPACE_DIR": str(workspace)},
                    capture_output=True,
                    text=True,
                    check=False,
                )
                with self.subTest(case=name):
                    if name in accepted:
                        self.assertEqual(result.returncode, 0, result.stderr)
                    else:
                        self.assertNotEqual(result.returncode, 0, result.stdout)

    def test_record_checker_resolves_one_shared_date(self) -> None:
        dated_plan = (
            ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis"
            "/plans/{date}-add-retry-note.md"
        )
        dated_work = (
            ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis"
            "/work/{date}-add-retry-note.md"
        )
        plan = dated_plan.replace("{date}", "2026-10-08")
        work = dated_work.replace("{date}", "2026-10-08")
        base = (
            ROOT
            / ".apm/evals/autogenesis/fixtures/design-stops-for-approval"
            / "reference"
        )
        script = self._record_script()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            resolved = root / "resolved"
            self._copy_fixture(base, resolved)
            passed = self._grade_program(
                "record", resolved, 0, (dated_plan, dated_work)
            )
            self.assertEqual(passed.returncode, 0, passed.stderr)
            self.assertIn("resolved:", passed.stdout)
            self.assertIn(plan, passed.stdout)
            self.assertIn(work, passed.stdout)

            missing = root / "missing"
            self._copy_fixture(base, missing)
            (missing / plan).unlink()
            failed = self._grade_program("record", missing, 0, (dated_plan,))
            self.assertNotEqual(failed.returncode, 0, failed.stdout)
            self.assertIn("missing " + dated_plan, failed.stderr)

            ambiguous = root / "ambiguous"
            self._copy_fixture(base, ambiguous)
            extra = ambiguous / plan.replace("2026-10-08", "2026-11-02")
            extra.write_bytes((ambiguous / plan).read_bytes())
            failed = self._grade_program("record", ambiguous, 0, (dated_plan,))
            self.assertNotEqual(failed.returncode, 0, failed.stdout)
            self.assertIn("ambiguous " + dated_plan, failed.stderr)

            invalid = root / "invalid-date"
            self._copy_fixture(base, invalid)
            (invalid / plan).unlink()
            (invalid / plan.replace("2026-10-08", "2026-13-40")).write_text(
                "---\nstatus: designed\n---\n",
                encoding="utf-8",
            )
            failed = self._grade_program("record", invalid, 0, (dated_plan,))
            self.assertNotEqual(failed.returncode, 0, failed.stdout)
            self.assertIn("missing " + dated_plan, failed.stderr)

            mismatch = root / "mismatch"
            self._copy_fixture(base, mismatch)
            shifted = mismatch / work.replace("2026-10-08", "2026-11-03")
            shifted.write_bytes((mismatch / work).read_bytes())
            (mismatch / work).unlink()
            failed = self._grade_program(
                "record", mismatch, 0, (dated_plan, dated_work)
            )
            self.assertNotEqual(failed.returncode, 0, failed.stdout)
            self.assertIn("dates differ", failed.stderr)

            linked = root / "symlink"
            self._copy_fixture(base, linked)
            source = linked / plan
            outside = root / "outside-plan.md"
            outside.write_bytes(source.read_bytes())
            source.unlink()
            source.symlink_to(outside)
            failed = self._grade_program("record", linked, 0, (dated_plan,))
            self.assertNotEqual(failed.returncode, 0, failed.stdout)
            self.assertIn(plan + " is a symlink", failed.stderr)

    def test_allow_modify_append_and_dated_fail_closed(self) -> None:
        subject = ROOT / ".apm/evals/autogenesis/fixtures/subjects/subject"
        baseline = ".apm/evals/autogenesis/fixtures/subjects/subject"
        store = ".atlas/example.invalid/fixtures/retry-helper-atlas"
        index = store + "/autogenesis/plans/index.md"
        log = store + "/log.md"
        dated = store + "/autogenesis/plans/{date}-add-retry-note.md"
        plan = dated.replace("{date}", "2026-11-02")

        def grade(workspace: Path, *flags: str) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [
                    "python3",
                    str(self._allowlist_script()),
                    "--baseline",
                    baseline,
                    *flags,
                ],
                cwd=ROOT,
                env={**os.environ, "WAZA_WORKSPACE_DIR": str(workspace)},
                capture_output=True,
                text=True,
                check=False,
            )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            changed = root / "changed-index"
            self._copy_fixture(subject, changed)
            target = changed / index
            target.write_text(target.read_text(encoding="utf-8") + "\n- added\n", encoding="utf-8")
            passed = grade(changed, "--allow-modify", index)
            self.assertEqual(passed.returncode, 0, passed.stderr)

            removed = root / "removed-index"
            self._copy_fixture(subject, removed)
            (removed / index).unlink()
            failed = grade(removed, "--allow-modify", index)
            self.assertNotEqual(failed.returncode, 0, failed.stdout)
            self.assertIn("missing " + index, failed.stderr)

            linked_index = root / "linked-index"
            self._copy_fixture(subject, linked_index)
            source = linked_index / index
            outside = root / "outside-index.md"
            outside.write_bytes(source.read_bytes())
            source.unlink()
            source.symlink_to(outside)
            failed = grade(linked_index, "--allow-modify", index)
            self.assertNotEqual(failed.returncode, 0, failed.stdout)
            self.assertIn(index + " is a symlink", failed.stderr)

            appended = root / "appended-log"
            self._copy_fixture(subject, appended)
            log_path = appended / log
            log_path.write_bytes(log_path.read_bytes() + b"\n- 2026-11-02: remembered.\n")
            passed = grade(appended, "--allow-log-entry", log)
            self.assertEqual(passed.returncode, 0, passed.stderr)

            rewritten = root / "rewritten-log"
            self._copy_fixture(subject, rewritten)
            (rewritten / log).write_text("# Log\n\n- rewritten\n", encoding="utf-8")
            failed = grade(rewritten, "--allow-log-entry", log)
            self.assertNotEqual(failed.returncode, 0, failed.stdout)
            self.assertIn("not an allowed log change: " + log, failed.stderr)

            added = root / "dated-plan"
            self._copy_fixture(subject, added)
            dest = added / plan
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text("---\nstatus: designed\n---\n", encoding="utf-8")
            passed = grade(added, "--allow-dated", dated)
            self.assertEqual(passed.returncode, 0, passed.stderr)

            linked_plan = root / "linked-plan"
            self._copy_fixture(subject, linked_plan)
            dest = linked_plan / plan
            dest.parent.mkdir(parents=True, exist_ok=True)
            outside_plan = root / "outside-plan.md"
            outside_plan.write_text("---\nstatus: designed\n---\n", encoding="utf-8")
            dest.symlink_to(outside_plan)
            failed = grade(linked_plan, "--allow-dated", dated)
            self.assertNotEqual(failed.returncode, 0, failed.stdout)
            self.assertIn(plan + " is a symlink", failed.stderr)

    def test_allow_log_entry_accepts_newest_first_and_rejects_other_edits(self) -> None:
        subject = ROOT / ".apm/evals/autogenesis/fixtures/subjects/subject"
        store = ".atlas/example.invalid/fixtures/retry-helper-atlas"
        log = store + "/log.md"
        baseline_flag = ".apm/evals/autogenesis/fixtures/subjects/subject"
        original = (subject / log).read_bytes()
        self.assertTrue(original.startswith(b"# Log\n"))
        self.assertFalse(original.endswith(b"\n\n"))
        entry = b"- 2026-10-11: opened design work; plan awaits approval.\n"

        def grade(
            workspace: Path, baseline: str = baseline_flag
        ) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [
                    "python3",
                    str(self._allowlist_script()),
                    "--baseline",
                    baseline,
                    "--allow-log-entry",
                    log,
                ],
                cwd=ROOT,
                env={**os.environ, "WAZA_WORKSPACE_DIR": str(workspace)},
                capture_output=True,
                text=True,
                check=False,
            )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            def workspace_with(
                name: str, content: bytes, source: Path = subject
            ) -> Path:
                dest = root / name
                self._copy_fixture(source, dest)
                (dest / log).write_bytes(content)
                return dest

            # Newest-first: one contiguous block after the blank line under # Log.
            newest = b"# Log\n\n" + entry + original.split(b"\n", 2)[2]
            self.assertTrue(newest.startswith(b"# Log\n\n" + entry))
            self.assertIn(original.split(b"\n", 2)[2], newest)
            passed = grade(workspace_with("newest", newest))
            self.assertEqual(passed.returncode, 0, passed.stderr)

            # Immediately after the heading, before the blank line that follows it.
            before_blank = b"# Log\n" + entry + b"\n" + original.split(b"\n", 2)[2]
            passed = grade(workspace_with("before-blank", before_blank))
            self.assertEqual(passed.returncode, 0, passed.stderr)

            two_blank_base = root / "two-blank-baseline"
            self._copy_fixture(subject, two_blank_base)
            body = original.split(b"\n", 2)[2]
            two_blank = b"# Log\n\n\n" + body
            (two_blank_base / log).write_bytes(two_blank)
            after_blanks = b"# Log\n\n\n" + entry + body
            between_blanks = b"# Log\n\n" + entry + b"\n" + body
            passed = grade(
                workspace_with("after-blanks", after_blanks, two_blank_base),
                str(two_blank_base),
            )
            self.assertEqual(passed.returncode, 0, passed.stderr)
            failed = grade(
                workspace_with("between-blanks", between_blanks, two_blank_base),
                str(two_blank_base),
            )
            self.assertNotEqual(failed.returncode, 0, failed.stdout)
            self.assertIn("not an allowed log change: " + log, failed.stderr)

            space_base = root / "space-blank-baseline"
            self._copy_fixture(subject, space_base)
            (space_base / log).write_bytes(b"# Log\n \n" + body)
            passed = grade(
                workspace_with("after-space", b"# Log\n \n" + entry + body, space_base),
                str(space_base),
            )
            self.assertEqual(passed.returncode, 0, passed.stderr)

            above = entry + b"\n" + original
            failed = grade(workspace_with("above", above))
            self.assertNotEqual(failed.returncode, 0, failed.stdout)
            self.assertIn("not an allowed log change: " + log, failed.stderr)

            two_entry_base = root / "two-entry-baseline"
            self._copy_fixture(subject, two_entry_base)
            trailing = b"- trailing line that must stay last.\n"
            (two_entry_base / log).write_bytes(original + trailing)
            mid = original + entry + trailing
            failed = grade(
                workspace_with("mid", mid, two_entry_base), str(two_entry_base)
            )
            self.assertNotEqual(failed.returncode, 0, failed.stdout)
            self.assertIn("not an allowed log change: " + log, failed.stderr)

            edited = (
                b"# Log\n\n"
                + entry
                + b"- 2026-10-08: fixture store was edited after creation.\n"
            )
            failed = grade(workspace_with("edited", edited))
            self.assertNotEqual(failed.returncode, 0, failed.stdout)
            self.assertIn("not an allowed log change: " + log, failed.stderr)

            removed = root / "removed"
            self._copy_fixture(subject, removed)
            (removed / log).unlink()
            failed = grade(removed)
            self.assertNotEqual(failed.returncode, 0, failed.stdout)
            self.assertIn("missing " + log, failed.stderr)

            no_heading_base = root / "no-heading-baseline"
            self._copy_fixture(subject, no_heading_base)
            no_heading = b"Notes\n\n- keep this line.\n"
            (no_heading_base / log).write_bytes(no_heading)
            passed = grade(
                workspace_with(
                    "no-heading-append",
                    no_heading + b"- added at the end.\n",
                    no_heading_base,
                ),
                str(no_heading_base),
            )
            self.assertEqual(passed.returncode, 0, passed.stderr)
            failed = grade(
                workspace_with(
                    "no-heading-insert",
                    b"Notes\n\n- inserted.\n- keep this line.\n",
                    no_heading_base,
                ),
                str(no_heading_base),
            )
            self.assertNotEqual(failed.returncode, 0, failed.stdout)
            self.assertIn("not an allowed log change: " + log, failed.stderr)

            bare_base = root / "bare-baseline"
            self._copy_fixture(subject, bare_base)
            bare = original[:-1] if original.endswith(b"\n") else original
            self.assertFalse(bare.endswith(b"\n"))
            (bare_base / log).write_bytes(bare)
            passed = grade(
                workspace_with("bare-newest", b"# Log\n\n" + entry + bare.split(b"\n", 2)[2] + b"\n", bare_base),
                str(bare_base),
            )
            self.assertEqual(passed.returncode, 0, passed.stderr)
            failed = grade(
                workspace_with("bare-extended", bare + b" extra", bare_base),
                str(bare_base),
            )
            self.assertNotEqual(failed.returncode, 0, failed.stdout)
            self.assertIn("not an allowed log change: " + log, failed.stderr)

        suite = ROOT / ".apm/evals/autogenesis/fixtures/design-stops-for-approval"
        remembered = self._grade_task_allowlist(
            "design-stops-for-approval", suite / "reference-log-newest-first"
        )
        self.assertEqual(remembered.returncode, 0, remembered.stderr)
        self.assertTrue((suite / "reference-log-newest-first.results.json").is_file())
        for variant in ("negative-log-insert-middle", "negative-log-edited-line"):
            with self.subTest(variant=variant):
                failed = self._grade_task_allowlist(
                    "design-stops-for-approval", suite / variant
                )
                self.assertNotEqual(failed.returncode, 0, failed.stdout)
                self.assertIn("not an allowed log change: " + log, failed.stderr)
                self.assertTrue((suite / f"{variant}.results.json").is_file())

    def test_declined_path_reply_names_the_written_plan_and_refuses(self) -> None:
        yaml = self._require_yaml()
        task = yaml.safe_load(
            (
                ROOT
                / ".apm/evals/autogenesis/tasks/declined-plan-path-explained.yaml"
            ).read_text(encoding="utf-8")
        )
        grader = next(
            item for item in task["graders"] if item["name"] == "named_path_explained"
        )
        self.assertEqual(grader["type"], "program")
        self.assertEqual(grader["config"]["command"], "python3")
        self.assertEqual(grader["config"]["timeout"], 30)
        args = grader["config"]["args"]
        self.assertEqual(
            args[0], ".apm/evals/autogenesis/graders/reply_path_check.py"
        )
        self.assertNotIn("-c", args)
        self.assertNotIn("import os", "\n".join(args))
        script = ROOT / args[0]
        source = script.read_text(encoding="utf-8")
        self.assertIn("sys.stdin.buffer.read", source)
        self.assertIn("WAZA_WORKSPACE_DIR", source)
        import importlib.util
        import sys

        write_bytecode = sys.dont_write_bytecode
        sys.dont_write_bytecode = True
        try:
            loaded = importlib.util.spec_from_file_location(
                "reply_path_check", script
            )
            self.assertIsNotNone(loaded)
            self.assertIsNotNone(loaded.loader)
            module = importlib.util.module_from_spec(loaded)
            loaded.loader.exec_module(module)
        finally:
            sys.dont_write_bytecode = write_bytecode
            cache = script.parent / "__pycache__"
            if cache.exists():
                for child in cache.iterdir():
                    child.unlink()
                cache.rmdir()
        self.assertFalse(hasattr(module, "POSITIVE_USE_PATTERN"))
        self.assertFalse(hasattr(module, "SENTENCE_LOOKBACK"))
        self.assertFalse(hasattr(module, "USE_PATH_WORD_WINDOW"))
        self.assertEqual(module.VERB_CUE_WORDS, 3)
        self.assertEqual(module.PATH_GAP_WORDS, 3)
        self.assertEqual(
            module.USE_VERBS,
            (
                "use",
                "uses",
                "used",
                "using",
                "write",
                "writes",
                "wrote",
                "writing",
                "written",
                "save",
                "saves",
                "saved",
                "saving",
                "store",
                "stores",
                "stored",
                "storing",
                "put",
                "puts",
                "putting",
                "keep",
                "keeps",
                "kept",
                "keeping",
                "persist",
                "persists",
                "persisted",
                "persisting",
                "place",
                "places",
                "placed",
                "placing",
                "move",
                "moves",
                "moved",
                "moving",
            ),
        )
        self.assertEqual(
            module.CLAUSE_WORDS,
            ("but", "however", "although", "though", "yet", "so"),
        )
        self.assertEqual(
            module.SINGLE_WORD_CUES,
            frozenset(
                {
                    "not",
                    "never",
                    "cannot",
                    "wont",
                    "didnt",
                    "dont",
                    "cant",
                    "avoid",
                    "avoided",
                }
            ),
        )
        self.assertEqual(
            module.PAIR_CUES,
            frozenset(
                {
                    "no longer",
                    "refuse to",
                    "refused to",
                    "declined to",
                }
            ),
        )
        self.assertNotIn("(?<=", source)
        self.assertNotIn("(?<!", source)
        patterns = (
            *module.REFUSAL_PATTERNS,
            module.REASON_PATTERN,
            module.USE_VERB_PATTERN,
            module.NAMED_PATH_PATTERN,
            module.PASSIVE_REFUSAL_PATTERN,
            module.INSTEAD_BEFORE_PATH_PATTERN,
            module.CLAUSE_BOUNDARY_PATTERN,
        )
        for pattern in patterns:
            self.assertNotIn("(?=", pattern)
            self.assertNotIn("(?!", pattern)
            self.assertNotIn("(?<", pattern)
            self.assertIsNone(re.search(r"\\[1-9]", pattern))
            re.compile(pattern, re.IGNORECASE)
        scan = module.tells_reader_to_use_named_path
        clause = module.clause_tells_reader_to_use
        self.assertEqual(
            module.split_clauses(
                "This is not required, but please use references/atlas "
                "for the next plan."
            ),
            [
                "This is not required",
                "please use references/atlas for the next plan",
            ],
        )
        self.assertEqual(
            module.split_clauses(
                "references/atlas was not used; the plan was saved in the "
                "resolved subject Atlas at "
                "autogenesis/plans/2026-10-08-add-retry-note.md."
            ),
            [
                "references/atlas was not used",
                "the plan was saved in the resolved subject Atlas at "
                "autogenesis/plans/2026-10-08-add-retry-note",
                "md",
            ],
        )
        self.assertEqual(
            module.split_clauses(
                "Instead, use the named legacy storage at references/atlas."
            ),
            ["Instead", "use the named legacy storage at references/atlas"],
        )
        self.assertEqual(
            module.split_clauses(
                "I did not use it.\nPlease move the plan to references/atlas."
            ),
            ["I did not use it", "Please move the plan to references/atlas"],
        )
        for boundary in (
            "however",
            "although",
            "though",
            "yet",
            "so",
            "and then",
        ):
            with self.subTest(boundary=boundary):
                governed = (
                    "I saved the plan "
                    + boundary
                    + " references/atlas was not used."
                )
                pieces = module.split_clauses(governed)
                self.assertEqual(pieces[0], "I saved the plan")
                self.assertFalse(clause(pieces[-1]))
                self.assertFalse(scan(governed))
                instructed = module.split_clauses(
                    "I did not use it "
                    + boundary
                    + " please use references/atlas."
                )
                self.assertTrue(clause(instructed[-1]))
                self.assertTrue(
                    scan(
                        "I did not use it "
                        + boundary
                        + " please use references/atlas."
                    )
                )
        self.assertTrue(
            scan("Please use references/atlas for all future plans.")
        )
        self.assertTrue(
            scan("You can save plans in references/atlas next time.")
        )
        self.assertFalse(
            scan(
                "I did not save the plan in references/atlas because "
                "the resolved subject Atlas owns it."
            )
        )
        self.assertTrue(
            scan("Instead, use the named legacy storage at references/atlas.")
        )
        self.assertFalse(scan("I did not use references/atlas."))
        self.assertTrue(
            scan(
                "I did not use references/atlas. Please use "
                "references/atlas for all future plans."
            )
        )
        self.assertFalse(
            scan("I will not write the plan in references/atlas.")
        )
        # "rather than" governs only when it is within three words of the path.
        self.assertTrue(
            scan("rather than store the plan in references/atlas")
        )
        self.assertFalse(scan("save the plan rather than references/atlas"))
        self.assertFalse(
            scan("use something instead of the old named references/atlas")
        )
        self.assertTrue(
            scan(
                "use something instead of the old named legacy "
                "references/atlas"
            )
        )
        self.assertFalse(scan("instead of references/atlas"))
        self.assertFalse(clause("instead of references/atlas"))
        self.assertFalse(scan("Never keep plans in references/atlas."))
        self.assertFalse(scan("I cannot put the plan in references/atlas."))
        self.assertFalse(
            scan("I declined to place the plan in references/atlas.")
        )
        self.assertFalse(scan("I refused to write the plan in references/atlas."))
        self.assertFalse(scan("I avoid saving plans in references/atlas."))
        self.assertFalse(scan("references/atlas should not be used."))
        self.assertFalse(scan("references/atlas will not be saved."))
        self.assertFalse(
            scan("Do not move the plan to references/atlas.")
        )
        self.assertTrue(
            scan("I did not use it! Please use references/atlas.")
        )
        self.assertTrue(
            scan("Was it saved? Please use references/atlas.")
        )
        self.assertTrue(
            scan("I did not use it.\nPlease move the plan to references/atlas.")
        )
        # A long token is still one word, so a cue two words before governs.
        self.assertFalse(scan("not " + ("x" * 40) + " use references/atlas"))
        self.assertFalse(scan("not " + ("x" * 10) + " use references/atlas"))
        self.assertFalse(scan("not one two use references/atlas"))
        self.assertTrue(scan("not one two three use references/atlas"))
        self.assertTrue(
            scan("I did not. " + ("y" * 10) + " use references/atlas")
        )
        should_be_used = "references/atlas should be used for future plans."
        self.assertEqual(
            module.split_clauses(should_be_used),
            ["references/atlas should be used for future plans"],
        )
        self.assertTrue(clause("references/atlas should be used for future plans"))
        self.assertTrue(scan(should_be_used))
        self.assertTrue(
            scan(
                "The named path was not used: references/atlas is not a "
                "storage override. " + should_be_used
            )
        )
        not_required = (
            "This is not required, but please use references/atlas "
            "for the next plan."
        )
        not_required_clauses = module.split_clauses(not_required)
        self.assertFalse(clause(not_required_clauses[0]))
        self.assertTrue(clause(not_required_clauses[1]))
        self.assertTrue(scan(not_required))
        was_not_used = (
            "references/atlas was not used; the plan was saved in the "
            "resolved subject Atlas at "
            "autogenesis/plans/2026-10-08-add-retry-note.md."
        )
        self.assertFalse(clause(module.split_clauses(was_not_used)[0]))
        self.assertFalse(scan(was_not_used))
        # instead of / rather than exempts only the path occurrence it
        # governs. A verb that also governs an un-exempted occurrence fails.
        quoted = (
            "Use references/atlas for plans instead of references/atlas "
            "for drafts"
        )
        quoted_paths = list(module.NAMED_PATH.finditer(quoted))
        self.assertEqual(len(quoted_paths), 2)
        self.assertFalse(module.path_is_instead_object(quoted, quoted_paths[0]))
        self.assertTrue(module.path_is_instead_object(quoted, quoted_paths[1]))
        self.assertEqual(module.split_clauses(quoted), [quoted])
        self.assertTrue(clause(quoted))
        self.assertTrue(scan(quoted))
        self.assertTrue(scan(quoted + "."))
        self.assertTrue(
            scan(
                "I did not use references/atlas. " + quoted + "."
            )
        )
        self.assertFalse(
            scan(
                "Do not use references/atlas for plans instead of "
                "references/atlas for drafts"
            )
        )
        self.assertFalse(
            scan(
                "save drafts instead of references/atlas rather than "
                "references/atlas"
            )
        )

        fixture = (
            ROOT / ".apm/evals/autogenesis/fixtures/declined-plan-path-explained"
        )
        reference = fixture / "reference"
        expect_pass = {
            "reference",
            "reference-proposed",
            "reference-paraphrase",
            "reference-negated-save",
            "reference-was-not-used",
        }
        expect_fail = {
            "negative": "reply does not refuse references/atlas",
            "negative-wrong-date": (
                "reply names autogenesis/plans/2026-10-09-add-retry-note.md, "
                "not autogenesis/plans/2026-10-08-add-retry-note.md"
            ),
            "negative-invalid-date": (
                "reply names autogenesis/plans/2026-99-99-add-retry-note.md, "
                "not autogenesis/plans/2026-10-08-add-retry-note.md"
            ),
            "negative-opposite-meaning": (
                "reply tells the reader to use references/atlas"
            ),
            "negative-please-use": (
                "reply tells the reader to use references/atlas"
            ),
            "negative-save-next-time": (
                "reply tells the reader to use references/atlas"
            ),
            "negative-should-be-used": (
                "reply tells the reader to use references/atlas"
            ),
            "negative-not-required": (
                "reply tells the reader to use references/atlas"
            ),
            "negative-use-instead-of": (
                "reply tells the reader to use references/atlas"
            ),
        }
        results_names = {
            path.name.removesuffix(".results.json")
            for path in fixture.glob("*.results.json")
        }
        self.assertEqual(results_names, expect_pass | set(expect_fail))
        for name in sorted(results_names):
            with self.subTest(variant=name):
                payload = json.loads(
                    (fixture / f"{name}.results.json").read_text(encoding="utf-8")
                )
                output = payload["tasks"][0]["runs"][0]["final_output"]
                result = subprocess.run(
                    ["python3", *args],
                    cwd=ROOT,
                    input=output,
                    env={**os.environ, "WAZA_WORKSPACE_DIR": str(fixture / name)},
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if name in expect_pass:
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("2026-10-08-add-retry-note.md", result.stdout)
                else:
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn(expect_fail[name], result.stderr)
                if name != "reference-proposed":
                    self.assertEqual(
                        self._fixture_bytes(fixture / name),
                        self._fixture_bytes(reference),
                    )
        paraphrase = json.loads(
            (fixture / "reference-paraphrase.results.json").read_text(
                encoding="utf-8"
            )
        )["tasks"][0]["runs"][0]["final_output"]
        self.assertNotIn("named path was not used", paraphrase.casefold())
        self.assertIn("did not use references/atlas", paraphrase.casefold())
        self.assertIn("resolved store", paraphrase.casefold())
        opposite = json.loads(
            (fixture / "negative-opposite-meaning.results.json").read_text(
                encoding="utf-8"
            )
        )["tasks"][0]["runs"][0]["final_output"]
        self.assertIn(
            "Instead, use the named legacy storage at references/atlas",
            opposite,
        )
        negated = json.loads(
            (fixture / "reference-negated-save.results.json").read_text(
                encoding="utf-8"
            )
        )["tasks"][0]["runs"][0]["final_output"]
        self.assertIn(
            "I did not save the plan in references/atlas because",
            negated,
        )
        self.assertFalse(scan(negated))
        please_use = json.loads(
            (fixture / "negative-please-use.results.json").read_text(
                encoding="utf-8"
            )
        )["tasks"][0]["runs"][0]["final_output"]
        self.assertIn(
            "Please use references/atlas for all future plans.",
            please_use,
        )
        self.assertTrue(scan(please_use))
        save_next = json.loads(
            (fixture / "negative-save-next-time.results.json").read_text(
                encoding="utf-8"
            )
        )["tasks"][0]["runs"][0]["final_output"]
        self.assertIn(
            "You can save plans in references/atlas next time.",
            save_next,
        )
        self.assertTrue(scan(save_next))
        should_be_used_reply = json.loads(
            (fixture / "negative-should-be-used.results.json").read_text(
                encoding="utf-8"
            )
        )["tasks"][0]["runs"][0]["final_output"]
        self.assertIn(
            "references/atlas should be used for future plans.",
            should_be_used_reply,
        )
        self.assertTrue(scan(should_be_used_reply))
        not_required_reply = json.loads(
            (fixture / "negative-not-required.results.json").read_text(
                encoding="utf-8"
            )
        )["tasks"][0]["runs"][0]["final_output"]
        self.assertIn(
            "This is not required, but please use references/atlas "
            "for the next plan.",
            not_required_reply,
        )
        self.assertTrue(scan(not_required_reply))
        use_instead = json.loads(
            (fixture / "negative-use-instead-of.results.json").read_text(
                encoding="utf-8"
            )
        )["tasks"][0]["runs"][0]["final_output"]
        self.assertIn(
            "Use references/atlas for plans instead of references/atlas "
            "for drafts",
            use_instead,
        )
        self.assertTrue(scan(use_instead))
        was_not_used_reply = json.loads(
            (fixture / "reference-was-not-used.results.json").read_text(
                encoding="utf-8"
            )
        )["tasks"][0]["runs"][0]["final_output"]
        self.assertIn(
            "references/atlas was not used; the plan was saved in the "
            "resolved subject Atlas at "
            "autogenesis/plans/2026-10-08-add-retry-note.md.",
            was_not_used_reply,
        )
        self.assertFalse(scan(was_not_used_reply))
        combined = subprocess.run(
            ["python3", *args],
            cwd=ROOT,
            input=(
                "The named path was not used. Instead, use the named legacy "
                "storage at references/atlas. The plan is at "
                "autogenesis/plans/2026-10-08-add-retry-note.md in the "
                "resolved subject Atlas."
            ),
            env={**os.environ, "WAZA_WORKSPACE_DIR": str(reference)},
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(combined.returncode, 0, combined.stdout)
        self.assertIn("reply tells the reader to use references/atlas", combined.stderr)

    def _fixture_bytes(self, root: Path) -> dict[str, bytes]:
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in root.rglob("*")
            if path.is_file()
        }

    def test_package_manifest_and_lock_have_no_evaluator_dependency(self) -> None:
        for name in ("apm.yml", "apm.lock.yaml"):
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertNotRegex(text, r"(?i)waza|agent-spec", name)

    def test_live_instructions_do_not_require_agent_spec_or_feature_files(
        self,
    ) -> None:
        live = [ROOT / "SKILL.md"] + sorted(
            (ROOT / "references/modules").glob("*/SKILL.md")
        )
        mention = re.compile(r"(?i)agent-spec|gherkin|\.feature\b")
        retired = re.compile(r"(?i)\b(retired|removed)\b")
        for path in live:
            for number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), 1
            ):
                if mention.search(line):
                    self.assertRegex(
                        line, retired, f"{path.relative_to(ROOT)}:{number}"
                    )

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

    def test_actual_root_version_surface_is_v0_9_0(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        manifest = (ROOT / "apm.yml").read_text(encoding="utf-8")

        self.assertRegex(skill, r"(?m)^name: autogenesis$")
        self.assertRegex(skill, r'(?m)^version: "?0\.9\.0"?$')
        self.assertRegex(skill, r"(?m)^activation_card: on$")
        self.assertIn("name: autogenesis\n", manifest)
        self.assertIn("version: 0.9.0\n", manifest)

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

    def test_live_instructions_do_not_reference_removed_atlas_query(self) -> None:
        """Atlas v0.13.0 removed path query and CLI search/query with no alias.

        Live instructions must say recall-first, not query-first. Historical
        scenario bodies keep their original wording, including
        atlas-storage-semantics-adversarial-v2 and the restored v3, which
        still name references/paths/query.md. The current successor asserts
        references/paths/recall.md. CHANGELOG records the rename and older
        release notes.
        """
        patterns = (
            re.compile(r"query-first"),
            re.compile(r"paths/query\.md"),
            re.compile(r"`query\.md`"),
            re.compile(r"\batlas(?:\.py)?\s+(?:query|search)\b"),
            re.compile(r"atlas\.py\b[^\n]*\s(?:query|search)\b"),
            re.compile(r"`query`\s*/\s*`remember`|`remember`,\s*`query`"),
            re.compile(r"\bAtlas query\b"),
            re.compile(r"read-only query\b"),
            re.compile(r"compile/query"),
            re.compile(r"Attempt query\b"),
            re.compile(r"Live ingest / query"),
        )
        roots = [
            ROOT / "SKILL.md",
            ROOT / "README.md",
            ROOT / "CONTRIBUTING.md",
            ROOT / "AGENTS.md",
            ROOT / "references",
            ROOT / "scripts",
            ROOT / ".apm" / "evals",
        ]
        skip_dirs = {
            ".git",
            ".atlas",
            "apm_modules",
            "scenarios",
            "__pycache__",
        }
        skip_files = {ROOT / "CHANGELOG.md", Path(__file__).resolve()}
        allowed_suffixes = {".md", ".py", ".yml", ".yaml", ".json", ".txt"}
        hits: list[str] = []
        for root in roots:
            candidates = [root] if root.is_file() else root.rglob("*")
            for path in candidates:
                if not path.is_file() or path.suffix not in allowed_suffixes:
                    continue
                if path in skip_files or any(
                    part in skip_dirs for part in path.parts
                ):
                    continue
                text = path.read_text(encoding="utf-8")
                for lineno, line in enumerate(text.splitlines(), start=1):
                    if any(pattern.search(line) for pattern in patterns):
                        hits.append(
                            f"{path.relative_to(ROOT)}:{lineno}:{line.strip()}"
                        )
        self.assertEqual(hits, [])

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


class SourceAuditBudgetTests(unittest.TestCase):
    def _timeouts(
        self,
        count: int,
        workers: int,
        *,
        monotonic: Callable[[], float] | None = None,
    ) -> list[float]:
        import audit_source

        timeouts: list[float] = []
        lock = threading.Lock()

        def fake_audit(
            path: str,
            root: Path,
            timeout: float,
        ) -> audit_source.AuditResult:
            del root
            with lock:
                timeouts.append(timeout)
            return audit_source.AuditResult(path, 0, "")

        clock = monotonic if monotonic is not None else (lambda: 0.0)
        results = audit_source.audit_files(
            [f"file-{index}.md" for index in range(count)],
            root=Path("."),
            max_workers=workers,
            monotonic=clock,
            audit=fake_audit,
        )
        self.assertEqual(len(results), count)
        self.assertTrue(all(result.returncode == 0 for result in results))
        return timeouts

    def test_per_file_timeout_is_not_shrunk_by_file_count(self) -> None:
        import audit_source

        expected = min(
            audit_source.AUDIT_TIMEOUT_SECONDS,
            audit_source.AUDIT_FILE_TIMEOUT_SECONDS,
        )
        waves = (900 + 8 - 1) // 8
        shrunk = audit_source.AUDIT_DEADLINE_SECONDS // waves
        self.assertEqual(shrunk, 6)
        self.assertGreater(expected, shrunk)

        one = self._timeouts(1, 1)
        many = self._timeouts(900, 8)
        self.assertEqual(one, [expected])
        self.assertEqual(set(many), {expected})
        self.assertEqual(len(many), 900)
        self.assertEqual(
            audit_source.file_audit_timeout(
                audit_source.AUDIT_DEADLINE_SECONDS
            ),
            expected,
        )

        originals = (
            audit_source.AUDIT_TIMEOUT_SECONDS,
            audit_source.AUDIT_FILE_TIMEOUT_SECONDS,
        )
        try:
            audit_source.AUDIT_TIMEOUT_SECONDS = 40
            audit_source.AUDIT_FILE_TIMEOUT_SECONDS = 90
            self.assertEqual(set(self._timeouts(3, 2)), {40})
            self.assertEqual(audit_source.file_audit_timeout(12.5), 12.5)
        finally:
            (
                audit_source.AUDIT_TIMEOUT_SECONDS,
                audit_source.AUDIT_FILE_TIMEOUT_SECONDS,
            ) = originals

    def test_remaining_deadline_caps_per_file_timeout(self) -> None:
        import audit_source

        remaining = 12.5
        reads = {"count": 0}

        def monotonic() -> float:
            reads["count"] += 1
            if reads["count"] == 1:
                return 10.0
            return 10.0 + audit_source.AUDIT_DEADLINE_SECONDS - remaining

        seen = self._timeouts(1, 4, monotonic=monotonic)
        self.assertEqual(seen, [remaining])
        self.assertLess(remaining, audit_source.AUDIT_FILE_TIMEOUT_SECONDS)
        self.assertLess(remaining, audit_source.AUDIT_TIMEOUT_SECONDS)
        self.assertEqual(audit_source.file_audit_timeout(remaining), remaining)

    def _assert_not_started_after_deadline(self, seconds_past: float) -> None:
        import audit_source

        reads = {"count": 0}
        calls: list[str] = []

        def monotonic() -> float:
            reads["count"] += 1
            if reads["count"] == 1:
                return 0.0
            return audit_source.AUDIT_DEADLINE_SECONDS + seconds_past

        def fake_audit(
            path: str,
            root: Path,
            timeout: float,
        ) -> audit_source.AuditResult:
            del root, timeout
            calls.append(path)
            raise AssertionError(path)

        results = audit_source.audit_files(
            ["first.md", "second.md"],
            root=Path("."),
            max_workers=2,
            monotonic=monotonic,
            audit=fake_audit,
        )
        self.assertEqual(calls, [])
        self.assertEqual(
            [result.path for result in results],
            ["first.md", "second.md"],
        )
        for result in results:
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.output, "not audited before the deadline")

    def test_files_not_started_after_the_deadline_fail(self) -> None:
        for seconds_past in (0, 5):
            with self.subTest(seconds_past=seconds_past):
                self._assert_not_started_after_deadline(seconds_past)

    def test_timeout_fails_closed(self) -> None:
        import audit_source

        calls: list[float] = []

        def fake_run(
            args: list[str],
            *,
            cwd: Path,
            timeout: float,
            label: str,
            check: bool,
        ) -> None:
            del args, cwd, check
            calls.append(timeout)
            raise audit_source.CommandError(
                f"{label} timed out after {timeout}s"
            )

        with patch("audit_source.run_command", fake_run):
            results = audit_source.audit_files(
                ["one.md", "two.md"],
                root=Path("."),
                max_workers=1,
                monotonic=lambda: 0.0,
            )
        self.assertEqual(len(calls), 2)
        self.assertEqual(
            calls,
            [
                audit_source.AUDIT_FILE_TIMEOUT_SECONDS,
                audit_source.AUDIT_FILE_TIMEOUT_SECONDS,
            ],
        )
        self.assertEqual([result.returncode for result in results], [124, 124])
        for result in results:
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("timed out", result.output)
            self.assertNotIn("not audited before the deadline", result.output)


if __name__ == "__main__":
    unittest.main()
