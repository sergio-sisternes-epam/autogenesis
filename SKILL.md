---
name: autogenesis
description: Use this skill to evolve, design, review, or initialise agent skills from durable experience, including module structure, invocation discipline and skill composition even when Autogenesis is not named. Route through parent-controlled operation modules. Use getting-started or help when the user asks how Autogenesis itself works or how a named Autogenesis module works; help with no target lists public operations. Discussion does not implement; design stops for explicit approval. Do not use for ordinary application refactoring, automatic wiring, bypassing parent-routed help to load private support modules, or unrelated help requests.
version: 0.8.0
activation_card: on
---

# autogenesis

**v0.8.0** (semver). Version history lives in `CHANGELOG.md`.

Grows a skillset from durable experience, or designs a new package using full
Genesis discipline. Derived skills receive the runtime capabilities their
purpose needs, not an Autogenesis framework by default.

**Core design process is genesis (fused, never superseded).**  
**Traversal is parent-routed, skill-shaped modules** (load before invoke).
**Discipline is three clusters: Enter → Change → Exit** (G0–G8 map into these).

```text
genesis     = design quality (packet, challenge, pin, criteria, persist)
invocation  = parent-owned context + module arguments + resolved entrypoint
activation card = visible request interface, not execution evidence
Enter|Change|Exit = only public blocking checkpoints
fusion      = genesis capabilities are the foundation; Autogenesis extends them
change-class = hardening | new-surface | new-skill (see workflow-discipline)
```

**Design depth:** load `references/modules/workflow-discipline/SKILL.md` —
classify before packet; `new-surface` requires mini-genesis; behavior changes
require portable scenarios and actual evaluation evidence.

## Authoring versus derived skills

Genesis, approval gates and Atlas lineage govern Autogenesis's design work.
They do not automatically become runtime dependencies of a skill it creates.
Use the S8 pattern only when distinct procedures justify private modules.
Derived modules describe inputs, procedure, boundaries and outcomes in
instructions; no custom validator, JSON protocol or trace infrastructure is
required. Task-serving scripts and explicitly approved full fusion remain
available. This repository's release tooling is a separate concern.

## SOLID principles for skills

After Genesis, every formal Autogenesis design considers the skill-native
SOLID lens in [`references/skill-design-principles.md`](references/skill-design-principles.md).
The lens is grounded in information hiding, cohesion and change locality.
New-surface and new-skill plans record all five principles; hardening records
the material principles. Consideration is mandatory, but modules, abstractions
and structural compliance are not.

## Evaluation boundary

Autogenesis owns portable scenario specifications, runs applicable checks
through tools available in the subject repository, and records actual evidence
or an explicit deferral. It does not require a separate evaluator package or
service. GitHub CI remains this repository's final release gate.


## Experience source

Process memory is **not** authored in the skill package. Each Run writes home
to the subject repository's declared Atlas. The Autogenesis subject store is
`github.com/sergio-sisternes-epam/autogenesis-atlas`; its git root is the OKF
root (`SCHEMA.json`).

```text
python3 <atlas-skill>/scripts/atlas.py mount github.com/sergio-sisternes-epam/autogenesis-atlas --ref main
python3 <atlas-skill>/scripts/atlas.py resolve github.com/sergio-sisternes-epam/autogenesis-atlas
```

**Canonical mount (this repository):**
`.atlas/github.com/sergio-sisternes-epam/autogenesis-atlas` (git submodule).
Do not mount or write at `<skill>/references/atlas`.

Always pass the path returned by `atlas resolve` as card `atlas_root` /
`root` and CLI `--root`.

- **Primary change memory:** **subject** skill Atlas via **Atlas** paths (`query` / `remember` / `work`). Autogenesis-authored pages live under **`autogenesis/`** inside that root.
  - Resolve the subject's store from the active subject repository.
  - **subject is autogenesis:** use the Autogenesis store declared in this repository's `atlas-mesh.json`.
  - **other subjects:** use that subject repository's declared store; do not write a second pointer into the Autogenesis store.
- **Plans (Autogenesis space):** `autogenesis/plans/<work_id>.md` with `type: plan` (SCHEMA `autogenesis_space`). Not experiences. Not `artifacts/autogenesis-plans/` as primary.  
  **work_id format (new work):** `YYYY-MM-DD-<kebab-slug>`; with external id: `YYYY-MM-DD-<external_id>-<kebab-slug>`. No renames of historical work_ids.
- **Atlas is the only ingestion authority** for process memory and design plans of this skill (no parallel ingest pipeline; okf-wiki is legacy read-only archive).

### Subject Atlas resolution (blocking before plan persist)

1. Require the active subject repository's git root. No git root means no persist.
2. Select `atlas_id` from an explicit card value or from exactly one
   `atlas-mesh.json` store. Zero or multiple candidates without an explicit id
   is a blocking ambiguity; never select the first row.
3. Load Atlas path `mount`, mount `atlas_id` with its `ref` and **no
   `--target`**, then run `atlas resolve <atlas_id>`.
