---
name: aware-runtime
description: Inject or maintain Autogenesis-aware runtime governance.
metadata:
  autogenesis-parent: autogenesis
  autogenesis-role: operation
---

# Operation: aware-runtime

## Arguments

- Required: `target_artifact`.
- Optional: `scope`, `governance_note`, `closing_step`.
- Do not override parent-owned subject, mode, operation, work identity, Atlas, or approval.

Follow `<skill_root>/references/modules/workflow-discipline/SKILL.md` and its
invocation contract. The parent resolves and reads this entrypoint, issues an
operation request and emits its configured full card before the procedure.
Scope is requested work, not approval evidence. Resolve shared assets from
skill_root and siblings from the registry, not cwd. Return an honest receipt.

## Procedure
1. Use canonical template
   `<skill_root>/references/aware-hook-template.md`.
2. Inject/update AwareHook + governance + closing step into subject skill as approved.
3. Resolve the subject Atlas through workflow-discipline. If no store is
   declared, use Atlas init with an existing remote or stop; never create a
   package-local memory skeleton.
4. Runtime records stay `source: runtime-aware`, `status: unverified`; never auto-implement.

## Gates
G0, G1, G2, G4 if material SKILL edit, G5/G6 as applicable.
