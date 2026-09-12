from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Any

import validate_consumer


class ValidateConsumerTests(unittest.TestCase):
    package_name = "autogenesis"
    package_version = "0.5.0"

    def create_package_root(
        self,
        parent: Path,
        directory_name: str = "feature-worktree-name",
    ) -> Path:
        package_root = parent / directory_name
        package_root.mkdir()
        (package_root / "apm.yml").write_text(
            f"""name: {self.package_name}
version: {self.package_version}
""",
            encoding="utf-8",
        )
        (package_root / "SKILL.md").write_text(
            f"""---
name: {self.package_name}
description: fixture root
version: {self.package_version}
---

See [workflow discipline](references/modules/workflow-discipline/SKILL.md).
""",
            encoding="utf-8",
        )
        for module_name, role in validate_consumer.EXPECTED_MODULE_ROLES.items():
            module_file = (
                package_root / "references" / "modules" / module_name / "SKILL.md"
            )
            module_file.parent.mkdir(parents=True, exist_ok=True)
            if module_name == "workflow-discipline":
                content = f"""---
name: workflow-discipline
description: discipline
version: {self.package_version}
---

Load skill named `okf` before continuing.
See [contract](references/invocation-contract.md) and [json](references/invocation-contract.json).
"""
            elif module_name == "patterns":
                content = f"""---
name: patterns
description: support
version: {self.package_version}
---

See [example](references/example.txt) and [discipline](../workflow-discipline/SKILL.md).
"""
            else:
                content = f"""---
name: {module_name}
description: {role}
version: {self.package_version}
---

See [discipline](../workflow-discipline/SKILL.md).
"""
            module_file.write_text(content, encoding="utf-8")

        contract_doc = package_root / validate_consumer.INVOCATION_CONTRACT_DOC.as_posix()
        contract_doc.parent.mkdir(parents=True, exist_ok=True)
        contract_doc.write_text(
            "See [json](invocation-contract.json).\n",
            encoding="utf-8",
        )
        (package_root / validate_consumer.INVOCATION_CONTRACT_JSON.as_posix()).write_text(
            json.dumps(
                {
                    "schema": validate_consumer.INVOCATION_CONTRACT_SCHEMA,
                    "modules": validate_consumer.EXPECTED_MODULE_ROLES,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        example = (
            package_root
            / "references"
            / "modules"
            / "patterns"
            / "references"
            / "example.txt"
        )
        example.parent.mkdir(parents=True, exist_ok=True)
        example.write_text("pattern-example\n", encoding="utf-8")
        return package_root

    def deploy(
        self,
        package_root: Path,
        consumer: Path,
        target: str,
    ) -> None:
        for skills_root in validate_consumer.expected_skill_roots(consumer, target):
            bundle_root = skills_root / package_root.name
            bundle_root.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(package_root, bundle_root, dirs_exist_ok=True)

    def create_dependency_skill(
        self,
        consumer: Path,
        target: str,
        directory_name: str,
        *,
        skill_name: str | None = None,
        version: str | None = None,
    ) -> None:
        for skills_root in validate_consumer.expected_skill_roots(consumer, target):
            skill_file = skills_root / directory_name / "SKILL.md"
            skill_file.parent.mkdir(parents=True, exist_ok=True)
            skill_file.write_text(
                f"""---
name: {skill_name or self.package_name}
description: dependency fixture
version: {version or self.package_version}
---
""",
                encoding="utf-8",
            )

    def deployed_hashes(
        self,
        consumer: Path,
        target: str,
        root_name: str,
    ) -> dict[str, str]:
        hashes: dict[str, str] = {}
        for skills_root in validate_consumer.expected_skill_roots(consumer, target):
            bundle_root = skills_root / root_name
            if not bundle_root.exists():
                continue
            for path in sorted(bundle_root.rglob("*")):
                if path.is_file():
                    hashes[path.relative_to(consumer).as_posix()] = validate_consumer.digest(path)
        return hashes

    def dependency_spec(
        self,
        *,
        name: str,
        version: str,
        source: str,
        deployed_hashes: dict[str, str],
        repo_url: str | None = None,
        resolved_ref: str | None = None,
        resolved_commit: str | None = None,
    ) -> dict[str, Any]:
        source_path = Path(source)
        if source_path.exists():
            return {
                "name": name,
                "version": version,
                "repo_url": repo_url or f"_local/{source_path.name}",
                "source": "local",
                "local_path": str(source_path.resolve()),
                "owner": str(source_path.resolve()),
                "deployed_hashes": deployed_hashes,
            }
        repo, separator, reference = source.rpartition("#")
        if not separator:
            raise AssertionError(f"remote source must use owner/repo#ref: {source}")
        return {
            "name": name,
            "version": version,
            "repo_url": repo_url or repo,
            "resolved_ref": resolved_ref or reference,
            "resolved_commit": resolved_commit or ("a" * 40),
            "owner": repo_url or repo,
            "deployed_hashes": deployed_hashes,
        }

    def write_lock(
        self,
        package_root: Path,
        consumer: Path,
        target: str,
        source: str,
        *,
        root_hashes: dict[str, str] | None = None,
        extra_dependencies: tuple[dict[str, Any], ...] = (),
    ) -> None:
        root_dependency = self.dependency_spec(
            name=self.package_name,
            version=self.package_version,
            source=source,
            deployed_hashes=root_hashes
            or self.deployed_hashes(consumer, target, package_root.name),
        )
        dependencies = (root_dependency, *extra_dependencies)
        lines = [
            "lockfile_version: '1'",
            "apm_version: 0.30.0",
            "dependencies:",
        ]
        for dependency in dependencies:
            lines.extend(self.dependency_block_lines(dependency))
        source_lock = (
            validate_consumer.ROOT / "apm.lock.yaml"
        ).read_text(encoding="utf-8")
        dependency_body = source_lock.split("dependencies:\n", 1)[1].split(
            "deployments:", 1
        )[0].strip("\n")
        if dependency_body:
            lines.extend(dependency_body.splitlines())
        lines.append("deployments:")
        for dependency in dependencies:
            lines.extend(self.deployment_lines(dependency))
        (consumer / "apm.lock.yaml").write_text(
            "\n".join(lines) + "\n",
            encoding="utf-8",
        )

    def dependency_block_lines(self, dependency: dict[str, Any]) -> list[str]:
        lines = [
            f"- repo_url: {dependency['repo_url']}",
            f"  name: {dependency['name']}",
            f"  version: {dependency['version']}",
            "  package_type: hybrid",
            "  deployed_file_hashes:",
        ]
        for path, digest in sorted(dependency["deployed_hashes"].items()):
            lines.append(f"    {path}: sha256:{digest}")
        if dependency.get("source") == "local":
            lines.extend(
                [
                    "  source: local",
                    f"  local_path: {dependency['local_path']}",
                ]
            )
        else:
            lines.extend(
                [
                    f"  resolved_ref: {dependency['resolved_ref']}",
                    f"  resolved_commit: {dependency['resolved_commit']}",
                ]
            )
        return lines

    def deployment_lines(self, dependency: dict[str, Any]) -> list[str]:
        lines: list[str] = []
        for path, digest in sorted(dependency["deployed_hashes"].items()):
            lines.extend(
                [
                    "- kind: project-relative",
                    "  target: agent-skills",
                    f"  value: {path}",
                    "  runtime: null",
                    "  scope: project",
                    "  owners:",
                    f"  - {dependency['owner']}",
                    f"  active_owner: {dependency['owner']}",
                    f"  content_hash: sha256:{digest}",
                ]
            )
        return lines

    def test_root_skill_is_required_but_transitive_same_name_skills_are_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            package_root = self.create_package_root(workspace)
            consumer = workspace / "consumer"
            consumer.mkdir()
            target = "agent-skills"
            self.deploy(package_root, consumer, target)
            self.create_dependency_skill(
                consumer,
                target,
                "dependency-collision",
                skill_name=self.package_name,
                version=self.package_version,
            )
            dependency_hashes = self.deployed_hashes(
                consumer,
                target,
                "dependency-collision",
            )
            dependency = self.dependency_spec(
                name=self.package_name,
                version=self.package_version,
                source="example/dependency#v9.9.9",
                deployed_hashes=dependency_hashes,
                repo_url="example/dependency",
                resolved_ref="v9.9.9",
                resolved_commit="b" * 40,
            )
            self.write_lock(
                package_root,
                consumer,
                target,
                str(package_root),
                extra_dependencies=(dependency,),
            )

            validate_consumer.validate_deployment(
                consumer,
                target,
                package_root,
                str(package_root),
            )
            validate_consumer.validate_lock(
                consumer / "apm.lock.yaml",
                consumer,
                target,
                str(package_root),
                package_root=package_root,
            )

    def test_root_skill_can_use_local_source_directory_name(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package_root = self.create_package_root(Path(directory))
            contract = validate_consumer.package_contract(package_root)
            skill_file = (
                Path(directory)
                / ".agents"
                / "skills"
                / package_root.name
                / "SKILL.md"
            )
            skill_file.parent.mkdir(parents=True)
            skill_file.write_text(
                f"""---
name: {contract.name}
description: fixture root
version: {contract.version}
---
""",
                encoding="utf-8",
            )

            actual = validate_consumer.validate_skill_root(
                Path(directory) / ".agents" / "skills",
                contract,
            )

            self.assertEqual(actual, skill_file)

    def test_lock_proves_root_and_direct_dependency_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            package_root = self.create_package_root(workspace)
            consumer = workspace / "consumer"
            consumer.mkdir()
            target = "agent-skills"
            source = f"sergio-sisternes-epam/autogenesis#v{self.package_version}"
            self.deploy(package_root, consumer, target)
            other = self.dependency_spec(
                name=self.package_name,
                version=self.package_version,
                source="example/other-root#v1.0.0",
                deployed_hashes={},
                repo_url="example/other-root",
                resolved_ref="v1.0.0",
                resolved_commit="c" * 40,
            )
            self.write_lock(
                package_root,
                consumer,
                target,
                source,
                extra_dependencies=(other,),
            )

            validate_consumer.validate_lock(
                consumer / "apm.lock.yaml",
                consumer,
                target,
                source,
                "a" * 40,
                package_root,
            )

    def test_omitted_passive_asset_is_rejected_even_without_ledger_entry(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            package_root = self.create_package_root(workspace)
            consumer = workspace / "consumer"
            consumer.mkdir()
            target = "agent-skills"
            self.deploy(package_root, consumer, target)
            skills_root = validate_consumer.expected_skill_roots(consumer, target)[0]
            missing = (
                skills_root / package_root.name / "references" / "modules"
                / "patterns" / "references" / "example.txt"
            )
            missing.unlink()
            self.write_lock(package_root, consumer, target, str(package_root))

            with self.assertRaisesRegex(RuntimeError, "missing required owned asset.*example.txt"):
                validate_consumer.validate_deployment(
                    consumer, target, package_root, str(package_root)
                )

    def test_deployment_field_treats_yaml_null_as_missing(self) -> None:
        block = """- kind: project-relative
  target: agent-skills
  value: .agents/skills/example
  runtime: null
  active_owner: /tmp/example
  content_hash: null
"""

        self.assertIsNone(validate_consumer.deployment_field(block, "runtime"))
        self.assertIsNone(validate_consumer.deployment_field(block, "content_hash"))
        self.assertEqual(
            validate_consumer.deployment_field(block, "active_owner"),
            "/tmp/example",
        )

    def test_block_deployed_hashes_accepts_yaml_complex_keys(self) -> None:
        block = """- repo_url: _local/example
  name: autogenesis
  version: 0.5.0
  deployed_file_hashes:
    .agents/skills/example/SKILL.md: sha256:1111111111111111111111111111111111111111111111111111111111111111
    ? .agents/skills/example/references/modules/workflow-discipline/references/invocation-contract.json
    : sha256:2222222222222222222222222222222222222222222222222222222222222222
  source: local
  local_path: /tmp/example
"""

        self.assertEqual(
            validate_consumer.block_deployed_file_hashes(block),
            {
                ".agents/skills/example/SKILL.md": (
                    "sha256:1111111111111111111111111111111111111111111111111111111111111111"
                ),
                ".agents/skills/example/references/modules/workflow-discipline/references/invocation-contract.json": (
                    "sha256:2222222222222222222222222222222222222222222222222222222222222222"
                ),
            },
        )

    def test_missing_required_nested_asset_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            package_root = self.create_package_root(workspace)
            consumer = workspace / "consumer"
            consumer.mkdir()
            target = "agent-skills"
            self.deploy(package_root, consumer, target)
            missing = (
                consumer
                / ".agents"
                / "skills"
                / package_root.name
                / validate_consumer.INVOCATION_CONTRACT_JSON.as_posix()
            )
            missing.unlink()
            self.write_lock(package_root, consumer, target, str(package_root))

            with self.assertRaisesRegex(RuntimeError, "missing required owned asset"):
                validate_consumer.validate_deployment(
                    consumer,
                    target,
                    package_root,
                    str(package_root),
                )

    def test_invalid_invocation_contract_json_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            package_root = self.create_package_root(workspace)
            consumer = workspace / "consumer"
            consumer.mkdir()
            target = "agent-skills"
            self.deploy(package_root, consumer, target)
            deployed_json = (
                consumer
                / ".agents"
                / "skills"
                / package_root.name
                / validate_consumer.INVOCATION_CONTRACT_JSON.as_posix()
            )
            deployed_json.write_text(
                json.dumps(
                    {
                        "schema": validate_consumer.INVOCATION_CONTRACT_SCHEMA,
                        "modules": {"design": "operation"},
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            self.write_lock(package_root, consumer, target, str(package_root))

            with self.assertRaisesRegex(RuntimeError, "invocation-contract modules"):
                validate_consumer.validate_deployment(
                    consumer,
                    target,
                    package_root,
                    str(package_root),
                )

    def test_markdown_link_corruption_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            package_root = self.create_package_root(workspace)
            consumer = workspace / "consumer"
            consumer.mkdir()
            target = "agent-skills"
            self.deploy(package_root, consumer, target)
            deployed_skill = (
                consumer / ".agents" / "skills" / package_root.name / "SKILL.md"
            )
            deployed_skill.write_text(
                deployed_skill.read_text(encoding="utf-8").replace(
                    "references/modules/workflow-discipline/SKILL.md",
                    "references/modules/not-workflow/SKILL.md",
                ),
                encoding="utf-8",
            )
            self.write_lock(package_root, consumer, target, str(package_root))

            with self.assertRaisesRegex(RuntimeError, "markdown content diverged"):
                validate_consumer.validate_deployment(
                    consumer,
                    target,
                    package_root,
                    str(package_root),
                )

    def test_extra_root_owned_export_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            package_root = self.create_package_root(workspace)
            consumer = workspace / "consumer"
            consumer.mkdir()
            target = "agent-skills"
            self.deploy(package_root, consumer, target)
            self.create_dependency_skill(consumer, target, "extra-owned-export")
            root_hashes = self.deployed_hashes(consumer, target, package_root.name)
            root_hashes.update(self.deployed_hashes(consumer, target, "extra-owned-export"))
            self.write_lock(
                package_root,
                consumer,
                target,
                str(package_root),
                root_hashes=root_hashes,
            )

            with self.assertRaisesRegex(RuntimeError, "expected one root-owned deployed export"):
                validate_consumer.validate_deployment(
                    consumer,
                    target,
                    package_root,
                    str(package_root),
                )

    def test_frozen_lock_mutation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            package_root = self.create_package_root(workspace)
            consumer = workspace / "consumer"
            consumer.mkdir()
            target = "agent-skills"

            def fake_runner(
                *args: str,
                cwd: Path,
                phase: str,
                timeout: int = validate_consumer.COMMAND_TIMEOUT_SECONDS,
            ) -> None:
                del args, timeout
                if phase == "initial-install":
                    self.deploy(package_root, cwd, target)
                    self.write_lock(package_root, cwd, target, str(package_root))
                elif phase == "frozen-replay":
                    with (cwd / "apm.lock.yaml").open("a", encoding="utf-8") as lock:
                        lock.write("# mutation\n")

            with self.assertRaisesRegex(RuntimeError, "frozen replay changed"):
                validate_consumer.validate_consumer_in_directory(
                    str(package_root),
                    target,
                    consumer,
                    runner=fake_runner,
                    package_root=package_root,
                )

    def test_frozen_replay_revalidates_deployed_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            package_root = self.create_package_root(workspace)
            consumer = workspace / "consumer"
            consumer.mkdir()
            target = "agent-skills"

            def fake_runner(
                *args: str,
                cwd: Path,
                phase: str,
                timeout: int = validate_consumer.COMMAND_TIMEOUT_SECONDS,
            ) -> None:
                del args, timeout
                if phase == "initial-install":
                    self.deploy(package_root, cwd, target)
                    self.write_lock(package_root, cwd, target, str(package_root))
                elif phase == "frozen-replay":
                    deployed_skill = (
                        cwd
                        / ".agents"
                        / "skills"
                        / package_root.name
                        / "SKILL.md"
                    )
                    deployed_skill.write_text(
                        deployed_skill.read_text(encoding="utf-8").replace(
                            "workflow discipline",
                            "broken workflow discipline",
                        ),
                        encoding="utf-8",
                    )

            with self.assertRaisesRegex(RuntimeError, "deployed hash|markdown content diverged"):
                validate_consumer.validate_consumer_in_directory(
                    str(package_root),
                    target,
                    consumer,
                    runner=fake_runner,
                    package_root=package_root,
                )

    def test_stable_target_profile_is_complete(self) -> None:
        self.assertEqual(
            ",".join(validate_consumer.TARGET_PROFILES["stable-runtimes"]),
            "claude,codex,copilot,cursor,gemini,grok-build,"
            "kiro,opencode,windsurf",
        )


if __name__ == "__main__":
    unittest.main()
