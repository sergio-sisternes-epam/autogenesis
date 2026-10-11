from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
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
        self.assertEqual(len(indexed_scenarios), 37)
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
        }
        trigger = {"ordinary-refactor-near-miss", "skill-change-should-trigger"}
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
            if path.is_file():
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
        suite = ROOT / ".apm/evals/autogenesis"
        lines = (
            suite / "tasks/plan-has-genesis-artifacts.yaml"
        ).read_text(encoding="utf-8").splitlines()
        start = next(
            index for index, line in enumerate(lines)
            if line.strip() == "must_match:"
        )
        patterns = []
        for line in lines[start + 1:]:
            match = re.fullmatch(r"\s*- '(.*)'", line)
            if not match:
                break
            patterns.append(match.group(1).replace("''", "'"))
        self.assertEqual(len(patterns), 2)
        artifacts, change_class = patterns
        self.assertIn("Genesis Artifacts", artifacts)
        plan = Path(
            ".atlas/example.invalid/fixtures/retry-helper-atlas/autogenesis"
            "/plans/2026-10-08-retry-backoff-guidance.md"
        )
        expected = {
            "reference": (True, True),
            "reference-heading": (True, True),
            "negative": (False, False),
            "negative-heading": (True, False),
        }
        for variant, (has_artifacts, has_class) in expected.items():
            with self.subTest(variant=variant):
                fixture = suite / "fixtures/plan-has-genesis-artifacts" / variant
                text = (fixture / plan).read_text(encoding="utf-8")
                self.assertEqual(bool(re.search(artifacts, text)), has_artifacts)
                self.assertEqual(bool(re.search(change_class, text)), has_class)
                self.assertTrue(
                    (fixture.parent / f"{variant}.results.json").is_file()
                )

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
                "negative-quoted": (plan, "status: 'approved'"),
                "negative-comment": (plan, "status: done # implemented"),
                "negative-work-approved": (work, "status: approved"),
                "negative-work-done": (work, "status: done"),
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
        scripts = []
        for name in (
            "design-stops-for-approval",
            "implement-blocks-without-approval",
        ):
            text = (
                ROOT / ".apm/evals/autogenesis/tasks" / f"{name}.yaml"
            ).read_text(encoding="utf-8")
            start = text.index("          import os\n")
            end = text.index("        - --\n", start)
            lines = []
            for line in text[start:end].splitlines():
                if line.startswith("          "):
                    lines.append(line[10:])
                else:
                    self.assertEqual(line, "")
                    lines.append("")
            scripts.append("\n".join(lines) + "\n")
        self.assertEqual(scripts[0], scripts[1])
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
        }
        accepted = {
            "plain": "status: designed\n",
            "single": "status: 'designed'\n",
            "double": 'status: "designed"\n',
            "comment": "status: designed # awaiting approval\n",
        }
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "status_check.py"
            script.write_text(scripts[0], encoding="utf-8")
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
                    ["python3", str(script), "--", plan],
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
            missing_fence = Path(tmp) / "unterminated"
            dest = missing_fence / plan
            dest.parent.mkdir(parents=True)
            dest.write_text(base.replace("\n---\n", "\n", 1), encoding="utf-8")
            env = os.environ.copy()
            env["WAZA_WORKSPACE_DIR"] = str(missing_fence)
            result = subprocess.run(
                ["python3", str(script), "--", plan],
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
        must_exist = [
            path
            for grader in task["graders"]
            if grader["type"] == "file"
            for path in grader["config"].get("must_exist", [])
        ]
        status = next(
            grader for grader in task["graders"]
            if grader["name"] == "plan_status_not_advanced"
        )
        self.assertIn(work, must_exist)
        self.assertIn(work, status["config"]["args"])
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
        text = (
            ROOT / ".apm/evals/autogenesis/tasks/help-does-not-mount.yaml"
        ).read_text(encoding="utf-8")
        start = text.index("          import os\n")
        end = text.index("          if __name__ == \"__main__\":\n", start)
        lines = []
        for line in text[start:end].splitlines():
            if line.startswith("          "):
                lines.append(line[10:])
            else:
                self.assertEqual(line, "")
                lines.append("")
        script = "\n".join(lines) + "if __name__ == \"__main__\":\n    main()\n"
        subject = (
            ROOT
            / ".apm/evals/autogenesis/fixtures/subjects/subject-unmounted"
        )

        def grade(workspace: Path) -> subprocess.CompletedProcess[str]:
            env = os.environ.copy()
            env["WAZA_WORKSPACE_DIR"] = str(workspace)
            return subprocess.run(
                ["python3", "-c", script],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

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

        missing_env = os.environ.copy()
        missing_env.pop("WAZA_WORKSPACE_DIR", None)
        unset = subprocess.run(
            ["python3", "-c", script],
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
                ["python3", "-c", script],
                cwd=elsewhere,
                env={**os.environ, "WAZA_WORKSPACE_DIR": str(subject)},
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(
                missing_baseline.returncode, 0, missing_baseline.stdout
            )
            self.assertIn("unmounted subject not found", missing_baseline.stderr)

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

        Frozen scenario bodies are not rewritten. The current suite
        atlas-storage-semantics-adversarial-v3 still asserts the old path
        name in SKILL.md; that smoke is reported, not edited. CHANGELOG
        records the rename and older release notes.
        """
        patterns = (
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


if __name__ == "__main__":
    unittest.main()
