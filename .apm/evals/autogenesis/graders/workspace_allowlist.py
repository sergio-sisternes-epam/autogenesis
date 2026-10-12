#!/usr/bin/env python3
"""Fail-closed whole-workspace allowlist check.

Compares the agent workspace (WAZA_WORKSPACE_DIR) with a subject baseline.
Every child is recorded with os.lstat and never followed: a directory, a
regular file plus its content hash, or a symlink plus its target. An lstat
error or any other file type fails closed.

Paths passed with --allow may be added, changed or removed. An allowed
path that exists must be a regular file reached only through real
directories: lstat each component below the workspace root, and fail closed
if any component is a symlink. --allow-under permits added or changed
regular files strictly inside that directory. Every path under an
allow-under directory that exists must likewise be a regular file reached
only through real directories; a symlink anywhere on that path fails
closed. Removals, new directories and symlinks there still fail.
--allow-modify names a baseline regular file that may change and must still
be a regular file reached only through real directories. It may not be
removed or replaced by a symlink or directory. --allow-log-entry is the
same constraint on the file type, and the new text may only add lines.
Added lines must be either only at the end, or one contiguous block
directly under the first `# Log` heading: immediately after that heading
line, or after the blank line or lines that directly follow it. Every
baseline line must remain, unchanged and in the same order. Nothing may
be removed or edited, and no insertion anywhere else is accepted. A file
with no `# Log` heading accepts only an end append. Lines are compared
without their LF terminator, so a missing trailing newline does not let
the original last line change.
--allow-dated names a relative path with one {date} placeholder in its
final component. {date} is any real YYYY-MM-DD. A matching added or changed
regular file, reached only through real directories, is allowed. Removal
is not excused, and a symlink at that path fails closed.
--allow-bytecode permits only added real directories named __pycache__ and
added or changed regular *.pyc files. Any other difference fails, including
symlinks of any kind. The only ignored entry is a real directory named .git
at the workspace root, which setup creates with git init -q. A .git symlink
or file is not ignored. Nested .git is not ignored.

program_grader.go does not set the child working directory and does not
rewrite arguments. python3 therefore resolves this script, and this script
resolves --baseline, from the Waza process working directory. Relative paths
in the task files match the run layout in the suite README.
"""

import datetime
import hashlib
import os
import re
import stat
import sys
from pathlib import Path


USAGE = (
    "usage: workspace_allowlist.py --baseline PATH "
    "[--allow REL]... [--allow-under REL_DIR]... "
    "[--allow-modify REL]... [--allow-log-entry REL]... "
    "[--allow-dated REL]... [--allow-bytecode]"
)

DATE_TEXT = re.compile(r"^\d{4}-\d{2}-\d{2}$")


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


def is_real_date(text):
    if not DATE_TEXT.fullmatch(text):
        return False
    try:
        datetime.date.fromisoformat(text)
    except ValueError:
        return False
    return True


def dated_pattern(raw):
    rel = workspace_relative(raw)
    if rel.count("{date}") != 1:
        fail("allow-dated path must contain one {date} placeholder: " + raw)
    parent, name = rel.rsplit("/", 1) if "/" in rel else ("", rel)
    if "{date}" in parent or name.count("{date}") != 1:
        fail("allow-dated {date} must be in the final component: " + raw)
    return rel


def dated_match(rel, pattern):
    parent, pattern_name = pattern.rsplit("/", 1) if "/" in pattern else ("", pattern)
    rel_parent, name = rel.rsplit("/", 1) if "/" in rel else ("", rel)
    if rel_parent != parent:
        return False
    prefix, suffix = pattern_name.split("{date}")
    if not name.startswith(prefix) or not name.endswith(suffix):
        return False
    middle = name[len(prefix) : len(name) - len(suffix) if suffix else None]
    return is_real_date(middle)


def strictly_inside(rel, directories):
    return any(rel.startswith(directory + "/") for directory in directories)


def entry_name(rel):
    return rel.rsplit("/", 1)[-1]


def allow_under_covers(rel, baseline, current, directories):
    if not strictly_inside(rel, directories):
        return False
    record = current.get(rel)
    if record is None or record[0] != "file":
        return False
    previous = baseline.get(rel)
    return previous is None or previous[0] == "file"


def bytecode_covers(rel, baseline, current):
    record = current.get(rel)
    if record is None:
        return False
    previous = baseline.get(rel)
    name = entry_name(rel)
    if record[0] == "dir" and name == "__pycache__":
        return previous is None
    if record[0] == "file" and name.endswith(".pyc"):
        return previous is None or previous[0] == "file"
    return False


def kept_regular(rel, baseline, current, names):
    if rel not in names:
        return False
    previous = baseline.get(rel)
    record = current.get(rel)
    if previous is None or previous[0] != "file":
        return False
    if record is None or record[0] != "file":
        return False
    return True


