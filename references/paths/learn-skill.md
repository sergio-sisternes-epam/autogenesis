---
name: autogenesis/paths/learn-skill
description: Use this path to formalise a peer-link from the calling/subject skill to another skill's repository-declared Atlas. Legacy wiki is read-only evidence. Progressive disclosure pointers only; never copy peer content or mutate the peer.
path_id: learn-skill
default: false
subject_scope: subject-atlas
---

# Path: learn-skill (peer-link)

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
