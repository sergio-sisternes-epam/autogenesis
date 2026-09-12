# Changelog

All notable changes to this package are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and releases follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). The skill body stays
in `SKILL.md`.

## [Unreleased]

### Added

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
  Maintainer install pins, dependency commits, and required-check names
  move to `CONTRIBUTING.md`.
- Document Atlas catalog consumer install
  (`apm marketplace add sergio-sisternes-epam/atlas-marketplace --name atlas`
  then `apm install autogenesis@atlas`). Direct git-tag install remains.
  Public github.com consumers do not need a PAT for public catalog and
  package sources. This repository's consumer CI jobs still require
  `APM_READ_TOKEN` and fail closed when it is absent.
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
- Clarify B17's portable request cue separately from its Autogenesis-specific
  receipt, retry and memory policy; retain its active status.
- Breaking cutover to 21 parent-routed modules under
  `references/modules/<name>/SKILL.md`, with the root skill remaining the only
  catalog export and module arguments unable to override parent-owned context.
- Update the current package/version surfaces to `v0.5.0`, including install
  commands, bug-report example, and release guidance.

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

[Unreleased]: https://github.com/sergio-sisternes-epam/autogenesis/compare/v0.7.0...HEAD
[0.7.0]: https://github.com/sergio-sisternes-epam/autogenesis/releases/tag/v0.7.0
[0.6.0]: https://github.com/sergio-sisternes-epam/autogenesis/releases/tag/v0.6.0
[0.5.0]: https://github.com/sergio-sisternes-epam/autogenesis/releases/tag/v0.5.0
[0.4.3]: https://github.com/sergio-sisternes-epam/autogenesis/releases/tag/v0.4.3
[0.4.2]: https://github.com/sergio-sisternes-epam/autogenesis/releases/tag/v0.4.2
[0.4.1]: https://github.com/sergio-sisternes-epam/autogenesis/releases/tag/v0.4.1
[0.4.0]: https://github.com/sergio-sisternes-epam/autogenesis/releases/tag/v0.4.0
