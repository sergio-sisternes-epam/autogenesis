---
name: autogenesis
description: Use this skill when the user wants to grow an existing skillset from its own experience store, run Autogenesis discipline, or initialise a brand-new skill/package from scratch. Core design process is genesis (fused, never superseded); activation uses path modules with default path design (stops for approval). Triggers on autogenesis, grow skills from references, expand this skillset from its wiki, path design, implement, or initialise / create new skill. Do not use for automatic wiring of new skills into parents.
version: 0.3.13
activation_card: on
---

# autogenesis

**v0.3.13** (semver) — parked future work is a protostar linked to the work hub. No `residuals/` bucket. Builds on 0.3.12.

### Changelog (0.3.12 → 0.3.13)

- **Exit / process memory:** deferred items are `type: protostar` with `work_id`, origin `derived_from`, work-hub `implements`. Folder `autogenesis/residuals/` is forbidden. Plan heading `Accepted risks` replaces `Residual risks` so leftover *risk* is not leftover *work*. Work_id `2026-08-26-residuals-vs-protostar`.

### Changelog (0.3.11 → 0.3.12)

- **path discuss / from active design:** a problem found in design review re-enters `mode: discussion` on the same `work_id`. `stage: design`, `artifact` = the plan, existing `discussion_root` reused, prior idea nodes in scope. No nested path, no blank hub. Work_id `2026-08-26-discuss-from-active-design`.

### Changelog (0.3.10 → 0.3.11)

- **path discuss:** `mode: discussion` must use `path: discuss`. Path module substrate-loads catalog skill discuss, passes subject `atlas_root`, fail-closed Enter if discuss load or discuss fields are missing. think-grill / think-ramble not loaded in discussion mode. think-challenge stays an internal validation gate. Work_id `2026-08-26-autogenesis-discuss-activation`.

### Changelog (0.3.9 → 0.3.10)

- **design path step 6b:** agent-spec path `specify` is now the **sole** legal producer of behavioural Gherkin. Direct authoring by Autogenesis forbidden. Explicit `deferred: <reason>` remains first-class. Activation card gains required `behavioural_contract: specify | deferred:<reason>` hint when behaviour is in scope. Discussion principles updated (explore via specify in discussion mode; only design materialises). Work_id `2026-08-25-specify-only-behavioural-contract`.

### Changelog (0.3.8 → 0.3.9)

- **card pattern (B17 / workflow-discipline):** Enter card and path receipt now begin with `skill:` and `skill_path:` (first two fields). Canonical schema updated; peers receive the same leading fields.

### Changelog (0.3.7 → 0.3.8)

- **design path step 6c:** `## Evaluation plan` required when behaviour is in scope — deterministic smokes primary, agent evaluations secondary; anti-pattern soft-only evaluation; gate **G-EVAL**.

### Changelog (0.3.6 → 0.3.7)

- **design path:** step 6b — agent-spec behavioural contract (`## Behavioural contract (agent-spec)`); G-BDD gate.
- Depends on skill `agent-spec` for layout / coverage validation when the gate runs.

### Changelog (0.3.5 → 0.3.6)

- **atlas-migrate:** mandatory thorough relationship review + quality `relates_to` before Exit (from 0.3.5).
- **Internal think modules** (challenge / grill / ramble): Atlas query/remember only; no okf-wiki substrate.
- **Paths** initialise / learn-skill / research: Atlas-first process memory.
- **activation-card / run-record-template:** `atlas_root` + compile on receipts.
- **validate-okf-conformance:** prefers Atlas store; optional `atlas compile`.
- **Canonical decision:** `wiki-folder-deletion-policy` — no auto-delete on migrate; human-gated archive removal.
- **Package metadata:** `apm.yml` deps on atlas + okf (not okf-wiki).

Grows a skillset from its own experience store, or initialises a brand-new package from scratch by fusing full genesis discipline with Autogenesis components.

**Core design process is genesis (fused, never superseded).**  
**Traversal is path modules** (load before execute).  
**Discipline is three clusters: Enter → Change → Exit** (G0–G8 map into these).

```text
genesis     = design quality (packet, challenge, pin, criteria, persist)
activation  = subject + path module must-load
Enter|Change|Exit = only public blocking checkpoints
fusion      = genesis capabilities are the foundation; Autogenesis extends them
change-class = hardening | new-surface | new-skill (see workflow-discipline)
```

**Design depth:** load `references/modules/workflow-discipline.md` — classify before packet; `new-surface` requires mini-genesis; construct Exit when scenarios/contracts involved.

## Boundary with construct (no cycles)

