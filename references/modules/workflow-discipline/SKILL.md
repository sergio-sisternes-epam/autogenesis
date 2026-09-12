---
name: workflow-discipline
description: Initialise or validate Autogenesis invocation discipline, gate ownership, and durable evidence for parent-routed modules.
metadata:
  autogenesis-parent: autogenesis
  autogenesis-role: support
  autogenesis-revision: "2026-09-11"
---

# workflow-discipline

This support module is the sole process authority for Autogenesis invocation
discipline. It is progressive disclosure only: never a catalogue skill and
never an execution engine.

These rules govern Autogenesis's own requests and authoring work. S8 adopters
do not have to copy this module, its schemas or the repository's checkers.
Derived skills use their own purpose-led runtime; importing the full
Autogenesis discipline requires an explicitly approved fusion scope.

Interpret this entrypoint with its module-local companions:

- `references/invocation-contract.md` — prose request/card/receipt/trace rules
- `references/invocation-contract.json` — frozen machine inventory for the
  listed fields, enums, card modes, module roles, and retry ceiling

Bootstrap reads of `<skill_root>/SKILL.md` and
`<skill_root>/references/modules/workflow-discipline/SKILL.md` are not
invocations. Once a root, operation, or support procedure is requested, the
agent must form the canonical request, render the configured card, and later
emit the matching receipt.

## Arguments

- Required when this support is itself requested: `request` (canonical
  root/operation/support request) and `phase`
  (`bootstrap|enter|change|exit|trace`).
- Optional: `evidence`, `receipt`, `trace`, `notes`.
- Parent-owned context (`subject`, `mode`, `operation`, `work_id`, `atlas_id`,
  `atlas_root`, `approval_ref`) is never a child-supplied override.
- Subject establishment is an explicit parent transition (for example root
  selection, initialise confirmation, or a fresh Autogenesis design request
  after catalog Discuss), never a child argument override. Catalog Discuss
  cannot reuse or hand off Autogenesis protected context.
- For formal design or reevaluation, the root assigns `work_id` before dispatch
  and the operation validates and records that inherited value.
- Task-specific inputs belong in `arguments`, not in protected context.

## Authority and packaging

- One root package, one parent router, 20 ordinary modules. No separate module
  packages, aliases, forwarding stubs, or invocation engine.
- Normal references resolve from this module root. Shared package resources
  resolve from `<skill_root>`. Siblings resolve through the active parent
  registry. Never use cwd as the base.
- External Atlas, Discuss, OKF, and Genesis keep their own paths and cards
  unchanged. Autogenesis records only its own requests, cards, and receipts
  honestly around those loads.
- Checker-facing argument inventory lives in
  `references/invocation-contract.json` and covers all 20 modules. Keep it aligned
  with each entrypoint's Arguments section; never infer extra allowed keys.

## Enter (blocking)

Every requested procedure starts with a canonical request plus the configured
visible card defined in `references/invocation-contract.md`. A file read never
proves execution.

1. **Load before follow.**
   - Root bootstrap: load `<skill_root>/SKILL.md` and this module.
   - Internal module request: read
     `<skill_root>/references/modules/<module>/SKILL.md`.
   - External skill request: use the harness skill loader, load the external
     skill body, and follow it exactly.
2. **One active operation at a time.** Support requests run under an active
   parent request and return to that caller. No silent operation-to-operation
   jumps and no child replaces the active operation.
3. **Durable discussion is external.** Catalog **discuss** owns durable
   discussion. Autogenesis has no `discuss` operation and no discussion-mode
   routing.
   - Discussion has zero implement authority and no product-file writes.
   - The only legal progression to changes is `discussion -> design -> explicit
     approval -> implement`.
   - Discussion may invoke agent-spec `specify` only for exploration or review
     of candidate behaviours. It may not materialise a finished
     `## Behavioural contract (agent-spec)` section or claim that the contract
     is complete.
   - Do not invoke internal `think-grill` or `think-ramble` while catalog
     Discuss is active. Those wrappers nest-load catalog think skills; the
     Discuss fence applies before that nested load.
4. **Default routing.** Root default remains `design` for Run. Durable
   discussion is activated by loading the catalog **discuss** package
   directly; it is not an Autogenesis operation. The requested operation is
   still explicit in the canonical request once selected.
