---
name: Activation Card
id: activation-card
genesis_id: B17
category: Behavioral / Control & Safety
status: active
version: 0.5
work_id: autogenesis-patterns-as-genesis-extension-v1
---

# B17. ACTIVATION CARD

**Genesis-style identity:** B17 (Behavioral extension owned by Autogenesis)  
**Classical analog:** Process Entry Gate + Receipt (Workflow Contract)  
**Relationship:** Autogenesis extension of the genesis catalogues. Injected whenever Autogenesis loads genesis; never written into the genesis skill.

## Context
Any skill that declares `activation_card: on` (or equivalent) and performs substantial module work — especially mutating work under Autogenesis or Atlas process-memory discipline.

## Problem
Without a visible, structured entry point and a matching exit receipt, agents:

- start work silently
- skip intermediate gates
- emit only late receipts
- lose lineage across sessions

Soft textual rules are easily overridden (latent policy failure). Discussion and implement authority become blurred.

## Solution
The **activation card** is the visible interface and cue that an invocation
was requested. It does not prove authorisation, execution or completion.
Declared arguments resemble function parameters; a request supplies values,
while the parent owns protected execution context.

For a derived skill, describe the visible cue and return an honest outcome or
blocker. Ordinary prose is sufficient; B17 does not require a JSON protocol,
request IDs, an Atlas or a validator. Keep approval distinct from the request,
redact sensitive inputs, and never let disabled cards disable declared gates.

## Autogenesis application

The following details govern Autogenesis and explicitly adopted full fusion,
not every skill using an activation card. Autogenesis's sole authority is
`<skill_root>/references/modules/workflow-discipline/SKILL.md` and its
module-local `references/invocation-contract.md` and JSON inventory. Use those
schemas rather than copying a second request or receipt definition here.

- Read the selected entrypoint before following its procedure.
- With cards enabled, render a full root/operation request card and compact
  support card as fenced `text`, before procedure execution.
- Keep one active operation. Supporting requests inherit context, have their
  own request identity and return to the caller without replacing the operation.
- Absent/off disables card rendering only; on requires the cards; debug adds
  redacted inherited context. Never display credentials.
- A requested card is followed by an honest receipt, including rejection,
  blocking or failure when appropriate. Completion needs actual outcome evidence.
- Discussion has zero implementation authority. The progression remains
  discussion, formal design, explicit approval, then implement.
- External skills retain their own card contracts; B17 does not rename them.

Autogenesis Exit still requires actual Atlas operations, honest persistence/compile
evidence, and a complete Changed files record for product changes. Safe retry
policy belongs to the invocation discipline, not to the visible card.

## Consequences

**Benefits**
- Auditability of mode, subject, and module
- Forced module-entrypoint load
- Clear discussion vs run boundary
- Durable lineage when the skill adopts a memory discipline

**Costs / residual risks**
- Friction on tiny tasks
- Card can become pure messaging if not paired with process gates (see type-normalise application gate)
- Prose compliance is imperfect without hooks (v1 residual)

## Known uses

- 2026-08-22 — okf-wiki — work_id okf-wiki-type-normalise-gate-v1 — design + implement Runs with Enter card and module receipts — application gate shipped
- 2026-08-22 — autogenesis — work_id autogenesis-patterns-module-v1 — design Run (this module) — pattern language bootstrap
- 2026-08-22 — okf-wiki / autogenesis — multi-skill ontology-type migration and process-discipline discussion — card used throughout discussion → design → implement arcs
- Prior activation_card:on Runs on okf-wiki and autogenesis (see subject stores for lineage)

## Related patterns

- (future) Application Gate — soft dry-run → review → apply sequence for type-normalise
- workflow-discipline module — normative source of Enter | Change | Exit rules

## Sketch (optional)

```text
Request + configured card → loaded procedure → actual outcome → invocation receipt
                ↑
         discussion has zero implement authority
```
