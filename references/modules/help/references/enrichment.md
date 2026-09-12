# Optional Atlas enrichment

Packaged baseline for Autogenesis **v0.7.0**. Read this only when bundled
references do not answer the actual question.

## Rule

If the catalog, first-journey, or named module entrypoint already answers,
stop. Extra Atlas reads are optional, not required.

## Read-only retrieval

Attempt query only when a subject or Autogenesis Atlas is already resolvable
without mounting:

1. Prefer parent context `atlas_root` when it contains `SCHEMA.json`.
2. Else, if `atlas-mesh.json` names exactly one store (or an explicit
   `atlas_id`) and that checkout already has `SCHEMA.json`, use that root.
3. If neither is resolvable, do not mount, authenticate, init, or repair.
   Return limited help and the reason (missing checkout, ambiguous mesh,
   missing schema, missing tool, denied access, timeout, or unknown).

When a root is resolvable, search or read only pages needed for the question
(about 1–3). Do not build indexes. Do not remember, compile for write, install
schema, or follow mutating Atlas paths. Treat historical, draft, retired, or
unapproved pages as evidence of risk, not current packaged capability.

## Provenance

- `atlas_status`: `consulted` when a search or read ran; `unavailable` when a
  required retrieval step failed; `baseline-only` when none ran.
- `atlas_used`: only store IDs that contributed eligible evidence. Empty when
  consulted with no usable hit, or when retrieval failed before evidence.
- A successful search with no relevant hit is a knowledge gap, not
  unavailability.
