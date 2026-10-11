# Optional Atlas enrichment

Packaged baseline for Autogenesis **v0.9.0**. Read this only when bundled
references do not answer the actual question.

## Rule

If the catalog, first-journey, or named module entrypoint already answers,
stop. Extra Atlas reads are optional, not required.

## Read-only retrieval

Attempt recall only when an `atlas_id` is already known without mounting
(inherited parent context, or exactly one mesh store name):

1. A checkout that merely contains `SCHEMA.json` is not the Atlas root.
2. Run `atlas resolve <atlas_id>` read-only. Do not mount, remount,
   authenticate, init, or repair. Use only the path that command returns.
3. Verify `<returned-root>/SCHEMA.json`. If resolve fails, returns nothing,
   or the schema is missing, stop as unavailable.

If no `atlas_id` is already known, the mesh is ambiguous, or resolve is
blocked, do not guess a root. Return limited help and the reason (missing
id, missing checkout, ambiguous mesh, missing schema, missing tool, denied
access, timeout, or unknown).

When a root is the resolve result, apply the multi-harness substrate
contract to the external `atlas` skill and load it with the harness skill
loader. Follow only a read-only recall tool or a page-read against that
root. Do not follow mount, init, remember, compile-for-write, or install
paths, and do not enter path `recall` as this operation. The tool is:

```text
python3 <atlas-skill>/scripts/atlas.py recall run "<question>" --root <returned-root> --json --engine grep
```

Do not pass `--profile`, do not run `atlas recall index build`, and do not
enable recall. `atlas recall` with a positional question is not a command.
Read only pages needed for the question (about 1–3). Do not build indexes.
Treat historical, draft, retired, or unapproved pages as evidence of risk,
not current packaged capability.

## Provenance

- `atlas_status`: `consulted` when a recall run or read ran; `unavailable` when a
  required retrieval step failed; `baseline-only` when none ran.
- `atlas_used`: only store IDs that contributed eligible evidence. Empty when
  consulted with no usable hit, or when retrieval failed before evidence.
- A successful recall run with no relevant hit is a knowledge gap, not
  unavailability.
