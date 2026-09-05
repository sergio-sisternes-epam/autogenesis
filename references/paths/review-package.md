---
name: autogenesis/paths/review-package
description: Deep multi-facet package conformance review. Use when the operator asks for a full structural / design-quality evaluation of a skill package (not the narrow link-only check). Triggers on deep review, package conformance, full skill audit, review package structure, or when genesis-level checks are needed alongside nesting validation. Stops for approval if changes are recommended.
path_id: review-package
default: false
subject_scope: subject-atlas
---

# Path: review-package (deep)

## Enter

Activation card must show `path: review-package` and this module **read**.

## Must announce

This path is **advisory**. It never mutates the subject under review.  
If the aggregated REPORT recommends changes, the path **stops for approval**; any subsequent fix requires a separate implement path (or manual edit).

## Purpose

Deep multi-facet evaluation of a target skill package. Combines:

- Genesis design-quality lens (mandatory first step)
- Nested substrate-contract check
- Progressive-disclosure hygiene
- OKF conformance of the repository-declared Atlas
- Gate-map and non-goals honesty

Produces a single structured REPORT. Does **not** replace the narrow `validate-skill-import-links` module (which remains available for fast link-only checks).

## Procedure (mandatory sequence)

1. **Apply substrate contract to skill named `genesis`**  
   Locate by name from the harness’s available skills list, load its full SKILL.md body with the on-demand skill-loader, then follow that body exactly.  
   Capture the design artifacts (diagrams, interface notes, cost notes) that apply to the *subject under review*. These become the design-quality section of the REPORT.

2. **Load and run the facet modules** (progressive disclosure; load only what is needed):  
   - `references/modules/validate-skill-import-links.md`  
   - `references/modules/validate-progressive-disclosure.md`  
   - `references/modules/validate-okf-conformance.md`  
   - `references/modules/validate-gate-map-and-non-goals.md`  

   Each module emits its own FACET report fragment.

3. **Synthesize a single REPORT** with this shape:

   ```text
   DEEP REVIEW-PACKAGE REPORT
   target: <path or name>
   genesis_summary: <one-paragraph design-quality notes or “n/a – subject too simple”>
   facets:
     - validate-skill-import-links: pass | needs-work
     - validate-progressive-disclosure: pass | needs-work
     - validate-okf-conformance: pass | needs-work | n/a
     - validate-gate-map-and-non-goals: pass | needs-work
   overall_status: pass | needs-work
   recommended_changes: |
     <bullet list or “none”>
   gaps_detail: |
     <concatenated facet gap lists>
   ```

4. **Present the REPORT**.  
   If `overall_status: needs-work` or recommended_changes is non-empty → announce **stop for approval**. Do not implement.

5. Optional: recommend re-running the canonical fixture **skill-test-a → skill-test-b** when nesting gaps were found.

## Gates

- G1: this path module read.
- G3 (genesis applied).
- No G4/G5 product mutation of the *subject under review*.
- Exit via Atlas remember of the review outcome (subject Atlas of the *reviewed* package when durable conclusions are claimed).

## Non-goals

- Mutation of the subject under review.
- Auto-implement of recommended changes.
- Redesign of other Autogenesis paths.
- Replacing the narrow link-only module (it remains available).
- Changing the multi-harness substrate contract itself.

## Compatibility note

Legacy triggers that only want the narrow nesting check may still load `references/modules/validate-skill-import-links.md` directly. This deep path is reserved for full conformance evaluation.
