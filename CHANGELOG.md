# Changelog

All notable changes to this package are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and releases follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). The skill body stays
in `SKILL.md`.

## [Unreleased]

## [0.9.0] - 2026-10-08

### Changed

- Harden root routing (work_id `2026-10-11-root-routing-hardening`). A discussion conclusion, prior agreement, or request to apply a package change starts formal design instead of only refusing. A user-named plan path outside the resolved subject Atlas is not a storage override: persist in the resolved store, say why the named path was not used, and do not stop to ask. A legacy `references/atlas` gitlink still routes to migrate; a plain directory does not block. Current successors are `explicit-discuss-integration-adversarial-v2` and `atlas-storage-semantics-adversarial-v5`. Dogfood `suite_version` moves from 14 to 19 (15 added the just-discuss and declined-path gates; 16 accepts a proposed plan status, scopes the work-node grader to the work node, and accepts inline change-class prose; 17 ties the declined-path reply to the written plan date and an explicit refusal of `references/atlas`; 18 rejects any instruction to use that declined path, not only an "Instead, use" wording; 19 scopes that guard to the clause and either order, so a path-before-verb instruction and a use after an unrelated negation both fail). Version surfaces stay 0.9.0.
- Bound the source audit by a 720-second wall-clock deadline instead of
  shrinking each file's timeout by the tracked-file count. Each file is
  limited to the minimum of the 300-second command cap, a 60-second
  per-file cap, and the time remaining before the deadline. A file that
  cannot start before the deadline fails as not audited, and a timed-out
  file fails closed with no retry.
- Cut behavioural evaluation over from the agent-spec/Gherkin gate to
  authored upstream Waza eval suites (work_id `2026-10-08-waza-evaluation`).
  Autogenesis designs and authors suites in the Waza 0.38.9 format
  (`schemaVersion: "1.4"`) and never runs suite tasks against an agent or
  makes a model call for evaluation. Running belongs to the subject owner or
  its CI; supplied results may be cited with provenance.
- `behavioural_contract` now accepts `waza | deferred:<reason>`; the removed
  value `specify` is rejected with a diagnostic (no alias). Gate G-BEHAVIOUR
  replaces G-BDD; G-EVAL stays deterministic-first.
- Design drafts `## Behavioural evaluation (Waza)` tasks with reference and
  negative fixtures for gate tasks, or preserves `deferred:<reason>`.
  Drafting tasks does not approve suite files. Implement authors files at
  `<subject>/evals/<skill>/` (or `<subject>/.apm/evals/<skill>/` with
  `paths.evals: .apm/evals` when the subject is an APM package with a root
  `SKILL.md`, because APM 0.30.0 ships every other path) only when the
  approved plan names that suite-file scope. Counter conversion into gate
  tasks is optional inside that scope and does not happen after a deferral.
  When suite files are in scope, implement runs only the model-free validity
  allowlist V1-V3 with `WAZA_NO_UPDATE_CHECK=1` and records the `waza_suite`
  block with `run_status: not-run-by-autogenesis`, which is not behavioural
  evidence.
- The source-contract tests require PyYAML 6.0.2, hash-pinned in
  `scripts/requirements-test.txt` and installed by CI before unittest. A
  missing parser fails those tests instead of skipping them.
- `specify-only-adversarial-v2` and `help-getting-started-adversarial-v1`
  become historical, succeeded by `waza-evaluation-adversarial-v1` and the
  parse-valid `help-getting-started-adversarial-v2`.
- `atlas-migrate-activation-adherence-v4` and
  `atlas-storage-semantics-adversarial-v3` stay historical with their
  original bodies. Successors `atlas-migrate-activation-adherence-v5` and
  `atlas-storage-semantics-adversarial-v4` carry the 0.9.0 release identity.
  The storage successor asserts Atlas path `references/paths/recall.md`
  instead of the removed `references/paths/query.md`.
