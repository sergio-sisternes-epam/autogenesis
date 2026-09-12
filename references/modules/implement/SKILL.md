---
name: implement
description: Implement only an explicitly approved persisted Autogenesis plan, preserving safety gates, version identity, evidence and subject-Atlas lineage.
metadata:
  autogenesis-parent: autogenesis
  autogenesis-role: operation
---

# Operation: implement

## Arguments

- Required: `plan_ref` (candidate persisted formal plan reference; it must
  exactly match the approved parent design receipt's `result.artifact`).
- Optional: none.
- Protected context and resolved locations come from the parent, not arguments.
  Follow `<skill_root>/references/modules/workflow-discipline/SKILL.md` and
  its module-local invocation contract. Resolve siblings through the parent
  registry and shared resources from skill_root.

## Enter

The parent issues a request targeting `implement`, role `operation`, reads
this entrypoint and emits the configured full card before the procedure.
Revalidate the persisted plan and actual explicit approval; approval_ref or
a requested card alone grants no authority. Before any procedure effect, bind
`arguments.plan_ref` to the parent design receipt: require
`result.disposition: approved`, the same non-empty `approval_ref`, an exact
`result.artifact` match, and the same protected `work_id`. Block on any missing
or mismatched value.

## When (Change)

1. **G4:** A **persisted plan produced by the formal design operation** (genesis → internal think-challenge → pin → C1–C5) exists **and** has received explicit user approval (“approve”, “implement the plan”, or equivalent). The requested `plan_ref` must equal that approved design receipt's `result.artifact`, and both requests must share the protected `work_id`.
2. **No product edits** if either is missing, or if the plan was produced by catalog Discuss or any discussion short-circuit → `incomplete: missing Change (G4)`.
3. Discussion never has implement authority. Reject a direct transition;
   the parent must first select Run mode and request the design operation.

## Procedure

1. Confirm the approved artifact binding and plan scope (no silent creep).
   Reject before effects when `arguments.plan_ref` differs from the approved
   parent design receipt's `result.artifact`, or when its approval reference,
   approved disposition, or protected work id is missing or mismatched.
   Read **work_id** from the approved plan. Create work node(s) if missing; set status `implementing`.
   If the plan declares **change-class: new-surface**, verify mini-genesis artifacts are present in the plan (mermaid, interface sketch, cost note, acceptance). If missing → `incomplete: missing Change (G3/G5)` — do not implement; return to design.
   If **change-class: new-skill**, verify full Genesis Artifacts section.
2. Apply only that scope.
3. Assign version / content identity where producing material skill changes.
4. No automatic wiring; no peer Atlas mutation.
5. When the plan introduces or changes skill chaining, verify the multi-harness substrate contract is present (or first run `review-package` on the target).
6. **Post-implement evaluation:**
   If the subject owns scenarios covering this change, change-class is
   `new-surface` affecting runtime behavior, or the plan lists deterministic
   checks, run every applicable command with tools available in the subject
   repository.
   - A red in-scope result without user waiver keeps implementation incomplete.
   - Record actual command/output evidence in lineage.
   - For a check that cannot run, record an exact deferral reason; never infer
     success from a scenario file or prose.
   Do not require, install or invoke a separate evaluator.

6b. **Adversarial scenarios (behaviour-changing implement):**
   Materialise the approved design draft as
   `<subject>/references/scenarios/<capability>-adversarial-vN.yaml` and fill
   only real paths/commands.
   Implement **may add** smokes; **must not drop** an approved smoke without a
   new design. Run applicable adversarial checks in addition to happy-path
   checks. Waive a red smoke **only if that counter is out of this change’s
   scope**; the reason must **name the counter**. New behavior or an approved
   smoke-set change requires a **new file + version bump**; keep the previous
   file as history.
7. **Exit:** Apply the multi-harness substrate contract to the skills named
   `atlas` and `okf` through
   `<skill_root>/references/modules/workflow-discipline/SKILL.md#exit-blocking`.
   Load the Atlas path module `remember` (or `work`) via substrate contract and follow it exactly; require green `atlas compile`.
   The remember experience **must** contain a structured `## Changed files` section listing every product file created or edited in this Run. Missing list → `incomplete: G8`.
8. **Update the subject work node:** set status `done` | `deferred` | `waived`;
   link the implement experience, plan path, scenario reference and actual
   evaluation evidence when present. Do not mirror it to a second Atlas.
9. Emit the canonical invocation receipt with actual work/context, loaded
   entrypoints, substrate, Atlas and compile evidence. Select current suites
   from `<skill_root>/references/scenarios/suite-index.json`; historical suites
   are not current acceptance. No uncertain partial effect may be replayed;
   apply the discipline's single-owner, two-attempt maximum.

## Gates

Enter · Change (**G4**, **G5**) · Exit (**G6**, **G8** via Atlas).

## work_id on implement experience

Frontmatter must include: `work_id`, `implements` (same id), `closes` (ids
closed), and `plan_path`. Optional: `external_ref` (opaque tracker link/key).
Record evaluation status and evidence in the body rather than binding lineage
to a particular evaluator.

## Outputs

Changed files · version identity · remember/ingest (or defer) · receipt
