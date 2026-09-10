# autogenesis

Private root-skill APM package (`SKILL.md` + `apm.yml` at the repository
root): `sergio-sisternes-epam/autogenesis`.

Install the immutable v0.4.3 release for the portable Agent Skills target:

```text
apm install sergio-sisternes-epam/autogenesis#v0.4.3 --target agent-skills
```

Or validate/deploy across the supported stable runtime profile:

```text
apm install sergio-sisternes-epam/autogenesis#v0.4.3 --target claude,codex,copilot,cursor,gemini,grok-build,kiro,opencode,windsurf
```

Autogenesis is validated with APM CLI 0.30.0 (`8c2e0d9`). The package is
private; configure a read-only GitHub credential with repository Contents read
access before installation.

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
The package source and dependency graph are immutable at `v0.4.3`, while the
store intentionally retains mutable `main` semantics in `.gitmodules` and
`atlas-mesh.json`. This repository records the reviewed store snapshot as
gitlink `56d81a3034b2454520bcc6461a4ff4402a9ba0df`; later store movement is a
separate governed change.

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

`apm.lock.yaml` is committed and is the reproducible v0.4.3 dependency
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
`references/modules/workflow-discipline.md` and
`references/modules/validate-okf-conformance.md` invoke it directly.

Catalog Atlas v0.11.2 and Discuss v0.3.10 resolve nested OKF/Atlas through
the same marketplace pins as this root, so there are no reviewed graph
divergences. Any graph warning or unexpected resolved commit is a release
blocker.

## Release process

Every pull request and `main` update runs stable checks for metadata, source
audit, frozen dependency replay, the exact checked-out store, Atlas v0.9.0
lint/compile, and disposable consumer installations. Private cross-repository
reads use the repository secret `APM_READ_TOKEN`; workflows fail clearly when
it is unavailable.

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

Do **not** update any global consumer yet. After v0.4.3 has been merged and
released, and only with explicit approval:

1. Back up `~/.apm/apm.yml` and `~/.apm/apm.lock.yaml`.
2. Prefer an immutable dependency:
   `sergio-sisternes-epam/autogenesis#v0.4.3`.
3. Preview:
   `apm update -g sergio-sisternes-epam/autogenesis --dry-run`.
4. Apply:
   `apm update -g sergio-sisternes-epam/autogenesis --yes`.
5. Verify the resolved version and run an Autogenesis design preflight from
   the subject repository.

Rollback restores the saved manifest/lock or pins the previous known-good ref,
then runs the same explicit update flow. This package never updates the global
installation automatically.

See `SKILL.md` and `CHANGELOG.md`.