def dated_covers(rel, baseline, current, patterns):
    record = current.get(rel)
    if record is None or record[0] != "file":
        return False
    if not any(dated_match(rel, pattern) for pattern in patterns):
        return False
    previous = baseline.get(rel)
    return previous is None or previous[0] == "file"


def excused(
    rel,
    baseline,
    current,
    allowed,
    allowed_under,
    allow_bytecode,
    allowed_modify,
    allowed_append,
    allowed_dated,
):
    # Diff exemption only. An allowed path, and every path under an
    # allow-under directory, is checked separately and must be a regular
    # file reached only through real directories. modify, log-entry and dated
    # do not excuse a removal or a non-file replacement.
    if rel in allowed:
        return True
    if allow_under_covers(rel, baseline, current, allowed_under):
        return True
    if kept_regular(rel, baseline, current, allowed_modify):
        return True
    if kept_regular(rel, baseline, current, allowed_append):
        return True
    if dated_covers(rel, baseline, current, allowed_dated):
        return True
    if allow_bytecode and bytecode_covers(rel, baseline, current):
        return True
    return False


def take_value(argv, index, flag):
    if index + 1 >= len(argv) or argv[index + 1].startswith("--"):
        fail(USAGE + " (" + flag + " needs a path)")
    return argv[index + 1]


def parse_args(argv):
    baseline = None
    allowed = []
    allowed_under = []
    allowed_modify = []
    allowed_append = []
    allowed_dated = []
    allow_bytecode = False
    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg == "--baseline":
            if baseline is not None or index + 1 >= len(argv):
                fail(USAGE)
            baseline = argv[index + 1]
            index += 2
            continue
        if arg == "--allow":
            allowed.append(workspace_relative(take_value(argv, index, arg)))
            index += 2
            continue
        if arg == "--allow-under":
            allowed_under.append(workspace_relative(take_value(argv, index, arg)))
            index += 2
            continue
        if arg == "--allow-modify":
            allowed_modify.append(workspace_relative(take_value(argv, index, arg)))
            index += 2
            continue
        if arg == "--allow-log-entry":
            allowed_append.append(workspace_relative(take_value(argv, index, arg)))
            index += 2
            continue
        if arg == "--allow-dated":
            allowed_dated.append(dated_pattern(take_value(argv, index, arg)))
            index += 2
            continue
        if arg == "--allow-bytecode":
            allow_bytecode = True
            index += 1
            continue
        fail("unexpected argument: " + arg)
    if not baseline:
        fail("missing --baseline")
    return (
        baseline,
        allowed,
        allowed_under,
        allowed_modify,
        allowed_append,
        allowed_dated,
        allow_bytecode,
    )


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


def require_real_path(root, rel, leaf_kind):
    """If rel exists, it must be a real leaf reached only through real directories.

    lstat each component below the workspace root. Absence is allowed, so a
    removed --allow path still passes this check. A symlink anywhere on the
    path fails closed. leaf_kind is "file" or "dir".
    """
    candidate = Path(rel)
    if candidate.is_absolute() or not candidate.parts:
        fail("path escapes the workspace: " + rel)
    current = root
    for index, part in enumerate(candidate.parts):
        if part in ("", ".", ".."):
            fail("path escapes the workspace: " + rel)
        current = current / part
        label = Path(*candidate.parts[: index + 1]).as_posix()
        try:
            info = os.lstat(current)
        except FileNotFoundError:
            return
        except OSError as exc:
            fail("cannot lstat " + label + ": " + str(exc))
        if stat.S_ISLNK(info.st_mode):
            fail(label + " is a symlink")
        leaf = index == len(candidate.parts) - 1
        if leaf and leaf_kind == "file":
            if not stat.S_ISREG(info.st_mode):
                fail(label + " is not a regular file")
        elif not stat.S_ISDIR(info.st_mode):
            fail(label + " is not a directory")


def read_regular_bytes(path, label):
    if not hasattr(os, "O_NOFOLLOW"):
        fail("os.O_NOFOLLOW is required so file reads never follow symlinks")
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    except OSError as exc:
        fail("cannot read " + label + ": " + str(exc))
    try:
        info = os.fstat(descriptor)
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
            fail(label + " is not a regular file")
        chunks = []
        while True:
            block = os.read(descriptor, 1024 * 1024)
            if not block:
                return b"".join(chunks)
            chunks.append(block)
    except OSError as exc:
        fail("cannot read " + label + ": " + str(exc))
    finally:
        os.close(descriptor)


def require_baseline_file(root, rel):
    require_real_path(root, rel, "file")
    try:
        info = os.lstat(root / rel)
    except FileNotFoundError:
        fail("allow path is not a baseline regular file: " + rel)
    except OSError as exc:
        fail("cannot lstat " + rel + ": " + str(exc))
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        fail("allow path is not a baseline regular file: " + rel)