5. **Card modes do not disable gates.**
   - `activation_card` absent or `off`: card rendering is disabled.
   - `on`: full root and operation cards, plus compact support cards, are
     required.
   - `debug`: same as `on`, plus redacted inherited support context must be
     shown.
   - Disabled cards do not disable approval, Atlas, lineage, or other safety
     gates.
6. **Behavioural hint on design.** When behaviour changes or is newly defined,
   the design request arguments and visible arguments summary carry
   `behavioural_contract: specify | deferred:<reason>`, not an extra envelope field.

## Change (blocking)

### Design and implement sequence

- `design` preserves the existing body: discussion-informed problem framing,
  Genesis depth by change-class, grounded challenge, pinned decisions, explicit
  approval stop, and no implementation.
- `implement` is legal only after a **persisted** formal design plan receives
  **explicit** approval. A visible request card or `approval_ref` alone is not
  enough.
- No automatic wiring or peer mutation is introduced anywhere in this protocol.

### Change-class

Before drafting a plan, classify the work and state it in the plan:

| Class | Meaning | Required design depth before implement |
|---|---|---|
| `hardening` | Edge fix, copy/docs, version bump, dead link, small contract tweak | Abbreviated `## Genesis Artifacts`: intent + scope + acceptance (+ pins/non-goals) |
| `new-surface` | New CLI/report/schema/smoke/storage/protocol surface | Mini-genesis: intent+scope+non-goals, one mermaid, interface sketch, cost note, acceptance, explicit stop-for-approval |
| `new-skill` | New package / skill init | Full Genesis artifacts |

Ambiguous work defaults to `new-surface`. Missing or wrong depth is a G3
failure.

### Behavioural contract and evaluation

When behaviour is in scope:

- agent-spec `specify` is the sole legal producer of behavioural Gherkin.
- Autogenesis must never author or edit `.feature` files directly.
- The plan must contain `## Behavioural contract (agent-spec)` with either
  produced contract IDs or an explicit one-line deferral reason.
- The plan must contain `## Evaluation plan` with deterministic-first checks;
  agent narrative is secondary only.
- Design approval does not waive these requirements.

### Hard boundaries during Change

| Rule | Requirement |
|---|---|
| Subject | Every Run declares a subject in protected context. |
| Atlas write-home | Resolve the subject repository's declared `atlas_id` through Atlas path `mount` and `atlas resolve`; write plans/memory only to that resolved root. |
| Plan home | Design plans persist only at `autogenesis/plans/<work_id>.md` inside the resolved subject Atlas. |
| Approval | Implement is forbidden until a persisted formal design plan is explicitly approved. |
| Discussion to implement | Forbidden; re-enter design first. |
| Wiring | Human approval + version provenance only. No auto-wiring. |
| Source of truth | This module plus `references/invocation-contract.md` and `references/invocation-contract.json` own the live request/card/receipt discipline. |
| Legacy owned fields | Reject structured Autogenesis requests that use removed owned fields such as `path_id`, `path`, or `path_module`; explain the new contract instead of silently mapping them. |
| Session vs Atlas | The Atlas persists across sessions; “empty session” never authorises store wipes or fresh-store assumptions. |

### work_id lineage

Every formal design plan, including hardening, has a stable `work_id`.

```text
YYYY-MM-DD-<kebab-slug>
YYYY-MM-DD-<external_id>-<kebab-slug>
```

- Date is the plan-creation date.
- Do not rename historical work IDs.
- Canonical subject-owned artefacts:
  - plan page: `autogenesis/plans/<work_id>.md`
  - work node: `autogenesis/work/<work_id>.md`
  - implement experience frontmatter: `work_id`, `implements`, `closes`,
    `plan_path`
- Status values remain `proposed | designed | approved | implementing | done |
  deferred | waived`.

### Subject Atlas resolution

The active subject git root is the write-home boundary.

1. Require the active subject git repository.
2. Resolve `atlas_id` from explicit context or exactly one mesh store;
   zero/many without an explicit ID is ambiguous.
3. Apply the substrate contract to the external `atlas` skill, load its
   `mount` path module, and mount if missing with no `--target`.
   Do not remount an already registered dirty checkout containing this Run's
   writes; resolve that existing mount instead.
4. Run `atlas resolve <atlas_id>`, set `atlas_root` only to that result, and
   verify `<atlas_root>/SCHEMA.json`.
