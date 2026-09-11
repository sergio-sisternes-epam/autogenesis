---
name: reflect-challenge
description: Reflect on observed behaviour and capture a behaviour challenge.
metadata:
  autogenesis-parent: autogenesis
  autogenesis-role: operation
---

# Operation: reflect-challenge

## Arguments

- Required: `objective`, `observations`.
- Optional: `current_behaviours`, `recalled_behaviours`, `tension`.
- Do not override parent-owned subject, mode, operation, work identity, Atlas, or approval.

Follow `<skill_root>/references/modules/workflow-discipline/SKILL.md` and its
invocation contract. The parent resolves and reads this entrypoint, issues an
operation request and emits its configured full card before the procedure.
Resolve shared assets from skill_root and siblings from the registry, not cwd.
Return a receipt with actual results, never card-only completion.

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
