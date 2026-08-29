---
name: autogenesis/modules/validate-gate-map-and-non-goals
description: Internal Autogenesis module. Check that a target skill’s declared G0–G8 / Enter-Change-Exit clusters and non-goals sections align with the actual path and module bodies. Also performs activation_card presence/wiring check when the feature is declared. Advisory only.
internal: true
version: 2026-08-22
---

# validate-gate-map-and-non-goals

Advisory only. Does **not** mutate the target.

## Procedure

1. Locate the target skill root and read its root SKILL.md plus any path modules under `references/paths/`.
2. Verify classic gate-map items:
   - Declared gate map (G0–G8 or equivalent Enter | Change | Exit clusters) matches the actual blocking points in the path bodies.
   - Every path that claims “stops for approval” actually contains the stop language and does not implement.
   - Non-goals sections exist, are explicit, and are not contradicted by the procedure text.
3. **Activation-card check** (new, work_id autogenesis-activation-card-extend):
   - Read front-matter key `activation_card` (legal values only: `off | on | debug`).
   - If absent or `off` → `card_check: disabled — skip` (do **not** set needs-work solely for this).
   - If `on` or `debug`:
     - Confirm the declaration is present.
     - Confirm explicit language exists stating that an Enter card must be emitted before path work (in SKILL.md or a path module).
     - Confirm path-receipt format is documented or referenced.
     - Any gap → add concrete `file:section` entry under gaps and set status needs-work for this facet.
   - The card check is **necessary but never sufficient** for overall_status = pass of the parent review-package.
4. Emit:

   ```text
   FACET: validate-gate-map-and-non-goals
   target: <path or name>
   gate_map_alignment: pass | gaps
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
