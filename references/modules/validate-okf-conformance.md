---
name: autogenesis/modules/validate-okf-conformance
description: Internal Autogenesis module. When a target skill contains a process store (prefer references/atlas/, else legacy references/wiki/), apply the substrate contract to the skill named okf and run its pure-format validator (frontmatter, type, reserved files). Advisory only.
internal: true
---

# validate-okf-conformance

Advisory only. Does **not** mutate the target.

## Procedure

1. Locate the target skill root.
2. Prefer `references/atlas/` as the process store; fall back to legacy `references/wiki/` only if Atlas is absent. If neither exists → report `n/a` and stop.
3. Apply the multi-harness substrate contract to the skill named `okf`:
   - Locate by name from the harness’s available skills list.
   - Load the full SKILL.md body with the on-demand loader.
   - Follow the loaded body (or its authority module) exactly to validate claim-bearing pages in the chosen store.
4. Prefer also running `atlas compile --root <atlas>` when Atlas is present (structural + link checks).
5. Emit:

   ```text
   FACET: validate-okf-conformance
   target: <path or name>
   store: atlas | wiki | none
   okf_status: pass | gaps | n/a
   atlas_compile: pass | fail | n/a
   gaps:
     - <file or rule> — <violation>
   status: pass | needs-work | n/a
   ```

## Non-goals

- Live ingest / query / expand of any session store (that is atlas / okf-wiki operational paths).
- Mutation of the target store.
- Nesting or progressive-disclosure checks.