4. Set `subject_atlas` only from the resolved path and verify
   `<subject_atlas>/SCHEMA.json`.
5. A legacy `<subject>/references/atlas` gitlink requires Atlas path `migrate`
   before the Run continues. A legacy okf-wiki may then be ingested through
   Autogenesis operation `atlas-migrate`.
6. Missing, ambiguous, or invalid storage fails closed with an actionable
   initiate/migrate/abort choice. Never use a path guess, compatibility
   symlink, dual-write, or plan directory outside the resolved subject Atlas.

## Progressive disclosure (modules are parent-routed)

Host catalog lists **root skills only**. Nested module `SKILL.md` files are
instruction assets in this package, not independent catalogue entries.

**Working pattern (sufficient when followed):**

1. Activate root skill **autogenesis** (catalog description match).
2. Read this root and the workflow-discipline definitions for bootstrap.
3. Form a root invocation request; select an operation from the registry.
4. Resolve the module from this loaded skill root and **read its entrypoint**
   before following its procedure. Emit the configured request card first.
5. If Exit needs memory ops: activate root skill **atlas**, then load the named path module (`references/paths/remember.md` / `query.md` / `work.md`) — do not invent remember/ingest from memory.

**Failure modes to avoid:** treating `design` / `implement` as peer root skills;
running from a registry stub without reading its module; eager loading; treating
a file read or card as execution; skipping Atlas's actual memory procedures.

## Invocation discipline (load before operation work)

**Source of truth:** `references/modules/workflow-discipline/SKILL.md`.
Its module-local `references/invocation-contract.md` and
`references/invocation-contract.json` define the request, card and receipt
interfaces. This is an agent-followed protocol, not a new execution engine.

Before emitting the root request card or executing an operation, load the internal module:

```text
read_file <skill_root>/references/modules/workflow-discipline/SKILL.md
```

Follow it exactly for:
- Activation card schema and rules
- Enter | Change | Exit clusters
- Gate map G0–G8
- Direct catalog Discuss activation and the formal-design requirement before implementation
- Invocation receipt format and bounded safe retries
- Substrate-contract reminders
- Future extraction notes

The root remains a thin router. All discipline detail lives in the module.

## Module registry

Root arguments: required `objective`; no optional argument keys. The root
establishes protected context and selects an operation from user intent;
the caller cannot smuggle approval or storage overrides into arguments. Before
dispatching formal design, root assigns its stable `work_id`; the design module
inherits and validates it rather than creating protected context.

Entrypoints are relative to the loaded skill root, never the shell cwd.
Default operation is `design` in Run mode. Route first-use questions to
`getting-started` and Autogenesis how-to questions to `help`. Unqualified
help about unrelated work must not select those operations. Durable
discussion is not an Autogenesis operation; activate the catalog **discuss**
package directly.
Supporting invocations retain the active operation and return to their caller.
The parent owns subject, mode, operation, work identity, storage, approval and
resolved locations. Module arguments cannot override them. Missing, duplicate
or escaping entrypoints reject explicitly; there is no catalogue fallback.

| Module | Role | Description | Entrypoint |
|--------|------|-------------|------------|
| design | operation | Genesis, instruction-first runtime selection, challenge and persisted plan; stop for approval | `references/modules/design/SKILL.md` |
| initialise | operation | Confirm purpose and fusion scope; design only needed runtime capabilities; stop for approval | `references/modules/initialise/SKILL.md` |
| implement | operation | Apply only an explicitly approved persisted plan; evaluate and record lineage | `references/modules/implement/SKILL.md` |
| research | operation | Expand the resolved subject Atlas with sourced knowledge | `references/modules/research/SKILL.md` |
| reflect-challenge | operation | Challenge observed behaviour without implementation authority | `references/modules/reflect-challenge/SKILL.md` |
| learn-skill | operation | Record subject-owned peer usage without peer mutation | `references/modules/learn-skill/SKILL.md` |
| reevaluate | operation | Assess material knowledge impact; advisory only | `references/modules/reevaluate/SKILL.md` |
| aware-runtime | operation | Maintain governed runtime awareness | `references/modules/aware-runtime/SKILL.md` |
| wire | operation | Explicitly approved wiring with version provenance | `references/modules/wire/SKILL.md` |
| review-package | operation | Review the target's chosen composition and applicable conformance facets; advisory report | `references/modules/review-package/SKILL.md` |
| atlas-migrate | operation | Migrate legacy storage through Atlas and preserve knowledge | `references/modules/atlas-migrate/SKILL.md` |
| help | operation | Explain Autogenesis modules without executing them | `references/modules/help/SKILL.md` |
| getting-started | operation | First-use purpose, prerequisites, and shortest useful journey | `references/modules/getting-started/SKILL.md` |
| workflow-discipline | support | Apply Autogenesis-local Enter, Change, Exit and invocation contracts | `references/modules/workflow-discipline/SKILL.md` |
| think-challenge | support | Nest-load catalog think-challenge; Run design-gate overlays | `references/modules/think-challenge/SKILL.md` |
| think-grill | support | Nest-load catalog think-grill; Run overlays, not discussion | `references/modules/think-grill/SKILL.md` |
| think-ramble | support | Nest-load catalog think-ramble; capture to the subject Atlas | `references/modules/think-ramble/SKILL.md` |
| patterns | support | Select B17 or instruction-first draft S8; load its optional module template when authoring | `references/modules/patterns/SKILL.md` |
| validate-skill-import-links | support | Audit actual external skill calls without requiring an adopter's Atlas | `references/modules/validate-skill-import-links/SKILL.md` |
| validate-progressive-disclosure | support | Audit the chosen layout; allow simple root-only and instruction-only module skills | `references/modules/validate-progressive-disclosure/SKILL.md` |
| validate-okf-conformance | support | Audit declared OKF/Atlas integration; report n/a when not adopted | `references/modules/validate-okf-conformance/SKILL.md` |
| validate-gate-map-and-non-goals | support | Audit declared gates and cards without imposing Autogenesis's protocol | `references/modules/validate-gate-map-and-non-goals/SKILL.md` |

