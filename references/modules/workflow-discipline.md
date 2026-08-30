---
name: autogenesis/modules/workflow-discipline
description: Internal Autogenesis module. Source of truth for the workflow engine (activation card, Enter | Change | Exit clusters, G0–G8 gates, path loading contract, discussion/run rules, path receipt, substrate-contract reminder). Progressive disclosure only — never a catalog skill. Designed for clean future extraction.
internal: true
version: 2026-08-26
---

# workflow-discipline (internal)

This module is the single source of truth for the Autogenesis workflow engine.  
Root `SKILL.md` and all path modules must load and follow it rather than re-implement the rules.

## Activation card (Enter – blocking)

**Before any path work**, emit exactly this card (fill all fields). Missing field ⇒ `incomplete: missing Enter`.

```text
skill: <activating skill name>
skill_path: <resolved path to that skill’s root directory>
mode: run | discussion
subject: <skill under change>
path: design | implement | research | reflect-challenge | learn-skill | reevaluate | aware-runtime | wire | review-package | atlas-migrate | discuss
path_module: references/paths/<path>.md
intent: <one line>
behavioural_contract: specify | deferred:<one-line reason>   # required on design when behaviour is in scope
```

### Rules

1. **Read** `path_module` via `read_file` (or harness equivalent) before executing that path — do not run from the registry stub or prior memory alone.
2. **One path at a time** — no silent path→path invokes. An in-flight design review that needs a discussion **re-issues** Enter for `mode: discussion`, `path: discuss` (same `work_id`, `stage: design`, `artifact` = the plan, existing `discussion_root`). It does not nest discuss under design.
3. **Discussion mode:** zero implement authority; no product file writes; no “Run complete” claim. Path **must** be `discuss`. Load `references/paths/discuss.md`, then substrate-load catalog skill **discuss** and follow its full body. Pass `atlas_root` = subject Atlas. Required extra card fields: `objective`, `atlas_root`, `discussion_root`, `current_branch`. Missing discuss load or missing those fields ⇒ `incomplete: missing Enter`. Do not load internal think-grill or think-ramble. Do not load internal think-challenge as a user verb. To change code/plan, re-issue card with `mode: run`.  
   - Discussion **may** invoke agent-spec path `specify` (mode=discussion) purely for exploration or review of candidate behaviours.  
   - Discussion may **never** materialise a finished `## Behavioural contract (agent-spec)` section into a plan, nor claim that a behavioural contract is complete. Only a formal design Run (via `specify` or explicit deferred) may write the section.
4. **No discussion → implement short-circuit:** Discussion mode must never transition directly to implement. The only legal path is discussion → formal design (`mode: run`, path: design) → persisted + challenged plan → explicit approval → implement. Any attempt to jump the gate is refused; the agent re-issues Enter for formal design.
5. Default path if unspecified in **Run**: **design** (stops for approval). Default path if unspecified in **discussion**: **discuss**.
6. **Behavioural-contract hint (design only):** When the design changes or defines skill/agent behaviour, the activation card **must** carry `behavioural_contract: specify | deferred:<reason>`. Missing hint on in-scope work → incomplete Enter.

### Optional activation-card feature (any skill)

Any skill may declare in its front-matter:

```yaml
activation_card: off | on | debug
```

- Legal values only (no further nesting).  
- When `off` or absent the card discipline is skipped.  
- When `on` or `debug` the Enter card + path receipt become required for that skill’s Runs (same schema as above).  
- New skills created by Autogenesis always receive the declaration (default `off`); operator may force `required` at initialise.  
- review-package (via validate-gate-map-and-non-goals) reports the status; the check is necessary but never sufficient for overall pass.  
- See work_id `autogenesis-activation-card-extend` and residual risks named in that plan.

## Change (blocking)

### Change-class (required on design)

Before drafting the design packet, **classify** the work (state class in the plan and Enter intent):

