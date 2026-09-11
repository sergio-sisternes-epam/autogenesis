---
name: validate-progressive-disclosure
description: Check module packaging, loading, and on-demand disclosure.
metadata:
  autogenesis-parent: autogenesis
  autogenesis-role: support
---

# validate-progressive-disclosure

Advisory only. Does **not** mutate the target.

## Arguments

- Required: `target`.
- Optional: `registry_hint`, `module_scope`.
- Do not override parent-owned subject, mode, operation, work identity, Atlas, or approval.

Follow `<skill_root>/references/modules/workflow-discipline/SKILL.md` and its
invocation contract. The parent reads this entrypoint and issues a support
request with its configured compact card before the procedure. Keep the active
operation and inherited context; return the facet result and an honest receipt.
Shared assets resolve from skill_root, not cwd.

## Procedure

1. Locate the target skill root (from subject or explicit path).
2. Identify the chosen layout, then verify:
   - A short single-procedure skill may keep its procedure in root SKILL.md.
     Do not require modules merely to obtain a thin registry.
   - For S8 adopters, the parent selects private entrypoints under
     `references/modules/<name>/SKILL.md`; detailed resources remain local.
   - Routing entries match module names and resolve within the package.
     Optional parent/role metadata is checked if declared, not required.
     Private modules are not separate catalogue exports.
   - Read the chosen entrypoint before its procedure. When cards are enabled,
     show the request cue; no JSON request or trace interpreter is required.
   - Off/absent cards skip rendering, not loading, approval or context checks.
   - Module-local and shared references use their declared roots, not cwd.
   - Modules are loaded only when the current request needs them (no eager bulk load).
   - Inputs, boundaries, outcomes and blockers are understandable from the
     instructions. Do not require specific headings or machine schemas.
3. Emit:

   ```text
   FACET: validate-progressive-disclosure
   target: <path or name>
   thin_registry: pass | gaps | n/a
   module_resource_separation: pass | gaps | n/a
   one_operation_at_a_time: pass | gaps | n/a
   parent_routing: pass | gaps | n/a
   reference_resolution: pass | gaps
   on_demand_only: pass | gaps
   applicability: <chosen layout and reasons for n/a>
   gaps:
     - <file:section> — <missing or violated rule>
   status: pass | needs-work
   ```

## Non-goals

- Full design-quality review (that is genesis).
- Nesting/substrate wording (that is validate-skill-import-links).
- Mutation of the target.