- Refresh the frozen dependency graph so Atlas follows the live catalog
  resolution `v0.13.0` (`b0b101243ffae8f6da16ab4d139057b4f29a01a5`).
  Autogenesis 0.9.0 requires Atlas v0.13.0 or later. Path `query` and CLI
  `search`/`query` were removed in that release with no alias, so those
  uses now follow path `recall` and `atlas recall run`. OKF `v0.2.1`,
  Discuss `v0.5.0`, and Think `v0.1.0` stay on their existing lock
  resolutions.

### Added

- Autogenesis dogfood eval suite at `.apm/evals/autogenesis/`
  (final `suite_version: 14`, Waza 0.38.9 format, `schemaVersion: "1.4"`):
  five gate tasks with deterministic outcome graders, two trigger tasks and
  one advisory quality task. The shipped suite is version 14. It ships
  minimal fixture subject repositories, reference and negative fixtures with
  hand-authored results files for every deterministic task, and a README with
  run instructions, required skills and the recommended pass rule. Authored
  and never run by Autogenesis (`run_status: not-run-by-autogenesis`); a
  structural unit test checks it. It lives under `.apm/evals/` so it is not
  shipped in the installed skill (the root `.waza.yaml` sets `paths.evals`).
  Diff-grader context is `fixtures/subjects`. A change class is accepted only
  as an exact `hardening`, `new-surface` or `new-skill` token on a
  `change_class:` / `change-class:` key, on the first non-blank line under
  a "Change class" heading, as an inline label, or as a whole-line table row. A value
  that only starts with a class still fails. On the heading form, prose may
  follow that exact token. A store log may gain lines at the end or in one
  block directly under the first `# Log` heading. The suite README adds a run layout that keeps the
  suite outside the agent's working directory and skill paths, recommends
  `config.skill_directories` over `paths.skills`, explains how to read
  `skill_invocation` scores, and requires `python3` in the runner image.
  Plan and work-node status is parsed rather than matched as YAML spelling.
  The complete legacy `references/atlas` tree is compared with its initial
  state. `config.inject_skill_body` is false, so trigger tasks are not handed
  the skill body. Status graders fail closed unless the value is the simple
  scalar `designed`, and the resolved plan file must exist. The canonical
  design work node must exist at status `designed`. The help workspace is
  compared with the unmounted subject, ignoring only the root `.git`
  directory. Complete-tree comparisons record every child with lstat,
  including directory and file symlinks, and never follow them. Status
  graders lstat each canonical path and its parents and fail closed on a
  symlink. Discussion must persist a designed plan and work node. Symlink
  fixtures are not committed, because a committed symlink breaks APM install.
  Every task uses one shared whole-workspace allowlist: any added, changed or
  removed path outside that list, including a symlink, fails. An allowed
  path, and every path under an allow-under directory, must be a regular file
  reached only through real directories. The near-miss trigger task may
  change `app/durations.py` and Python bytecode caches, and the skill-change
  trigger task may add or change regular files under the resolved store's
  plans and work directories. Any other path, including a symlink, still
  fails. The suite README records the model-free validity re-run and leaves
  `plan-has-genesis-artifacts` to the runner because it contains a prompt
  grader.
  Plan tasks require the canonical work node at status designed, sharing
  the plan date. Status whitespace is only spaces and tabs, so a trailing
  Unicode space fails closed.
  History of `suite_version` bumps (not the shipped version; the shipped
  suite is version 14): version 2 placed the suite under `.apm/evals/` and
  accepted a "Change class" heading; version 3 parsed status and set
  `inject_skill_body: false`; version 4 failed closed on a non-scalar status
  and required the resolved plan; version 5 required the designed work node
  and compared the help tree; version 6 recorded symlink children without
  following them; version 7 lstat-checked status paths, required a discussion
  plan and work node, and stopped committing symlink fixtures; version 8
  introduced the shared allowlist; version 9 widened the two trigger
  allowlists; version 10 rejected a symlink on an allowed path; version 11
  requires an exact change-class token; version 12 makes design tasks
  date-agnostic, parses indented frontmatter in one shared checker, allows
  Atlas-owned experience, index and log writes on the design tasks, and
  gives the fixture SCHEMA a minimal compile block that Atlas v0.13.1 accepts;
  version 13 accepts a newest-first log entry under `# Log` and heading-led
  change-class prose; version 14 requires the canonical work node on the
  plan tasks and keeps status whitespace to spaces and tabs; version 15
  adds the just-discuss and declined-path gates; version 16 accepts a
  proposed or designed plan status, checks work-node status only on the
  work node, and accepts prose after a bold or underscore inline
  change-class label; version 17 requires the declined-path reply to name
  the written plan path and to refuse `references/atlas` with a reason
  tied to the resolved subject Atlas; version 18 rejects any instruction
  to use that declined path, not only an "Instead, use" wording.