Update the matching registry row in the same change as its module.

## Skill chaining rule (mandatory)

When any skill body or module must invoke another external skill, the **multi-harness substrate contract** is mandatory:

1. Load the full body of the target skill using the harness’s on-demand skill-loader tool.
2. Follow the loaded body instructions exactly.
3. Re-execute any live tool calls the body requires.

See Atlas decision `autogenesis/decisions/skill-nesting-invocation-pattern.md` (skill Atlas) for the full contract and the per-harness mapping table. Legacy wiki copy is archive only.  
The `review-package` operation (and its facet module `validate-skill-import-links`) audits any target package for consistent application of this rule.
Never rely on short descriptions or prior memory for nested skill execution.

The living verification of this contract is the pair **skill-test-a → skill-test-b**. Any harness can re-run that test to confirm its activation protocol is correct.

## Challenge types

- **Design challenge (Change/design):** attacks the *plan*; pins; C1–C5.
- **Adversarial scenario (behaviour-changing work):** every grounded /
  named-theory counter becomes a subject-skill scenario
  (`*-adversarial-vN.yaml`) that is red if shipped behaviour does the warned
  thing. Design emits a full draft; implement fills and runs applicable checks
  at Exit. Historical decision names remain provenance, not live dependencies.
- **Behaviour challenge (reflect-challenge):** attacks behaviours; optional; not plan approval.

## Internal think modules (progressive disclosure)

While an Autogenesis **Run** is active, the three think verbs resolve to
parent-routed wrappers (not a direct user activation of catalog `think-*`):

| Trigger | Module |
|---------|--------|
| challenge / think-challenge / steel-man / counter-arguments | `references/modules/think-challenge/SKILL.md` |
| grill / think-grill / probe / clarify | `references/modules/think-grill/SKILL.md` |
| ramble / think-ramble / brain dump / capture thoughts | `references/modules/think-ramble/SKILL.md` |

Load with `read_file` on the Autogenesis module path. Each wrapper then
nest-loads catalog `think@atlas` as the matching **external catalog** skill from
the pinned package
through the harness skill loader. That nested load must not re-enter the
Autogenesis module or the parent registry. Root-level `think-*` skills remain
available for non-Autogenesis use and are never deleted or overwritten by this
skill.

## Discuss package boundary

Autogenesis declares `discuss@atlas` as an immutable direct APM dependency,
but does not expose a `discuss` operation or proxy its runtime protocol. Activate the
catalog **discuss** package directly for durable discussion. Discuss has no
implementation authority: a discussion conclusion that changes a package must start a formal Autogenesis `mode: run` design operation, followed by a persisted, challenged plan and explicit approval before implementation.

While an Autogenesis Run is active, think-challenge is an internal validation
gate only; it is not user-activable as a discussion verb. The wrapper
nest-loads catalog `think-challenge` and may add named-theory adversarial
smokes. Do not invoke think-grill or think-ramble while catalog Discuss is
active. During a Run, think memory uses the subject Atlas; conversation-only
catalog fallback is not legal.

## Current evaluations

Select current suites through `references/scenarios/suite-index.json`.
Historical suites retain their original bodies and are not current acceptance.
Invocation requests never prove execution; completed receipts need actual
outcome/tool evidence. External skills retain their own schemas and paths.

## Templates

- `references/aware-hook-template.md`
- `references/behaviour-challenge-template.md`
- `references/run-record-template.md`
- `references/activation-plan-template.md`
- `references/challenge-success-criteria.md`

## Non-goals

- Supersede or overwrite genesis capabilities (Autogenesis fuses and extends them; genesis remains the foundation)
- Auto-wire or auto-implement from reflection/runtime experiences
- Primary writes outside the resolved subject Atlas
- Hand-craft Atlas stores (must follow Atlas SCHEMA/bootstrap patterns and leave compile green)
- Apply harness-specific hard bounds (must remain harness-agnostic)
- RSPL/SEPL (not implemented here)
