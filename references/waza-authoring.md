# Waza suite authoring guide

Shared Autogenesis resource. Load it when a design drafts behavioural
evaluation, when implement authors or updates a suite, and when initialise
plans a new skill's behavioural evaluation. Workflow-discipline owns the gate;
this guide owns the authoring rules.

Autogenesis **designs and authors** behavioural eval suites in the upstream
Waza format. It never runs suite tasks against an agent, never runs a judge
and never makes a model call for evaluation. Authored suites and the
model-free validity checks below are **not behavioural evidence**.

## Format pin

- Target: upstream Waza (`microsoft/waza`, MIT) **0.38.9**, commit
  `774df00`; eval `schemaVersion: "1.4"`.
- Waza is a **format target and model-free validator**. It is never an APM
  dependency of Autogenesis or of a derived skill, and no wrapper around it is
  used or named.
- Changing the version or schema pin is a versioned design change, never a
  silent edit.

## Suite home and layout

Suites live in the subject repository, versioned with the skill they describe,
and are never read at skill runtime:

```text
<subject>/evals/<skill>/
  eval.yaml        # skill, schemaVersion: "1.4", config, metrics, task globs
  tasks/*.yaml     # one task per file
  fixtures/        # tiny subject repos, reference and negative outcomes
  .waza.yaml       # optional; set paths.skills when skills land in a dot-folder
  README.md        # how to run, recommended pass rule, required skills,
                   # which tasks were grader-checked and which are left to the runner
```

- `.waza.yaml` must set `paths.skills` whenever the candidate skill or its
  required skills are installed under a dot-folder (for example `.agents/`),
  because dot-folders are skipped otherwise.
- The README states how the runner installs the candidate skill and every
  required skill, so any runner can run the suite without asking Autogenesis.

## Tiers and tags

| Tier | Purpose | Typical graders |
|---|---|---|
| `gate` | Protected behaviour; a prompt that tempts the warned behaviour | `file`, `diff`, `skill_invocation` |
| `quality` | Advisory quality of produced artefacts | `file` patterns plus an advisory `prompt` judge |
| `trigger` | Dispatch: should and should not activate | `trigger`, `skill_invocation` |

Every task carries `tags`: its tier; `adversarial` and
`<capability>-adversarial-vN` plus the matching smoke id when it comes from an
adversarial counter; and the `work_id` that introduced it. The task
`description` names the source counter.

When the skill description carries `USE FOR:` / `DO NOT USE FOR:` phrases,
trigger tasks map one to one to those phrases (a positive task per `USE FOR`
phrase and a near-miss task per `DO NOT USE FOR` phrase). Record the mapping
in the plan as coverage.

## Authoring rules

- Prefer **outcome graders** (`file`, `diff`, `skill_invocation`, `trigger`)
  over tool-name graders. Tool-name graders (`tool_calls`, `tool_constraint`,
  `action_sequence`) are tagged `harness: copilot`.
- Check produced content with **`file` graders** on a named file
  (`must_exist`, `must_not_exist`, `content_patterns`). Text graders read only
  the chat reply.
- `diff` graders set `update_snapshots: false` and resolve snapshots through
  `config.context_dir` (for example `context_dir: evals/fixtures`).
- A `prompt` (judge) grader embeds the original input between explicit
  `BEGIN ORIGINAL INPUT` / `END ORIGINAL INPUT` markers, so the judge can
  assess fidelity. Judge graders are **advisory**; `judge_model` is left to
  the runner, with README advice to use a different model family from the
  agent. Judge timeout belongs to the runner.
- **Suites are safe to run:** fixtures use local-only remotes (a local bare
  repository or none); no prompt asks for a push, a token or any credential.
- List every required skill in the README.
- **Goodhart guard:** any grader, threshold, prompt or fixture change bumps
  `suite_version` with a recorded reason, and is never bundled silently with
  the skill change it describes.

## Grader trust: reference and negative fixtures

Every gate task ships two hand-authored final states:

```text
fixtures/<task-id>/reference/                 # known-good final state; must pass
fixtures/<task-id>/reference.results.json
fixtures/<task-id>/negative/                  # known-bad final state; must fail
fixtures/<task-id>/negative.results.json
```

The `.results.json` files are hand-authored outcome files in Waza's results
format (final output, transcript, tool events, skill invocations). They are
not the output of a run. A fixture change bumps `suite_version` with a reason.

## Authored pass-bar metadata

Suites carry run guidance as metadata; Autogenesis writes it and never
enforces it:

- `eval.yaml`: `config.trials_per_task: 3`; `metrics` with thresholds for
  quality and trigger accuracy.
- README "Recommended pass rule": gate tasks pass in every trial; quality
  tasks are advisory with the confidence interval that Waza reports; mock
  executor runs prove plumbing only.

## Model-free validity checks (closed allowlist)

Autogenesis may run only these checks, locally, against suites it wrote.
Every call sets `WAZA_NO_UPDATE_CHECK=1`. First verify the binary:

```text
WAZA_NO_UPDATE_CHECK=1 waza --version     # must report 0.38.9
```

