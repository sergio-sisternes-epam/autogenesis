# Invocation contract

This file is the module-local protocol companion for
`<skill_root>/references/modules/workflow-discipline/SKILL.md`.

Scope: Autogenesis's own invocation protocol. It is not a portable S8
requirement, a derived-skill template or an instruction to generate validators.
Other skills can express their module inputs and outcomes in ordinary prose.

- Prose authority: this file plus the module root `SKILL.md` interpret the
  contract, gates, ownership rules, and rendering semantics.
- JSON authority: `<skill_root>/references/modules/workflow-discipline/references/invocation-contract.json`
  is authoritative only for the listed fields, enums, module inventory, card
  modes, and retry ceiling.

## Request object

Use the canonical request shape for every requested root, operation, or support
procedure:

```yaml
schema: autogenesis.invocation-request/v1
request_id: "<unique request identifier>"
parent_request_id: "<caller request identifier or null for root>"
target:
  skill: autogenesis
  module: design
  role: operation
arguments:
  objective: "<task-specific input>"
context:
  subject: "<parent-owned subject>"
  mode: run
  operation: design
  work_id: "<parent-assigned work id or null before assignment>"
  atlas_id: "<declared subject store or null before resolution>"
  atlas_root: "<resolved subject store or null before resolution>"
  approval_ref: null
resolved:
  skill_root: "<actual loaded package root>"
  module_root: "<actual module directory or null for root>"
  entrypoint: "<actual SKILL.md location>"
```

Rules:

- Root request: `target.module: null`, `target.role: root`,
  `parent_request_id: null`.
- Support requests keep the caller's `context.operation`; they do not replace
  the active operation.
- The parent owns protected context and resolved locations. Child arguments
  cannot override subject, mode, operation, work id, Atlas identity/root, or
  approval.
- An implement request may establish `approval_ref` only from its parent design
  receipt. That receipt must be completed with `result.disposition: approved`
  and the same non-empty `result.approval_ref`; a child-supplied token is not
  approval evidence.
- Establishing or changing the protected `subject` is an explicit parent
  transition, not a child override. That includes initialise confirmation and a
  discussion-to-design return.
- Unknown envelope fields, unknown module arguments, or alias fields such as
  `path_id`, `path`, and `path_module` are rejected with an actionable
  diagnostic.
- Required keys with unresolved nullable values describe preflight only.
  Validate each module's prerequisites before procedure effects. An unresolved
  store or approval blocks work that needs it; it is never a success fallback.
- The root and discipline files may be read for bootstrap before a request is
  formed. That bootstrap load is not itself an invocation.
- Internal modules resolve from the active parent and direct entrypoint reads.
  External skills resolve through the harness skill loader and the external
  body's own contract.
- Ordinary filesystem paths and external skill path fields remain ordinary data;
  only the owned Autogenesis request surface changed.

## Checker-facing module argument inventory

`references/invocation-contract.json` may expose `module_arguments` so the
source/trace checker can validate exact operation argument names without
inventing execution logic.

The JSON inventory covers all 21 migrated modules. Each entrypoint declares
the matching required/optional keys. The core operation and discipline inputs
are summarised here:

| Module | Required arguments | Optional arguments |
|---|---|---|
| `design` | `objective` | `change_evidence`, `behavioural_contract` |
| `initialise` | `objective` | `proposed_name`, `activation_card`, `behavioural_contract` |
| `implement` | `plan_ref` | none |
| `discuss` | `objective`, `discussion_root`, `current_branch` | `stage`, `artifact` |
| `atlas-migrate` | `storage_evidence` | `wiki_source` |
| `workflow-discipline` | `request`, `phase` | `evidence`, `receipt`, `trace`, `notes` |

Reject keys absent from that module's declared inventory. There are no implicit
argument aliases. In particular, research does not accept a subject override
and OKF validation does not accept an atlas_id override. A scope or store hint
is advisory input, never authority to change protected context.

## Cards are a view, not execution evidence

Cards are renderings of a request, not a second protocol and not execution
proof. Render visible cards in fenced Markdown code blocks with the `text`
info string. Redact secrets in summaries, errors, traces and receipts as well
as cards; an input argument is not permission to persist its credential value.

### Full root and operation cards

When `activation_card` is `on` or `debug`, root and operation requests render a
full card showing the request cue:

- `schema`
- `request_id`
- `parent_request_id`
- `target`
- `operation`
- arguments or an arguments summary
- protected context or a context summary
- resolved entrypoint
- `atlas_id`
- `atlas_root`
- `approval_ref`
- `state: requested`

Null or unresolved values must be shown honestly.

### Compact support cards

When `activation_card` is `on` or `debug`, support requests render a compact
card with:

- `request_id`
- caller or `parent_request_id`
- support module and role
- active operation
- resolved entrypoint
- `context_ref` to the inherited parent context
- short intent or arguments summary
- `state: requested`

