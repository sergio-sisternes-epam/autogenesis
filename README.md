# autogenesis

Private APM package (`SKILL.md` + `apm.yml` at repo root): `sergio-sisternes-epam/autogenesis`

```text
apm install sergio-sisternes-epam/autogenesis
```

Process memory is **not** in this repo. Do not add `references/atlas/` here. Canonical store:

https://github.com/sergio-sisternes-epam/autogenesis-atlas

OKF root inside that repo is `atlas/` (`atlas/SCHEMA.json`), not git root.

```text
atlas mount github.com/sergio-sisternes-epam/autogenesis-atlas --ref main
```

Default clone path: `.atlas/github.com/sergio-sisternes-epam/autogenesis-atlas`  
Compile/query root: `.atlas/github.com/sergio-sisternes-epam/autogenesis-atlas/atlas`

See `SKILL.md`.
