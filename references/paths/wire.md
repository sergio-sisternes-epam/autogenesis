---
name: autogenesis/paths/wire
description: Use this path only for human-approved wiring of a skill into a parent or peer with recorded provenance of exact skill name and version. Autogenesis never auto-wires.
path_id: wire
default: false
subject_scope: either
---

# Path: wire

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