| # | Command | Rule |
|---|---|---|
| V1 | `WAZA_NO_UPDATE_CHECK=1 waza check <skill-path> --format json` | Frontmatter compliance, token budget, eval presence, eval schema |
| V2 | `WAZA_NO_UPDATE_CHECK=1 waza spec verify --skill <skill-path> --eval <eval.yaml> --format json` | Deterministic coverage mapping. Add `--fail --threshold 1` only when the description has `USE FOR:` / `DO NOT USE FOR:` requirements. Never pass the semantic flag or a judge-model flag |
| V3 | `WAZA_NO_UPDATE_CHECK=1 waza grade <eval.yaml> --task <id> --results <fixture>.results.json --workspace <fixture-dir>` | Only for tasks whose graders, including suite-level `graders:`, are all deterministic; always pass `--task` |

V3 rules:

- Deterministic graders are `file`, `diff`, `text`, `json_schema`,
  `trigger`, `skill_invocation`, `tool_calls`, `tool_constraint`,
  `action_sequence`, `behavior`, and `program` / `code` scripts that
  Autogenesis authored and that make no network or model calls.
- A task with any `prompt` grader is never graded by Autogenesis; it is listed
  `left_to_runner` and keeps its fixtures for the runner's own grader check.
- A reference that fails or a negative that passes makes the suite
  **invalid**: fix the grader or fixture, bump `suite_version`, and re-check
  before claiming "authored and valid".

Everything else is out of scope and never run by Autogenesis:

- never `waza run` in any form; the mock executor is still a task run;
- never `waza quality` and never `waza adversarial`;
- never run suggestions, never `waza models`, never any Waza MCP mode;
- never `--semantic` and never `--judge-model`;
- never any Waza command without `WAZA_NO_UPDATE_CHECK=1`.

If the version check does not report 0.38.9, or Waza is not installed, record
`validity: deferred: waza 0.38.9 unavailable` plus repository-native
structural checks (YAML parses, files referenced by `eval.yaml` exist, every
gate task has both fixtures). Never install a different version and never fall
back to a model.

## Evidence block (implement experience)

Record under `## Evaluation evidence`, after the deterministic smoke block:

```text
waza_suite:
  path: evals/<skill>/ @ <commit>
  suite_version: <n>   (bumped on any grader, threshold, prompt or fixture change, with reason)
  format: waza 0.38.9, schemaVersion 1.4
  tasks: <n> (gate <g>, quality <q>, trigger <t>)
  coverage: USE FOR <a>/<b>, DO NOT USE FOR <c>/<d> (authored mapping)
  grader_controls: reference + negative fixture for <g>/<g> gate tasks
  validity:                       # model-free checks only
    waza: 0.38.9 (774df00)        # from the version check; any other version is deferred, not a pass
    env: WAZA_NO_UPDATE_CHECK=1
    check:
      cmd: WAZA_NO_UPDATE_CHECK=1 waza check <skill-path> --format json
      exit_code: <n>
      summary: <compliance level, token budget, eval presence, schema result>
    spec_verify:
      cmd: WAZA_NO_UPDATE_CHECK=1 waza spec verify --skill <skill-path> --eval <eval.yaml> --format json
      exit_code: <n>
      coverage: USE FOR <a>/<b>, DO NOT USE FOR <c>/<d> (as reported)
    grader_fixtures:
      cmd: WAZA_NO_UPDATE_CHECK=1 waza grade <eval.yaml> --task <id> --results fixtures/<id>/<variant>.results.json --workspace fixtures/<id>/<variant>/
      checked: <k> deterministic tasks; reference passed <k>/<k>, negative failed <k>/<k>
      left_to_runner: <task ids with a prompt grader>
    output_log: <path to captured JSON outputs>
  run_status: not-run-by-autogenesis
```

This block is **not behavioural evidence**. It shows that the suite is well
formed, covers the description, and that its deterministic graders tell a
known-good state from a known-bad one. It shows nothing about how an agent
behaves. A claim that behaviour works rests on deterministic smokes or on
cited supplied results, never on the existence or validity of a suite. The
receipt may carry `evidence.waza_suite`; the work node records
`eval_suite_ref` and `behavioural_status: authored-not-run`.

## Run boundary and supplied results

- **Who runs:** the owner of the subject repository, or its CI, under their
  own token, budget, environment and network policy.
- **Intended runner:** a separate on-demand evaluator bot. It is not part of
  Autogenesis, not an APM dependency and never invoked by any Autogenesis
  module. Its results reach Autogenesis only as supplied results.
- Autogenesis may cite supplied results in the subject Atlas (implement
  experience or a later experience) and in `evidence.supplied_results`, only
  in this form:

```text
supplied_results:
  supplied_by: <person or CI run id>
  run_at: <timestamp with zone>
  suite: evals/<skill>/ @ <commit>, suite_version <n>
  matches_authored: yes | no (stale)
  waza: <version>; executor/harness: <as reported>; models: <as reported>
  trials: <as reported>
  summary: <as reported, quoted not recomputed>
  location: <path or CI artifact>; sha256: <as supplied or computed on the supplied file>
  label: supplied; not produced, re-run or re-graded by Autogenesis
```

- Trials, pass counts, confidence intervals and result hashes appear only
  inside this citation block; Autogenesis never produces them.
- A stale result (suite commit or `suite_version` differs) is recorded as
  stale and backs no claim.
- A supplied red gate result is recorded, and the behaviour is not claimed to
  work. Whether to ship is the owner's decision.
- Autogenesis does not average, re-grade or interpret results beyond quoting
  them. The work node then records `behavioural_status: owner-results-cited`.

## Derived skills

Derived skills get **no suite by default**. Design may recommend the Waza
format in a derived skill's evaluation plan; `evals/` files are added to a
derived skill only with explicit approval in that skill's plan.
