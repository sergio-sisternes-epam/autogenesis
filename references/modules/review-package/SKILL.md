---
name: review-package
description: Review a skill package for conformance and gate honesty.
metadata:
  autogenesis-parent: autogenesis
  autogenesis-role: operation
---

# Operation: review-package (deep)

## Arguments

- Required: `target`.
- Optional: `scope`, `focus`, `related_suites`.
- Do not override parent-owned subject, mode, operation, work identity, Atlas, or approval.

Follow `<skill_root>/references/modules/workflow-discipline/SKILL.md` and its
invocation contract. Resolve siblings through the parent registry and shared
resources from skill_root, not cwd. The parent issues the operation request
and configured full card after reading this entrypoint. Facets are supporting
requests with compact configured cards, inherited context and honest receipts.

## Enter

Activation card must show `module: review-package` and this module **read**.

## Must announce

This operation is **advisory**. It never mutates the subject under review.
If the report recommends changes, **stop for approval**; an Autogenesis fix
requires a persisted, explicitly approved design and a separate implement request.

## Purpose

Deep multi-facet evaluation of a target skill package. Combines:

- Genesis design-quality lens (mandatory first step)
- Nested substrate-contract check
- Progressive-disclosure hygiene
- OKF conformance when the target declares OKF/Atlas integration
- The target's own approval boundaries and non-goals honesty

Produces a single structured REPORT. Does **not** replace the narrow `validate-skill-import-links` module (which remains available for fast link-only checks).

## Procedure (mandatory sequence)

1. **Apply substrate contract to skill named `genesis`**
   Locate by name from the harness’s available skills list, load its full SKILL.md body with the on-demand skill-loader, then follow that body exactly.
   Capture the design artifacts (diagrams, interface notes, cost notes) that apply to the *subject under review*. These become the design-quality section of the REPORT.
   Request support `patterns` with `arguments.intent: load` and this review's
   target as `arguments.target`. For module composition, consider
   `autogenesis:S8`; report `pattern_applicability: applicable | not-applicable`
   with a reason and `pattern_admission: draft | active | not-selected`.
   A draft is advisory, not a mandatory conformance rule or automatic promotion.
   A simple or independently released skill need not adopt private modules.
   Distinguish the target's runtime from the Autogenesis process performing
   this review. S8 does not require a workflow engine, JSON protocol, Python
   validator, role taxonomy or Atlas. Missing optional machinery is not a gap.

1b. **Apply SOLID principles for skills prospectively**
   Load
   [`../../skill-design-principles.md`](../../skill-design-principles.md)
   and assess the principles that apply to the target's current or materially changed
   design. Do not report untouched legacy artifacts as nonconforming
   solely because they lack historical lens evidence. Treat `not-applicable`
   and explicit trade-offs as valid reasoned outcomes; do not force modules,
   speculative extension points or dependency abstractions.

2. **Invoke the facet modules through the parent registry**:
   - `validate-skill-import-links`
   - `validate-progressive-disclosure`
   - `validate-okf-conformance`
   - `validate-gate-map-and-non-goals`

   Pass each `arguments.target` from this review request. Each module inherits
   the active review context and emits its FACET report plus invocation receipt.
   Facets apply the target's declared contract, not the reviewer's local
   protocol. Report an unadopted integration as n/a with a reason; a declared
   but missing or broken integration is still a gap.

3. **Synthesize a single REPORT** with this shape:

   ```text
   DEEP REVIEW-PACKAGE REPORT
   target: <path or name>
   genesis_summary: <one-paragraph design-quality notes or “n/a – subject too simple”>
   pattern_applicability: applicable | not-applicable
   pattern_reason: <why S8 fits or does not fit>
   pattern_admission: draft | active | not-selected
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

- G1: this module entrypoint read.
- G3 (genesis applied).
- No G4/G5 product mutation of the *subject under review*.
- Exit via Atlas remember of the review outcome (subject Atlas of the *reviewed* package when durable conclusions are claimed).
  If the reviewed package has no Atlas, do not invent or create one as a
  conformance prerequisite. Return the advisory report and record an explicit
  memory deferral under the reviewer's existing write-home discipline.

## Non-goals

- Mutation of the subject under review.
- Auto-implement of recommended changes.
- Redesign of other Autogenesis operations.
- Replacing the narrow link-only module (it remains available).
- Changing the multi-harness substrate contract itself.

## Narrow review

A parent may request only the import-link support when that is the needed
facet. It must still follow the parent-bound invocation contract. This operation
is reserved for full conformance evaluation; no legacy structured alias or
direct catalogue module invocation is supported.
