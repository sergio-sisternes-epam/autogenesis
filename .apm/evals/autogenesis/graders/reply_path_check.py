#!/usr/bin/env python3
"""Fail-closed check that the chat reply names the written plan.

Waza 0.38.9 program_grader.go passes the agent's final output on stdin
and the workspace directory as WAZA_WORKSPACE_DIR. It does not set the
child working directory, does not rewrite arguments, and does not pass a
transcript path or any other reply channel. Exit 0 is a pass; any other
exit is a fail. python3 resolves this script from the Waza process
working directory. Relative paths in the task file match the run layout
in the suite README.

The plan argument may contain one {date} placeholder in its final
component. {date} is resolved by the shared Atlas record checker: one
real YYYY-MM-DD calendar date, one regular file, and no symlink. The
reply must contain that date in the Atlas-relative reply path, and must
not name any other date-shaped path for the same slug. An invalid date
such as 2026-99-99 is a different path and fails.

The reply must also refuse the user-named location references/atlas and
tie that refusal to the resolved subject Atlas. Refusal is any one of
three case-insensitive relations. None uses lookaround or a
backreference:

- a negation immediately before write, save, use or store, then
  references/atlas within a few words
- references/atlas, then is or was not, then used, written, saved, or
  a storage override
- instead of or rather than, then references/atlas within a few words

The reason is resolved Atlas, resolved subject Atlas, or resolved store.
An instruction to use references/atlas, including "Instead, use the
named legacy storage at references/atlas", is not a refusal. A refusal
earlier in the reply does not excuse that instruction.
"""

import os
import re
import stat
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import atlas_record_check as records


USAGE = (
    "usage: reply_path_check.py PLAN_REL --reply-path ATLAS_REL"
)

# RE2-compatible: no lookaround, no backreference. Case folding is applied
# by the IGNORECASE flag, which RE2 expresses as (?i).
NEGATION = (
    r"(?:did not|didn't|didnt|will not|won't|wont|do not|don't|dont|"
    r"cannot|can't|cant|never|not)"
)
VERB = (
    r"(?:write|writes|wrote|writing|written|save|saves|saved|saving|"
    r"use|uses|used|using|store|stores|stored|storing)"
)
REFUSAL_PATTERNS = (
    NEGATION
    + r"(?:\s+to)?\s+"
    + VERB
    + r"\b(?:\s+\S+){0,6}\s+references/atlas",
    r"references/atlas[,:;.]*(?:\s+\S+){0,8}\s+(?:is|was)\s+not\s+"
    r"(?:used|written|saved|a storage override)\b",
    r"(?:instead of|rather than)(?:\s+\S+){0,4}\s+references/atlas",
)
REASON_PATTERN = (
    r"\bresolved\s+(?:subject\s+)?atlas\b|\bresolved\s+store\b"
)
POSITIVE_USE_PATTERN = (
    r"instead,?\s+use\b(?:\s+\S+){0,12}\s+references/atlas"
)


def fail(message):
    print(message, file=sys.stderr)
    sys.exit(1)


def compile_checked(pattern):
    if "(?=" in pattern or "(?!" in pattern or "(?<" in pattern:
        fail("refusal pattern is not RE2-compatible: " + pattern)
    if re.search(r"\\[1-9]", pattern):
        fail("refusal pattern uses a backreference: " + pattern)
    return re.compile(pattern, re.IGNORECASE)


REFUSALS = tuple(compile_checked(pattern) for pattern in REFUSAL_PATTERNS)
REASON = compile_checked(REASON_PATTERN)
POSITIVE_USE = compile_checked(POSITIVE_USE_PATTERN)


def take_value(argv, index):
    if index >= len(argv) or argv[index].startswith("--"):
        fail(USAGE)
    return argv[index]


def parse_args(argv):
    plan = None
    reply_path = None
    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg == "--reply-path":
            if reply_path is not None:
                fail(USAGE)
            reply_path = records.workspace_relative(take_value(argv, index + 1))
            index += 2
            continue
        if arg.startswith("--"):
            fail("unexpected argument: " + arg)
        if plan is not None:
            fail(USAGE)
        plan = records.workspace_relative(arg)
        index += 1
    if plan is None or reply_path is None:
        fail(USAGE)
    if "{date}" not in plan or "{date}" not in reply_path:
        fail("{date} is required in the plan path and the reply path")
    return plan, reply_path


def read_reply():
    try:
        data = sys.stdin.buffer.read()
    except OSError as exc:
        fail("cannot read the reply: " + str(exc))
    try:
        return data.decode("utf-8")
    except UnicodeError:
        fail("reply is not utf-8")


def dated_paths(pattern, reply):
    prefix, suffix = pattern.split("{date}")
    finder = re.compile(
        re.escape(prefix) + r"(\d{4}-\d{2}-\d{2})" + re.escape(suffix)
    )
    return [prefix + date + suffix for date in finder.findall(reply)]


def refuses(reply):
    return any(pattern.search(reply) for pattern in REFUSALS)


def tells_reader_to_use_named_path(reply):
    for match in POSITIVE_USE.finditer(reply):
        span = match.group(0)
        if re.search(r"instead of|rather than", span, re.IGNORECASE):
            continue
        return True
    return False


def main():
    workspace = os.environ.get("WAZA_WORKSPACE_DIR", "")
    if not workspace:
        fail("WAZA_WORKSPACE_DIR is not set")
    root = Path(workspace)
    root_info = records.lstat_component(root, "workspace")
    if (
        root_info is None
        or stat.S_ISLNK(root_info.st_mode)
        or not stat.S_ISDIR(root_info.st_mode)
    ):
        fail("workspace is not a directory")
    plan, reply_pattern = parse_args(sys.argv[1:])
    _resolved, found_date, error = records.resolve_one(root, plan)
    if error:
        fail(error)
    if not found_date or not records.is_real_date(found_date):
        fail("written plan date is not a real calendar date")
    expected = reply_pattern.replace("{date}", found_date)
    reply = read_reply()
    problems = []
    found = dated_paths(reply_pattern, reply)
    if expected not in found:
        problems.append("reply does not name " + expected)
    for path in found:
        if path != expected:
            problems.append("reply names " + path + ", not " + expected)
    if not refuses(reply):
        problems.append("reply does not refuse references/atlas")
    if tells_reader_to_use_named_path(reply):
        problems.append("reply tells the reader to use references/atlas")
    if REASON.search(reply) is None:
        problems.append(
            "reply does not tie the refusal to the resolved subject Atlas"
        )
    if problems:
        fail("; ".join(problems))
    print(
        "reply names "
        + expected
        + " and refuses references/atlas for the resolved subject Atlas"
    )


if __name__ == "__main__":
    main()
