#!/usr/bin/env python3
"""Audit every tracked source file within a wall-clock deadline."""

from __future__ import annotations

import argparse
import concurrent.futures
import os
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from ci_output import emit_error, print_summary, write_github_outputs
from command_runner import CommandError, run_command, run_git


ROOT = Path(__file__).resolve().parents[1]
GIT_TIMEOUT_SECONDS = 120
AUDIT_TIMEOUT_SECONDS = 300
AUDIT_FILE_TIMEOUT_SECONDS = 60
AUDIT_DEADLINE_SECONDS = 720
NOT_AUDITED_BEFORE_DEADLINE = "not audited before the deadline"


class SourceAuditError(RuntimeError):
    """Raised when the authoritative source set cannot be audited."""


@dataclass(frozen=True)
class AuditResult:
    path: str
    returncode: int
    output: str


def tracked_files(root: Path = ROOT) -> list[str]:
    try:
        tracked = run_git(
            "ls-files",
            "--cached",
            "-z",
            cwd=root,
            timeout=GIT_TIMEOUT_SECONDS,
            strip=False,
            capture_limit=None,
        )
    except CommandError as error:
        raise SourceAuditError(str(error)) from error
    resolved_root = root.resolve()
    files = []
    for path in tracked.split("\0"):
        if not path:
            continue
        candidate = resolved_root / path
        if candidate.is_symlink():
            raise SourceAuditError(f"{path}: tracked symbolic links are not auditable")
        try:
            candidate.resolve().relative_to(resolved_root)
        except ValueError as error:
            raise SourceAuditError(f"{path}: tracked path escapes the repository") from error
        if candidate.is_file():
            files.append(path)
    return sorted(files)


def audit_file(path: str, root: Path, timeout: float) -> AuditResult:
    try:
        result = run_command(
            ["apm", "audit", "--file", path],
            cwd=root,
            timeout=timeout,
            label=f"APM source audit for {path}",
            check=False,
        )
    except CommandError as error:
        # Fail closed with no retry: a later attempt could hide a hang.
        return AuditResult(path, 124, str(error))
    output = "\n".join(
        part.strip() for part in (result.stdout, result.stderr) if part.strip()
    )
    return AuditResult(path, result.returncode, output)


def file_audit_timeout(remaining_seconds: float) -> float:
    """Return one file's limit. The tracked-file count does not shrink it."""
    return min(
        AUDIT_TIMEOUT_SECONDS,
        AUDIT_FILE_TIMEOUT_SECONDS,
        remaining_seconds,
    )


def audit_files(
    files: Sequence[str],
    *,
    root: Path,
    max_workers: int,
    deadline_seconds: float = AUDIT_DEADLINE_SECONDS,
    monotonic: Callable[[], float] = time.monotonic,
    audit: Callable[[str, Path, float], AuditResult] = audit_file,
) -> list[AuditResult]:
    """Audit every file before the wall-clock deadline.

    The deadline is the monotonic time at entry plus ``deadline_seconds``.
    A file is not started once that instant has passed. A timed-out file is
    not retried.
    """
    if not files:
        return []
    deadline = monotonic() + deadline_seconds

    def worker(path: str) -> AuditResult:
        remaining = deadline - monotonic()
        if remaining <= 0:
            return AuditResult(path, 1, NOT_AUDITED_BEFORE_DEADLINE)
        return audit(path, root, file_audit_timeout(remaining))

    workers = min(max_workers, len(files))
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(worker, files))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args(argv)
    if args.jobs < 1:
        parser.error("--jobs must be at least 1")
    try:
        files = tracked_files()
    except SourceAuditError as error:
        emit_error(str(error), title="Source enumeration failed")
        return 1
    max_workers = min(args.jobs, len(files)) if files else 1
    results = audit_files(files, root=ROOT, max_workers=max_workers)
    failures = [result for result in results if result.returncode != 0]
    for result in failures:
        diagnostic = result.output.splitlines()[0] if result.output else "no diagnostic"
        emit_error(
            f"APM source audit failed: {diagnostic}",
            title="APM source audit failed",
            file=result.path,
        )
    fields = {
        "source_audit_files": len(results),
        "source_audit_failures": len(failures),
        "source_audit": "failed" if failures else "pass",
    }
    print_summary(fields)
    write_github_outputs(args.github_output, fields)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
