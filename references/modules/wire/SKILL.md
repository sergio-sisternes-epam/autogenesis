---
name: wire
description: Record approved wiring provenance for a skill.
metadata:
  autogenesis-parent: autogenesis
  autogenesis-role: operation
---

# Operation: wire

## Arguments

- Required: `target`, `version_evidence`.
- Optional: `provenance`, `reversible_note`.
- Do not override parent-owned subject, mode, operation, work identity, Atlas, or approval.

Follow `<skill_root>/references/modules/workflow-discipline/SKILL.md` and its
invocation contract. The parent resolves and reads this entrypoint, issues an
operation request and emits its configured full card before the procedure.
Target/version arguments do not grant approval: revalidate the parent's actual
authorisation. Resolve shared assets from skill_root, never cwd, and return
an honest receipt. Unknown partial wiring must not be automatically replayed.

## Procedure
1. Explicit human approval to wire.
2. Record provenance: skill name + version/hash trusted.
3. Apply minimal wiring change; record approval experience in the resolved
   subject Atlas.
4. Wiring must remain reversible in documentation.
5. Compile the resolved subject Atlas and require exit 0.

## Gates
G0, G1, G4-style human approval, G6.

## Non-goals
Never part of automatic design/implement path completion.