- **construct** never depends on or invokes **autogenesis** (R1).
- **autogenesis** may call **construct CLI** after implement when scenarios cover the change (R2).
- Activation evidence: construct `activation.jsonl` when a fixture is active; discipline remains path/receipt rules.
- Ownership: Autogenesis designs and changes; construct evaluates in isolation.


## Experience source

Process memory is **not** in this repo. Canonical store: `github.com/sergio-sisternes-epam/autogenesis-atlas`. OKF root is the git clone root (`SCHEMA.json`), not a nested `atlas/` folder.

```text
atlas mount github.com/sergio-sisternes-epam/autogenesis-atlas --ref main
```

**Default store (this skill):** `.atlas/github.com/sergio-sisternes-epam/autogenesis-atlas`

Do not add `references/atlas/` here.

- **Primary change memory:** **subject** skill Atlas via **Atlas** paths (`query` / `remember` / `work`). Autogenesis-authored pages live under **`autogenesis/`** inside that root.
  - Other subjects: `<subject>/references/atlas/`
  - **subject is autogenesis:** this skill’s default store (mounted path above)
- **This skill’s Atlas:** meta lineage when subject is autogenesis, or optional run **pointers** when subject is another skill. Same mounted default store.
- **Plans (Autogenesis space):** `autogenesis/plans/<work_id>.md` with `type: plan` (SCHEMA `autogenesis_space`). Not experiences. Not `artifacts/autogenesis-plans/` as primary.  
  **work_id format (new work):** `YYYY-MM-DD-<kebab-slug>`; with external id: `YYYY-MM-DD-<external_id>-<kebab-slug>`. No renames of historical work_ids.
- **Atlas is the only ingestion authority** for process memory and design plans of this skill (no parallel ingest pipeline; okf-wiki is legacy read-only archive).

### Subject Atlas resolution (blocking before plan persist)

1. If **subject is autogenesis:** `subject_atlas = .atlas/github.com/sergio-sisternes-epam/autogenesis-atlas` after `atlas mount github.com/sergio-sisternes-epam/autogenesis-atlas --ref main`. Do not use or create `references/atlas/` in this repo.
2. Else resolve `subject_atlas = <subject>/references/atlas/`.
3. **Atlas present** (`SCHEMA.json` exists) → persist plans and memory there; `atlas compile` must go green.
4. **No Atlas, but okf-wiki present** (`<subject>/references/wiki/` with SCHEMA/index) → **stop and inform the user**. Offer:
   - **(A) Initiate Atlas** for the subject (bootstrap `references/atlas/` via Atlas patterns), then continue;
   - **(B) Migrate okf-wiki → Atlas** (`atlas migrate` + promote/claims), then continue;
   - **(C) Abort** this Run’s plan persist.
   Do not offer initiate-into-this-repo when subject is autogenesis.
5. **Neither Atlas nor okf-wiki** → **stop and inform the user**. Offer **(A) Initiate Atlas** or **(C) Abort**. When subject is autogenesis, offer **mount autogenesis-atlas** instead of initiate.
6. Never invent a silent fallback plan directory outside the subject Atlas.

## Progressive disclosure (path modules are not skills)

Host catalog lists **root skills only**. Path modules under `references/paths/` are **not** separate catalog entries.

**Working pattern (sufficient when followed):**

1. Activate root skill **autogenesis** (catalog description match).
2. Read this root `SKILL.md` (router + Enter card).
3. Hint/select the path from the registry or user intent.
4. **`read_file` the `path_module`** before executing that path’s procedure.
5. If Exit needs memory ops: activate root skill **atlas**, then load the named path module (`references/paths/remember.md` / `query.md` / `work.md`) — do not invent remember/ingest from memory.

**Failure modes to avoid:** treating `design` / `implement` as peer root skills; running off the thin registry stub without reading the path file; loading every path module at once; skipping Atlas and hand-writing “lineage” as a substitute for remember/query/work.

## Workflow engine (load before any path work)

**Source of truth:** `references/modules/workflow-discipline.md`  

Before emitting the Enter card or executing any path, load the internal module:

```text
read_file references/modules/workflow-discipline.md
```

Follow it exactly for:
- Activation card schema and rules
- Enter | Change | Exit clusters
- Gate map G0–G8
- Discussion vs Run mode (including the hard block on discussion → implement)
- Path receipt format
- Substrate-contract reminders
- Future extraction notes

The root remains a thin router. All discipline detail lives in the module.

## Capabilities (thin registry — load path module before executing)

