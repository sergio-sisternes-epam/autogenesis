# Run record / invocation receipt template

This records Autogenesis's own authoring work. Derived skills do not inherit
these schemas merely by adopting S8; their results may be ordinary prose.

Read `<skill_root>/references/modules/workflow-discipline/SKILL.md` and its
module-local `references/invocation-contract.md` before using this template.
That contract owns request/card/receipt fields and configured rendering.

## Request

Record the actual request identity, parent, target, task arguments, protected
context and resolved entrypoint under `autogenesis.invocation-request/v1`.
When enabled, emit the full root/operation or compact support activation card
with requested state before following the procedure. Never record credentials.

## Receipt

Use `autogenesis.invocation-receipt/v1`, correlating the same request and parent.
Record the actual status, attempts, result, evidence and Enter/Change/Exit gates.
Include reasons for rejected, blocked or failed outcomes. A read/card alone
cannot justify completion. Each retry records its owner, transient failure and
repeat-safety evidence; a missing or uncertain history does not grant a budget.
No store write means remember=false, not fabricated success.

## Body (Atlas remember experience)

- What the user asked.
- What was actually done and any explicit deferral.
- Pinned decisions and remaining blockers.
- Authoritative `relates_to` edges, including the canonical work hub.

## Changed files

List every product file created, moved, edited or deleted, relative to the
subject root, and distinguish Atlas memory paths. For example:

```text
references/modules/design/SKILL.md (created)
SKILL.md (updated)
```