Compact cards do not hide a context change or replace required new input.

### Card modes

- `off` or absent: card rendering is disabled.
- `on`: full root/operation cards and compact support cards are required.
- `debug`: same as `on`, plus the support card must show redacted inherited
  context for debugging.

Disabled cards do not disable approval, Atlas, retry, lineage, or other safety
gates. Never show secrets or credentials in cards; use a redaction marker.

Render-only additions are allowed in `cards[].fields` when they do not
contradict the canonical request. The frozen JSON inventory documents the
permitted render-only names.

## Lifecycle, attempts, and safe retry

Canonical states:

| State | Meaning |
|---|---|
| `requested` | Request issued; no success claim |
| `rejected` | Invalid target, arguments, or context; no execution |
| `blocked` | Missing approval, prerequisite, or required evidence |
| `running` | Validated procedure is being followed |
| `failed` | An executed attempt did not complete successfully |
| `completed` | Required outcome and evidence were produced |

Design may complete with `result.disposition: awaiting-approval`; that is not
implement authority.

Retry discipline:

- The immediate caller is the single retry owner.
- `max_attempts = 2`.
- Attempt 2 is legal only after an actually observed transient failure **and**
  known repeat-safe repetition.
- Read-only or proven idempotent work may qualify.
- Unknown partial effects, permission denials, invalid input, missing approval,
  request renaming, parent replay, or any reset of request ownership do not.
- Retries keep the same `request_id`.
- If interruption leaves unknown partial state, reconcile or block; do not
  auto-replay.

Every receipt or trace should record attempt number, outcome, transient
classification, repeat-safety evidence, retry owner, and any known underlying
tool retries.

Attempt number and outcome are required for every actual attempt. Authorising
a second attempt requires the failed attempt's transient classification,
repeat_safe=true, retry_owner, a concrete reason, and repeat_safety_evidence;
optimistic booleans alone are insufficient. Record evidence references, not
secrets. Respect an applicable tool/service retry-after instruction without
inventing a polling or backoff engine. The two-attempt ceiling bounds module
invocations, not every underlying SDK/network retry. Do not add a competing
recovery layer around a tool which already owns recovery.

A required child failure or blocker stops dependent parent work; do not emit
completed gates for an operation whose necessary supporting result is missing.
Root and operation requests are not automatically idempotent.

## Receipt object

```yaml
schema: autogenesis.invocation-receipt/v1
request_id: "<same request identifier>"
parent_request_id: "<same caller identifier or null>"
target: {skill: autogenesis, module: design, role: operation}
operation: design
status: completed
attempts:
  - number: 1
    outcome: completed
result:
  artifact: "<Atlas-relative plan path>"
  disposition: awaiting-approval
evidence:
  loaded_entrypoints: ["<files actually read>"]
  tool_results: ["<actual tool-result references>"]
  atlas_root: "<resolved root>"
  remember: true
  compile: true
gates: {Enter: pass, Change: pass, Exit: pass}
```

Failed, blocked, or rejected receipts carry real attempt history and the actual
reason. They do not claim completed gates or fabricated evidence.

## Trace envelope

Synthetic traces prove only checker/schema conformance; they do not prove live
runtime execution.

```yaml
schema: autogenesis.invocation-trace/v1
requests:
  - "<canonical autogenesis.invocation-request/v1 object>"
receipts:
  - "<canonical autogenesis.invocation-receipt/v1 object>"
cards:
  - request_id: "<request identifier>"
    format: full
    fields:
      schema: autogenesis.invocation-request/v1
      request_id: "<request identifier>"
      state: requested
    mode: on
```

Rules:

- `requests[]` contains canonical request objects.
- `receipts[]` contains canonical receipt objects.
- `cards[]` contains rendering projections only.
- `meta.activation_card` records the skill's off/on/debug setting; absent
  means disabled cards, not disabled safety checks. An optional per-card mode
  must agree with it, rather than enabling an individual hidden request.
- Each card entry requires `request_id`, `format`, and `fields`; `mode` is
  optional trace metadata.
- `format` is `full` or `compact`.
- `fields` contains the renderable required values for that card format, plus
  any documented render-only additions.

## External invocation boundary

- External Atlas, Discuss, OKF, and Genesis keep their current cards, paths,
  and procedures unchanged.
- Autogenesis may record correlation evidence around those loads, but must not
  falsely claim that an external skill adopted this schema.
- The external skill body is authoritative for its own execution steps.
- Root/bootstrap file loads are not invocations. Requested module procedures are.

## Legacy owned-field cutover

The owned Autogenesis structured surface no longer uses `path_id`, `path`, or
`path_module`. Use request, card, receipt, module, operation, and entrypoint.

- Natural-language user intent may still mention old wording; that is not a
  supported structured request.
- Ordinary file-system paths, Atlas path modules, and external skill path terms
  are unchanged.