| Class | Meaning | Design bar before implement |
|-------|---------|------------------------------|
| **hardening** | Fix edge, expect, copy, docs, version bump, dead link, small contract tweak | Autogenesis packet: problem, pins, acceptance, non-goals. Genesis Artifacts may be **abbreviated** (intent+scope + acceptance only). |
| **new-surface** | New CLI subcommand, ledger, report schema, smoke type, storage file, cross-skill protocol | **Mini-genesis required** (see below). |
| **new-skill** | New package / skill init | Full genesis + initialise path (existing). |

**Default when ambiguous: `new-surface`.**

#### Mini-genesis (new-surface) — minimum in plan `## Genesis Artifacts`

1. Intent + scope + non-goals  
2. One mermaid (sequence or component)  
3. Interface sketch (CLI / file formats / smoke types)  
4. Cost note (qualitative tokens/ops OK)  
5. Acceptance criteria  
6. Explicit stop-for-approval  

#### Full genesis (new-skill / default large design)

Named `## Genesis Artifacts`: intent+scope, component diagram, sequence diagram, composition decision, cost stance (unchanged G3 full bar).

| Path | Requirement |
|------|-------------|
| **design** | Full procedure in `paths/design.md`: **change-class** → genesis depth by class → internal `modules/think-challenge.md` → pin → C1–C5 → **Catalogue Review** (genesis + patterns module when topology/gate/panel shaped; else n/a) → present for approval. **No implement.** See `modules/patterns.md`. |
| **implement** | **Only** after explicit user approval of a **persisted plan**. Apply approved scope only; version identity; **no auto-wire**. **Refuse** if plan class is `new-surface` and mini-genesis artifacts are missing. |
| Other paths | Follow that path module only. |

### Hard boundaries during Change

| Rule | Statement |
|------|-----------|
| Subject | Every Run declares `subject`. |
| Atlas | Always resolve subject Atlas root = `<subject>/references/atlas/` (when subject is autogenesis: this skill’s `references/atlas` submodule after `atlas mount github.com/sergio-sisternes-epam/autogenesis-atlas --ref main --target references/atlas`). Use Atlas paths only. |
| Plan home | Design plans persist **only** under subject Atlas **`autogenesis/plans/<work_id>.md`** (`type: plan`). Not experiences; not `artifacts/autogenesis-plans/` as primary. |
| Atlas missing | If subject has no Atlas: **inform user** and offer **initiate Atlas** (and **migrate okf-wiki→Atlas** when `references/wiki/` exists). When subject is autogenesis, mount `github.com/sergio-sisternes-epam/autogenesis-atlas --ref main --target references/atlas`. Do not silent-fallback. |
| Approval | Implement forbidden until a **persisted plan produced by formal design** is explicitly approved. |
| Discussion→Implement | Forbidden. Discussion has zero implement authority; short-circuit is incomplete. |
| Wiring | Human approval + version provenance only. |
| Sharing | Links + skill-feedback; no peer content copy/remote mutation. |
| Integrated plans | Every design plan **must** contain `## Genesis Artifacts` and state **change-class**. Depth follows class: hardening abbreviated; new-surface mini-genesis; new-skill/full design full genesis. Wrong depth for class is a G3 failure. |
| Source of truth | This module is the sole source of the Enter/Change/Exit rules, card schema, gate map and path receipt. Any full copy of those rules outside this module is a drift defect. |
| Session vs Atlas | Subject Atlas persistence across sessions is required. “Empty session” means only that no run is active in the *current conversation*. Test plans and path language must **not** request store wipes or “treat the Atlas as empty”. See decisions/empty-session-vs-persistent-atlas.md under the Atlas root. |

### work_id lineage (navigable design ↔ implement ↔ todo)

Every formal design plan — **including hardening** — must declare a stable **`work_id`**.

**Format (mandatory for new work from 2026-08-24 onward):**

```text
YYYY-MM-DD-<kebab-slug>
```

