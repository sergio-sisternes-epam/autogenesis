---
name: learn-skill
description: Formalise a peer link to another skill’s repository-declared Atlas.
metadata:
  autogenesis-parent: autogenesis
  autogenesis-role: operation
---

# Operation: learn-skill (peer-link)

## Arguments

- Required: `peer_identity`.
- Optional: `evidence`, `reliance_notes`.
- Do not override parent-owned subject, mode, operation, work identity, Atlas, or approval.

Follow `<skill_root>/references/modules/workflow-discipline/SKILL.md` and its
invocation contract. The parent resolves and reads this entrypoint, issues an
operation request and emits its configured full card before the procedure.
Resolve shared assets from skill_root and siblings from the registry, not cwd.
Return a receipt with actual results, never card-only completion.

## Procedure

1. Probe the peer repository's `atlas-mesh.json`. Resolve an explicit store id,
   or the only store when exactly one exists. Multiple stores without an
   explicit id are ambiguous; stop rather than guessing. A legacy
   `references/wiki/` is read-only archive evidence, not a live store.
2. Write usage-memory / peer-link experience in the **subject** Atlas only (`autogenesis/experiences/` via atlas remember).
3. Record what we rely on, contracts, progressive-disclosure load notes.
4. `atlas compile` green on subject Atlas. Stop.

## Gates

G0, G1, G2, G6 as applicable.

## Non-goals

No auto-wiring; no peer mutation; no content copy.
