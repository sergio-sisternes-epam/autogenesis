#!/usr/bin/env python3
"""Install Autogenesis into a disposable consumer and verify frozen replay."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from ci_output import emit_error, print_summary, write_github_outputs
from command_runner import CommandError, run_command
from dependency_contract import find_dependency_block, validate_lock_text
from release_readiness import manifest_version


ROOT = Path(__file__).resolve().parents[1]
COMMAND_TIMEOUT_SECONDS = 300
TARGET_SKILL_ROOTS = {
    "agent-skills": ".agents/skills",
    "claude": ".claude/skills",
    "codex": ".agents/skills",
    "copilot": ".agents/skills",
    "cursor": ".agents/skills",
    "gemini": ".agents/skills",
    "grok-build": ".grok/skills",
    "kiro": ".kiro/skills",
    "opencode": ".agents/skills",
    "windsurf": ".agents/skills",
}
TARGET_PROFILES = {
    "agent-skills": ("agent-skills",),
    "stable-runtimes": (
        "claude",
        "codex",
        "copilot",
        "cursor",
        "gemini",
        "grok-build",
        "kiro",
        "opencode",
        "windsurf",
    ),
}
SUPPORTED_TARGETS = set(TARGET_SKILL_ROOTS)


@dataclass(frozen=True)
class PackageContract:
    name: str
    version: str


def package_contract(root: Path = ROOT) -> PackageContract:
    manifest = (root / "apm.yml").read_text(encoding="utf-8")
    name_match = re.search(r"(?m)^name:\s*(\S+)\s*$", manifest)
    if not name_match:
        raise RuntimeError(f"{root / 'apm.yml'}: package name is missing")
    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    skill_name = re.search(r"(?m)^name:\s*(\S+)\s*$", skill)
    skill_version = re.search(r"(?m)^version:\s*(\S+)\s*$", skill)
    if not skill_name or not skill_version:
        raise RuntimeError(f"{root / 'SKILL.md'}: name or version is missing")
    version = manifest_version(root)
    if skill_name.group(1) != name_match.group(1):
        raise RuntimeError("SKILL.md name does not match apm.yml")
    if skill_version.group(1) != version:
        raise RuntimeError("SKILL.md version does not match apm.yml")
    return PackageContract(name_match.group(1), version)


def run(
    *args: str,
    cwd: Path,
    phase: str,
    timeout: int = COMMAND_TIMEOUT_SECONDS,
) -> None:
    print(f"consumer_phase={phase}:start", flush=True)
    try:
        result = run_command(
            list(args),
            cwd=cwd,
            timeout=timeout,
            label=phase,
        )
    except CommandError as error:
        print(f"consumer_phase={phase}:fail", flush=True)
        raise RuntimeError(str(error)) from error
    if result.stderr:
        print(
            f"consumer_phase={phase}:diagnostic\n{result.stderr}",
            file=sys.stderr,
            flush=True,
        )
    print(f"consumer_phase={phase}:pass", flush=True)


def digest(path: Path) -> str:
    if not path.is_file():
        raise RuntimeError(f"{path}: expected generated consumer lock is missing")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_targets(target: str) -> set[str]:
    targets = {value.strip() for value in target.split(",") if value.strip()}
    unsupported = targets - SUPPORTED_TARGETS
    if unsupported:
        raise RuntimeError(
            f"unsupported APM target(s): {', '.join(sorted(unsupported))}"
        )
    if not targets:
        raise RuntimeError("at least one supported APM target is required")
    return targets


def expected_skill_roots(consumer: Path, target: str) -> tuple[Path, ...]:
    targets = parse_targets(target)
    roots = {consumer / TARGET_SKILL_ROOTS[value] for value in targets}
    return tuple(sorted(roots))


def validate_skill_root(
    skills_root: Path,
    contract: PackageContract,
) -> Path:
    if not skills_root.is_dir():
        raise RuntimeError(
            f"{skills_root}: expected deployed skills directory is missing"
        )
    matches = []
    installed = []
    for skill_file in sorted(skills_root.glob("*/SKILL.md")):
        content = skill_file.read_text(encoding="utf-8")
        installed.append(skill_file.parent.name)
        lines = content.splitlines()
        if (
            f"name: {contract.name}" in lines
            and f"version: {contract.version}" in lines
        ):
            matches.append(skill_file)
    if len(matches) != 1:
        raise RuntimeError(
            f"expected one deployed {contract.name} skill, found {len(matches)}; "
            f"installed skills include {installed}"
        )
    return matches[0]


def validate_deployment(
    consumer: Path,
    target: str,
    package_root: Path = ROOT,
) -> None:
    contract = package_contract(package_root)
    for skills_root in expected_skill_roots(consumer, target):
        validate_skill_root(skills_root, contract)


def validate_lock(
    lock: Path,
    consumer: Path,
    target: str,
    source: str,
    expected_revision: str | None = None,
    package_root: Path = ROOT,
) -> None:
    if not lock.is_file():
        raise RuntimeError(f"{lock}: expected generated consumer lock is missing")
    content = lock.read_text(encoding="utf-8")
    contract = package_contract(package_root)
    dependency_errors = validate_lock_text(content, exact=False)
    if dependency_errors:
        raise RuntimeError("; ".join(dependency_errors))
    block = find_dependency_block(content, contract.name)
    if block is None:
        raise RuntimeError(f"{lock}: missing root package {contract.name}")
    for expected in (f"name: {contract.name}", f"version: {contract.version}"):
        if expected not in block:
            raise RuntimeError(f"{lock}: missing expected root metadata '{expected}'")

    source_path = Path(source)
    if source_path.exists():
        provenance = ("source: local", f"local_path: {source_path.resolve()}")
    else:
        repo, separator, reference = source.rpartition("#")
        if not separator or not repo or not reference:
            raise RuntimeError(f"remote source must use owner/repo#ref: {source}")
        provenance = (f"repo_url: {repo}", f"resolved_ref: {reference}")
        commit_match = re.search(
            r"(?m)^\s+resolved_commit:\s+([0-9a-f]{40})\s*$",
            block,
        )
        if not commit_match:
            raise RuntimeError(f"{lock}: missing resolved commit for {source}")
        if expected_revision and commit_match.group(1) != expected_revision:
            raise RuntimeError(
                f"{lock}: resolved commit {commit_match.group(1)} "
                f"!= expected {expected_revision}"
            )
    for expected in provenance:
        if expected not in block:
            raise RuntimeError(f"{lock}: missing source provenance '{expected}'")

    deployed_hashes = dict(
        re.findall(r"(?m)^\s+(\S.*?):\s+sha256:([0-9a-f]{64})\s*$", block)
    )
    for root in expected_skill_roots(consumer, target):
        skill_file = validate_skill_root(root, contract)
        relative = skill_file.relative_to(consumer).as_posix()
        expected_hash = deployed_hashes.get(relative)
        if expected_hash is None:
            raise RuntimeError(f"{lock}: missing deployed hash for {relative}")
        actual = hashlib.sha256(skill_file.read_bytes()).hexdigest()
        if expected_hash != actual:
            raise RuntimeError(
                f"{lock}: deployed hash mismatch for {relative}: "
                f"{expected_hash} != {actual}"
            )


def validate_consumer_in_directory(
    source: str,
    target: str,
    consumer: Path,
    runner: Callable[..., None] = run,
    expected_revision: str | None = None,
    package_root: Path = ROOT,
) -> str:
    parse_targets(target)
    runner("git", "init", "--quiet", cwd=consumer, phase="git-init")
    runner(
        "apm",
        "install",
        source,
        "--target",
        target,
        "--no-policy",
        cwd=consumer,
        phase="initial-install",
    )
    validate_deployment(consumer, target, package_root)
    lock = consumer / "apm.lock.yaml"
    validate_lock(
        lock,
        consumer,
        target,
        source,
        expected_revision,
        package_root,
    )
    before = digest(lock)
    runner(
        "apm",
        "install",
        "--frozen",
        "--target",
        target,
        "--no-policy",
        cwd=consumer,
        phase="frozen-replay",
    )
    after = digest(lock)
    if before != after:
        raise RuntimeError(
            f"frozen replay changed apm.lock.yaml: {before} != {after}"
        )
    runner(
        "apm",
        "audit",
        "--ci",
        "--no-policy",
        "--no-fail-fast",
        cwd=consumer,
        phase="consumer-audit",
    )
    return after


def validate_consumer(
    source: str,
    target: str,
    expected_revision: str | None = None,
) -> str:
    with tempfile.TemporaryDirectory(prefix="autogenesis-consumer-") as directory:
        return validate_consumer_in_directory(
            source,
            target,
            Path(directory),
            expected_revision=expected_revision,
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(ROOT))
    parser.add_argument("--target", required=True)
    parser.add_argument("--expected-revision")
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args(argv)
    if args.expected_revision and not re.fullmatch(
        r"[0-9a-f]{40}",
        args.expected_revision,
    ):
        parser.error("--expected-revision must be a full lowercase commit SHA")
    try:
        source = args.source
        if Path(source).exists():
            source = str(Path(source).resolve())
        lock_hash = validate_consumer(source, args.target, args.expected_revision)
    except RuntimeError as error:
        emit_error(
            f"{args.target}: {error}",
            title="Consumer validation failed",
        )
        fields = {
            "consumer_target": args.target,
            "consumer_validation": "failed",
        }
        write_github_outputs(args.github_output, fields)
        print_summary(fields)
        return 1
    fields = {
        "consumer_target": args.target,
        "installed_skill": package_contract().name,
        "frozen_lock_sha256": lock_hash,
        "consumer_validation": "pass",
    }
    print_summary(fields)
    write_github_outputs(args.github_output, fields)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