When an external tracker id is known at plan time:

```text
YYYY-MM-DD-<external_id>-<kebab-slug>
```

Examples: `2026-08-24-work-id-date-prefix`, `2026-08-24-gh-1234-output-agnostic`, `2026-08-24-PROJ-42-migrate`.

- Date = calendar date of plan creation (consistent within the Run).
- `<external_id>` = filesystem-safe short form of the tracker key (optional).
- Descriptive kebab slug remains required (not date-only or id-only).
- **No backward renames:** existing work_ids, plan files, and work hubs stay as-is.

| Artifact | Requirement |
|----------|-------------|
| Plan page (subject Atlas) | `type: plan` at **`autogenesis/plans/<work_id>.md`**. `plan_path` Atlas-relative. |
| Work node (subject Atlas) | `autogenesis/work/<work_id>.md` (type: work) |
| Work node (autogenesis meta) | Same `work_id` when subject ≠ autogenesis; single home when subject is autogenesis |
| Implement experience | Frontmatter: `work_id`, `implements`, `closes`, `plan_path`, `construct_eval` |
| Backlog rows | Keyed by `work_id` (local aliases like C-P1 optional) |

**Status values:** proposed | designed | approved | implementing | done | deferred | waived  

**Optional `external_ref`:** opaque string for an outside tracker (GitHub issue URL, Jira key, Linear id, etc.). Agnostic — no built-in client. Omit when unused. May appear on plan, work node, and implement experience for correlation only. When present, embed a short filesystem-safe form in the `work_id` slug after the date (see format above).  

**Navigability:** work node body lists plan path, implement experience, backlog, optional construct report.  
**Gate:** design persist without `work_id` → incomplete G3. Implement complete without updating work node(s) → incomplete G8.  
**construct:** may be cited as evidence path only; does not interpret `work_id` (boundary R1).

### Subject Atlas resolution (before plan persist or memory write)

Resolve `subject_atlas = <subject>/references/atlas/` (when subject is autogenesis: `references/atlas` after `atlas mount github.com/sergio-sisternes-epam/autogenesis-atlas --ref main --target references/atlas`).

| Situation | Agent action |
|-----------|----------------|
| `SCHEMA.json` present under subject Atlas | Persist plans + memory there; `atlas compile` green required |
| No Atlas, but `<subject>/references/wiki/` looks like okf-wiki | **Inform user.** Offer **(A) Initiate Atlas**, **(B) Migrate okf-wiki → Atlas**, **(C) Abort**. Do not persist plan until A or B completes or user aborts |
| Neither Atlas nor okf-wiki | **Inform user.** Offer **(A) Initiate Atlas** or **(C) Abort**. When subject is autogenesis, mount with `--target references/atlas` instead of initiate |
| User chooses Initiate Atlas | Bootstrap subject Atlas (SCHEMA with `autogenesis_space`, full `autogenesis/` tree, templates including plan.md, empty staging) using Atlas skill patterns; then continue. When subject is autogenesis, mount the `references/atlas` submodule instead of bootstrapping a new store |
| User chooses Migrate | `atlas migrate <wiki> --root <subject_atlas>` then promote/claims until staging empty and compile green; then continue |

Primary plan home is **never** `artifacts/autogenesis-plans/`. External copies are optional provenance only.

### Path-load rule (reevaluate / challenged_plan honesty)

When this Run **claims** Autogenesis reevaluate, challenged plan, or equivalent:

1. **Load** the relevant path module (`references/paths/reevaluate.md` or successor) via `read_file` **before** emitting the claim.  
2. Record path modules loaded in the plan receipt, train-report, or (when present) construct `activation.jsonl`.  
3. Claiming `challenged_plan` / reevaluate **without** path load is a **discipline violation** → incomplete Change.

### Construct boundary (acyclic) + post-implement evaluation

**Dependency rules (never reverse):**

