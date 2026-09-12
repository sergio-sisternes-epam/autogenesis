---
name: validate-gate-map-and-non-goals
description: Check gate maps, stop-for-approval language, and non-goals honesty.
metadata:
  autogenesis-parent: autogenesis
  autogenesis-role: support
---

# validate-gate-map-and-non-goals

Advisory only. Does **not** mutate the target.

## Arguments

- Required: `target`.
- Optional: `card_state`, `gate_scope`.
- Do not override parent-owned subject, mode, operation, work identity, Atlas, or approval.

Follow `<skill_root>/references/modules/workflow-discipline/SKILL.md` and its
invocation contract. The parent reads this entrypoint and issues a support
request with its configured compact card before the procedure. Keep the active
operation and inherited context; return the facet result and an honest receipt.
Shared assets resolve from skill_root, not cwd. card_state is observed evidence,
not an override of the target skill's actual configuration.

## Procedure

1. Locate the target skill root and read its root SKILL.md plus any module
   entrypoints under `<target>/references/modules/`.
2. Verify the target's own declared boundaries:
   - A declared gate map matches actual blocking points. Do not require
     Autogenesis's G0–G8 names or a gate map for a simple skill.
   - Every module that claims “stops for approval” actually contains the stop language and does not implement.
   - Scope and non-goals are clear and not contradicted by the procedure;
     a small skill need not have a separately titled Non-goals section.
3. **Activation-card check** (new, work_id autogenesis-activation-card-extend):
   - Read front-matter key `activation_card` (legal values only: `off | on | debug`).
   - If absent or `off` → `card_check: disabled — skip` (do **not** set needs-work solely for this).
   - If `on` or `debug`:
     - Confirm the declaration is present.
     - Confirm a visible request cue identifies the skill/module and relevant
       inputs before the procedure, not approval or execution evidence.
     - Confirm debug redacts sensitive context and off never disables
       declared approval boundaries.
     - Confirm results distinguish actual outcomes from requested work.
       Ordinary prose is sufficient; no canonical JSON receipt is required.
     - Any gap → add concrete `file:section` entry under gaps and set status needs-work for this facet.
   - The card check is **necessary but never sufficient** for overall_status = pass of the parent review-package.
   - For Autogenesis itself, or a target explicitly adopting its full protocol,
     additionally check its declared full/compact cards, protected context,
     receipts and retry policy. Do not export these local rules to every S8
     adopter. A declared retry policy must not license unsafe partial replay.
4. Emit:

   ```text
   FACET: validate-gate-map-and-non-goals
   target: <path or name>
   gate_map_alignment: pass | gaps | n/a
   stop_for_approval_honesty: pass | gaps
   non_goals_present: pass | gaps
   non_goals_honesty: pass | gaps
   card_check: disabled — skip | pass | needs-work
   gaps:
     - <file:section> — <mismatch or missing>
   status: pass | needs-work
   ```

## Non-goals

- Running the gates themselves.
- Design-quality critique (that is genesis).
- Mutation of the target.
- Hard runtime enforcement of the card (that remains A-P1 / future work).
