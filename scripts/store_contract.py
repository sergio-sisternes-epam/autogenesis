#!/usr/bin/env python3
"""Verify the mutable store pointer and run the pinned Atlas validator."""

from __future__ import annotations

import argparse
import configparser
import json
from pathlib import Path

from ci_output import emit_error, emit_warning, print_summary, write_github_outputs
from command_runner import CommandError, run_command, run_git


ROOT = Path(__file__).resolve().parents[1]
STORE_PATH = Path(".atlas/github.com/sergio-sisternes-epam/autogenesis-atlas")
STORE_ID = "github.com/sergio-sisternes-epam/autogenesis-atlas"
STORE_URL = "https://github.com/sergio-sisternes-epam/autogenesis-atlas.git"
STORE_REF = "main"
STORE_COMMIT = "1ba15358a3157e3c946436ee60e73b87f3c77a0f"
ATLAS_VERSION = "0.9.0"
ATLAS_COMMIT = "2b6659e5440886c7abbd9ad10686fa3a0100813b"
COMMAND_TIMEOUT_SECONDS = 300


class StoreContractError(RuntimeError):
    """Raised when store identity or validation evidence is not exact."""


def verify_store(root: Path = ROOT, *, require_index: bool = False) -> None:
    parser = configparser.ConfigParser()
    parser.read(root / ".gitmodules", encoding="utf-8")
    section = f'submodule "{STORE_PATH.as_posix()}"'
    if not parser.has_section(section):
        raise StoreContractError(f".gitmodules: missing {section}")
    expected_config = {"path": STORE_PATH.as_posix(), "url": STORE_URL, "branch": STORE_REF}
    for key, expected in expected_config.items():
        actual = parser.get(section, key, fallback=None)
        if actual != expected:
            raise StoreContractError(
                f".gitmodules: {key} {actual!r} != {expected!r}"
            )

    mesh = json.loads((root / "atlas-mesh.json").read_text(encoding="utf-8"))
    expected_mesh = {
        "version": 1,
        "stores": [
            {
                "id": STORE_ID,
                "ref": STORE_REF,
                "path": STORE_PATH.as_posix(),
            }
        ],
    }
    if mesh != expected_mesh:
        raise StoreContractError("atlas-mesh.json: store contract is not exact")

    store = root / STORE_PATH
    if not store.is_dir():
        raise StoreContractError(f"{STORE_PATH}: checked-out store is missing")
    actual = run_git(
        "rev-parse",
        "HEAD",
        cwd=store,
        timeout=60,
    )
    if actual != STORE_COMMIT:
        raise StoreContractError(
            f"{STORE_PATH}: checkout {actual} != {STORE_COMMIT}"
        )
    if require_index:
        entry = run_git(
            "ls-files",
            "--stage",
            "--",
            STORE_PATH.as_posix(),
            cwd=root,
            timeout=60,
        ).split()
        if (
            len(entry) < 4
            or entry[0] != "160000"
            or entry[1] != STORE_COMMIT
            or entry[2] != "0"
        ):
            raise StoreContractError(
                f"{STORE_PATH}: candidate index gitlink is not exact {STORE_COMMIT}"
            )


def warning_ids(payload: dict[str, object]) -> tuple[str, ...]:
    warnings = payload.get("warnings", [])
    if not isinstance(warnings, list):
        raise StoreContractError("Atlas output field 'warnings' must be a list")
    result = []
    for warning in warnings:
        if not isinstance(warning, dict) or not isinstance(warning.get("id"), str):
            raise StoreContractError("Atlas warning is missing a string id")
        result.append(warning["id"])
    return tuple(result)


def validate_payload(
    payload: dict[str, object],
    returncode: int,
    allowed_warnings: set[str],
    phase: str,
) -> tuple[str, ...]:
    warnings = warning_ids(payload)
    unexpected = sorted(set(warnings) - allowed_warnings)
    critical = payload.get("critical")
    staging_count = payload.get("staging_count")
    if critical != []:
        raise StoreContractError(f"Atlas {phase}: critical findings: {critical!r}")
    if staging_count != 0:
        raise StoreContractError(
            f"Atlas {phase}: staging_count {staging_count!r} != 0"
        )
    if unexpected:
        raise StoreContractError(
            f"Atlas {phase}: unreviewed warning ids: {', '.join(unexpected)}"
        )
    expected_returncode = 1 if warnings else 0
    if returncode != expected_returncode:
        raise StoreContractError(
            f"Atlas {phase}: exit {returncode} != {expected_returncode} "
            "for the reported warning set"
        )
    if payload.get("ok") is not True:
        raise StoreContractError(f"Atlas {phase}: output did not report ok=true")
    return warnings


def run_atlas(
    atlas_cli: Path,
    store: Path,
    *,
    allowed_warnings: set[str] | None = None,
) -> dict[str, tuple[str, ...]]:
    allowed = allowed_warnings or set()
    version = run_command(
        ["python3", str(atlas_cli), "--version"],
        cwd=store,
        timeout=60,
        label="Atlas version check",
    ).stdout
    if version != f"atlas, version {ATLAS_VERSION}":
        raise StoreContractError(
            f"Atlas CLI version {version!r} != 'atlas, version {ATLAS_VERSION}'"
        )

    results = {}
    for command, phase in (("validate", "lint"), ("compile", "compile")):
        completed = run_command(
            ["python3", str(atlas_cli), command, "--root", str(store), "--json"],
            cwd=store,
            timeout=COMMAND_TIMEOUT_SECONDS,
            label=f"Atlas {phase}",
            check=False,
        )
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            raise StoreContractError(
                f"Atlas {phase}: invalid JSON output: {error}"
            ) from error
        results[phase] = validate_payload(
            payload,
            completed.returncode,
            allowed,
            phase,
        )
    return results


def main(argv: list[str] | None = None, root: Path = ROOT) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--atlas-cli", type=Path)
    parser.add_argument("--require-index", action="store_true")
    parser.add_argument("--allow-warning", action="append", default=[])
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args(argv)
    results: dict[str, tuple[str, ...]] = {}
    try:
        verify_store(root, require_index=args.require_index)
        if args.atlas_cli:
            results = run_atlas(
                args.atlas_cli.resolve(),
                (root / STORE_PATH).resolve(),
                allowed_warnings=set(args.allow_warning),
            )
    except (OSError, ValueError, CommandError, StoreContractError) as error:
        emit_error(str(error), title="Store contract failed")
        return 1

    observed = sorted({item for warnings in results.values() for item in warnings})
    for item in observed:
        emit_warning(
            f"Atlas warning '{item}' is explicitly allowed by this invocation.",
            title="Reviewed Atlas warning",
        )
    fields = {
        "store_contract": "pass",
        "store_commit": STORE_COMMIT,
        "atlas_cli_commit": ATLAS_COMMIT,
        "atlas_lint": "pass" if "lint" in results else "not-run",
        "atlas_compile": "pass" if "compile" in results else "not-run",
        "atlas_warning_count": len(observed),
    }
    print_summary(fields)
    write_github_outputs(args.github_output, fields)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