| ID | Rule |
|----|------|
| **R1** | **construct MUST NOT** depend on, import, or invoke **autogenesis**. |
| **R2** | **autogenesis MAY** invoke **construct CLI only** after implement when a scenario covers the change. |
| **R3** | agent-brain may call both; neither is under the other. |
| **R4** | Atlas is the process-memory SoT for Autogenesis; construct workspaces are ephemeral evaluation. |
| **R5** | Scenarios encode acceptance criteria; they do not invent product behaviour (behaviour changes go through Autogenesis design → implement first). |

**Activation vs discipline:** Activation SoT = construct `activation.jsonl` when a workspace exists. Discipline = path rules + structural gates; construct checks only the machine-checkable subset. Opening a file ≠ process followed.

### Construct-aware Exit (additional checks)

When any of the following holds — subject owns `references/scenarios/*.yaml`; work touches construct / train-report / activation ledger; user named construct evaluation; **or** implement changed runtime behaviour covered by a scenario — Exit **must** also state:

| Check | Rule |
|-------|------|
| Scenario contract | Scenario id + **version bump** if behaviour contract changed |
| Construct smokes | Smoke list updated **or** explicitly deferred with reason |
| Schema | Report/ledger schema version noted if contract changed |
| Green construct | **Post-implement:** if a scenario covers this change, run `construct create` (or reuse) → `run`. Red without user **waive** → `incomplete: evaluation (construct)`. Doc-only hardenings may defer construct with reason. |
| Adversarial suite | Behaviour-changing implement: run `<capability>-adversarial-vN` as well as happy-path. Empty suite forbidden. **Waive** a red smoke only when that **named counter is out of scope**. Implement may add smokes; must not drop approved smokes without a new design. Scenario lives on the subject skill. New file + version bump; keep prior. |
| Lineage | Experience links `last-report.json` / workspace evidence path when construct ran |

## Exit (blocking)

**Lineage is an intent, not a file format.** Completing a Run path **must** activate the skill named `atlas` (and `okf` for format questions) using the multi-harness substrate contract. Abbreviated or memory-only activation is forbidden.

**Hard rule (never hand-craft):** If the subject Atlas root is missing or incomplete, Autogenesis must never invent a parallel store. Bootstrap via Atlas SCHEMA + templates (or the atlas skill’s own bootstrap patterns) and leave compile green. Do not fall back to okf-wiki for new process memory.

**Hard rule (claim = action):** Prose is not fulfilment.  
- `remember: yes` in the path receipt is allowed **only if** an Atlas `remember` path (or equivalent CLI write + compile) actually ran and produced a durable page in the subject Atlas (or a durable failure record).  
- `compile: yes` is allowed **only if** `atlas compile --root <atlas>` exited 0.  
- `defer: <reason>` is allowed **only if** the experience body contains that exact explicit deferral line.  
- A chat sentence or experience line that says “remembered” without the Atlas call + green compile is **not** fulfilment → `incomplete: Exit (G6/G8)`.  
Evidence of Exit success is in the subject Atlas root (and its `log.md` / compile status), not in conversation narrative.

### Exit activation checklist

