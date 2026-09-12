# Repository instructions

## Package boundary

This repository is one private APM root-skill package. `apm.yml`, `SKILL.md`,
and `references/` are authoritative package source. Do not introduce a
`packages/` tree or marketplace manifest.

## Layout

- `SKILL.md`: root Autogenesis skill and version surface.
- `references/`: skill-relative path modules, internal modules, scenarios, and
  templates.
- `apm.yml`: package metadata and immutable direct dependency pins. The
  separately versioned `discuss@atlas` dependency is the durable discussion
  mechanism; do not add an Autogenesis discussion-path proxy.
- `apm.lock.yaml`: committed APM 0.30.0 dependency resolution.
- `.atlas/github.com/sergio-sisternes-epam/autogenesis-atlas`: mutable-main
  store gitlink, checked out at the reviewed commit.
- `atlas-mesh.json` and `.gitmodules`: mutable store identity/configuration.
- `scripts/`: deterministic local and CI release checks.
- `.github/`: pinned CI/release automation and contribution templates.

## Generated state

Commit `apm.lock.yaml`. Never commit `apm_modules/` or disposable harness
deployments such as `.agents/`, `.claude/`, `.grok/`, or `.kiro/`. Regenerate
the lock only with the pinned APM CLI after an intentional manifest change.
Do not hand-edit generated lock entries.

## Validation

Run `python3 -m unittest discover -s scripts -p 'test_*.py'` first. For
release-sensitive work, follow `CONTRIBUTING.md`; private dependency and store
reads require `APM_READ_TOKEN`. Do not suppress the two documented dependency
anchor warnings, and do not accept additional warnings without review.

Do not create, move, delete, or push tags; publish releases; change repository
settings; or update global APM consumers as part of local release preparation.
