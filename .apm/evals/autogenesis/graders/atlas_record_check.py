#!/usr/bin/env python3
"""Fail-closed Atlas plan and work-node check.

Resolves each workspace-relative path, reads it without following symlinks,
and checks frontmatter status. A path may contain one {date} placeholder in
its final component. {date} matches a real YYYY-MM-DD calendar date. The
parent directory is lstat-verified and listed without following links;
exactly one matching regular file is required. Every {date} path in one
invocation must resolve to the same date. Zero matches is missing; two or
more is ambiguous.

--exists-only checks existence, uniqueness and the shared date only.
Otherwise exactly one top-level status key must be a simple plain or
quoted scalar. --status may be repeated; any listed value is accepted.
When --status is omitted the allowed value is designed. --status-for
REL VALUE may be repeated and names one allowed value for that positional
path. When it is used, only those paths are status-checked; every other
positional path is resolved for existence and the shared date and is not
read. --status and --status-for cannot be combined. A trailing `#` comment
counts only when at least one space or tab separates it from the scalar.
Only a space or a tab is whitespace in this parser. A NBSP or other
Unicode space is not stripped and is not a comment separator, so the
value fails closed. `#` glued to a closing quote is not a comment, and a
plain token such as `designed#x` is that whole token, not `designed`. A
nested status key is not that top-level key. --must-match applies each expression to the first
resolved path with Python re.search.

os.lstat every component below the workspace root. A symlink, or the wrong
file type, fails closed before the read. The read uses O_NOFOLLOW. Indented
frontmatter, a column-0 block sequence after an empty value, and a blank
line belong to the preceding non-status key and are skipped. A tab-indented
line, a continuation before the first key, a column-0 sequence item after an
inline value, and an unterminated frontmatter fail closed.

program_grader.go does not set the child working directory and does not
rewrite arguments. python3 resolves this script from the Waza process
working directory. Relative paths in the task files match the run layout
in the suite README.
"""

import datetime
import os
import re
import stat
import sys
from pathlib import Path


USAGE = (
    "usage: atlas_record_check.py REL... "
    "[--exists-only] [--status VALUE]... "
    "[--status-for REL VALUE]... [--must-match REGEX]..."
)

DATE_TEXT = re.compile(r"^\d{4}-\d{2}-\d{2}$")
KEY_LINE = re.compile(r"^([A-Za-z0-9_-]+):(.*)$")


def fail(message):
    print(message, file=sys.stderr)
    sys.exit(1)


def is_real_date(text):
    if not DATE_TEXT.fullmatch(text):
        return False
    try:
        datetime.date.fromisoformat(text)
    except ValueError:
        return False
    return True


def quoted_scalar(raw):
    quote = raw[0]
    if quote not in "'\"":
        return None
    out = []
    i = 1
    while i < len(raw):
        ch = raw[i]
        if quote == "'" and raw.startswith("''", i):
            out.append("'")
            i += 2
            continue
        if quote == '"' and ch == "\\":
            if i + 1 >= len(raw):
                return None
            mapping = {
                "\\": "\\",
                '"': '"',
                "'": "'",
                "n": "\n",
                "t": "\t",
                "r": "\r",
                "/": "/",
            }
            esc = raw[i + 1]
            if esc not in mapping:
                return None
            out.append(mapping[esc])
            i += 2
            continue
        if ch == quote:
            # A comment needs a space or tab before `#`. Optional trailing
            # spaces and tabs are fine. A Unicode space, or `#` glued to
            # the closing quote, is not a comment.
            rest = raw[i + 1 :]
            if rest.strip(" \t") == "":
                return "".join(out)
            if rest[0] in " \t" and rest.lstrip(" \t").startswith("#"):
                return "".join(out)
            return None
        out.append(ch)
        i += 1
    return None


def plain_scalar(raw):
    if not raw or raw[0] in "!&*{[}]|>%@`'\"?-":
        return None
    # A comment needs a space or tab before `#`. `designed#x` is one
    # plain scalar, and a NBSP before `#` is not a comment separator.
    cut = len(raw)
    for i, ch in enumerate(raw):
        if ch == "#" and (i == 0 or raw[i - 1] in " \t"):
            cut = i
            break
    value = raw[:cut].rstrip(" \t")
    if not value or any(ch in value for ch in ":{}[],&*!|>"):
        return None
    return value


def simple_scalar(raw):
    text = raw.strip(" \t")
    if not text:
        return None
    if text[0] in "'\"":
        return quoted_scalar(text)
    return plain_scalar(text)


def line_kind(line):
    if line.strip(" \t") == "":
        return "blank"
    if line[:1] == "\t":
        return "tab"
    if line[:1] == " ":
        return "indent"
    if line == "-" or line.startswith("- ") or line.startswith("-\t"):
        return "sequence"
    if line.startswith("#"):
        return "comment"
    return "other"


