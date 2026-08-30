# autogenesis

Private APM package (`SKILL.md` + `apm.yml` at repo root): `sergio-sisternes-epam/autogenesis`

```text
apm install sergio-sisternes-epam/autogenesis
```

Process memory is **not** authored here. Canonical store:

https://github.com/sergio-sisternes-epam/autogenesis-atlas

Git root **is** the OKF root (`SCHEMA.json`). Mount it at `references/atlas` as a git submodule:

```text
atlas mount github.com/sergio-sisternes-epam/autogenesis-atlas --ref main --target references/atlas
```

Mount path = compile/query root: `references/atlas`

See `SKILL.md`.
