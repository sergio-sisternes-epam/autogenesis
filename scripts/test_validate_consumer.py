from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import validate_consumer


class ValidateConsumerTests(unittest.TestCase):
    def deploy(self, consumer: Path, target: str, transitive: bool = False) -> None:
        contract = validate_consumer.package_contract()
        for root in validate_consumer.expected_skill_roots(consumer, target):
            skill = root / contract.name / "SKILL.md"
            skill.parent.mkdir(parents=True, exist_ok=True)
            skill.write_text(
                f"---\nname: {contract.name}\nversion: {contract.version}\n---\n",
                encoding="utf-8",
            )
            if transitive:
                dependency = root / "atlas" / "SKILL.md"
                dependency.parent.mkdir(parents=True, exist_ok=True)
                dependency.write_text("---\nname: atlas\n---\n", encoding="utf-8")

    def write_lock(self, consumer: Path, target: str, source: str) -> None:
        contract = validate_consumer.package_contract()
        root_lines = [
            f"- name: {contract.name}",
            f"  version: {contract.version}",
            "  deployed_file_hashes:",
        ]
        for root in validate_consumer.expected_skill_roots(consumer, target):
            skill = root / contract.name / "SKILL.md"
            relative = skill.relative_to(consumer).as_posix()
            root_lines.append(
                f"    {relative}: sha256:{validate_consumer.digest(skill)}"
            )
        if "#" in source:
            repo, ref = source.rsplit("#", 1)
            root_lines.extend(
                [
                    f"  repo_url: {repo}",
                    f"  resolved_ref: {ref}",
                    f"  resolved_commit: {'a' * 40}",
                ]
            )
        else:
            root_lines.extend(
                ["  source: local", f"  local_path: {Path(source).resolve()}"]
            )
        source_lock = (
            validate_consumer.ROOT / "apm.lock.yaml"
        ).read_text(encoding="utf-8")
        dependency_body = source_lock.split("dependencies:\n", 1)[1].split(
            "deployments:", 1
        )[0]
        (consumer / "apm.lock.yaml").write_text(
            "lockfile_version: '1'\n"
            "apm_version: 0.30.0\n"
            "dependencies:\n"
            + "\n".join(root_lines)
            + "\n"
            + dependency_body,
            encoding="utf-8",
        )

    def test_root_skill_is_required_but_transitive_skills_are_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            consumer = Path(directory)
            self.deploy(consumer, "agent-skills", transitive=True)
            validate_consumer.validate_deployment(consumer, "agent-skills")

    def test_root_skill_can_use_local_source_directory_name(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            consumer = Path(directory)
            contract = validate_consumer.package_contract()
            skill_file = (
                consumer
                / ".agents"
                / "skills"
                / "feature-worktree-name"
                / "SKILL.md"
            )
            skill_file.parent.mkdir(parents=True)
            skill_file.write_text(
                f"---\nname: {contract.name}\nversion: {contract.version}\n---\n",
                encoding="utf-8",
            )

            actual = validate_consumer.validate_skill_root(
                consumer / ".agents" / "skills",
                contract,
            )

            self.assertEqual(actual, skill_file)

    def test_lock_proves_root_and_direct_dependency_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            consumer = Path(directory)
            target = "agent-skills"
            contract = validate_consumer.package_contract()
            source = (
                "sergio-sisternes-epam/autogenesis"
                f"#v{contract.version}"
            )
            self.deploy(consumer, target)
            self.write_lock(consumer, target, source)
            validate_consumer.validate_lock(
                consumer / "apm.lock.yaml",
                consumer,
                target,
                source,
                "a" * 40,
            )

    def test_frozen_lock_mutation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            consumer = Path(directory)
            target = "agent-skills"

            def fake_runner(
                *args: str,
                cwd: Path,
                phase: str,
                timeout: int = validate_consumer.COMMAND_TIMEOUT_SECONDS,
            ) -> None:
                del args, timeout
                if phase == "initial-install":
                    self.deploy(cwd, target)
                    self.write_lock(cwd, target, str(consumer))
                elif phase == "frozen-replay":
                    with (cwd / "apm.lock.yaml").open("a", encoding="utf-8") as lock:
                        lock.write("# mutation\n")

            with self.assertRaisesRegex(RuntimeError, "frozen replay changed"):
                validate_consumer.validate_consumer_in_directory(
                    str(consumer),
                    target,
                    consumer,
                    runner=fake_runner,
                )

    def test_stable_target_profile_is_complete(self) -> None:
        self.assertEqual(
            ",".join(validate_consumer.TARGET_PROFILES["stable-runtimes"]),
            "claude,codex,copilot,cursor,gemini,grok-build,"
            "kiro,opencode,windsurf",
        )


if __name__ == "__main__":
    unittest.main()
