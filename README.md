# autogenesis

Private APM package (`SKILL.md` + `apm.yml` at repo root): `sergio-sisternes-epam/autogenesis`

```text
apm install sergio-sisternes-epam/autogenesis
```

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

## Update a global APM consumer

After v0.4.0 has been merged and released, and only with explicit approval:

1. Back up `~/.apm/apm.yml` and `~/.apm/apm.lock.yaml`.
2. Prefer an immutable dependency:
   `sergio-sisternes-epam/autogenesis#v0.4.0`.
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
