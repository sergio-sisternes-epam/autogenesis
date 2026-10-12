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
Those three relations are unchanged. They are not the use guard.

The use guard is a bounded lexical check. It cannot prove meaning,
quotation, or that a cue actually governs a verb. It splits the reply
into clauses and fails when any clause is a use clause that is not a
refusal. Sentence boundaries are . ! ? and newline. Clause boundaries
are , ; : and the words but, however, although, though, yet, so, and
the phrase and then. A full stop inside a token, including the stop in
a .md suffix, is also a boundary, so words on opposite sides of it are
not one clause.

A clause is a use clause when it mentions references/atlas and contains
a use-verb, in either order. Use-verbs are use, uses, used, using;
write, writes, wrote, writing, written; save, saves, saved, saving;
store, stores, stored, storing; put, puts, putting; keep, keeps, kept,
keeping; persist, persists, persisted, persisting; place, places,
placed, placing; move, moves, moved, moving.

Government is evaluated per matched (verb, path) pair. Every use-verb
is paired with every references/atlas occurrence in the same clause.
A pair is governed only when one of these holds, and no other form
counts:

- a cue within three words before that verb: not; n't inside the word
  (didn't, won't, don't, can't); the apostrophe-less didnt, dont, wont
  and cant already accepted by the refusal relations; never; no longer;
  cannot; refuse to; refused to; declined to; avoid; avoided