- Consumer validation fails when an installed `autogenesis` skill contains an
  `evals/` directory, a `.apm/` directory or any `eval.yaml`; source checks
  and the `suite-not-shipped` smoke keep the suite under `.apm/evals/`.
- Shared authoring guide `references/waza-authoring.md`: format pin, suite
  layout, tiers and tags, authoring rules, reference and negative fixtures,
  pass-bar metadata, the closed model-free validity allowlist, the evidence
  block, the run boundary and the `supplied_results` citation format.
- Work-node fields `eval_suite_ref` and `behavioural_status`.
- Unit tests that every current scenario parses, that the guide carries the
  pins, that no Waza wrapper is named, that Waza and agent-spec stay out of
  the APM manifest and lock, and that no live instruction requires agent-spec
  or `.feature` files.

### Removed

- The agent-spec `specify` behavioural contract, the
  `## Behavioural contract (agent-spec)` plan section and the rule set around
  behavioural Gherkin. Waza is not an APM dependency, and no CI job runs it.

## [0.8.1] - 2026-09-28

### Changed

- Drop `APM_READ_TOKEN` from Autogenesis CI now that Atlas-family GitHub
  sources are public. Marketplace add and consumer install run
  unauthenticated; missing-token fail-closed steps are gone. Public
  consumers still need no PAT. Package version, GitHub visibility, and
  Genesis credit are unchanged.
- Align the APM package description in `apm.yml` with the human-owned
  README purpose lede. Package version, GitHub visibility, and Genesis
  credit are unchanged.
- Refresh the frozen dependency graph so Discuss follows the live catalog
  resolution `v0.5.0` (`480fc5fc9f0b1c280cd2301dccbf76ff63ddbc4e`). Atlas
  `v0.12.0`, OKF `v0.2.1`, and Think `v0.1.0` stay on their existing lock
  resolutions.

## [0.8.0] - 2026-09-13

### Added

- Add parent-routed `help` and `getting-started` operations: packaged
  baseline first (including bundled help topics), optional read-only Atlas
  enrichment when a store is already resolvable, explain-without-execute,
  and fenced cards that show `intent` plus `atlas_used`. Public `help`
  lists operations; it does not bypass parent routing to load private
  support modules.
- Align GitHub issue and pull request templates with the family hybrid set,
  including a security-advisory contact link and Autogenesis-specific PR
  extras.
- Add the complete Apache License 2.0 text, Autogenesis copyright notice, and
  preserved Genesis attribution; document that the separately published
  Genesis book uses CC BY-NC 4.0 while the repository code uses Apache-2.0.
- Add a shared skill-native SOLID design authority, prospective application
  guidance across design, initialise, package review and S8, plus an additive
  adversarial scenario and structural linkage coverage.
- Add an optional instruction-only skill-module template without runtime
  validators, protocol schemas or mandatory resource directories.
- Add Autogenesis-scoped S8 Parent-routed Skill Module as a draft structural
  pattern, with applicability/admission guidance in design, initialise and
  package review. B17 Activation Card remains active; Genesis is unchanged.

### Changed

