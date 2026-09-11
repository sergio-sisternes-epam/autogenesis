---
name: validate-skill-import-links
description: Audit skill nesting contracts and full-body invocation links.
metadata:
  autogenesis-parent: autogenesis
  autogenesis-role: support
---

# validate-skill-import-links

Advisory audit only. Does **not** mutate the target package.

Given a target skill directory (or list of skills), verify that every skill-to-skill invocation follows the portable multi-harness substrate contract defined in the Autogenesis Atlas page `autogenesis/decisions/skill-nesting-invocation-pattern.md`.

## Arguments

- Required: `target` (one package or an explicit list of packages).
- Optional: `report_format`, `harness_filter`.
- Do not override parent-owned subject, mode, operation, work identity, Atlas, or approval.

Follow `<skill_root>/references/modules/workflow-discipline/SKILL.md` and its
invocation contract. The parent reads this entrypoint and issues a support
request with its configured compact card before the procedure. Keep the active
operation and inherited context; return the facet result and an honest receipt.
Shared assets resolve from skill_root, not cwd.

## Procedure

1. Read the Skill chaining rule in the activated Autogenesis root SKILL.md,
   resolved from `resolved.skill_root`, as the baseline for external calls.
2. If additional mapping detail is needed, consult the canonical reference
   page through Atlas in an already available Autogenesis reference store.
   Obtain its identity from the activated package's mesh, not the target's.
   Keep the resolved location in a local `reference_store_root`; never
   overwrite protected `context.atlas_root` or mount a store into the target
   as part of this advisory check. If needed detail is unavailable, report
   that review limitation rather than invent it. The target need not declare
   Atlas or copy the reviewer's reference store.

3. Identify the target(s).
   Accept a path such as `/home/workdir/.grok/skills/<name>/` or a list of skill names.
   Default if unspecified: the skill named in the current subject (if any).

4. For each target SKILL.md (and any referenced module entrypoints inside it):

   - Distinguish a parent reading a private module from invoking another
     external skill. Internal reads use declared relative entrypoints; they
     do not require catalogue loading or an invocation validator.
   - Locate every actual external skill call and check the **substrate
     contract** (the three mandatory steps), directly or through a clear
     shared instruction. A mere resource link is not an external skill call.
   - If the package claims multi-target or lists specific harnesses, also check that the corresponding rows from the per-harness mapping table are present or clearly delegated.
   - With no external skill calls, report substrate_contract n/a and explain
     why. Do not require unused dependencies or boilerplate.

5. Emit a structured report fragment with **exactly** this shape:

   ```text
   FACET: validate-skill-import-links
   target: <path or name>
   substrate_contract: pass | gaps | n/a
   harness_mapping: pass | gaps | n/a
   gaps:
     - <file:line or section> — <missing element>
   suggested_fix: |
     <exact portable text that should be inserted>
   status: pass | needs-work
   ```

6. Do **not** edit the target.
   If the operator wants the gaps fixed, they must later run an implement path (or edit manually) after reviewing the aggregated REPORT.

7. Optional protocol check: when the target under review implements or claims nesting, the report may recommend re-running the canonical reference fixture **skill-test-a → skill-test-b** on the current harness.

## Non-goals

- Automatic rewriting of the target.
- Design or implement of new skills.
- Changing genesis.
- Full package conformance (that is the deep review-package path).