1. Resolve subject Atlas root: `<subject>/references/atlas/` (when subject is autogenesis: `references/atlas` after `atlas mount github.com/sergio-sisternes-epam/autogenesis-atlas --ref main --target references/atlas`).
2. **Cheap existence check:** does `<atlas_root>/SCHEMA.json` exist?
3. **If SCHEMA.json is missing:** when subject is autogenesis, **stop** and mount `github.com/sergio-sisternes-epam/autogenesis-atlas --ref main --target references/atlas`. Other subjects: bootstrap a minimal Atlas root (SCHEMA, index.md, log.md, templates, empty staging) following the atlas skill patterns; then continue. Prefer the atlas skill’s own guidance over inventing structure.
4. Apply the multi-harness substrate contract to the skill named `atlas`.
5. Because Atlas defers format rules, also apply the substrate contract to the skill named `okf` when format questions arise.
6. Set `--root` to the resolved subject Atlas root.
7. Load the appropriate Atlas path module (`remember` / `query` / `work`) via the multi-harness substrate contract and follow it exactly.
8. **Changed-files linkage (mandatory when product files were created or edited):** the experience body must contain a structured `## Changed files` section that lists every relative path touched. Missing or incomplete list → `incomplete: G8`.
9. **Claim-bearing page rule (hard):** If any decision/experience/work page was created or materially updated during the Run, an Atlas `remember` + green `atlas compile` **must** have been executed **or** the experience body must contain an explicit one-line deferral with reason. Path/plan completion is forbidden while only a textual “remember requested” exists.
10. Structural gates: `atlas compile` must be green (staging empty).
11. **Parked future work is a protostar, not a residuals folder.** Do not create `autogenesis/residuals/` (or any `residuals/` work bucket). If a refine, question, probe, tension, or later action survives the Run, write `type: protostar` beside the origin page (plan or work hub folder). Required: `work_id`, `kva: forming`, `growth: true`, `star_kind`, `relates_to` origin `derived_from`, `relates_to` work hub `implements`. Follow discuss sprout when a discussion graph exists. Search key is `type: protostar` / `kva: forming`. A protostar is not implement authority.

### Path receipt (required to claim path complete)

```text
skill: <activating skill name>
skill_path: <resolved path to that skill’s root directory>
subject: …
path: …
approved: yes | n/a | no
atlas_root: <subject>/references/atlas   # subject=autogenesis → references/atlas
nested_skills_loaded: …
substrate_contract: applied | missing
remember: yes | no
compile: yes | no | defer: <reason>
Enter|Change|Exit: pass | incomplete: <cluster>
```

Missing receipt or `substrate_contract: missing` ⇒ path **not** complete.  
`remember` / `compile` fields that do not match executed substrate actions ⇒ path **not** complete.

## Gate map G0–G8 → clusters

| Gate | Cluster | Requirement |
|------|---------|-------------|
| **G0** | Enter | mode; Run ⇒ subject + intent; discussion ⇒ no implement |
| **G1** | Enter | path + **path module read**; one path; no silent invokes |
| **G2** | Change/Exit | Atlas → subject Atlas root; primary writes to subject Atlas |
| **G3** | Change | design: **change-class** + genesis depth by class + challenge + pin + C1–C5 + `## Genesis Artifacts` |
| **G4** | Change | explicit approval before implement |
| **G5** | Change | implement matches plan; version; no auto-wire |
| **G6** | Exit | lineage/reflection on subject (via Atlas remember / query / work) |
| **G7** | Change | design announces stop-for-approval |
| **G8** | Exit | consolidate: remember + green compile (or explicit defer) |

## Skill chaining reminder

When any skill body or path module must invoke another skill, the **multi-harness substrate contract** is mandatory. See `knowledge/skill-nesting-invocation-pattern.md`.

## Future extraction notes

This module is intentionally written with a pure interface (card schema, gate checks, receipt format, mode rules).  

To extract later into a peer skill:

1. Move this file (or a refined copy) into a new root skill directory.
2. Change all load sites from relative `read_file references/modules/workflow-discipline.md` to the multi-harness substrate contract loading the new root skill by name.
3. No behavioural change to the engine itself is required.
4. Update callers (root SKILL.md, path modules, knowledge pages) in a dedicated Autogenesis design + implement run.

### Extraction readiness

- Interface purity: high (card, gates, receipt, mode rules only)
- Hard-coded Autogenesis assumptions: none material
- Call sites that would need updating: root SKILL.md, paths/design.md, knowledge/discipline-enter-change-exit.md (and any future path that loads the module)
- Status: ready for extraction when external reuse demand appears

When this module itself is the subject of a Run, the path receipt may optionally include the line `extraction_readiness: ready | needs-work`.

---

**End of workflow-discipline module**
