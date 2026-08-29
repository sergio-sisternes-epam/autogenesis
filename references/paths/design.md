---
name: autogenesis/paths/design
description: Default Autogenesis path. Apply substrate contract to skill named `genesis` (and the Autogenesis patterns extension injector so B17 is visible), then load the internal module references/modules/think-challenge.md, evaluate adversarial feedback and pin autonomously, define challenge-success criteria, present pinned plan for approval. Stops for approval — do not implement here.
path_id: design
default: true
subject_scope: subject-atlas
---

# Path: design (default)

## Enter

Activation card must already show `path: design` and this file **read**.

## Must announce

This path **stops for approval**. Activate **implement** only after explicit approval of the pinned plan.

## Procedure (mandatory sequence)

0. **Assign work_id** (blocking)  
   Format: `YYYY-MM-DD-<kebab-slug>`. When an external tracker id is known: `YYYY-MM-DD-<external_id>-<kebab-slug>`.  
   Required for **all** change-classes including **hardening**. Date = plan-creation date.  
   Do **not** rename existing historical work_ids.  
   Persist on the plan; optional `external_ref` (full opaque reference) for outside trackers; create/update work node(s) at status `designed` (subject Atlas + autogenesis meta when subject ≠ autogenesis).

0b. **Classify change-class** (blocking)  
   State in the plan: `hardening` | `new-surface` | `new-skill`.  
   Ambiguous → `new-surface`.  
   Depth of genesis artifacts follows `workflow-discipline.md` (hardening abbreviated; new-surface mini-genesis; new-skill full genesis).

1. **Apply substrate contract to skill named `genesis`** (depth by class)  
   Locate the skill by name from the harness’s available skills list, load its full SKILL.md body with the harness’s on-demand skill-loader, then follow that body to the depth required by change-class.  
   Design artifacts as needed; **persist plan in the subject Atlas** under Autogenesis space as `type: plan` at `autogenesis/plans/<work_id>.md`. Record Atlas-relative `plan_path`. If subject Atlas is missing, follow **Subject Atlas resolution** in workflow-discipline (inform user; offer initiate Atlas and/or migrate okf-wiki). Memory writes use Atlas paths (G2).  
   **Integrated plan rule (G3):** the plan **must** contain `## Genesis Artifacts` and **change-class**:
   - **hardening:** intent + scope + acceptance (+ pins); diagrams optional  
   - **new-surface (mini-genesis):** intent+scope+non-goals; one mermaid; interface sketch; cost note; acceptance; stop-for-approval  
   - **new-skill / full:** intent+scope; component diagram; sequence diagram; composition decision; cost stance  
   Absence of required depth for the class is a G3 failure.  
   If the design produces a skill that itself chains/invokes another skill, the plan **must** include the multi-harness substrate contract (see `knowledge/skill-nesting-invocation-pattern.md`).

2. **Load and follow the internal module `references/modules/think-challenge.md`**  
   Use `read_file` (or harness equivalent) on the module path. Do **not** perform a name-based root-skill lookup. Prefer grounded counters; if internal-only, state that. (The module itself applies the substrate contract to `atlas` when memory ops are needed.)

3. **Evaluate feedback and pin autonomously**  
   Accept / reject / modify each material counter. Visible **Pinned decisions** in the plan. **Do not implement** SKILL/code here.

4. **Challenge-success criteria (C1–C5 + Genesis check)**  
   C1 non-trivial counter · C2 high-severity pinned or rejected with rationale · C3 visible pins · C4 scope intact · C5 no implementation in this path · **change-class stated** · **Genesis Artifacts complete for that class**.

5. **Catalogue Review (when in scope)**  
   After loading genesis (step 1), **also load** the Autogenesis extension injector `references/modules/patterns.md` so that B17 ACTIVATION CARD is visible.  
   Follow the injector’s contract and any remaining Design-time catalogue review procedure.  
   **In scope** (block required): topology, gate, multi-agent fan-out, Enter/Exit discipline, pattern-catalogue topology, extension/injection contracts.  
   **Out of scope**: pure docs, typo, version bump, non-topology fix → plan may set `catalogue_review: n/a` with one-line rationale.  
   When in scope, the plan **must** contain `## Catalogue Review` with: genesis matches (refines/uses/conflicts/none + ids); Autogenesis extension matches (B17 or future deltas); composition mode (INLINE / LOCAL SIBLING / EXTERNAL / EXTENSION); inherited anti-patterns; delta only; admission note.  
   Load genesis pattern catalogues **read-only** and **progressively** (relevant Tier-2/Tier-3 entries only — e.g. A1 PANEL, B1 Fan-out + Synthesizer — not a full dump).  
   Missing block on in-scope work → **Change incomplete**; do not claim design complete or stop-for-approval as satisfied.

