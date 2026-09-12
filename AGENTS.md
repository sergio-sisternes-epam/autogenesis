# Repository instructions

## Package boundary

This repository is one private APM root-skill package. `apm.yml`, `SKILL.md`,
and `references/` are authoritative package source. Do not introduce a
`packages/` tree or marketplace manifest.

## Layout

- `SKILL.md`: root Autogenesis skill and version surface.
- `references/`: module entrypoints, shared resources, scenarios, and
  templates.
- `apm.yml`: package metadata and immutable direct dependency pins. The
  separately versioned `discuss@atlas` dependency is the durable discussion
  mechanism; do not add an Autogenesis `discuss` operation or path proxy.
- `apm.lock.yaml`: committed APM 0.30.0 dependency resolution.
- `.atlas/github.com/sergio-sisternes-epam/autogenesis-atlas`: mutable-main
  store gitlink, checked out at the reviewed commit.
- `atlas-mesh.json` and `.gitmodules`: mutable store identity/configuration.
- `scripts/`: deterministic local and CI release checks.
- `.github/`: pinned CI/release automation and contribution templates.

Autogenesis v0.6.0 has 20 parent-routed modules and no `discuss` operation. The
root `SKILL.md` owns the version surface and module registry; module
arguments cannot override parent-owned subject, mode, operation, work
identity, Atlas, or approval. The removed path surface has no aliases.

`references/modules/patterns/references/parent-routed-skill-module.md` is the
Autogenesis-scoped S8 draft pattern, not a 22nd module. Keep B17 active, Genesis
read-only, and draft application/admission distinct from implementation approval.

S8 is instruction-first for derived skills. Do not turn this repository's
invocation schemas, validators, role metadata or release tooling into required
generated runtime. Keep generic review conditional on the target's declared
architecture and integrations. The optional module template is a passive
authoring resource, not a new export. Domain scripts and explicitly approved
full fusion remain valid.

Autogenesis has no external evaluator dependency. Current scenarios are
portable specifications; run applicable commands with repository tools and
record actual evidence. GitHub CI remains the final release gate.

## Generated state

Commit `apm.lock.yaml`. Never commit `apm_modules/` or disposable harness
deployments such as `.agents/`, `.claude/`, `.grok/`, or `.kiro/`. Regenerate
the lock only with the pinned APM CLI after an intentional manifest change.
Do not hand-edit generated lock entries.

## Validation

Run `python3 -m unittest discover -s scripts -p 'test_*.py'` first with a
Python 3.12 interpreter (`python3.12`, or `python3` if it reports 3.12). For
release-sensitive work, follow `CONTRIBUTING.md`; local checks can use an
existing `gh` login or other read-only GitHub credential with repository
Contents access. The CI convention uses `APM_READ_TOKEN` and fails closed
when it is absent. Do not expose normal `gh` credentials in logs or files. Do
not suppress the two documented dependency anchor warnings, and do not accept
additional warnings without review.

Do not create, move, delete, or push tags; publish releases; change repository
settings; or update global APM consumers as part of local release preparation.
