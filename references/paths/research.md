---
name: autogenesis/paths/research
description: Use this path to expand the subject skill’s corpus with user material or online research plus capture. Triggers on research, expand corpus, capture sources. Writes only into the subject Atlas via Atlas.
path_id: research
default: false
subject_scope: subject-atlas
---

# Path: research

## Procedure

1. Bind subject; process root = subject Atlas (`<subject>/references/atlas/`; when subject is autogenesis: `.atlas/github.com/sergio-sisternes-epam/autogenesis-atlas` after mount).
2. User material and/or controlled web research.
3. Capture external material into the subject Atlas (prefer experiences/resources under `autogenesis/`; cite local paths only for derived knowledge).
4. Optional knowledge extraction after capture; sources-check / validate; `atlas compile` green.

## Gates

G0, G1, G2, G6 as applicable.

## Non-goals

Does not replace genesis design; does not implement SKILL changes.
