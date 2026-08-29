---
name: Activation Card
id: activation-card
genesis_id: B17
category: Behavioral / Control & Safety
status: active
version: 0.3
work_id: autogenesis-patterns-as-genesis-extension-v1
---

# B17. ACTIVATION CARD

**Genesis-style identity:** B17 (Behavioral extension owned by Autogenesis)  
**Classical analog:** Process Entry Gate + Receipt (Workflow Contract)  
**Relationship:** Autogenesis extension of the genesis catalogues. Injected whenever Autogenesis loads genesis; never written into the genesis skill.

## Context
Any skill that declares `activation_card: on` (or equivalent) and performs substantial path work — especially mutating work under Autogenesis or Atlas process-memory discipline.

## Problem
Without a visible, structured entry point and a matching exit receipt, agents:

- start work silently
- skip intermediate gates
- emit only late receipts
- lose lineage across sessions

Soft textual rules are easily overridden (latent policy failure). Discussion and implement authority become blurred.

## Solution
Require an explicit **Enter card** before path work, follow the loaded path module, and emit a matching **path receipt** at Exit.

**Enter card (blocking):**

```text
skill: <activating skill name>
skill_path: <resolved path to that skill’s root directory>
mode: run | discussion
subject: <skill under change>
path: design | implement | research | reflect-challenge | learn-skill | reevaluate | aware-runtime | wire | review-package | atlas-migrate | discuss
path_module: references/paths/<path>.md
intent: <one line>
```

Rules:
- The matching `path_module` must be read before the path is executed.
- One path at a time.
- **discussion** mode has zero implement authority and uses path `discuss` (catalog skill discuss, subject `atlas_root`).
- No discussion → implement short-circuit; only discussion → formal design → approved plan → implement.

**Path receipt / Exit (blocking):**

```text
skill: <activating skill name>
skill_path: <resolved path to that skill’s root directory>
subject: …
path: …
approved: yes | n/a | no
atlas_root: <subject>/references/atlas   # subject=autogenesis → .atlas/github.com/sergio-sisternes-epam/autogenesis-atlas/atlas
nested_skills_loaded: …
substrate_contract: applied | missing
remember: yes | no
compile: yes | no
Enter|Change|Exit: pass | incomplete: <cluster>
```

Hard rules on Exit: substrate contract on **atlas** (and okf for format) must actually run; remember claims must match real actions and compile green; implement experiences must list `## Changed files`.

Source of process detail: `references/modules/workflow-discipline.md`.

## Consequences

**Benefits**
- Auditability of mode, subject, and path
- Forced path-module load
- Clear discussion vs run boundary
- Durable lineage via subject wiki

**Costs / residual risks**
- Friction on tiny tasks
- Card can become pure messaging if not paired with process gates (see type-normalise application gate)
- Prose compliance is imperfect without hooks (v1 residual)

## Known uses

- 2026-08-22 — okf-wiki — work_id okf-wiki-type-normalise-gate-v1 — design + implement Runs with Enter card and path receipts — application gate shipped
- 2026-08-22 — autogenesis — work_id autogenesis-patterns-module-v1 — design Run (this module) — pattern language bootstrap
- 2026-08-22 — okf-wiki / autogenesis — multi-skill ontology-type migration and process-discipline discussion — card used throughout discussion → design → implement arcs
- Prior activation_card:on Runs on okf-wiki and autogenesis (see subject wikis for lineage)

## Related patterns

- (future) Application Gate — soft dry-run → review → apply sequence for type-normalise
- workflow-discipline module — normative source of Enter | Change | Exit rules

## Sketch (optional)

```text
Enter card → load path_module → Change (path work) → path receipt / Exit
                ↑
         discussion has zero implement authority
```
