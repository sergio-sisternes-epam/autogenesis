---
name: getting-started
description: First-use guidance for Autogenesis: purpose, prerequisites, and the shortest useful journey. Does not implement.
metadata:
  autogenesis-parent: autogenesis
  autogenesis-role: operation
---

# Operation: getting-started

First-use for Autogenesis. Explain how to begin. Do not design, implement,
wire, or write the subject skill. Do not auto-mount Atlas.

## Arguments

- Required: none. Do not block Enter to collect extra inputs.
- Optional: `goal` (what the user hopes to do first).
- Do not override parent-owned subject, mode, operation, work identity, Atlas,
  or approval.

Follow `<skill_root>/references/modules/workflow-discipline/SKILL.md` and its
invocation contract. The parent resolves and reads this entrypoint, issues an
operation request and emits its configured full card before the procedure.
Resolve shared assets from skill_root and siblings from the parent registry,
not cwd. Return a receipt with the guidance actually given; a card alone
never proves execution.

## When to use

Use when the user is new to Autogenesis or asks how it works as a skill.
Unqualified getting-started requests about unrelated products must not route
here.

## Enter

Emit the configured full operation card as a fenced `text` block before any
guidance. Include learning `intent` near the top, plus `atlas_used`,
`atlas_status`, and `help_status`:

```text
schema: autogenesis.invocation-request/v1
request_id: <id>
parent_request_id: <caller or null>
target: {skill: autogenesis, module: getting-started, role: operation}
operation: getting-started
arguments_summary: goal=<optional or none>
entrypoint: <resolved getting-started entrypoint>
atlas_id: none
atlas_root: none
approval_ref: null
state: requested
intent: Learn what Autogenesis does and choose a first useful step
atlas_used: []
atlas_status: baseline-only
help_status: complete
```

This operation does not need a `work_id`. A requested card is not approval or
execution evidence.

## Procedure

1. Read `references/first-journey.md`. That packaged baseline is enough for
   purpose, prerequisites, and the shortest useful first journey.
2. Answer from it. Distinguish discussion, design, and implement. State the
   approval stop. State that discussion does not implement.
3. Point to Autogenesis **help** (overview) and **help** for named modules.
   Do not invoke those operations from here; name them so the parent can
   route a later request. Do not load every module.
4. If `goal` names a single later module, still finish this first-use answer,
   then point at that module's help. Do not run that module.
5. If the question exceeds first-use (rationale, history, or a named module's
   full contract), say so and point to help. Do not auto-mount Atlas to pad
   onboarding. Getting-started remains usable with no Atlas mounted.

If this baseline already answers, keep `atlas_used: []` and do not duplicate
an identical card.

## Outputs

A first-use explanation, a matching card, and a receipt listing
`references/first-journey.md` as loaded evidence. No package writes. No
subject-skill writes. No Atlas writes.

## Gates

G0 and G1 as applicable. Write, approval, and lineage gates do not apply.

## Non-goals

- Implementing from discussion or from this guidance
- Designing or wiring a subject skill
- Auto-mounting Atlas
- Visualisation