6. **Adversarial scenario draft (behaviour-changing work)**  
   After pins, emit a **full construct scenario draft** (`id`, `packages`, `smokes`, `expect`, `adversarial: true`, `work_id`).  
   One smoke per grounded / named-theory counter; each smoke names its `source`. Empty draft is forbidden.  
   Filename contract: `<subject>/references/scenarios/<capability>-adversarial-vN.yaml` (new file + bump; keep prior).  
   Implement may later **add** smokes; it must not **drop** approved ones without a new design.

6b. **agent-spec BDD / behavioural gate (when behaviour is in scope)**  
   For any design that changes or defines skill/agent behaviour (new-skill, new-surface affecting runtime, or explicit behavioural contract):  
   - **Sole producer rule:** agent-spec path `specify` is the **only** legal writer of behavioural Gherkin. Autogenesis must never author, paste, or edit `.feature` files directly. Ownership sentence: “agent-spec owns writing and evolving all behavioural Gherkin specifications. Autogenesis supplies the design packet and consumes the resulting contract section + `b-` IDs (or an explicit deferral).”  
   - Invoke agent-spec path `specify` (substrate contract) with target = current plan work_id or subject/path, **or** record an explicit `deferred: <one-line reason>`.  
   - Plan must include a `## Behavioural contract (agent-spec)` section that either lists the `b-` IDs produced by `specify` or contains the deferred reason.  
   - `@forbidden` / `@critical` scenarios that protect the change must be named (via the specify output or deferred note).  
   - Load skill `agent-spec` (substrate) when calling specify or validating layout/coverage.  
   - Activation card for this design Run must carry the hint `behavioural_contract: specify | deferred:<reason>` when behaviour is in scope.  
   Missing section, missing hint, or direct authoring of Gherkin → **Change incomplete**; do not claim design complete.

6c. **Deterministic-first evaluation plan (when behaviour is in scope)**  
   Behavioural claims that can be checked by machine must not rely only on LLM/agent narrative.  
   Plan must include an `## Evaluation plan` section with two layers:  
   - **Deterministic smokes (primary):** file/dir presence or absence, JSON/front-matter keys, receipts, exit codes, fail-closed artefacts, forbidden roots, network/process checks as applicable. Map each in-scope `b-` ID (or contract family) to a probe kind Construct (or equivalent) can execute.  
   - **Agent evaluations (secondary, optional):** trajectory / “did the agent ask” / soft adherence — never the sole evidence for a contract that admits a deterministic check.  
   Anti-pattern: **soft-only evaluation** (behavioural claim validated only by prose).  
   Missing Evaluation plan on in-scope behavioural work → **Change incomplete**.

7. **Present pinned plan for approval**  
   Plan path, pins, C1–C5 + Genesis check, Catalogue Review (or n/a), behavioural contract (or deferred), evaluation plan (or n/a), exact scope, non-goals, adversarial draft, explicit wait-for-approval statement, path receipt.  
   The presented plan **must** visibly contain the `## Genesis Artifacts` section.  
   Without approval = plan only / blocked.

## Change gates

G3 (change-class + genesis depth by class), G7 (stop-for-approval), **G-BDD** (agent-spec behavioural contract section present or explicit deferral when behaviour is in scope), **G-EVAL** (deterministic-first evaluation plan when behaviour is in scope). No G4/G5 implement work.  
Consistency note: the workflow-discipline module remains the sole source of Enter/Change/Exit rules; this path only specialises the design procedure.

## Exit

Apply the multi-harness substrate contract to the skills named `atlas` and `okf` (see root Exit activation checklist).  
Load the Atlas path module `remember` (or `work`) via substrate contract and follow it exactly; require green `atlas compile`.  
Emit **path receipt** including `nested_skills_loaded`, `substrate_contract`, `atlas_root` and `compile`.

## Outputs

**work_id** · Persisted plan path · challenge summary · pinned decisions · C1–C5 · wait-for-approval · receipt

## Non-goals

Implement, wire, auto-approve after “successful” challenge.
