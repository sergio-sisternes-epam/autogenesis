---
name: autogenesis/paths/initialise
description: Use this path when the user wants to initialise a brand-new skill/package from scratch under Autogenesis. Informs the user, asks for confirmation, locks the subject, mints v0.1.0, applies full genesis discipline (fused, never superseded), merges autogenesis layers, produces a unified plan with mandatory ## Genesis Artifacts section, and stops for approval. Never implements.
path_id: initialise
default: false
subject_scope: subject-atlas
---

# Path: initialise

## Enter

Activation card must already show `path: initialise` and this file **read**.

## Must announce

This path **stops for approval**. Activate **implement** only after explicit approval of the pinned plan.

## Procedure (mandatory sequence)

1. **Inform + confirm**  
   Explicitly tell the user that a from-scratch initialisation is in scope for Autogenesis.  
   State that Autogenesis will apply the full genesis discipline and then fuse its own components (Atlas process memory, path modules, workflow-discipline, substrate-contract enforcement, Exit lineage).  
   Ask for explicit confirmation to proceed.  
   If the user declines, stop cleanly and return to the previous context.

2. **Lock subject + mint version**  
   On confirmation, set `subject` to the confirmed name.  
   Mint version identity `v0.1.0` for the new package.

3. **Apply substrate contract to skill named `genesis`**  
   Locate the skill by name from the harness’s available skills list, load its full SKILL.md body with the harness’s on-demand skill-loader, then follow that body exactly.  
   Design artifacts as needed; **persist plan in the subject Atlas** as a `type: plan` at `autogenesis/plans/<work_id>.md`. Record Atlas-relative `plan_path`. New packages: use Atlas path `init` with an existing remote, then mount with no `--target` and resolve the root (or stop if blocked). Memory writes use Atlas paths (G2).
   **Integrated plan rule (G3):** the Autogenesis plan **must** contain a named section `## Genesis Artifacts` that includes:
   - intent + scope
   - component diagram
   - sequence diagram
   - composition decision
   - cost stance  
   Absence of this section is a G3 failure.  
   If the design produces a skill that itself chains/invokes another skill, the plan **must** include the multi-harness substrate contract (see Atlas decision `autogenesis/decisions/skill-nesting-invocation-pattern.md`).

4. **Load and follow the internal module `references/modules/think-challenge.md`**  
   Use `read_file` (or harness equivalent) on the module path. Do **not** perform a name-based root-skill lookup. Prefer grounded counters; if internal-only, state that.

5. **Evaluate feedback and pin autonomously**  
   Accept / reject / modify each material counter. Visible **Pinned decisions** in the plan. **Do not implement** SKILL/code here.

6. **Fuse autogenesis layers**  
   Into the same plan document, merge:
   - Atlas skeleton expectations (via substrate → atlas; never hand-craft a parallel store)
   - path registry + default design path
   - workflow-discipline module
   - multi-harness substrate-contract enforcement
   - Exit lineage rules
   - unified folder layout (genesis folders + autogenesis folders merged)
   - **activation_card declaration** (work_id autogenesis-activation-card-extend): always emit `activation_card: off` in the new skill’s front-matter by default. Operator may request `--activation-card=required` (or equivalent) to force `on`. Only legal values: off | on | debug. No further nested flags.
   The fusion rule is absolute: genesis capabilities are the foundation; autogenesis extends them and never supersedes or overwrites them.

7. **Challenge-success criteria (C1–C5 + Genesis check)**  
   C1 non-trivial counter · C2 high-severity pinned or rejected with rationale · C3 visible pins · C4 scope intact · C5 no implementation in this path · **Genesis Artifacts section present and complete**.

8. **Present pinned plan for approval**  
   Plan path, pins, C1–C5 + Genesis check, exact scope, non-goals, explicit wait-for-approval statement, path receipt.  
   The presented plan **must** visibly contain the `## Genesis Artifacts` section.  
   Without approval = plan only / blocked.

## Change gates

G3 (this sequence + mandatory Genesis Artifacts section), G7 (stop-for-approval). No G4/G5 implement work.  
Consistency note: the workflow-discipline module remains the sole source of Enter/Change/Exit rules; this path only specialises the initialise procedure.

## Exit

Apply the multi-harness substrate contract to the skills named `atlas` and `okf` (see root Exit activation checklist).  
Persist Exit lineage via atlas `remember` under the subject Atlas (`autogenesis/experiences/`); compile must go green.  
Emit **path receipt** including `nested_skills_loaded` and `substrate_contract`.

## Outputs

Persisted plan path · challenge summary · pinned decisions · C1–C5 · wait-for-approval · receipt

## Non-goals

Implement, wire, auto-approve after “successful” challenge, supersede genesis, hand-craft Atlas skeletons, apply harness-specific hard bounds.
