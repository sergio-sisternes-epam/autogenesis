---
name: patterns
description: Expose Autogenesis extensions while preserving Genesis authority.
metadata:
  autogenesis-parent: autogenesis
  autogenesis-role: support
  autogenesis-origin-version: "0.4.0"
  autogenesis-origin-work: autogenesis-patterns-as-genesis-extension-v1
---

# patterns (Autogenesis extension injector)

**This module is no longer a parallel pattern language.**
It is a thin **extension injector** that makes Autogenesis-owned deltas visible when genesis is invoked.

## Arguments

- Required: `intent` (load, record-known-use, identify, extract or create).
- Optional: `target`, `genesis_load_context`, `extension_scope`, `pattern_name`.
- Do not override parent-owned subject, mode, operation, work identity, Atlas, or approval.

Follow `<skill_root>/references/modules/workflow-discipline/SKILL.md` and its
invocation contract. The parent reads this entrypoint and issues a support
request with its configured compact card before the procedure. Keep the active
operation and inherited context; return the result and an honest receipt.
Resources below resolve from this module directory; siblings use the parent
registry and shared resources use skill_root, never cwd.

## Injection contract (mandatory)

When Autogenesis applies the multi-harness substrate contract to the skill named `genesis` (design step 1, or any other load of genesis):

1. Load the full genesis body as usual.
2. **Also** request this support through the parent registry with `intent: load`.
3. Present **B17. ACTIVATION CARD** and the status-labelled extension index
   alongside the genesis Tier-2 / Tier-3 catalogues. For module composition,
   load `references/parent-routed-skill-module.md` before evaluating S8.
   Draft is not automatic application or promotion: record applicability and
   admission status, and apply a draft only within an explicitly approved design.

Genesis itself remains **read-only**. This module never writes into the genesis skill.

## Extension index

### Sole remaining pattern in active status

| id (genesis-style) | Name | Category | Status | File |
|--------------------|------|----------|--------|------|
| B17 | ACTIVATION CARD | Behavioral / Control & Safety | active | `references/activation-card.md` |

### Draft extensions

| id (Autogenesis-scoped) | Name | Category | Status | File |
|------------------------|------|----------|--------|------|
| autogenesis:S8 | PARENT-ROUTED SKILL MODULE | Structural / Composition | draft | `references/parent-routed-skill-module.md` |

S8 is a private callable-leaf contract, not a replacement for Genesis's
distribution-module concept or B17's request interface. Do not infer independent
catalogue discovery, thread isolation or a security sandbox from its file shape.
It is instruction-first: do not require an adopter to inherit Autogenesis's
workflow, schemas or validators. Domain scripts remain optional and useful
when the task warrants them.

## Definition & admission (unchanged for any future extension)

A pattern is a generalisation of a solution that repeats over time and works.
Proven use first. Single observation → draft only. Create to active requires repeated use evidence.

## Template

Canonical template remains `references/template.md` for any future true extension.
When an approved design needs a private module, load
`references/skill-module-template.md` for a small optional authoring example.
It is not another pattern or catalogue export.

## Deprecated

The former parallel catalogue entries (Triage Panel, Panel Review) have been moved to `references/deprecated/`. They were thin specialisations of genesis A1 + B1 and are no longer maintained as top-level Autogenesis patterns. Future panel-style work should compose the atomic genesis patterns directly.

## Capabilities (still available, now scoped to the extension)

- **Load** — returns B17 (and future extensions). Include the S8 draft index
  entry; load its full body only for relevant module-composition work.
- Default **Record known-use** — append to the living Known uses section of B17.
  With `pattern_name`, select `B17` or `autogenesis:S8` explicitly and append to
  that pattern's Known uses instead. Reject unknown selections with a diagnostic;
  do not silently fall back. Record subject, work identity, evidence and actual
  outcome; recording use never promotes a draft automatically.
- **Identify / Extract / Create** — only for genuine new deltas that cannot be expressed as composition of genesis patterns; subject to the same admission bar.

Scan/detect and Relate remain deferred.

## Related

- Source of process detail for B17: `<skill_root>/references/modules/workflow-discipline/SKILL.md`
- Upstream catalogues (read-only): genesis `assets/design-patterns.md` and `assets/architectural-patterns.md`
