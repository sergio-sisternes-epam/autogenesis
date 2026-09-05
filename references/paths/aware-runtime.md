---
name: autogenesis/paths/aware-runtime
description: Use this path to inject or maintain Autogenesis-aware runtime (AwareHook) plus governance and mandatory closing step into a skill. Does not auto-implement improvement opportunities recorded at runtime.
path_id: aware-runtime
default: false
subject_scope: subject-atlas
---

# Path: aware-runtime

## Procedure
1. Use canonical template `references/aware-hook-template.md`.
2. Inject/update AwareHook + governance + closing step into subject skill as approved.
3. Resolve the subject Atlas through workflow-discipline. If no store is
   declared, use Atlas init with an existing remote or stop; never create a
   package-local memory skeleton.
4. Runtime records stay `source: runtime-aware`, `status: unverified`; never auto-implement.

## Gates
G0, G1, G2, G4 if material SKILL edit, G5/G6 as applicable.
