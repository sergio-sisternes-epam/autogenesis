# autogenesis

Private APM package (`SKILL.md` + `apm.yml` at repo root): `sergio-sisternes-epam/autogenesis`

```text
apm install sergio-sisternes-epam/autogenesis
```

Process memory is **not** in this repo. Do not add `references/atlas/` here. Canonical store:

https://github.com/sergio-sisternes-epam/autogenesis-atlas

OKF root is the git clone root (`SCHEMA.json`), not a nested `atlas/` folder.

```text
atlas mount github.com/sergio-sisternes-epam/autogenesis-atlas --ref main
```

Default clone path and compile/query root: `.atlas/github.com/sergio-sisternes-epam/autogenesis-atlas`

See `SKILL.md`.
