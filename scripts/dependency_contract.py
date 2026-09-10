#!/usr/bin/env python3
"""Validate immutable direct dependencies and reviewed graph divergences."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from ci_output import emit_error, emit_warning, print_summary, write_github_outputs


ROOT = Path(__file__).resolve().parents[1]
APM_VERSION = "0.30.0"
MARKETPLACE = "atlas"


@dataclass(frozen=True)
class Dependency:
    name: str
    repo: str
    ref: str
    version: str
    commit: str

    @property
    def source(self) -> str:
        return f"{self.name}@{MARKETPLACE}"


EXPECTED_DEPENDENCIES = (
    Dependency(
        "atlas",
        "sergio-sisternes-epam/atlas",
        "579e8090273ce991ea0717abed0775dc03f28de2",
        "0.11.2",
        "579e8090273ce991ea0717abed0775dc03f28de2",
    ),
    Dependency(
        "okf",
        "sergio-sisternes-epam/okf",
        "5246f7b193b58a32ac8a15fc76aedf37c42b042c",
        "0.2.1",
        "5246f7b193b58a32ac8a15fc76aedf37c42b042c",
    ),
    Dependency(
        "discuss",
        "sergio-sisternes-epam/discuss",
        "c1c0936d9a0346dce7d877646046c918de335d69",
        "0.3.10",
        "c1c0936d9a0346dce7d877646046c918de335d69",
    ),
    Dependency(
        "think",
        "sergio-sisternes-epam/think",
        "874613a67018c74ee95f857416fb315d2f80b92b",
        "0.1.0",
        "874613a67018c74ee95f857416fb315d2f80b92b",
    ),
)

KNOWN_ANCHOR_DIVERGENCES: tuple[tuple[str, str], ...] = ()


class DependencyContractError(RuntimeError):
    """Raised when dependency source or lock evidence is not exact."""


def manifest_sources(root: Path = ROOT) -> tuple[str, ...]:
    content = (root / "apm.yml").read_text(encoding="utf-8")
    match = re.search(
        r"(?ms)^dependencies:\s*\n\s+apm:\s*\n(?P<body>.*)",
        content,
    )
    if not match:
        raise DependencyContractError("apm.yml: dependencies.apm is missing")
    body = match.group("body")
    names = re.findall(r"(?m)^\s+-\s+name:\s+(\S+)\s*$", body)
    marketplaces = re.findall(r"(?m)^\s+marketplace:\s+(\S+)\s*$", body)
    if not names or len(names) != len(marketplaces):
        raise DependencyContractError(
            "apm.yml: dependencies.apm must use name+marketplace object form"
        )
    if any(marketplace != MARKETPLACE for marketplace in marketplaces):
        raise DependencyContractError(
            f"apm.yml: marketplace must be {MARKETPLACE}"
        )
    return tuple(
        f"{name}@{marketplace}"
        for name, marketplace in zip(names, marketplaces)
    )


def dependency_blocks(content: str) -> list[str]:
    match = re.search(
        r"(?ms)^dependencies:\s*\n(?P<body>.*?)(?=^deployments:|\Z)",
        content,
    )
    if not match:
        raise DependencyContractError("apm.lock.yaml: dependencies are missing")
    return [
        block
        for block in re.split(r"(?m)(?=^-\s)", match.group("body"))
        if block.lstrip().startswith("-")
    ]


def field(block: str, name: str) -> str | None:
    match = re.search(
        rf"(?m)^(?:-\s+|\s+){re.escape(name)}:\s*(\S+)\s*$",
        block,
    )
    return match.group(1) if match else None


def find_dependency_block(content: str, name: str) -> str | None:
    for block in dependency_blocks(content):
        if field(block, "name") == name:
            return block
    return None


def validate_manifest(root: Path = ROOT) -> list[str]:
    expected = tuple(dependency.source for dependency in EXPECTED_DEPENDENCIES)
    try:
        actual = manifest_sources(root)
    except (OSError, DependencyContractError) as error:
        return [str(error)]
    if actual != expected:
        return [f"apm.yml: dependency sources {actual!r} != {expected!r}"]
    return []


def validate_lock_text(content: str, *, exact: bool = True) -> list[str]:
    errors: list[str] = []
    if not re.search(
        rf"(?m)^apm_version:\s*['\"]?{re.escape(APM_VERSION)}['\"]?\s*$",
        content,
    ):
        errors.append(f"apm.lock.yaml: expected APM version {APM_VERSION}")
    try:
        blocks = dependency_blocks(content)
    except DependencyContractError as error:
        return errors + [str(error)]
    names = {field(block, "name") for block in blocks}
    expected_names = {dependency.name for dependency in EXPECTED_DEPENDENCIES}
    if exact and names != expected_names:
        errors.append(
            "apm.lock.yaml: direct dependency names "
            f"{sorted(name for name in names if name)} != {sorted(expected_names)}"
        )
    for dependency in EXPECTED_DEPENDENCIES:
        block = find_dependency_block(content, dependency.name)
        if block is None:
            errors.append(f"apm.lock.yaml: missing {dependency.name}")
            continue
        expected_fields = {
            "repo_url": dependency.repo,
            "resolved_ref": dependency.ref,
            "resolved_commit": dependency.commit,
            "version": dependency.version,
        }
        for key, expected in expected_fields.items():
            actual = field(block, key)
            if actual != expected:
                errors.append(
                    f"apm.lock.yaml: {dependency.name}.{key} "
                    f"{actual!r} != {expected!r}"
                )
    return errors


def validate_lock(root: Path = ROOT) -> list[str]:
    try:
        content = (root / "apm.lock.yaml").read_text(encoding="utf-8")
    except OSError as error:
        return [str(error)]
    return validate_lock_text(content)


def validate_direct_okf_usage(root: Path = ROOT) -> list[str]:
    required = (
        root / "references/modules/workflow-discipline.md",
        root / "references/modules/validate-okf-conformance.md",
    )
    errors = []
    for path in required:
        try:
            content = path.read_text(encoding="utf-8").lower()
        except OSError as error:
            errors.append(str(error))
            continue
        if "skill named `okf`" not in content:
            errors.append(
                f"{path.relative_to(root)}: direct invocation of skill named `okf` "
                "is required"
            )
    return errors


def main(argv: list[str] | None = None, root: Path = ROOT) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args(argv)
    errors = validate_manifest(root) + validate_lock(root) + validate_direct_okf_usage(root)
    fields = {
        "dependency_contract": "blocked" if errors else "pass",
        "direct_dependencies": len(EXPECTED_DEPENDENCIES),
        "reviewed_anchor_divergences": len(KNOWN_ANCHOR_DIVERGENCES),
    }
    for error in errors:
        emit_error(error, title="Dependency contract failed")
    if not errors:
        for warning_id, message in KNOWN_ANCHOR_DIVERGENCES:
            emit_warning(
                f"{warning_id}: {message}. Root direct released pins are authoritative.",
                title="Reviewed dependency anchor divergence",
            )
    print_summary(fields)
    write_github_outputs(args.github_output, fields)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
