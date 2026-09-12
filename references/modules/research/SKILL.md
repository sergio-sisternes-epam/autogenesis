---
name: research
description: Expand the subject Atlas with sourced knowledge.
metadata:
  autogenesis-parent: autogenesis
  autogenesis-role: operation
---

# Operation: research

## Arguments

- Required: `question`.
- Optional: `source_material`, `capture_scope`.
- Do not override parent-owned subject, mode, operation, work identity, Atlas, or approval.

Follow `<skill_root>/references/modules/workflow-discipline/SKILL.md` and its
invocation contract. The parent resolves and reads this entrypoint, issues an
operation request and emits its configured full card before the procedure.
Resolve shared assets from skill_root, siblings from the registry, not cwd.
Return a receipt with actual results; a card alone never proves execution.

## Procedure

1. Bind subject; resolve the process root from the active subject repository
   through workflow-discipline (Atlas mount with no `--target`, then
   `atlas resolve <atlas_id>`).
2. User material and/or controlled web research.
3. Capture external material into the subject Atlas (prefer experiences/resources under `autogenesis/`; cite local paths only for derived knowledge).
4. Optional knowledge extraction after capture; sources-check / validate; `atlas compile` green.

## Gates

G0, G1, G2, G6 as applicable.

## Non-goals

Does not replace genesis design; does not implement SKILL changes.
