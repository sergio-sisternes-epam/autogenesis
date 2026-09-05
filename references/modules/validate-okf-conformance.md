---
name: autogenesis/modules/validate-okf-conformance
description: Internal Autogenesis module. Resolve the target repository's declared Atlas, apply the substrate contract to the skill named okf, and run its pure-format validator (frontmatter, type, reserved files). Legacy wiki is read-only evidence, never the live store. Advisory only.
internal: true
---

# validate-okf-conformance

Advisory only. Does **not** mutate the target.

## Procedure

1. Locate the target skill root.
2. Resolve the target repository's declared Atlas through workflow-discipline
   (Atlas mount with no `--target`, then `atlas resolve`). If no store is
   declared or resolution fails, report the blocking gap; do not validate a
   legacy `references/wiki/` as the live store.
3. Apply the multi-harness substrate contract to the skill named `okf`:
   - Locate by name from the harness’s available skills list.
   - Load the full SKILL.md body with the on-demand loader.
   - Follow the loaded body (or its authority module) exactly to validate claim-bearing pages in the chosen store.
4. Prefer also running `atlas compile --root <atlas>` when Atlas is present (structural + link checks).
5. Emit:

   ```text
   FACET: validate-okf-conformance
   target: <path or name>
   store: atlas | none
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
