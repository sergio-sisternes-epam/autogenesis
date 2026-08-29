---
name: autogenesis/modules/validate-skill-import-links
description: Internal Autogenesis module. Audit a target skill package for consistent application of the multi-harness skill-nesting substrate contract (load/hand-off/invoke wording). Progressive-disclosure only; loaded by the deep review-package path or for fast link-only checks.
internal: true
---

# validate-skill-import-links

Advisory audit only. Does **not** mutate the target package.

Given a target skill directory (or list of skills), verify that every skill-to-skill invocation follows the portable multi-harness substrate contract defined in the autogenesis knowledge page `skill-nesting-invocation-pattern.md`.

## Procedure

1. Load the nesting knowledge page `skill-nesting-invocation-pattern.md` from the autogenesis wiki (use the path the harness surfaces for that knowledge page; do not hard-code absolute paths).

2. Identify the target(s).  
   Accept a path such as `/home/workdir/.grok/skills/<name>/` or a list of skill names.  
   Default if unspecified: the skill named in the current subject (if any).

3. For each target SKILL.md (and any referenced path modules inside it):

   - Locate every place that claims to invoke, load, call, or nest another skill.
   - Check for presence of the **substrate contract** (the three mandatory steps).
   - If the package claims multi-target or lists specific harnesses, also check that the corresponding rows from the per-harness mapping table are present or clearly delegated.

4. Emit a structured report fragment with **exactly** this shape:

   ```text
   FACET: validate-skill-import-links
   target: <path or name>
   substrate_contract: pass | gaps
   harness_mapping: pass | gaps | n/a
   gaps:
     - <file:line or section> — <missing element>
   suggested_fix: |
     <exact portable text that should be inserted>
   status: pass | needs-work
   ```

5. Do **not** edit the target.  
   If the operator wants the gaps fixed, they must later run an implement path (or edit manually) after reviewing the aggregated REPORT.

6. Optional protocol check: when the target under review implements or claims nesting, the report may recommend re-running the canonical reference fixture **skill-test-a → skill-test-b** on the current harness.

## Non-goals

- Automatic rewriting of the target.
- Design or implement of new skills.
- Changing genesis.
- Full package conformance (that is the deep review-package path).
