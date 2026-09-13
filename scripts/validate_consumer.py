#!/usr/bin/env python3
"""Install Autogenesis into a disposable consumer and verify frozen replay."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

from ci_output import emit_error, print_summary, write_github_outputs
from command_runner import CommandError, run_command
from dependency_contract import dependency_blocks, field, validate_lock_text
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
MARKDOWN_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
INVOCATION_CONTRACT_SCHEMA = "autogenesis.invocation-contract/v1"
EXPECTED_OPERATION_MODULES = (
    "design",
    "initialise",
    "implement",
    "research",
    "reflect-challenge",
    "learn-skill",
    "reevaluate",
    "aware-runtime",
    "wire",
    "review-package",
    "atlas-migrate",
    "help",
    "getting-started",
)
EXPECTED_SUPPORT_MODULES = (
    "workflow-discipline",
    "think-challenge",
    "think-grill",
    "think-ramble",
    "patterns",
    "validate-skill-import-links",
    "validate-progressive-disclosure",
    "validate-okf-conformance",
    "validate-gate-map-and-non-goals",
)
EXPECTED_MODULE_ROLES = {
    **{name: "operation" for name in EXPECTED_OPERATION_MODULES},
    **{name: "support" for name in EXPECTED_SUPPORT_MODULES},
}
INVOCATION_CONTRACT_DOC = PurePosixPath(
    "references/modules/workflow-discipline/references/invocation-contract.md"
)
INVOCATION_CONTRACT_JSON = PurePosixPath(
    "references/modules/workflow-discipline/references/invocation-contract.json"
)


@dataclass(frozen=True)
class PackageContract:
    name: str
    version: str


@dataclass(frozen=True)
class DeploymentRecord:
    value: str
    active_owner: str | None
    content_hash: str | None


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


def deployment_blocks(content: str) -> list[str]:
    match = re.search(
        r"(?ms)^deployments:\s*\n(?P<body>.*?)(?=^[A-Za-z0-9_]+:\s|\Z)",
        content,
    )
    if not match:
        return []
    return [
        block
        for block in re.split(r"(?m)(?=^-\s)", match.group("body"))
        if block.lstrip().startswith("-")
    ]


def deployment_field(block: str, name: str) -> str | None:
    match = re.search(
        rf"(?m)^(?:-\s+|\s+){{1}}{re.escape(name)}:\s*(.+?)\s*$",
        block,
    )
    if not match:
        return None
    value = match.group(1).strip()
    return None if value in {"null", "~"} else value


def deployment_owners(block: str) -> tuple[str, ...]:
    match = re.search(
        r"(?ms)^\s+owners:\s*\n(?P<body>(?:\s+-\s+.+\n)+)",
        block,
    )
    if not match:
        return ()
    return tuple(
        owner.strip()
        for owner in re.findall(r"(?m)^\s+-\s+(.+?)\s*$", match.group("body"))
    )


def deployment_records(content: str) -> tuple[DeploymentRecord, ...]:
    records = []
    for block in deployment_blocks(content):
        value = deployment_field(block, "value")
        if value is None:
            continue
        records.append(
            DeploymentRecord(
                value=value,
                active_owner=deployment_field(block, "active_owner"),
                content_hash=deployment_field(block, "content_hash"),
            )
        )
    return tuple(records)


def block_deployed_file_hashes(block: str) -> dict[str, str]:
    match = re.search(
        r"(?ms)^\s+deployed_file_hashes:\s*\n(?P<body>.*?)(?=^\s{2}[A-Za-z0-9_]+:\s|^\S|\Z)",
        block,
    )
    if not match:
        return {}
    hashes: dict[str, str] = {}
    pending_path: str | None = None
    for raw_line in match.group("body").splitlines():
        line = raw_line.rstrip()
        simple = re.match(r"^\s{4}(\S.*?):\s+(sha256:[0-9a-f]{64})\s*$", line)
        if simple:
            hashes[simple.group(1)] = simple.group(2)
            pending_path = None
            continue
        complex_key = re.match(r"^\s{4}\?\s+(.+?)\s*$", line)
        if complex_key:
            pending_path = complex_key.group(1)
            continue
        complex_value = re.match(r"^\s{4}:\s+(sha256:[0-9a-f]{64})\s*$", line)
        if complex_value and pending_path is not None:
            hashes[pending_path] = complex_value.group(1)
            pending_path = None
    return hashes


def hash_without_prefix(value: str) -> str:
    return value.split(":", 1)[1] if value.startswith("sha256:") else value


def semver_tuple(version: str) -> tuple[int, int, int]:
    match = re.match(r"^([0-9]+)\.([0-9]+)\.([0-9]+)", version)
    if not match:
        raise RuntimeError(f"unsupported version format: {version}")
    return tuple(int(part) for part in match.groups())


def requires_module_inventory(contract: PackageContract) -> bool:
    return semver_tuple(contract.version) >= (0, 5, 0)


def required_owned_relative_paths(
    contract: PackageContract, package_root: Path
) -> tuple[PurePosixPath, ...]:
    if not requires_module_inventory(contract):
        return ()
    module_paths = tuple(
        PurePosixPath("references/modules") / module_name / "SKILL.md"
        for module_name in EXPECTED_MODULE_ROLES
    )
    source_assets = {
        PurePosixPath(path.relative_to(package_root).as_posix())
        for path in (package_root / "references").rglob("*")
        if path.is_file()
    }
    return tuple(sorted(
        source_assets
        | set(module_paths)
        | {INVOCATION_CONTRACT_DOC, INVOCATION_CONTRACT_JSON}
    ))


def dependency_matches_source(block: str, source: str, contract: PackageContract) -> bool:
    if field(block, "name") != contract.name or field(block, "version") != contract.version:
        return False
    source_path = Path(source)
    if source_path.exists():
        return (
            field(block, "source") == "local"
            and field(block, "local_path") == str(source_path.resolve())
        )
    repo, separator, reference = source.rpartition("#")
    if not separator or not repo or not reference:
        raise RuntimeError(f"remote source must use owner/repo#ref: {source}")
    repo_url = field(block, "repo_url")
    resolved_ref = field(block, "resolved_ref")
    return (
        repo_url is not None
        and repo_url.lower() == repo.lower()
        and resolved_ref == reference
    )


def dependency_owner_key(block: str) -> str:
    local_path = field(block, "local_path")
    if field(block, "source") == "local" and local_path:
        return str(Path(local_path).resolve())
    repo_url = field(block, "repo_url")
    if repo_url is None:
        raise RuntimeError("lock entry is missing repo_url")
    host = field(block, "host")
    if host and host.lower() != "github.com":
        return f"{host.lower()}/{repo_url}"
    return repo_url


def find_root_dependency_block(
    content: str,
    source: str,
    contract: PackageContract,
) -> str:
    matches = [
        block
        for block in dependency_blocks(content)
        if block.lstrip().startswith("-") and dependency_matches_source(block, source, contract)
    ]
    if len(matches) != 1:
        raise RuntimeError(
            "consumer lock must contain exactly one root package entry for "
            f"{contract.name} from {source!r}; found {len(matches)}"
        )
    return matches[0]


def is_within_prefix(path: str, prefix: str) -> bool:
    return path == prefix or path.startswith(f"{prefix}/")


def owned_file_hashes_for_target(
    content: str,
    consumer: Path,
    target: str,
    source: str,
    contract: PackageContract,
) -> dict[str, str]:
    block = find_root_dependency_block(content, source, contract)
    block_hashes = {
        path: hash_without_prefix(value)
        for path, value in block_deployed_file_hashes(block).items()
    }
    owner = dependency_owner_key(block)
    prefixes = tuple(
        skills_root.relative_to(consumer).as_posix()
        for skills_root in expected_skill_roots(consumer, target)
    )
    relevant_block_hashes = {
        path: value
        for path, value in block_hashes.items()
        if any(is_within_prefix(path, prefix) for prefix in prefixes)
    }
    relevant_record_hashes = {
        record.value: hash_without_prefix(record.content_hash)
        for record in deployment_records(content)
        if record.active_owner == owner
        and record.content_hash is not None
        and any(is_within_prefix(record.value, prefix) for prefix in prefixes)
    }
    if not relevant_record_hashes:
        raise RuntimeError(
            "consumer lock deployments do not record active ownership for the "
            f"root package {contract.name}"
        )

    problems: list[str] = []
    missing = sorted(set(relevant_block_hashes) - set(relevant_record_hashes))
    if missing:
        problems.append(
            "deployment ownership missing for " + ", ".join(missing)
        )
    extra = sorted(set(relevant_record_hashes) - set(relevant_block_hashes))
    if extra:
        problems.append(
            "deployment ledger contains unexpected owned files "
            + ", ".join(extra)
        )
    mismatched = sorted(
        path
        for path in set(relevant_block_hashes) & set(relevant_record_hashes)
        if relevant_block_hashes[path] != relevant_record_hashes[path]
    )
    if mismatched:
        details = ", ".join(
            f"{path} ({relevant_block_hashes[path]} != {relevant_record_hashes[path]})"
            for path in mismatched
        )
        problems.append("deployment hash mismatch for " + details)
    if problems:
        raise RuntimeError("; ".join(problems))
    return relevant_block_hashes


def markdown_normalized(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def is_external_url(path: str) -> bool:
    path = path.strip()
    if not path:
        return False
    parsed = urlparse(path)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def is_rewritable_relative_link(path: str) -> bool:
    stripped = path.strip()
    if not stripped or stripped.startswith(("#", "//", "/")):
        return False
    try:
        return not urlparse(stripped).scheme
    except ValueError:
        return False


def split_link_target(link_path: str) -> tuple[str, str]:
    candidates = [link_path.find(sep) for sep in ("#", "?")]
    positions = [index for index in candidates if index != -1]
    if not positions:
        return link_path, ""
    index = min(positions)
    return link_path[:index], link_path[index:]


def allowed_markdown_targets(
    source_target: str,
    source_file: Path,
    deployed_file: Path,
    source_root: Path,
    deployed_root: Path,
) -> set[str]:
    allowed = {source_target}
    if is_external_url(source_target) or not is_rewritable_relative_link(source_target):
        return allowed
    path_part, suffix = split_link_target(source_target)
    if not path_part:
        return allowed
    try:
        candidate = (source_file.parent / path_part).resolve()
        source_root_resolved = source_root.resolve()
    except (OSError, ValueError):
        return allowed
    if not candidate.exists() or not candidate.is_file():
        return allowed
    try:
        relative_source = candidate.relative_to(source_root_resolved)
    except ValueError:
        return allowed
    deployed_candidate = deployed_root / relative_source
    rewritten = os.path.relpath(deployed_candidate, start=deployed_file.parent)
    allowed.add(rewritten.replace(os.sep, "/") + suffix)
    return allowed


def markdown_contents_match(
    source_text: str,
    deployed_text: str,
    source_file: Path,
    deployed_file: Path,
    source_root: Path,
    deployed_root: Path,
) -> bool:
    if source_text == deployed_text:
        return True
    source_text = markdown_normalized(source_text)
    deployed_text = markdown_normalized(deployed_text)
    source_matches = list(MARKDOWN_LINK_PATTERN.finditer(source_text))
    deployed_matches = list(MARKDOWN_LINK_PATTERN.finditer(deployed_text))
    if len(source_matches) != len(deployed_matches):
        return False

    source_cursor = 0
    deployed_cursor = 0
    for source_match, deployed_match in zip(source_matches, deployed_matches):
        if source_text[source_cursor:source_match.start()] != deployed_text[
            deployed_cursor:deployed_match.start()
        ]:
            return False
        if source_match.group(1) != deployed_match.group(1):
            return False
        if deployed_match.group(2) not in allowed_markdown_targets(
            source_match.group(2),
            source_file,
            deployed_file,
            source_root,
            deployed_root,
        ):
            return False
        source_cursor = source_match.end()
        deployed_cursor = deployed_match.end()
    return source_text[source_cursor:] == deployed_text[deployed_cursor:]


def validate_invocation_contract_json(
    source_file: Path,
    deployed_file: Path,
) -> list[str]:
    errors: list[str] = []
    expected_modules = EXPECTED_MODULE_ROLES
    for label, path in (("source", source_file), ("deployed", deployed_file)):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"{path}: invalid {label} invocation-contract json ({error})")
            continue
        if not isinstance(data, dict):
            errors.append(f"{path}: {label} invocation-contract json must be an object")
            continue
        if data.get("schema") != INVOCATION_CONTRACT_SCHEMA:
            errors.append(
                f"{path}: {label} invocation-contract schema "
                f"{data.get('schema')!r} != {INVOCATION_CONTRACT_SCHEMA!r}"
            )
        modules = data.get("modules")
        if not isinstance(modules, dict):
            errors.append(f"{path}: {label} invocation-contract modules must be an object")
            continue
        if set(modules) != set(expected_modules):
            errors.append(
                f"{path}: {label} invocation-contract modules "
                f"{sorted(modules)} != {sorted(expected_modules)}"
            )
            continue
        for module_name, role in expected_modules.items():
            if modules.get(module_name) != role:
                errors.append(
                    f"{path}: {label} invocation-contract role for {module_name} "
                    f"{modules.get(module_name)!r} != {role!r}"
                )
    return errors


def validate_owned_skill_root(
    consumer: Path,
    skills_root: Path,
    contract: PackageContract,
    owned_hashes: dict[str, str],
) -> Path:
    root_prefix = skills_root.relative_to(consumer).as_posix()
    owned_exports = sorted(
        {
            PurePosixPath(path).parts[len(PurePosixPath(root_prefix).parts)]
            for path in owned_hashes
            if is_within_prefix(path, root_prefix)
            and len(PurePosixPath(path).parts) > len(PurePosixPath(root_prefix).parts)
        }
    )
    if len(owned_exports) != 1:
        raise RuntimeError(
            f"{root_prefix}: expected one root-owned deployed export, found {owned_exports}"
        )
    skill_root = skills_root / owned_exports[0]
    skill_file = skill_root / "SKILL.md"
    if not skill_file.is_file():
        raise RuntimeError(f"{skill_file}: expected root-owned deployed SKILL.md is missing")
    lines = skill_file.read_text(encoding="utf-8").splitlines()
    if f"name: {contract.name}" not in lines or f"version: {contract.version}" not in lines:
        raise RuntimeError(
            f"{skill_file}: root-owned deployed SKILL.md does not match {contract.name} {contract.version}"
        )
    return skill_root


def validate_owned_files(
    consumer: Path,
    export_root: Path,
    package_root: Path,
    contract: PackageContract,
    owned_hashes: dict[str, str],
) -> list[str]:
    errors: list[str] = []
    export_prefix = PurePosixPath(export_root.relative_to(consumer).as_posix())
    owned_relative_hashes: dict[PurePosixPath, str] = {}
    for path, expected_hash in owned_hashes.items():
        pure_path = PurePosixPath(path)
        if not is_within_prefix(path, export_prefix.as_posix()):
            continue
        owned_relative_hashes[pure_path.relative_to(export_prefix)] = expected_hash

    for required in required_owned_relative_paths(contract, package_root):
        if required not in owned_relative_hashes:
            errors.append(
                f"{export_root.relative_to(consumer).as_posix()}: missing required owned asset {required.as_posix()}"
            )

    for relative_path, expected_hash in sorted(owned_relative_hashes.items()):
        source_file = package_root / relative_path.as_posix()
        deployed_file = export_root / relative_path.as_posix()
        if not source_file.is_file():
            errors.append(f"{source_file}: root-owned deployed file has no source counterpart")
            continue
        if not deployed_file.is_file():
            errors.append(f"{deployed_file}: root-owned deployed file is missing")
            continue
        actual_hash = digest(deployed_file)
        if actual_hash != expected_hash:
            errors.append(
                f"{deployed_file}: deployed hash {actual_hash} != expected {expected_hash}"
            )
            continue
        if deployed_file.suffix.lower() == ".md":
            source_text = source_file.read_text(encoding="utf-8")
            deployed_text = deployed_file.read_text(encoding="utf-8")
            if not markdown_contents_match(
                source_text,
                deployed_text,
                source_file,
                deployed_file,
                package_root,
                export_root,
            ):
                errors.append(
                    f"{deployed_file}: markdown content diverged beyond allowed APM link rewriting"
                )
            continue
        if source_file.read_bytes() != deployed_file.read_bytes():
            errors.append(
                f"{deployed_file}: deployed content differs from source {source_file}"
            )

    if requires_module_inventory(contract):
        source_json = package_root / INVOCATION_CONTRACT_JSON.as_posix()
        deployed_json = export_root / INVOCATION_CONTRACT_JSON.as_posix()
        if source_json.is_file() and deployed_json.is_file():
            errors.extend(validate_invocation_contract_json(source_json, deployed_json))
    return errors


def validate_deployment(
    consumer: Path,
    target: str,
    package_root: Path = ROOT,
    source: str | None = None,
) -> None:
    contract = package_contract(package_root)
    lock = consumer / "apm.lock.yaml"
    if source is None or not lock.is_file():
        for skills_root in expected_skill_roots(consumer, target):
            validate_skill_root(skills_root, contract)
        return

    content = lock.read_text(encoding="utf-8")
    owned_hashes = owned_file_hashes_for_target(content, consumer, target, source, contract)
    errors: list[str] = []
    for skills_root in expected_skill_roots(consumer, target):
        skill_root = validate_owned_skill_root(consumer, skills_root, contract, owned_hashes)
        errors.extend(
            validate_owned_files(
                consumer,
                skill_root,
                package_root,
                contract,
                owned_hashes,
            )
        )
    if errors:
        raise RuntimeError("; ".join(errors))


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
    block = find_root_dependency_block(content, source, contract)
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

    owned_hashes = owned_file_hashes_for_target(content, consumer, target, source, contract)
    for skills_root in expected_skill_roots(consumer, target):
        skill_root = validate_owned_skill_root(consumer, skills_root, contract, owned_hashes)
        relative = (skill_root / "SKILL.md").relative_to(consumer).as_posix()
        expected_hash = owned_hashes.get(relative)
        if expected_hash is None:
            raise RuntimeError(f"{lock}: missing deployed hash for {relative}")
        actual = hashlib.sha256((skill_root / "SKILL.md").read_bytes()).hexdigest()
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
    validate_deployment(consumer, target, package_root, source)
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
    validate_deployment(consumer, target, package_root, source)
    validate_lock(
        lock,
        consumer,
        target,
        source,
        expected_revision,
        package_root,
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