| path_id | Activation stub | file | default |
|---------|-----------------|------|---------|
| **design** | substrate contract → genesis, then internal module `references/modules/think-challenge.md` → pin → C1–C5 → adversarial scenario draft on behaviour change → mandatory `## Genesis Artifacts` section → approval stop | `references/paths/design.md` | **yes** |
| initialise | Inform + confirm → lock subject → mint v0.1.0 → substrate genesis → fuse layers → full Genesis Artifacts → stop for approval | `references/paths/initialise.md` | no |
| implement | Approved plan only; version; adversarial suite + happy-path construct Exit; lineage | `references/paths/implement.md` | no |
| research | Expand corpus into subject wiki | `references/paths/research.md` | no |
| reflect-challenge | Behaviour challenge (optional) | `references/paths/reflect-challenge.md` | no |
| learn-skill | Peer-link / usage memory; no peer mutation | `references/paths/learn-skill.md` | no |
| **reevaluate** | Material knowledge change or explicit request: impact related skills; advisory only; recurrence → design candidate | `references/paths/reevaluate.md` | no |
| aware-runtime | AwareHook + governance | `references/paths/aware-runtime.md` | no |
| wire | Human-approved wiring + version provenance | `references/paths/wire.md` | no |
| review-package | Deep multi-facet package conformance (genesis + 4 facet modules); stops for approval if changes recommended | `references/paths/review-package.md` | no |
| **atlas-migrate** | Autodiscover okf-wiki → atlas migrate → full claim conversion under `autogenesis/` → **thorough relationship review (quality relates_to)** → compile green → rewrite subject discipline Atlas-only | `references/paths/atlas-migrate.md` | no |
| **discuss** | Discussion mode only. Substrate-load catalog skill discuss; subject Atlas write-home; fail-closed Enter; from-design review reuses existing graph; no implement | `references/paths/discuss.md` | discussion-mode default |

When you change a path module file, update the matching stub row in the **same Run**.

## Skill chaining rule (mandatory)

When any skill body or path module must invoke another skill, the **multi-harness substrate contract** is mandatory:

1. Load the full body of the target skill using the harness’s on-demand skill-loader tool.
2. Follow the loaded body instructions exactly.
3. Re-execute any live tool calls the body requires.

See Atlas decision `autogenesis/decisions/skill-nesting-invocation-pattern.md` (skill Atlas) for the full contract and the per-harness mapping table. Legacy wiki copy is archive only.  
The deep `review-package` path (and its facet module `validate-skill-import-links`) audits any target package for consistent application of this rule.  
Never rely on short descriptions or prior memory for nested skill execution.

The living verification of this contract is the pair **skill-test-a → skill-test-b**. Any harness can re-run that test to confirm its activation protocol is correct.

## Challenge types

- **Design challenge (Change/design):** attacks the *plan*; pins; C1–C5.
- **Adversarial construct (behaviour-changing work):** every grounded / named-theory counter becomes a subject-skill scenario (`*-adversarial-vN.yaml`) that is red if shipped behaviour does the warned thing. Design emits a full draft; implement fills and runs it at Exit. See Atlas decision `autogenesis/decisions/challenge-adversarial-construct.md`.
- **Behaviour challenge (reflect-challenge):** attacks behaviours; optional; not plan approval.

## Internal think modules (progressive disclosure)

While an Autogenesis **Run** is active, the three think verbs resolve to internal modules (not the root catalog skills):

| Trigger | Module |
|---------|--------|
| challenge / think-challenge / steel-man / counter-arguments | `references/modules/think-challenge.md` |
| grill / think-grill / probe / clarify | `references/modules/think-grill.md` |
| ramble / think-ramble / brain dump / capture thoughts | `references/modules/think-ramble.md` |

Load with `read_file` on the module path. Root-level `think-*` skills remain available for non-Autogenesis use and are never deleted or overwritten by this skill.

While `mode: discussion` / path **discuss** is active: do **not** load think-grill or think-ramble. Catalog skill discuss is the discussion mechanism. think-challenge is not user-activable; Autogenesis may use it only as a validation gate on Run paths such as design.

## Templates

- `references/aware-hook-template.md`
- `references/behaviour-challenge-template.md`
- `references/run-record-template.md`
- `references/activation-plan-template.md`
- `references/challenge-success-criteria.md`

## Non-goals

- Supersede or overwrite genesis capabilities (Autogenesis fuses and extends them; genesis remains the foundation)
- Auto-wire or auto-implement from reflection/runtime experiences
- Primary writes into a non-subject wiki
- Hand-craft Atlas stores (must follow Atlas SCHEMA/bootstrap patterns and leave compile green)
- Apply harness-specific hard bounds (must remain harness-agnostic)
- RSPL/SEPL (not implemented here)
