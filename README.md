# autogenesis

Root-skill APM package (`SKILL.md` + `apm.yml` at the repository
root): `sergio-sisternes-epam/autogenesis`.

Install from the Atlas catalog on github.com:

```text
apm marketplace add sergio-sisternes-epam/atlas-marketplace --name atlas
apm install autogenesis@atlas
```

Public github.com consumers do not need a personal access token for public
catalog and package sources. This repository's consumer CI jobs still
require the `APM_READ_TOKEN` workflow secret and fail closed when it is
absent.

Or install the immutable v0.7.0 release by git tag for the portable Agent
Skills target:

```text
apm install sergio-sisternes-epam/autogenesis#v0.7.0 --target agent-skills
```

Or validate/deploy across the supported stable runtime profile:

```text
apm install sergio-sisternes-epam/autogenesis#v0.7.0 --target claude,codex,copilot,cursor,gemini,grok-build,kiro,opencode,windsurf
```

Autogenesis is validated with APM CLI 0.30.0 (`8c2e0d9`).

## Breaking invocation cutover

Autogenesis v0.6.0 is a breaking cutover to 20 parent-routed modules: the
`discuss` operation is removed and durable discussion is the catalog Discuss
package. Autogenesis v0.7.0 nest-loads catalog `think@atlas` from the
parent-routed think wrappers; it does not vendor forked think procedure.
The root skill remains the only catalog export; it owns the version
surface and module registry. Each module is loaded by its named entrypoint
under `references/modules/<name>/SKILL.md`, and the parent-owned request
context cannot be overridden by module arguments. There are no compatibility
aliases for the removed path surface or the removed discuss operation.

An invocation request carries task arguments, parent-owned context and the
resolved entrypoint. Its **activation card** is a visible request cue, not
approval or execution evidence: full for root/operation requests, compact for
supports. Absent/off skips cards, on enables them, and debug adds redacted
context without disabling gates. Receipts record actual outcomes. Only one
automatic retry is permitted, and only for transient, known-repeat-safe work.

Current scenario suites are selected by `references/scenarios/suite-index.json`;
older suites remain unchanged as history. External skill protocols and installed
global consumers are not migrated by this repository change. Source changes
are checked locally; GitHub CI is the final acceptance gate. APM deployment
coverage is distinct from actual discovery or behaviour in each host.

## Skill Module pattern

Autogenesis hosts **S8. Parent-routed Skill Module** as a **draft** structural
extension to Genesis. During design, initialise or package review, the patterns
support makes it available when several cohesive procedures should share one
public skill and release owner. It is not appropriate merely to split a short
procedure or hide independently released skills.

The [pattern](references/modules/patterns/references/parent-routed-skill-module.md)
separates module structure from invocation and B17 Activation Card's visible
request interface. Genesis remains unchanged and B17 remains active. Applying
the draft requires an approved design; active admission additionally requires
repeated observed use and a separate decision.

S8 is instruction-first. A derived skill needs clear module inputs, procedures,
boundaries and outcomes, not Autogenesis's JSON protocol, validators or trace
infrastructure. Use the [optional module template](references/modules/patterns/references/skill-module-template.md)
when private procedures genuinely help; a short skill can remain root-only.
Task-serving scripts are allowed. Full Genesis discipline applies to the design
process; generated runtime capabilities, including memory or full Autogenesis
fusion, must be chosen explicitly. This repository's release checks are separate.

## SOLID principles for skills

Autogenesis applies a
[skill-native SOLID lens](references/skill-design-principles.md) after Genesis
for formal design work. New surfaces and new skills record all five principles
as applicable, not-applicable or a trade-off; hardening records the material
principles. The lens protects cohesive responsibilities, governed semantics,
complete progressive interfaces and justified dependencies without requiring
modules or speculative abstractions. Substitutability is assessed only when an
interchangeable contract is claimed.

## Immutable package, mutable store

Process memory is **not** authored in the installed skill package. The
Autogenesis subject store is:

https://github.com/sergio-sisternes-epam/autogenesis-atlas

Git root **is** the OKF root (`SCHEMA.json`). From the active Autogenesis
repository, load Atlas path `mount`, then mount with no `--target` and resolve
the root:

```text
python3 <atlas-skill>/scripts/atlas.py mount github.com/sergio-sisternes-epam/autogenesis-atlas --ref main
python3 <atlas-skill>/scripts/atlas.py resolve github.com/sergio-sisternes-epam/autogenesis-atlas
```

Default mount and compile/query root:
`.atlas/github.com/sergio-sisternes-epam/autogenesis-atlas`.
The package source and dependency graph are immutable at `v0.7.0`, while the
store intentionally retains mutable `main` semantics in `.gitmodules` and
`atlas-mesh.json`. This repository records the reviewed store snapshot as
gitlink `110cab3deb3a87695003c6276ad92426e6262521`. Companion Discuss lineage
and later store movement remain separate governed changes.

For work on another subject, Autogenesis uses that subject repository's
declared Atlas. It never writes process memory into the installed skill tree.

## Migrate from v0.3.x

