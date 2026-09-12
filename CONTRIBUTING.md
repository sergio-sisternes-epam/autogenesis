# Contributing

## Prerequisites

| Tool | Required version | Purpose |
|---|---|---|
| Git | 2.x | Source and gitlink verification |
| Python | 3.12 | Repository-owned checks |
| APM CLI | 0.30.0 (`8c2e0d9`) | Frozen install and audit |

The private repositories used by this package require a read-only token with
Metadata and Contents read access. Export it locally without writing it to a
file:

```text
export APM_READ_TOKEN=<read-only-token>
export GITHUB_APM_PAT_SERGIO_SISTERNES_EPAM="$APM_READ_TOKEN"
```

Never print, persist, or commit the value. GitHub Actions reads the repository
secret named `APM_READ_TOKEN` and fails closed when it is absent.

## Repository contract

The package root contains `SKILL.md` and `apm.yml`. Direct dependency refs in
`apm.yml` are marketplace objects (`name` + `marketplace:
atlas`). APM 0.30.0 rejects `package@marketplace` string
shorthand in the manifest (it is parsed as an unsupported alias). Catalog
entries resolve to released tags, and their exact resolutions are committed
in `apm.lock.yaml`. The lock is generated state: commit it, but never edit
it by hand. `apm_modules/` and harness deployment directories are disposable
and must remain untracked.

The Autogenesis Atlas uses mutable `main` semantics in `.gitmodules` and
`atlas-mesh.json`; the gitlink itself must match the reviewed commit. Updating
the store pointer requires separate store evidence and review.

`discuss@atlas` is a direct external dependency. Do not add a local
`references/paths/discuss.md` adapter or discussion-mode routing to
Autogenesis. Changes identified through a Discuss session must return through
the normal Autogenesis design and approval flow.

## Local checks

Run the focused offline suite first:

```text
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/release_readiness.py
python3 scripts/dependency_contract.py
python3 scripts/store_contract.py
```

With the private read credential configured, register the catalog (required
`--name`; do not use alias `me` or default `atlas-marketplace`), then replay
the exact dependency lock and audit source:

```text
apm marketplace add sergio-sisternes-epam/atlas-marketplace --name atlas
apm lock --no-policy --target agent-skills
python3 scripts/audit_source.py --jobs 8
```

APM 0.30.0 `apm install --frozen` compares marketplace placeholder keys
(`_marketplace/atlas/<name>`) to resolved git lock keys and
cannot validate this manifest. Replay with `apm lock` and require the
committed lock to stay byte-identical.

For the complete consumer checks:

```text
python3 scripts/validate_consumer.py --target agent-skills
python3 scripts/validate_consumer.py --target claude,codex,copilot,cursor,gemini,grok-build,kiro,opencode,windsurf
```

These validators require Autogenesis itself, matching name/version metadata,
source provenance, exact direct dependency locks, stable frozen replay, and a
green APM audit. Transitive dependency skills are expected and permitted.

## Reviewed dependency divergence

Do not remove direct OKF: two Autogenesis modules invoke it directly.
Catalog Atlas v0.11.2 and Discuss v0.3.10 now resolve nested OKF/Atlas through
the same marketplace pins as this root. There are no reviewed graph
divergences. Any new divergence requires an explicit dependency review.

## Release handoff

1. Keep `apm.yml`, `SKILL.md`, both README install commands, the bug-report
   example, the current changelog section, and changelog links on one version.
2. Regenerate `apm.lock.yaml` with APM 0.30.0 only when dependency declarations
   change, then verify every expected commit.
3. Run the local checks and obtain normal review before merge.
4. After merge, manually dispatch **Autogenesis CI** with the exact current
   `main` SHA. Its final stable check must report
   `release_readiness_decision=ready-to-tag`.
5. Hand the exact SHA and matching `vX.Y.Z` name to an authorized maintainer.
   Tag creation/push requires separate approval and must use an annotated tag.
6. The tag workflow verifies the remote object in `refs/release-tags/`, reruns
   reusable CI against the immutable package source, and re-verifies immediately
   before creating the GitHub Release.

Never move, delete, overwrite, or reuse a pushed release tag. Never create a
tag, push, publish a release, change repository settings, or update a global
APM consumer during local preparation.

Protect `main` with the stable CI job names documented in `README.md`, require
current branches and review, and protect `v*` tags against update/deletion.
Repository settings remain an administrator-owned action outside this change.