def status_of_text(text, label):
    """Return the single top-level status scalar, or fail closed."""
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        fail("missing YAML frontmatter: " + label)
    end = None
    for index, line in enumerate(lines[1:], 1):
        if line == "---":
            end = index
            break
    if end is None:
        fail("unterminated frontmatter: " + label)
    found = []
    seen_key = False
    preceding_empty = False
    index = 1
    while index < end:
        line = lines[index]
        kind = line_kind(line)
        if kind == "tab":
            fail("tab-indented frontmatter line: " + line)
        if kind == "blank" or kind == "comment":
            index += 1
            continue
        if kind == "indent" or kind == "sequence":
            if not seen_key:
                fail("continuation line before the first key: " + line)
            if kind == "sequence" and not preceding_empty:
                fail(
                    "column-0 sequence item after a key with an inline value: "
                    + line
                )
            index += 1
            continue
        match = KEY_LINE.fullmatch(line)
        if not match:
            fail("frontmatter line not understood: " + line)
        key = match.group(1)
        rest = match.group(2)
        if rest == "":
            empty = True
            raw = ""
        elif rest[0] in (" ", "\t"):
            empty = rest.strip(" \t") == ""
            raw = rest
        else:
            fail("frontmatter line not understood: " + line)
        if key.casefold() == "status" and key != "status":
            fail("frontmatter status key is not the plain key status: " + line)
        if key == "status":
            probe = index + 1
            while probe < end:
                probe_kind = line_kind(lines[probe])
                if probe_kind in ("blank", "comment"):
                    probe += 1
                    continue
                if probe_kind in ("indent", "tab", "sequence"):
                    fail("status value is not a simple scalar: " + line)
                break
            value = simple_scalar(raw)
            if value is None:
                fail(
                    "status value is not a simple plain or quoted scalar: "
                    + line
                )
            found.append(value)
        seen_key = True
        preceding_empty = empty
        index += 1
    if len(found) != 1:
        fail(
            "frontmatter must have exactly one status key, found "
            + str(len(found))
            + ": "
            + label
        )
    return found[0]


def workspace_relative(raw):
    candidate = Path(raw)
    if candidate.is_absolute() or not candidate.parts:
        fail("path escapes the workspace: " + raw)
    if any(part in ("", ".", "..") for part in candidate.parts):
        fail("path escapes the workspace: " + raw)
    if raw.count("{date}") > 1:
        fail("{date} placeholder must appear once: " + raw)
    rel = candidate.as_posix()
    if "{date}" in rel:
        parent, name = rel.rsplit("/", 1) if "/" in rel else ("", rel)
        if "{date}" in parent or name.count("{date}") != 1:
            fail("{date} placeholder must be in the final component: " + raw)
    return rel


def lstat_component(path, label):
    try:
        return os.lstat(path)
    except FileNotFoundError:
        return None
    except OSError as exc:
        fail("cannot lstat " + label + ": " + str(exc))


def real_leaf(root, rel, leaf_kind):
    """Return the real leaf path, None if missing, or fail closed.

    lstat each component. A symlink fails. Parents must be real
    directories. leaf_kind is "file" or "dir".
    """
    candidate = Path(rel)
    current = root
    for index, part in enumerate(candidate.parts):
        current = current / part
        label = Path(*candidate.parts[: index + 1]).as_posix()
        info = lstat_component(current, label)
        if info is None:
            return None
        if stat.S_ISLNK(info.st_mode):
            fail(label + " is a symlink")
        leaf = index == len(candidate.parts) - 1
        if leaf and leaf_kind == "file":
            if not stat.S_ISREG(info.st_mode):
                fail(label + " is not a regular file")
        elif not stat.S_ISDIR(info.st_mode):
            fail(label + " is not a directory")
    return current


def read_regular(path, label):
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
                data = b"".join(chunks)
                break
            chunks.append(block)
    except OSError as exc:
        fail("cannot read " + label + ": " + str(exc))
    finally:
        os.close(descriptor)
    try:
        return data.decode("utf-8")
    except UnicodeError:
        fail("not utf-8: " + label)


def list_real_dir(path, label):
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        fail("O_NOFOLLOW and O_DIRECTORY are required so listings never follow symlinks")
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError as exc:
        fail("cannot list " + label + ": " + str(exc))
    try:
        return os.listdir(descriptor)
    except OSError as exc:
        fail("cannot list " + label + ": " + str(exc))
    finally:
        os.close(descriptor)


def dated_name_match(name, pattern_name):
    prefix, suffix = pattern_name.split("{date}")
    if not name.startswith(prefix) or not name.endswith(suffix):
        return None
    middle = name[len(prefix) : len(name) - len(suffix) if suffix else None]
    if not is_real_date(middle):
        return None
    return middle


