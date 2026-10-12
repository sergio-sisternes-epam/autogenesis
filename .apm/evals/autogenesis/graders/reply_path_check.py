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
An instruction to use references/atlas is not a refusal, whatever the
wording. Each use-verb (use, write, save, store, put, keep, persist,
place or move, including ordinary inflections) followed within six words
by references/atlas is checked in Python, without a lookbehind. The scan
reads the same sentence before that verb, back to the previous . ! ? or
newline, and no more than 40 characters. A negation or refusal cue in
that prefix (not, n't, never, no longer, instead of, rather than,
cannot, won't, refuse, declined, avoid) keeps the occurrence a refusal.
Without one, the reply tells the reader to use the named path and fails.
A refusal earlier in the reply does not excuse that instruction.
"Please use references/atlas for all future plans." fails. "I did not
save the plan in references/atlas" does not.
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
# Positive-use scan. Python re, no lookaround. Each use-verb is paired
# only with references/atlas in the same sentence, within six words.
# Six words is the same window as the refusal relations, and it still
# reaches "use the named legacy storage at references/atlas". A later
# instruction is not swallowed by an earlier negated verb.
SENTENCE_LOOKBACK = 40
USE_PATH_WORD_WINDOW = 6
USE_VERB_PATTERN = (
    r"\b(?:use|uses|used|using|write|writes|wrote|writing|written|"
    r"save|saves|saved|saving|store|stores|stored|storing|"
    r"put|puts|putting|keep|keeps|kept|keeping|"
    r"persist|persists|persisted|persisting|"
    r"place|places|placed|placing|move|moves|moved|moving)\b"
)
# Apostrophe-less didnt/dont/wont/cant are the same cues the refusal
# patterns already accept, so a recognised refusal is not also an instruction.
NEGATION_CUE_PATTERN = (
    r"n't|\b(?:not|never|cannot|didnt|dont|wont|cant)\b|"
    r"\bno longer\b|\binstead of\b|\brather than\b|"
    r"\bwon't\b|\brefuse|\bdeclined\b|\bavoid"
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
USE_VERB = re.compile(USE_VERB_PATTERN, re.IGNORECASE)
NEGATION_CUE = re.compile(NEGATION_CUE_PATTERN, re.IGNORECASE)


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


def sentence_prefix(text, verb_start):
    """Same-sentence text before a use-verb, capped at SENTENCE_LOOKBACK."""
    start = max(0, verb_start - SENTENCE_LOOKBACK)
    window = text[start:verb_start]
    boundary = -1
    for mark in ".!?\n":
        found = window.rfind(mark)
        if found > boundary:
            boundary = found
    if boundary >= 0:
        return window[boundary + 1 :]
    return window


def followed_by_named_path(after):
    """True when references/atlas is within a few words, same sentence."""
    end = len(after)
    for mark in ".!?\n":
        found = after.find(mark)
        if found >= 0 and found < end:
            end = found
    words = re.findall(r"\S+", after[:end])
    for word in words[: USE_PATH_WORD_WINDOW + 1]:
        token = word.lower().strip(".,:;!?\"'")
        if token == "references/atlas" or token.startswith("references/atlas/"):
            return True
    return False


def tells_reader_to_use_named_path(reply):
    for match in USE_VERB.finditer(reply):
        if not followed_by_named_path(reply[match.end() :]):
            continue
        prefix = sentence_prefix(reply, match.start())
        if NEGATION_CUE.search(prefix) is None:
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
