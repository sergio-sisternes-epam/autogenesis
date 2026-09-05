---
name: autogenesis/paths/implement
description: Use this path only after a persisted Autogenesis plan is explicitly approved. Applies the plan under safety gates with version identity and subject-Atlas lineage via Atlas. Do not use to design from scratch or to skip approval.
path_id: implement
default: false
subject_scope: subject-atlas
---

# Path: implement

## Enter

Activation card: `path: implement`, this module **read**.

## When (Change)

1. **G4:** A **persisted plan produced by a formal design path** (genesis → internal think-challenge → pin → C1–C5) exists **and** has received explicit user approval (“approve”, “implement the plan”, or equivalent).
2. **No product edits** if either is missing, or if the plan was produced by a discussion-mode short-circuit → `incomplete: missing Change (G4)`.
3. Discussion mode never has implement authority. Any attempt to enter implement directly from discussion is refused; the agent must re-issue Enter for `mode: run, path: design`.

## Procedure

1. Confirm approved plan scope (no silent creep).  
   Read **work_id** from the approved plan. Create work node(s) if missing; set status `implementing`.  
   If the plan declares **change-class: new-surface**, verify mini-genesis artifacts are present in the plan (mermaid, interface sketch, cost note, acceptance). If missing → `incomplete: missing Change (G3/G5)` — do not implement; return to design.  
   If **change-class: new-skill**, verify full Genesis Artifacts section.  
2. Apply only that scope.
3. Assign version / content identity where producing material skill changes.
4. No automatic wiring; no peer Atlas mutation.
5. When the plan introduces or changes skill chaining, verify the multi-harness substrate contract is present (or first run `review-package` on the target).
6. **Post-implement construct evaluation (R2):**  
   If the subject owns scenarios covering this change, **or** change-class is `new-surface` affecting runtime behaviour, **or** the plan lists construct expects:  
   run construct CLI (`create` if needed → `run`).  
   - Red + no user waive → `incomplete: evaluation (construct)` — do not claim implement complete.  
   - Green → record report path in lineage.  
   - Doc-only / no scenario → explicit deferral reason in receipt.  
   **Never** ask construct to invoke autogenesis (R1).

6b. **Adversarial construct (behaviour-changing implement):**  
   Materialise the approved design draft as `<subject>/references/scenarios/<capability>-adversarial-vN.yaml` (fill paths/commands only).  
   Implement **may add** smokes; **must not drop** an approved smoke without a new design.  
   Run the adversarial suite **in addition to** happy-path smokes.  
   Waive a red smoke **only if that counter is out of this change’s scope**; the reason must **name the counter**.  
   New behaviour or approved smoke-set change → **new file + version bump**; keep the previous file.
7. **Exit:** Apply the multi-harness substrate contract to the skills named `atlas` and `okf` (see root Exit activation checklist).  
   Load the Atlas path module `remember` (or `work`) via substrate contract and follow it exactly; require green `atlas compile`.  
   The remember experience **must** contain a structured `## Changed files` section listing every product file created or edited in this Run. Missing list → `incomplete: G8`.
8. **Update the subject work node:** set status `done` | `deferred` | `waived`; link implement experience, plan_path, and construct_report if any. Do not mirror it to a second Atlas.
9. Emit **path receipt** including `work_id`, `nested_skills_loaded`, `substrate_contract`, `atlas_root` and `compile`.

## Gates

Enter · Change (**G4**, **G5**) · Exit (**G6**, **G8** via Atlas).

## work_id on implement experience

Frontmatter must include: `work_id`, `implements` (same id), `closes` (ids closed), `plan_path`, `construct_eval` (green|red|deferred|waived). Optional: `external_ref` (opaque tracker link/key).

## Outputs

Changed files · version identity · remember/ingest (or defer) · receipt