def resolve_one(root, rel):
    """Return (resolved_rel, date or None, error or None)."""
    if "{date}" not in rel:
        path = real_leaf(root, rel, "file")
        if path is None:
            return None, None, "missing " + rel
        return rel, None, None
    parent, pattern_name = rel.rsplit("/", 1) if "/" in rel else ("", rel)
    if parent:
        parent_path = real_leaf(root, parent, "dir")
        if parent_path is None:
            return None, None, "missing " + rel
        names = list_real_dir(parent_path, parent)
        parent_prefix = parent + "/"
    else:
        names = list_real_dir(root, ".")
        parent_prefix = ""
    matches = []
    for name in names:
        found = dated_name_match(name, pattern_name)
        if found is None:
            continue
        child_rel = parent_prefix + name
        # Fail closed on a symlink or the wrong type before counting it.
        real_leaf(root, child_rel, "file")
        matches.append((found, child_rel))
    if not matches:
        return None, None, "missing " + rel
    if len(matches) > 1:
        listed = ", ".join(sorted(item[1] for item in matches))
        return None, None, "ambiguous " + rel + ": " + listed
    found, child_rel = matches[0]
    return child_rel, found, None


def take_value(argv, index):
    if index >= len(argv) or argv[index].startswith("--"):
        fail(USAGE)
    return argv[index]


def parse_args(argv):
    paths = []
    exists_only = False
    statuses = []
    status_for = {}
    must_match = []
    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg == "--exists-only":
            exists_only = True
            index += 1
            continue
        if arg == "--status":
            value = take_value(argv, index + 1)
            if value not in statuses:
                statuses.append(value)
            index += 2
            continue
        if arg == "--status-for":
            path = workspace_relative(take_value(argv, index + 1))
            value = take_value(argv, index + 2)
            allowed = status_for.setdefault(path, [])
            if value not in allowed:
                allowed.append(value)
            index += 3
            continue
        if arg == "--must-match":
            if index + 1 >= len(argv):
                fail(USAGE)
            must_match.append(argv[index + 1])
            index += 2
            continue
        if arg.startswith("--"):
            fail("unexpected argument: " + arg)
        paths.append(workspace_relative(arg))
        index += 1
    if not paths:
        fail(USAGE)
    if exists_only and (statuses or status_for):
        fail("--exists-only cannot be combined with --status")
    if statuses and status_for:
        fail("--status cannot be combined with --status-for")
    for path in status_for:
        if path not in paths:
            fail("--status-for path is not checked: " + path)
    if not exists_only and not statuses and not status_for:
        statuses = ["designed"]
    return paths, exists_only, statuses, status_for, must_match


def expected_phrase(expected):
    if len(expected) == 1:
        return "expected " + repr(expected[0])
    return "expected one of " + ", ".join(repr(item) for item in expected)


def main():
    workspace = os.environ.get("WAZA_WORKSPACE_DIR", "")
    if not workspace:
        fail("WAZA_WORKSPACE_DIR is not set")
    root = Path(workspace)
    root_info = lstat_component(root, "workspace")
    if root_info is None or stat.S_ISLNK(root_info.st_mode) or not stat.S_ISDIR(root_info.st_mode):
        fail("workspace is not a directory")
    paths, exists_only, statuses, status_for, must_match = parse_args(sys.argv[1:])
    resolved = []
    dates = []
    problems = []
    for rel in paths:
        child, found_date, error = resolve_one(root, rel)
        if error:
            problems.append(error)
            continue
        resolved.append((rel, child))
        if found_date is not None:
            dates.append((child, found_date))
    if len({item[1] for item in dates}) > 1:
        problems.append(
            "dates differ: "
            + ", ".join(path + " " + found for path, found in dates)
        )
    if problems:
        fail("; ".join(problems))
    notes = []
    if not exists_only:
        for pattern, rel in resolved:
            # A path named by --status-for is checked against its own
            # values. Every other path in that invocation is date-only:
            # do not read its status or content.
            if status_for:
                expected = status_for.get(pattern)
                if expected is None:
                    continue
            else:
                expected = statuses
            value = status_of_text(read_regular(root / rel, rel), rel)
            if value not in expected:
                problems.append(
                    rel
                    + " status is "
                    + repr(value)
                    + ", "
                    + expected_phrase(expected)
                )
            else:
                notes.append(rel + " status " + repr(value))
    if must_match:
        first = resolved[0][1]
        text = read_regular(root / first, first)
        for pattern in must_match:
            if re.search(pattern, text) is None:
                problems.append(first + " does not match " + pattern)
    if problems:
        fail("; ".join(problems))
    if notes:
        print("; ".join(notes))
    print("resolved: " + " ".join(child for _, child in resolved))


if __name__ == "__main__":
    main()
