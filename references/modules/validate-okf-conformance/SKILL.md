---
name: validate-okf-conformance
description: Audit subject-store format through Atlas and OKF.
metadata:
  autogenesis-parent: autogenesis
  autogenesis-role: support
---

# validate-okf-conformance

Advisory only. Does **not** mutate the target.

## Arguments

- Required: `target`.
- Optional: `store_hint`, `format_scope`.
- Do not override parent-owned subject, mode, operation, work identity, Atlas, or approval.

Follow `<skill_root>/references/modules/workflow-discipline/SKILL.md` and its
invocation contract. The parent reads this entrypoint and issues a support
request with its configured compact card before the procedure. Keep the active
operation and inherited context; return the facet result and an honest receipt.
A store_hint cannot override the parent's resolved Atlas. Shared assets resolve
from skill_root, not cwd. Auditing another target does not change write-home.

## Procedure

1. Locate the target skill root.
2. Determine whether the target declares OKF or Atlas integration.
   - If neither is adopted, report n/a with that reason. A plain S8 skill
     does not require runtime memory merely because Autogenesis designed it.
     Skip format validation and compile; proceed to the report.
   - For declared Atlas integration, resolve the already mounted target store
     through Atlas and retain the result as a local read-only review binding,
     not a change to the parent-owned write-home. Missing configuration or
     failed resolution is a gap, not n/a; do not mount or repair the target
     during an advisory review.
   - For a standalone OKF bundle, use its declared bundle root without
     requiring an Atlas. Do not validate legacy storage as a live Atlas.
3. If step 2 found declared OKF or Atlas integration, apply the multi-harness
   substrate contract to the skill named `okf`; otherwise retain the `n/a`
   result and skip this load:
   - Locate by name from the harness’s available skills list.
   - Load the full SKILL.md body with the on-demand loader.
   - Follow the loaded body (or its authority module) exactly to validate claim-bearing pages in the chosen store.
4. Prefer also running `atlas compile --root <atlas>` when Atlas is present (structural + link checks).
5. Emit:

   ```text
   FACET: validate-okf-conformance
   target: <path or name>
   store: atlas | okf-bundle | none
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
