---
name: autogenesis/modules/validate-progressive-disclosure
description: Internal Autogenesis module. Check that a target skill package obeys progressive disclosure — thin registry, path modules under references/paths/, internal modules under references/modules/, one-path-at-a-time, no silent path→path invokes, on-demand load only.
internal: true
---

# validate-progressive-disclosure

Advisory only. Does **not** mutate the target.

## Procedure

1. Locate the target skill root (from subject or explicit path).
2. Verify:
   - Root SKILL.md contains only a thin capabilities / registry table (stubs), not full procedures.
   - Detailed procedures live under `references/paths/` (paths) or `references/modules/` (internal progressive modules).
   - No path module silently invokes another path without an explicit Enter card / path_module read.
   - Modules are loaded only when the current request needs them (no eager bulk load).
3. Emit:

   ```text
   FACET: validate-progressive-disclosure
   target: <path or name>
   thin_registry: pass | gaps
   path_module_separation: pass | gaps
   one_path_at_a_time: pass | gaps
   on_demand_only: pass | gaps
   gaps:
     - <file:section> — <missing or violated rule>
   status: pass | needs-work
   ```

## Non-goals

- Full design-quality review (that is genesis).
- Nesting/substrate wording (that is validate-skill-import-links).
- Mutation of the target.
