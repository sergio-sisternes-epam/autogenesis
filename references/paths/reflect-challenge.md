---
name: autogenesis/paths/reflect-challenge
description: Use this path to reflect on current vs recalled subject behaviours and write a behaviour challenge with clear objective and motivations. Stored as an Atlas experience; might not be used. Does not implement fixes.
path_id: reflect-challenge
default: false
subject_scope: subject-atlas
---

# Path: reflect-challenge

## Procedure
1. Load subject SKILL + relevant experiences from the resolved subject Atlas.
2. State current behaviours in this Run or implementation under review.
3. Write the challenge experience through Atlas `remember` in the resolved
   subject Atlas, using template `references/behaviour-challenge-template.md`
   with objective, motivations, tension, claims, and use disposition.
4. Default `status: unverified`. **Do not implement** from this experience.
5. Require `atlas compile --root <resolved-subject-atlas>` exit 0.

## Gates
G0, G1, G2, G6 as applicable. Not G4.

## Non-goals
Not a substitute for design internal think-challenge module (G3) or plan approval (G4).