- the passive or modal form references/atlas (is|was|will|should|must|
  can) (not|n't|never) (be )?verb, covering that verb for that path
  occurrence
- that path occurrence is the object of instead of or rather than, with
  at most three words between the phrase and that occurrence, and the
  verb does not also govern another references/atlas occurrence in the
  clause that is not such an object

Any un-governed pair fails the grader. An instead-of exemption on one
occurrence does not excuse a use of another. A refusal in another
clause does not excuse it. In particular the check rejects:

- references/atlas should be used for future plans.
- This is not required, but please use references/atlas for the next plan.
- Please use references/atlas for all future plans.
- You can save plans in references/atlas next time.
- Instead, use the named legacy storage at references/atlas.
- Use references/atlas for plans instead of references/atlas for drafts.

It does not reject a same-clause governed use, including "I did not
save the plan in references/atlas", "references/atlas was not used",
and "save the plan rather than references/atlas". A cue more than
three words before the verb does not govern it. An instead-of phrase
more than three words before that path occurrence does not exempt it.

Known limits (accepted by the owner on 2026-10-12 as a bounded lexical
check):

- repeated references/atlas occurrences under one "rather than" or
  "instead of" may still be read as exempt
- the refusal and the resolved-Atlas reason are checked independently,
  so a reply that refuses but denies the reason can pass
- the check cannot prove meaning
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
# Clause-scoped use guard. Python re, no lookaround. A use clause names
# references/atlas and a use-verb in either order. Government is per
# matched (verb, path) pair, as the module docstring lists. An instead-of
# exemption covers only the path occurrence it governs, and only when
# that verb governs no other un-exempted occurrence in the clause. A
# cue in another clause does not.
VERB_CUE_WORDS = 3
PATH_GAP_WORDS = 3
USE_VERBS = (
    "use",
    "uses",
    "used",
    "using",
    "write",
    "writes",
    "wrote",
    "writing",
    "written",
    "save",
    "saves",
    "saved",
    "saving",
    "store",
    "stores",
    "stored",
    "storing",
    "put",
    "puts",
    "putting",
    "keep",
    "keeps",
    "kept",
    "keeping",
    "persist",
    "persists",
    "persisted",
    "persisting",
    "place",
    "places",
    "placed",
    "placing",
    "move",
    "moves",
    "moved",
    "moving",
)
USE_VERB_PATTERN = r"\b(?:" + "|".join(USE_VERBS) + r")\b"
NAMED_PATH_PATTERN = r"\breferences/atlas\b"
# didnt/dont/wont/cant are the apostrophe-less cues the refusal relations
# already accept, so a recognised refusal is not also an instruction.
# n't is matched inside the word, so didn't, won't, don't and can't count.
SINGLE_WORD_CUES = frozenset(
    {
        "not",
        "never",
        "cannot",
        "wont",
        "didnt",
        "dont",
        "cant",
        "avoid",
        "avoided",
    }
)
PAIR_CUES = frozenset(
    {
        "no longer",
        "refuse to",
        "refused to",
        "declined to",
    }
)
PASSIVE_REFUSAL_PATTERN = (
    NAMED_PATH_PATTERN
    + r"\s+(?:is|was|will|should|must|can)"
    + r"(?:n't|\s+not|\s+never)"
    + r"(?:\s+be)?"
    + r"\s+"
    + USE_VERB_PATTERN
)
INSTEAD_BEFORE_PATH_PATTERN = (
    r"\b(?:instead\s+of|rather\s+than)\b"
    + r"(?:\s+\S+){0,"
    + str(PATH_GAP_WORDS)
    + r"}\s+"
    + NAMED_PATH_PATTERN
)
CLAUSE_WORDS = ("but", "however", "although", "though", "yet", "so")
CLAUSE_BOUNDARY_PATTERN = (
    r"[.!?,\r\n;:]|\band\s+then\b|\b(?:" + "|".join(CLAUSE_WORDS) + r")\b"
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
USE_VERB = compile_checked(USE_VERB_PATTERN)
NAMED_PATH = compile_checked(NAMED_PATH_PATTERN)
PASSIVE_REFUSAL = compile_checked(PASSIVE_REFUSAL_PATTERN)
INSTEAD_BEFORE_PATH = compile_checked(INSTEAD_BEFORE_PATH_PATTERN)
CLAUSE_BOUNDARY = compile_checked(CLAUSE_BOUNDARY_PATTERN)


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


def split_clauses(text):
    """Split on sentence and clause boundaries. Boundaries are not kept."""
    clauses = []
    start = 0
    for match in CLAUSE_BOUNDARY.finditer(text):
        chunk = text[start:match.start()].strip()
        if chunk:
            clauses.append(chunk)
        start = match.end()
    tail = text[start:].strip()
    if tail:
        clauses.append(tail)
    return clauses


def clause_words(text):
    words = []
    for raw in re.findall(r"\S+", text):
        token = raw.lower().strip(".,:;!?\"'()[]{}")
        if token:
            words.append(token)
    return words


def cue_governs_verb(words_before):
    """True when a listed cue sits in the three words before the verb."""
    window = words_before[-VERB_CUE_WORDS:]
    for word in window:
        if word in SINGLE_WORD_CUES or "n't" in word:
            return True
    for index in range(len(window) - 1):
        if window[index] + " " + window[index + 1] in PAIR_CUES:
            return True
    return False


def path_is_instead_object(clause, path_match):
    """True when instead of / rather than has at most three words before this path."""
    window = clause[: path_match.end()]
    return any(
        match.end() == path_match.end()
        for match in INSTEAD_BEFORE_PATH.finditer(window)
    )


def passive_covers_pair(clause, verb_match, path_match):
    """True when the passive or modal negation covers this verb for this path."""
    for match in PASSIVE_REFUSAL.finditer(clause):
        if (
            match.start() <= path_match.start()
            and path_match.end() <= match.end()
            and match.start() <= verb_match.start()
            and verb_match.end() <= match.end()
        ):
            return True
    return False


def clause_tells_reader_to_use(clause):
    """True when any (verb, path) pair in this clause is ungoverned."""
    paths = list(NAMED_PATH.finditer(clause))
    verbs = list(USE_VERB.finditer(clause))
    if not paths or not verbs:
        return False
    exempted = [path_is_instead_object(clause, path) for path in paths]
    any_unexempted = not all(exempted)
    for verb in verbs:
        verb_negated = cue_governs_verb(clause_words(clause[: verb.start()]))
        for path, path_exempted in zip(paths, exempted):
            if verb_negated:
                continue
            if passive_covers_pair(clause, verb, path):
                continue
            # The instead-of object is exempt only when this verb governs
            # no other un-exempted references/atlas occurrence.
            if path_exempted and not any_unexempted:
                continue
            return True
    return False


def tells_reader_to_use_named_path(reply):
    return any(
        clause_tells_reader_to_use(clause) for clause in split_clauses(reply)
    )


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