Repositories that still track an Atlas at `references/atlas` must run the
Atlas `migrate` path before using Autogenesis v0.4.0. The migration:

1. verifies the legacy gitlink identity and cleanliness;
2. moves it to `.atlas/<host>/<org>/<repo>`;
3. aligns `.gitmodules` and `atlas-mesh.json`;
4. mounts with no `--target` and verifies `atlas resolve`;
5. compiles the resolved store before removing stale local registration.

There is no compatibility symlink, dual-write, or silent fallback. A repository
that has not migrated fails closed with an actionable error.

## Dependency contract

`apm.lock.yaml` is committed and is the reproducible v0.7.0 dependency
contract. Direct dependencies are declared as marketplace objects on
`atlas` (`name` + `marketplace`) and resolve to the same
released pins:

| Direct package | Marketplace ref | Released pin | Resolved commit |
|---|---|---|---|
| Atlas | `atlas@atlas` | `v0.11.2` | `579e8090273ce991ea0717abed0775dc03f28de2` |
| OKF | `okf@atlas` | `v0.2.1` | `5246f7b193b58a32ac8a15fc76aedf37c42b042c` |
| Discuss | `discuss@atlas` | `v0.3.10` | `c1c0936d9a0346dce7d877646046c918de335d69` |
| Think | `think@atlas` | `v0.1.0` | `874613a67018c74ee95f857416fb315d2f80b92b` |

OKF remains a direct dependency because
`references/modules/workflow-discipline/SKILL.md` and
`references/modules/validate-okf-conformance/SKILL.md` invoke it directly.

Catalog Atlas v0.11.2 and Discuss v0.3.10 resolve nested OKF/Atlas through
the same marketplace pins as this root, so there are no reviewed graph
divergences. Any graph warning or unexpected resolved commit is a release
blocker.

## Discuss integration

`discuss@atlas` is a direct immutable package dependency. For durable
discussion, activate the catalog Discuss package directly; Autogenesis no
longer provides a `discuss` operation, `path: discuss` adapter, or Discuss Atlas
handoff. Discuss never authorizes implementation. A discussion conclusion that
requires a package change must begin a formal Autogenesis design Run and
receive the normal persisted-plan approval before implementation.

## Think integration

`think@atlas` is a direct immutable package dependency. During an Autogenesis
Run, `think-challenge`, `think-grill`, and `think-ramble` remain parent-routed
wrappers. Each wrapper nest-loads the matching catalog skill through the
harness skill loader and then applies Run overlays: parent invocation,
think-challenge as a design validation gate with named-theory smokes,
subject-Atlas write-home, and no grill/ramble while catalog Discuss is active.
The nested load must not re-enter the Autogenesis module or parent registry.

## Release process

Every pull request and `main` update runs stable checks for metadata, source
audit, frozen dependency replay, the exact checked-out store, Atlas v0.9.0
lint/compile, and disposable consumer installations. Workflows use the
repository secret `APM_READ_TOKEN` and fail clearly when it is unavailable.

The stable required-check names are **Release metadata**, **APM source
integrity**, **Frozen dependency graph**, **Atlas store validation**,
**Consumer install (agent-skills)**, **Consumer install (stable-runtimes)**,
and **Release readiness decision**.

A maintainer manually validates an exact current-`main` candidate before
separately creating an annotated `vX.Y.Z` tag. The tag workflow accepts only a
new authoritative remote annotated tag that peels to current `main`, reruns CI
against `sergio-sisternes-epam/autogenesis#<tag>`, re-verifies the remote tag
object immediately before publication, and combines this changelog's curated
notes with generated GitHub notes. Tags are never moved, deleted, or reused.
See `CONTRIBUTING.md` for the local commands and approval boundaries.

## Update a global APM consumer

Do **not** update any global consumer yet. After v0.7.0 has been merged and
released, and only with explicit approval:

1. Back up `~/.apm/apm.yml` and `~/.apm/apm.lock.yaml`.
2. Prefer an immutable dependency:
   `sergio-sisternes-epam/autogenesis#v0.7.0`.
3. Preview:
   `apm update -g sergio-sisternes-epam/autogenesis --dry-run`.
4. Apply:
   `apm update -g sergio-sisternes-epam/autogenesis --yes`.
5. Verify the resolved version and run an Autogenesis design preflight from
   the subject repository.

Rollback restores the saved manifest/lock or pins the previous known-good ref,
then runs the same explicit update flow. This package never updates the global
installation automatically.

## License and attribution

Autogenesis is Copyright 2026 Sergio Sisternes and is licensed under the
[Apache License 2.0](LICENSE), as declared in `apm.yml`.

Autogenesis integrates with and builds upon concepts from
[Genesis](https://github.com/danielmeppiel/genesis), Copyright 2025 Daniel
Meppiel. The Genesis repository code is licensed under Apache-2.0. Its
long-form book is a separate work licensed under CC BY-NC 4.0; that book
license does not apply to the Genesis repository code or to Autogenesis.
See [NOTICE](NOTICE) for the preserved attribution.

See `SKILL.md` and `CHANGELOG.md`.
