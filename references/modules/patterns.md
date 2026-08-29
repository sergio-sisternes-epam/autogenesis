---
name: autogenesis/modules/patterns
description: Thin extension injector for Autogenesis. When Autogenesis loads genesis via substrate contract, this module MUST also be loaded so that B17 ACTIVATION CARD (and any future true deltas) are visible alongside the genesis catalogues. No parallel catalogue is maintained.
internal: true
version: 0.4.0
work_id: autogenesis-patterns-as-genesis-extension-v1
---

# patterns (Autogenesis extension injector)

**This module is no longer a parallel pattern language.**  
It is a thin **extension injector** that makes Autogenesis-owned deltas visible when genesis is invoked.

## Injection contract (mandatory)

When Autogenesis applies the multi-harness substrate contract to the skill named `genesis` (design path step 1, or any other load of genesis):

1. Load the full genesis body as usual.
2. **Also** load this module (`references/modules/patterns.md`).
3. Present **B17. ACTIVATION CARD** (and any future true extensions listed below) alongside the genesis Tier-2 / Tier-3 catalogues for pattern selection and Catalogue Review.

Genesis itself remains **read-only**. This module never writes into the genesis skill.

## Sole remaining pattern

| id (genesis-style) | Name | Category | Status | File |
|--------------------|------|----------|--------|------|
| B17 | ACTIVATION CARD | Behavioral / Control & Safety | active | `patterns/activation-card.md` |

## Definition & admission (unchanged for any future extension)

A pattern is a generalisation of a solution that repeats over time and works.  
Proven use first. Single observation → draft only. Create to active requires repeated use evidence.

## Template

Canonical template remains `references/modules/patterns/template.md` for any future true extension.

## Deprecated

The former parallel catalogue entries (Triage Panel, Panel Review) have been moved to `patterns/deprecated/`. They were thin specialisations of genesis A1 + B1 and are no longer maintained as top-level Autogenesis patterns. Future panel-style work should compose the atomic genesis patterns directly.

## Capabilities (still available, now scoped to the extension)

- **Load** — returns B17 (and future extensions).
- **Record known-use** — append to the living Known uses section of B17.
- **Identify / Extract / Create** — only for genuine new deltas that cannot be expressed as composition of genesis patterns; subject to the same admission bar.

Scan/detect and Relate remain deferred.

## Related

- Source of process detail for B17: `references/modules/workflow-discipline.md`
- Upstream catalogues (read-only): genesis `assets/design-patterns.md` and `assets/architectural-patterns.md`