- Restructure the root README to the family outline (purpose, why / what
  this is not, install, use, modules, related, contributing, license).
  README Install documents only the public marketplace path
  (`apm marketplace add ... --name atlas` then `apm install autogenesis@atlas`).
  Maintainer install pins, git-tag commands, dependency commits, and
  required-check names stay in `CONTRIBUTING.md`.
- Document Atlas catalog consumer install
  (`apm marketplace add sergio-sisternes-epam/atlas-marketplace --name atlas`
  then `apm install autogenesis@atlas`). Public github.com consumers do
  not need a PAT for public catalog and package sources. This
  repository's consumer CI jobs still require `APM_READ_TOKEN` and fail
  closed when it is absent.
- Keep the module discipline instruction-first by removing the proposed generic
  Python source/trace validator and its dedicated test harness; current scenario
  checks now use existing repository tests and lightweight shell assertions.
- Advance the reviewed Autogenesis Atlas snapshot to
  `161fb87c0420f149cd1efba9e998eab575bce13a` for the approved SOLID design,
  explicit approval, verified implementation evidence, and closed work hub.
- Remove the unavailable external evaluator dependency from Autogenesis's live
  workflow, lineage fields and current acceptance contract. Portable
  scenarios, repository-native checks, actual evidence and GitHub CI remain.
- Refine draft S8 to version 0.2 as instruction-first guidance for derived
  skills. Separate Genesis authoring discipline from generated runtime;
  make full fusion explicit and generic review conditional on adopted
  modules, gates and memory integration. Autogenesis's own protocol and
  release tooling remain local policy.
- Advance the reviewed catalog Atlas pin to `v0.12.0`
  (`40e11c65e243236850c26fc6cd5a04acdd483eb4`). OKF `v0.2.1`, Discuss
  `v0.3.10`, and Think `v0.1.0` stay on their existing lock resolutions.

## [0.7.0]

### Changed

- Nest-load catalog `think@atlas` from the parent-routed `think-challenge`,
  `think-grill`, and `think-ramble` wrappers. Autogenesis no longer vendors
  forked think procedure. Run overlays remain: parent invocation, think-challenge
  as a design validation gate with named-theory smokes, subject-Atlas
  write-home, and no grill/ramble while catalog Discuss is active.
- Advance the reviewed Autogenesis Atlas snapshot to
  `110cab3deb3a87695003c6276ad92426e6262521` for the approved nest-load plan,
  decision, and implementation experience.

## [0.6.0] - 2026-09-12

### Changed

- Remove the parent-routed Autogenesis `discuss` operation and discussion-mode
  routing. Durable discussion belongs exclusively to the pinned
  `discuss@atlas` package; activate that catalog skill directly. Conclusions
  that require a package change must re-enter formal Autogenesis design and
  approval before implementation.

## [0.5.0] - 2026-09-11

### Changed

- Promote Autogenesis to `v0.5.0` as a breaking release. The root skill now
  routes 21 parent-owned modules, the old path surface is removed, and the
  invocation contract requires module entrypoints under
  `references/modules/<name>/SKILL.md`.
- Update the release and consumer guidance to use `v0.5.0` install / update
  examples while preserving the historical `v0.4.3` release notes below.
- Keep the repository release process locked to the existing dependency pins
  and reviewed store snapshot; no lock refresh was required for this surface
  cutover.
- Separate invocation requests, configured full/compact activation cards and
  evidence-bearing receipts; protect parent context and permit at most one
  transient, known-repeat-safe retry without parent replay resets.
- Add instruction-first module contracts and complete owned deployment checks,
  including frozen-replay content validation. Version current scenario
  contracts while preserving historical suites. GitHub CI remains the final
  acceptance gate.

## [0.4.3] - 2026-09-10

### Changed

- Resolve Atlas, OKF, Discuss, and Think through marketplace `atlas`
  (`name` + `marketplace: atlas`; install identifiers `pkg@atlas`).
  Lock catalog Atlas `v0.11.2` (`579e809`), Discuss `v0.3.10` (`c1c0936`),
  OKF `v0.2.1` (`5246f7b`), and Think `v0.1.0` (`874613a`). Consumers
  register with
  `apm marketplace add sergio-sisternes-epam/atlas-marketplace --name atlas`.

