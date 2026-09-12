---
name: initialise
description: Initialise a purpose-led skill design after confirmation, apply full Genesis design discipline and stop for approval. Do not inherit a runtime framework by default.
metadata:
  autogenesis-parent: autogenesis
  autogenesis-role: operation
---

# Operation: initialise

## Arguments

- Required: `objective` (the new skill's purpose).
- Optional: `proposed_name`, `activation_card` (off, on or debug),
  `behavioural_contract` (specify or explicit deferral).
- The parent owns confirmed subject, mode, operation, work identity, storage
  and approval. A proposed name is not authority to switch subject.
- Follow `<skill_root>/references/modules/workflow-discipline/SKILL.md` and
  its module-local invocation contract. Resolve siblings from the registry
  and shared resources from skill_root.

## Enter

The parent issues an operation request for `initialise`, reads this entrypoint
and emits the configured full request card before the procedure.

## Must announce

This operation **stops for approval**. Request **implement** only after explicit approval of the pinned plan.

## Procedure (mandatory sequence)

1. **Inform + confirm**
   Explicitly tell the user that a from-scratch initialisation is in scope for Autogenesis.
   State that Autogenesis will apply full Genesis design discipline, authoring
   memory, approval and lineage. The derived skill receives only runtime
   capabilities its purpose needs. Modules, runtime memory and full fusion
   require an explicit applicability decision; no framework is inherited by
   default. If full fusion is requested, confirm its concrete runtime scope.
   Ask for explicit confirmation to proceed.
   If the user declines, stop cleanly and return to the previous context.

2. **Lock subject + mint version**
   On confirmation, the parent explicitly establishes the confirmed subject
   context; this child cannot override it through arguments.
   Mint version identity `v0.1.0` for the new package.

3. **Apply substrate contract to skill named `genesis`**
   Locate the skill by name from the harness’s available skills list, load its full SKILL.md body with the harness’s on-demand skill-loader, then follow that body exactly.
   Design artifacts as needed; **persist plan in the subject Atlas** as a `type: plan` at `autogenesis/plans/<work_id>.md`. Record Atlas-relative `plan_path`. New packages: use Atlas path `init` with an existing remote, then mount with no `--target` and resolve the root (or stop if blocked). Memory writes use Atlas paths (G2).
   **Integrated plan rule (G3):** the Autogenesis plan **must** contain a named section `## Genesis Artifacts` that includes:
   - `change-class: new-skill`
   - intent + scope
   - component diagram
   - sequence diagram
   - composition decision
   - cost stance
   Absence of this section is a G3 failure.
   If the design produces a skill that itself chains/invokes another skill, the plan **must** include the multi-harness substrate contract (see Atlas decision `autogenesis/decisions/skill-nesting-invocation-pattern.md`).

3b. **Apply the full SOLID principles for skills lens**
   Load
   `<skill_root>/references/skill-design-principles.md`
   after Genesis. Every new-skill plan must contain the five-row applicable /
   not-applicable / trade-off record before approval presentation. Use the
   record to make the root-only versus modular consequence explicit.
   It must not assume that a new skill needs modules, adapters or runtime
   machinery.

4. **Invoke support `think-challenge` through the parent registry**
   Pass the candidate plan as `arguments.design_target`; retain confirmed parent context.
   Use `read_file` (or harness equivalent) on the module path. Do **not** perform a name-based root-skill lookup. Prefer grounded counters; if internal-only, state that.

5. **Evaluate feedback and pin autonomously**
   Accept / reject / modify each material counter. Visible **Pinned decisions** in the plan. **Do not implement** SKILL/code here.

6. **Compose the derived skill's runtime**
   Into the same plan document, specify:
   - The subject's needed capabilities; keep a short single-purpose skill root-only.
     Retain the root's required Agent Skills name and description frontmatter
     in either layout; a procedure body alone is not the complete SKILL.md.
   - A parent registry and instruction-only modules when distinct procedures
     justify them; no default design operation or workflow-discipline copy.
   - Full-body substrate loading for actual external skill calls.
   - Runtime memory only when the subject needs it. Atlas authoring memory
     remains required for this design, but does not force runtime Atlas into
     the generated skill.
   - The subject's own approval boundaries, actual outcomes and resource layout.
   - **activation_card declaration** (work_id autogenesis-activation-card-extend): always emit `activation_card: off` in the new skill’s front-matter by default. Operator may request `--activation-card=on` (or equivalent) to enable it. Only legal values: off | on | debug. No further nested flags.
   Genesis remains the design foundation; Autogenesis extends rather than
   supersedes it. This is not automatic inheritance of either designer's
   runtime. For an explicitly requested self-evolving/full-fusion skill,
   enumerate and approve the included capabilities and dependencies.
   Do not scaffold custom JSON protocols, trace ledgers, validators or empty
   resource directories merely to adopt modules. Task-serving scripts remain
   allowed when their need is justified.
   Request support `patterns` with `arguments.intent: load` and the candidate
   plan as `arguments.target`. For module composition consider `autogenesis:S8`;
   record `pattern_applicability: applicable | not-applicable` with a reason
   and `pattern_admission: draft | active | not-selected`. Preserve the
   confirmed runtime scope; do not blindly scaffold extra modules or apply a
   draft before design approval. Admission remains separate from approval.

6b. **Behavioural contract (agent-spec)**
   A new skill is behavioural work. The plan must contain
   `## Behavioural contract (agent-spec)` with produced `b-` IDs or an explicit
   deferral. Agent-spec remains the sole writer of behavioural Gherkin;
   Autogenesis supplies the design packet and consumes the returned contract.
   Name applicable `@forbidden` or `@critical` scenarios. The operation request
   must carry `arguments.behavioural_contract: specify | deferred:<reason>`.

6c. **Deterministic-first evaluation plan**
   The plan must contain `## Evaluation plan`. Map every machine-checkable
   behavioural claim or `b-` family to an executable command or existing
   repository check. Agent evaluations are optional secondary evidence and
   cannot replace deterministic checks.

7. **Challenge-success criteria (C1–C5 + Genesis check)**
   C1 non-trivial counter · C2 high-severity pinned or rejected with rationale · C3 visible pins · C4 scope intact · C5 no implementation in this operation · **change-class: new-skill** · **Genesis Artifacts section present and complete** · **behavioural contract present or explicitly deferred** · **evaluation plan complete**.

8. **Present pinned plan for approval**
   Plan location, pins, C1–C5 + Genesis check, change-class, behavioural
   contract, evaluation plan, exact scope, non-goals, explicit
   wait-for-approval statement and invocation receipt.
   The presented plan **must** visibly contain the `## Genesis Artifacts` section.
   Without approval = plan only / blocked.

## Change gates

G3 (change-class: new-skill + mandatory Genesis Artifacts section), G7
(stop-for-approval), **G-BDD** (agent-spec behavioural contract or explicit
deferral), **G-EVAL** (deterministic-first evaluation plan). No G4/G5 implement
work.
Consistency note: workflow-discipline remains the sole source of Enter/Change/Exit rules; this operation only specialises the initialise procedure.

## Exit

Apply the multi-harness substrate contract to the skills named `atlas` and
`okf` through
`<skill_root>/references/modules/workflow-discipline/SKILL.md#exit-blocking`.
Persist Exit lineage via atlas `remember` under the subject Atlas (`autogenesis/experiences/`); compile must go green.
Emit the canonical invocation receipt with actual loaded entrypoints and
substrate evidence, and `result.disposition: awaiting-approval`.

## Outputs

Persisted plan path · challenge summary · pinned decisions · C1–C5 · wait-for-approval · receipt

## Non-goals

Implement, wire, auto-approve after “successful” challenge, supersede genesis, hand-craft Atlas skeletons, apply harness-specific hard bounds.