def enforce_real_allowed_paths(
    root, current, allowed, allowed_under, allowed_modify, allowed_append, allowed_dated
):
    for rel in sorted(allowed):
        require_real_path(root, rel, "file")
    for rel in sorted(set(allowed_modify) | set(allowed_append)):
        require_real_path(root, rel, "file")
    for directory in sorted(allowed_under):
        require_real_path(root, directory, "dir")
        prefix = directory + "/"
        for rel in sorted(current):
            if rel.startswith(prefix):
                require_real_path(root, rel, "file")
    for pattern in sorted(allowed_dated):
        parent = pattern.rsplit("/", 1)[0] if "/" in pattern else ""
        if parent:
            require_real_path(root, parent, "dir")
        for rel in sorted(current):
            if dated_match(rel, pattern):
                require_real_path(root, rel, "file")


def line_contents(data):
    """Return LF-separated line contents, without terminators.

    A missing final LF keeps the last line and does not add an empty line.
    A CR stays inside the line, so the original last line is byte-identical
    only when its content is unchanged.
    """
    if not data:
        return []
    parts = data.split(b"\n")
    if data.endswith(b"\n"):
        del parts[-1]
    return parts


def is_log_heading(line):
    return line.rstrip(b" \t") == b"# Log"


def is_blank_line(line):
    return line.strip(b" \t") == b""


def log_entry_allowed(old, new):
    old_lines = line_contents(old)
    new_lines = line_contents(new)
    if new_lines == old_lines:
        return True
    extra = len(new_lines) - len(old_lines)
    if extra <= 0:
        return False
    allowed = {len(old_lines)}
    heading = next(
        (index for index, line in enumerate(old_lines) if is_log_heading(line)),
        None,
    )
    if heading is not None:
        allowed.add(heading + 1)
        blank = 0
        while heading + 1 + blank < len(old_lines) and is_blank_line(
            old_lines[heading + 1 + blank]
        ):
            blank += 1
        allowed.add(heading + 1 + blank)
    for index in allowed:
        if (
            new_lines[:index] == old_lines[:index]
            and new_lines[index + extra :] == old_lines[index:]
        ):
            return True
    return False


def enforce_log_entry(baseline_root, current_root, baseline, current, allowed_append):
    for rel in sorted(allowed_append):
        previous = baseline.get(rel)
        record = current.get(rel)
        if previous is None or record is None or previous == record:
            continue
        if previous[0] != "file" or record[0] != "file":
            continue
        old = read_regular_bytes(baseline_root / rel, rel)
        new = read_regular_bytes(current_root / rel, rel)
        if not log_entry_allowed(old, new):
            fail("not an allowed log change: " + rel)


def compare(
    baseline,
    current,
    allowed,
    allowed_under,
    allow_bytecode,
    allowed_modify,
    allowed_append,
    allowed_dated,
):
    problems = []

    def covers(rel):
        return excused(
            rel,
            baseline,
            current,
            allowed,
            allowed_under,
            allow_bytecode,
            allowed_modify,
            allowed_append,
            allowed_dated,
        )

    missing = sorted(rel for rel in set(baseline) - set(current) if not covers(rel))
    extra = sorted(rel for rel in set(current) - set(baseline) if not covers(rel))
    changed = sorted(
        rel
        for rel in set(baseline) & set(current)
        if current[rel] != baseline[rel] and not covers(rel)
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
    (
        baseline_arg,
        allowed,
        allowed_under,
        allowed_modify,
        allowed_append,
        allowed_dated,
        allow_bytecode,
    ) = parse_args(sys.argv[1:])
    baseline_root = resolve_baseline(baseline_arg)
    for rel in sorted(set(allowed_modify) | set(allowed_append)):
        require_baseline_file(baseline_root, rel)
    baseline = snapshot(baseline_root, False)
    current = snapshot(current_root, True)
    enforce_real_allowed_paths(
        current_root,
        current,
        set(allowed),
        set(allowed_under),
        set(allowed_modify),
        set(allowed_append),
        set(allowed_dated),
    )
    enforce_log_entry(
        baseline_root,
        current_root,
        baseline,
        current,
        set(allowed_append),
    )
    compare(
        baseline,
        current,
        set(allowed),
        set(allowed_under),
        allow_bytecode,
        set(allowed_modify),
        set(allowed_append),
        set(allowed_dated),
    )
    print(
        "workspace matches baseline ("
        + str(len(baseline))
        + " baseline entries; "
        + str(len(allowed))
        + " allowed paths; "
        + str(len(allowed_under))
        + " allow-under directories; "
        + str(len(allowed_modify))
        + " allow-modify paths; "
        + str(len(allowed_append))
        + " allow-log-entry paths; "
        + str(len(allowed_dated))
        + " allow-dated paths; "
        + (
            "bytecode caches allowed; "
            if allow_bytecode
            else "bytecode caches not allowed; "
        )
        + "root .git directory ignored; symlinks not followed)"
    )


if __name__ == "__main__":
    main()