## [0.4.2] - 2026-09-08

### Changed

- Declare Atlas, OKF, Discuss, and Think as marketplace objects
  (`name` + `marketplace: sergio-sisternes-epam`; equivalent to
  `package@sergio-sisternes-epam`). Lock catalog Atlas `v0.9.1`
  (`a1074e5`), Discuss `v0.3.9` (`95b5191`), OKF `v0.2.1` (`5246f7b`),
  and Think `v0.1.0` (`874613a`). APM 0.30.0 rejects the string shorthand
  in `apm.yml`; catalog `source.ref` values are the peeled release commits,
  so the lock records those SHAs as `resolved_ref`.
- Register catalog `sergio-sisternes-epam` before lock replay and
  consumer validation so marketplace refs resolve in CI. Replay the
  committed lock with `apm lock` because APM 0.30.0 `--frozen` cannot
  match marketplace placeholder keys to resolved git lock keys.
- Pin the reviewed APM CLI to 0.30.0 (`8c2e0d9`) with checksum
  `8b84bebf19c350faf36d21aebb350dc656d04c0b7a1c2bf8ea35c0caa0e44bb9`.

## [0.4.1] - 2026-09-06

### Added

- Add local release-candidate automation with checksum-pinned APM setup,
  stable named CI checks, isolated annotated-tag verification, and
  re-verification immediately before GitHub Release creation.
- Add repository-owned offline contract tests and disposable consumer
  validation for Agent Skills and stable runtime targets.

### Changed

- Pin Atlas `v0.9.0`, OKF `v0.2.1`, Discuss `v0.3.8`, and Think `v0.1.0`
  as immutable direct dependencies and commit their resolved lock state.
- Advance the mutable Autogenesis Atlas store gitlink to
  `56d81a3034b2454520bcc6461a4ff4402a9ba0df`; the mesh intentionally continues
  to track `main` for governed process-memory evolution.
- Add deterministic source, dependency, store, consumer, release-readiness,
  and annotated-tag validation with a tag-triggered GitHub Release workflow.
- Document the reviewed contribution and release procedure, including the
  direct OKF invocation contract and its expected different-parent-anchor
  warning.
- Treat root direct released pins as authoritative while retaining and
  reporting the reviewed Atlas-to-OKF and Discuss-to-Atlas anchor divergence.

## [0.4.0]

- **Atlas storage:** process memory now writes home to the active subject
  repository's declared `.atlas/<host>/<org>/<repo>` mount. Autogenesis loads
  Atlas path `mount`, mounts with no `--target`, and uses only the root returned
  by `atlas resolve`.
- **Migration:** the Autogenesis store gitlink moved from
  `references/atlas` to
  `.atlas/github.com/sergio-sisternes-epam/autogenesis-atlas`. Path
  `atlas-migrate` composes Atlas storage migration before optional legacy
  okf-wiki intake.
- **Safety:** missing or ambiguous store identity, failed resolution, and
  missing SCHEMA fail closed. Compatibility symlinks, dual-write, and silent
  fallback are forbidden.
- **Evaluation:** adds current happy-path
  `atlas-migrate-activation-adherence-v2` and adversarial
  `atlas-storage-semantics-adversarial-v1` scenarios while retaining v1 as
  historical evidence.
- **Compatibility:** existing repositories must migrate their Atlas metadata
  before using this release. Global APM consumers update only after release,
  using dry-run and explicit approval.
- Work_id `2026-09-05-atlas-storage-semantics`.

## 0.3.13

- **Exit / process memory:** deferred items are `type: protostar` with `work_id`, origin `derived_from`, work-hub `implements`. Folder `autogenesis/residuals/` is forbidden. Plan heading `Accepted risks` replaces `Residual risks` so leftover *risk* is not leftover *work*. Work_id `2026-08-26-residuals-vs-protostar`.
- **APM:** `apm.yml` depends on atlas, okf, discuss, and think. Path discuss substrate-loads catalog skill discuss (fail-closed Enter if missing). Root think-ramble / think-grill / think-challenge stay available outside Autogenesis Runs.

