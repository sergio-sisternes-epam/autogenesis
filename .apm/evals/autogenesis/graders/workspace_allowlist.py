#!/usr/bin/env python3
"""Fail-closed whole-workspace allowlist check.

Compares the agent workspace (WAZA_WORKSPACE_DIR) with a subject baseline.
Every child is recorded with os.lstat and never followed: a directory, a
regular file plus its content hash, or a symlink plus its target. An lstat
error or any other file type fails closed.

Paths passed with --allow may be added, changed or removed. Any other
difference fails, including symlinks of any kind. The only ignored entry is
a real directory named .git at the workspace root, which setup creates with
git init -q. A .git symlink or file is not ignored. Nested .git is not ignored.

program_grader.go does not set the child working directory and does not
rewrite arguments. python3 therefore resolves this script, and this script
resolves --baseline, from the Waza process working directory. Relative paths
in the task files match the run layout in the suite README.
"""

import hashlib
import os
import stat
import sys
from pathlib import Path


def fail(message):
    print(message, file=sys.stderr)
    sys.exit(1)


def lstat_entry(path, label):
    try:
        return os.lstat(path)
    except OSError as exc:
        fail("cannot lstat " + label + ": " + str(exc))


def readlink_entry(path, label):
    try:
        return os.readlink(path)
    except OSError as exc:
        fail("cannot readlink " + label + ": " + str(exc))


def hash_regular(path, label):
    if not hasattr(os, "O_NOFOLLOW"):
        fail("os.O_NOFOLLOW is required so file reads never follow symlinks")
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    except OSError as exc:
        fail("cannot read " + label + ": " + str(exc))
    try:
        info = os.fstat(descriptor)
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
            fail("unexpected file type for " + label)
        digest = hashlib.sha256()
        while True:
            block = os.read(descriptor, 1024 * 1024)
            if not block:
                return digest.hexdigest()
            digest.update(block)
    except OSError as exc:
        fail("cannot read " + label + ": " + str(exc))
    finally:
        os.close(descriptor)


def classify(path, label):
    info = lstat_entry(path, label)
    mode = info.st_mode
    if stat.S_ISLNK(mode):
        return ("symlink", readlink_entry(path, label))
    if stat.S_ISDIR(mode):
        return ("dir",)
    if stat.S_ISREG(mode):
        return ("file", hash_regular(path, label))
    fail("unexpected file type for " + label)


def require_real_dir(path, label, missing_message):
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        fail(missing_message)
    except OSError as exc:
        fail("cannot lstat " + label + ": " + str(exc))
    if stat.S_ISLNK(info.st_mode):
        fail(label + " is a symlink")
    if not stat.S_ISDIR(info.st_mode):
        fail(label + " is not a directory")


def snapshot(root, skip_root_git):
    entries = {}

    def onerror(exc):
        name = getattr(exc, "filename", None) or str(root)
        fail("cannot list " + str(name) + ": " + str(exc))

    for dirpath, dirnames, filenames in os.walk(root, followlinks=False, onerror=onerror):
        rel_dir = Path(dirpath).relative_to(root).as_posix()
        overlap = sorted(set(dirnames) & set(filenames))
        if overlap:
            fail("directory listing overlaps at " + rel_dir + ": " + ", ".join(overlap))
        names = list(dirnames) + list(filenames)
        if skip_root_git and rel_dir == "." and ".git" in dirnames:
            git_info = lstat_entry(Path(dirpath) / ".git", ".git")
            if stat.S_ISDIR(git_info.st_mode) and not stat.S_ISLNK(git_info.st_mode):
                dirnames.remove(".git")
                names.remove(".git")
        for name in list(dirnames):
            child = Path(dirpath) / name
            rel = child.relative_to(root).as_posix()
            info = lstat_entry(child, rel)
            if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
                dirnames.remove(name)
        for name in names:
            child = Path(dirpath) / name
            rel = child.relative_to(root).as_posix()
            if rel in entries:
                fail("duplicate entry " + rel)
            entries[rel] = classify(child, rel)
    return entries


def workspace_relative(raw):
    candidate = Path(raw)
    if candidate.is_absolute() or not candidate.parts:
        fail("allow path escapes the workspace: " + raw)
    if any(part in ("", ".", "..") for part in candidate.parts):
        fail("allow path escapes the workspace: " + raw)
    return candidate.as_posix()


def parse_args(argv):
    baseline = None
    allowed = []
    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg == "--baseline":
            if baseline is not None or index + 1 >= len(argv):
                fail("usage: workspace_allowlist.py --baseline PATH [--allow REL]...")
            baseline = argv[index + 1]
            index += 2
            continue
        if arg == "--allow":
            if index + 1 >= len(argv):
                fail("usage: workspace_allowlist.py --baseline PATH [--allow REL]...")
            allowed.append(workspace_relative(argv[index + 1]))
            index += 2
            continue
        fail("unexpected argument: " + arg)
    if not baseline:
        fail("missing --baseline")
    return baseline, allowed


def resolve_baseline(raw):
    path = Path(raw)
    if not path.is_absolute():
        path = Path.cwd() / path
    require_real_dir(
        path,
        "baseline",
        "baseline not found at " + str(path) + " (resolved from the working directory)",
    )
    return path


def describe(rel, record):
    if record[0] == "symlink":
        return rel + " (symlink)"
    return rel


def compare(baseline, current, allowed):
    problems = []
    missing = sorted(
        rel for rel in set(baseline) - set(current) if rel not in allowed
    )
    extra = sorted(
        rel for rel in set(current) - set(baseline) if rel not in allowed
    )
    changed = sorted(
        rel
        for rel in set(baseline) & set(current)
        if rel not in allowed and current[rel] != baseline[rel]
    )
    if missing:
        problems.append("missing " + ", ".join(missing))
    if extra:
        problems.append(
            "unexpected " + ", ".join(describe(rel, current[rel]) for rel in extra)
        )
    if changed:
        problems.append("changed " + ", ".join(changed))
    if problems:
        fail("workspace differs from baseline: " + "; ".join(problems))


def main():
    workspace = os.environ.get("WAZA_WORKSPACE_DIR", "")
    if not workspace:
        fail("WAZA_WORKSPACE_DIR is not set")
    current_root = Path(workspace)
    require_real_dir(current_root, "workspace", "workspace is not a directory")
    baseline_arg, allowed = parse_args(sys.argv[1:])
    baseline_root = resolve_baseline(baseline_arg)
    baseline = snapshot(baseline_root, False)
    current = snapshot(current_root, True)
    compare(baseline, current, set(allowed))
    print(
        "workspace matches baseline ("
        + str(len(baseline))
        + " baseline entries; "
        + str(len(allowed))
        + " allowed paths; root .git directory ignored; symlinks not followed)"
    )


if __name__ == "__main__":
    main()
