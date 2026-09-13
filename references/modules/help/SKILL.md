---
name: help
description: Explain Autogenesis modules without executing them. List capability-facing modules, or describe one named module or bundled topic.
metadata:
  autogenesis-parent: autogenesis
  autogenesis-role: operation
---

# Operation: help

Explain Autogenesis. Do not design, implement, wire, migrate, or write the
subject skill. Do not auto-mount Atlas.

## Arguments

- Required: none. Missing `target` is a valid overview request, not a prompt
  for clarification.
- Optional: `target` (a capability-facing module name, or a bundled topic
  from `references/topics.md`).
- Do not override parent-owned subject, mode, operation, work identity, Atlas,
  or approval.

Follow `<skill_root>/references/modules/workflow-discipline/SKILL.md` and its
invocation contract. The parent resolves and reads this entrypoint, issues an
operation request and emits its configured full card before the procedure.
Resolve shared assets from skill_root and siblings from the parent registry,
not cwd. Return a receipt with the explanation actually given; a card alone
never proves execution.

## When to use

Use only when Autogenesis is already the active skill, or the user is asking
how Autogenesis itself works. Unqualified "help" about unrelated tasks must
not route here.

## Capability-facing modules

List **operations** from the live parent registry, including `help` and
`getting-started`. Do not list `validate-*`, think wrappers, `patterns`, or
`workflow-discipline` unless the parent registry already marks them
`operation`. One-line purposes come from the registry Description column and
the versioned snapshot in `references/capability-catalog.md`.

## Enter

Emit the configured full operation card as a fenced `text` block before any
help work. Include learning `intent` near the top, plus `atlas_used`,
`atlas_status`, and `help_status`. At Enter:

```text
schema: autogenesis.invocation-request/v1
request_id: <id>
parent_request_id: <caller or null>
target: {skill: autogenesis, module: help, role: operation}
operation: help
arguments_summary: target=<name or none>
context_summary: subject=<inherited>, mode=<inherited>, work_id=none, approval_ref=null
entrypoint: <resolved help entrypoint>
atlas_id: <inherited parent atlas_id or none>
atlas_root: <inherited parent atlas_root or none>
approval_ref: null
state: requested
intent: <user learning goal, not an operation to run>
atlas_used: []
atlas_status: baseline-only
help_status: pending
```

Render inherited protected Atlas context honestly. Do not select a store on
this card. Keep `operation: help` even when explaining `design`, `implement`,
or `wire`. Never label the card as those operations. A requested card is not
approval or execution evidence. This operation does not need a `work_id`.

## Procedure

1. **Overview (no target).** List each capability-facing module from the
   live parent registry with its one-line purpose. The packaged catalog is
   supplemental snapshot text, not listing authority; if a registry
   operation is missing from the snapshot, still list the registry row.
   Do not ask a clarifying question just to list. Do not read every module
   entrypoint. After the registry list, keep `atlas_used: []` and set
   `atlas_status: baseline-only`, `help_status: complete`.
2. **Named module or topic.** Resolve `target` in this order, then stop if
   those files answer the question (`atlas_status: baseline-only`,
   `atlas_used: []`, `help_status: complete`):
   - If it matches a parent-registry **operation** name, read **that**
     entrypoint only. Cover intent, inputs, prerequisites, examples, outputs,
     side effects, and boundaries. Do not follow the target's procedure.
     Support, think, `patterns`, and `validate-*` names are unknown unless
     the live registry marks them `operation`.
   - Else if it matches a name or alias in `references/topics.md`, read that
     topic page only. Do not invent extra modules.
3. **Unknown target.** Say it is unknown. List valid capability-facing
   modules plus the bundled topic names. Do not invent flags, modules, or
   behaviour. Keep `atlas_used: []`, set `atlas_status: baseline-only` and
   `help_status: complete`, then refresh the card.
4. **Insufficient references.** Topic overlap is not enough. If the loaded
   files do not evidence the actual question, read
   `references/enrichment.md` and attempt read-only Atlas retrieval only when
   a store is already resolvable. Do not mount, authenticate, initialise,
   remember, or install. Set status before refresh:
   - blocked or failed retrieval: `help_status: limited`,
     `atlas_status: unavailable`, `atlas_used: []`
   - retrieval ran with no eligible hit: `help_status: limited`,
     `atlas_status: consulted`, `atlas_used: []`
   - retrieval contributed eligible pages: `help_status: complete`,
     `atlas_status: consulted`, `atlas_used` lists those store IDs
5. **Refresh the card** before the explanation when status, root, or
   `atlas_used` changed. Final cards have no pending placeholders.
   `atlas_used` lists only store IDs whose eligible evidence contributed.

Suggested limited-help wording when Atlas is unavailable:

> The bundled references do not cover this question fully, so my help is
> limited. I could not access the Atlas knowledge store, where fuller
> information is maintained, because [known reason]. I can explain
> [supported part], but I cannot confirm [missing part] from the available
> sources.

## Outputs

A user-facing explanation, a matching card, and a receipt whose evidence lists
files actually read, `help_status` (`complete` or `limited`), `atlas_status`,
and `atlas_used`. No package writes. No subject-skill writes. No Atlas writes.

## Gates

G0 and G1 as applicable. Write, approval, and lineage gates do not apply;
do not claim G2/G8 completion via remember or compile.

## Non-goals

- Executing the described module
- Auto-mounting or repairing Atlas
- Loading every module to produce an overview
- Hijacking unrelated help requests
- Visualisation