## 0.3.12

- **path discuss / from active design:** a problem found in design review re-enters `mode: discussion` on the same `work_id`. `stage: design`, `artifact` = the plan, existing `discussion_root` reused, prior idea nodes in scope. No nested path, no blank hub. Work_id `2026-08-26-discuss-from-active-design`.

## 0.3.11

- **path discuss:** `mode: discussion` must use `path: discuss`. Path module substrate-loads catalog skill discuss, passes subject `atlas_root`, fail-closed Enter if discuss load or discuss fields are missing. think-grill / think-ramble not loaded in discussion mode. think-challenge stays an internal validation gate. Work_id `2026-08-26-autogenesis-discuss-activation`.

## 0.3.10

- **design path step 6b:** agent-spec path `specify` is now the **sole** legal producer of behavioural Gherkin. Direct authoring by Autogenesis forbidden. Explicit `deferred: <reason>` remains first-class. Activation card gains required `behavioural_contract: specify | deferred:<reason>` hint when behaviour is in scope. Discussion principles updated (explore via specify in discussion mode; only design materialises). Work_id `2026-08-25-specify-only-behavioural-contract`.

## 0.3.9

- **card pattern (B17 / workflow-discipline):** Enter card and path receipt now begin with `skill:` and `skill_path:` (first two fields). Canonical schema updated; peers receive the same leading fields.

## 0.3.8

- **design path step 6c:** `## Evaluation plan` required when behaviour is in scope — deterministic smokes primary, agent evaluations secondary; anti-pattern soft-only evaluation; gate **G-EVAL**.

## 0.3.7

- **design path:** step 6b — agent-spec behavioural contract (`## Behavioural contract (agent-spec)`); G-BDD gate.
- Depends on skill `agent-spec` for layout / coverage validation when the gate runs.

## 0.3.6

- **atlas-migrate:** mandatory thorough relationship review + quality `relates_to` before Exit (from 0.3.5).
- **Internal think modules** (challenge / grill / ramble): Atlas query/remember only; no okf-wiki substrate.
- **Paths** initialise / learn-skill / research: Atlas-first process memory.
- **activation-card / run-record-template:** `atlas_root` + compile on receipts.
- **validate-okf-conformance:** prefers Atlas store; optional `atlas compile`.
- **Canonical decision:** `wiki-folder-deletion-policy` — no auto-delete on migrate; human-gated archive removal.
- **Package metadata:** `apm.yml` deps on atlas + okf (not okf-wiki).

[Unreleased]: https://github.com/sergio-sisternes-epam/autogenesis/compare/v0.9.0...HEAD
[0.9.0]: https://github.com/sergio-sisternes-epam/autogenesis/releases/tag/v0.9.0
[0.8.1]: https://github.com/sergio-sisternes-epam/autogenesis/releases/tag/v0.8.1
[0.8.0]: https://github.com/sergio-sisternes-epam/autogenesis/releases/tag/v0.8.0
[0.7.0]: https://github.com/sergio-sisternes-epam/autogenesis/releases/tag/v0.7.0
[0.6.0]: https://github.com/sergio-sisternes-epam/autogenesis/releases/tag/v0.6.0
[0.5.0]: https://github.com/sergio-sisternes-epam/autogenesis/releases/tag/v0.5.0
[0.4.3]: https://github.com/sergio-sisternes-epam/autogenesis/releases/tag/v0.4.3
[0.4.2]: https://github.com/sergio-sisternes-epam/autogenesis/releases/tag/v0.4.2
[0.4.1]: https://github.com/sergio-sisternes-epam/autogenesis/releases/tag/v0.4.1
[0.4.0]: https://github.com/sergio-sisternes-epam/autogenesis/releases/tag/v0.4.0