5. Persist only there and pass the exact resolved root to every Atlas CLI call.
6. Missing, legacy, ambiguous, or failed Atlas states block normal work; use
   Atlas init/migrate rather than guessing, symlinking, or dual-writing.

### Entrypoint-load honesty

If a Run claims `reevaluate`, `challenged_plan`, design challenge, or other
module-specific behaviour:

1. Read the actual requested module entrypoint before making the claim.
2. Record loaded entrypoints in the receipt and, when present, in the trace.
3. Claiming module-specific behaviour without that load is incomplete.

### Scenario and evaluation boundary

- Current suites are selected through
  `<skill_root>/references/scenarios/suite-index.json`.
- Behavior-changing implement work runs applicable happy-path and adversarial
  checks using tools available in the subject repository. Scenario files are
  specifications, not evidence that their commands ran.
- Approved adversarial smokes may be added, not silently dropped. A red
  in-scope result keeps the Run incomplete. Only a named out-of-scope counter
  can be waived with an explicit reason; changes to approved behavior or the
  smoke set require a new design.
- Autogenesis does not require a separate evaluator package or service.
  Record actual command/output evidence or a precise deferral in lineage.

## Exit (blocking)

Lineage is an obligation, not a chat claim.

1. Re-resolve the subject Atlas through the rules above.
2. Apply the substrate contract to the external skill named `atlas` and, when
   format questions arise, to the skill named `okf`.
3. Load the appropriate Atlas path module (`remember`, `query`, or `work`) and
   follow it exactly.
4. If product files were created or edited, the durable experience must contain
   `## Changed files` listing every touched relative path.
5. A completion claim needs either:
   - a real Atlas write plus green `atlas compile --root <atlas_root>`, or
   - an explicit one-line deferral in the durable experience.
6. No parallel store, no hand-crafted SCHEMA replacement, and no okf-wiki
   fallback for new process memory.
7. Parked future work becomes a protostar beside the origin page, never a
   residual bucket and never implement authority.
8. Emit the canonical invocation receipt from `references/invocation-contract.md`.
   Missing receipt or fabricated evidence means the request is not complete.

## Gate map G0-G8

| Gate | Cluster | Requirement |
|---|---|---|
| G0 | Enter | mode is explicit Run; subject required; catalog Discuss is external and has no implement authority |
| G1 | Enter | actual requested entrypoint read; one active operation; no silent invokes |
| G2 | Change/Exit | Atlas writes go to the resolved subject Atlas root |
| G3 | Change | design has change-class, required Genesis depth, challenge, pins, and `## Genesis Artifacts` |
| G4 | Change | explicit approval before implement |
| G5 | Change | implement matches approved plan, preserves version identity, and does not auto-wire |
| G6 | Exit | subject lineage and memory are handled through Atlas procedures |
| G7 | Change | design explicitly stops for approval |
| G8 | Exit | remember + green compile, or an explicit durable deferral |

## Support return discipline

Support requests do not replace the active operation. They validate, challenge,
or inform it and return their result plus receipt to the caller. The immediate
caller owns any eligible retry and the bounded attempt budget.

## Skill chaining reminder

When a root body or module must invoke another external skill, the
multi-harness substrate contract is mandatory:

1. Resolve the external skill by name from the active harness catalogue.
2. Load its full body with the harness skill loader.
3. Follow that loaded body exactly and re-run any live tool calls it requires.

Never execute an external skill from a short description, stale memory, or a
request card alone.

## Internal think modules

During an Autogenesis Run, the think verbs resolve through the parent registry
to internal support modules:

| Trigger family | Entrypoint |
|---|---|
| `think-challenge`, counter-arguments, steel-man | `think-challenge/SKILL.md` |
| `think-grill`, probe, clarify | `think-grill/SKILL.md` |
| `think-ramble`, capture thoughts, brain dump | `think-ramble/SKILL.md` |

These are parent-routed support calls, not peer root-skill activation. While
catalog Discuss is active, do not invoke `think-grill` or `think-ramble`;
external Discuss remains the discussion mechanism.

## Non-goals

- A new dispatcher, scheduler, server, hook, or permissions engine
- Separate module packages or independent module discovery
- Compatibility aliases or forwarding wrappers for removed owned request fields
- Converting external Atlas, Discuss, OKF, or Genesis paths/cards to
  Autogenesis's schema
- Auto-approval, auto-wiring, or discussion-to-implement shortcuts
- Treating a card, file read, or self-authored narrative as execution evidence
