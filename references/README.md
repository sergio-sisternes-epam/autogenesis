# Atlas store lives in its own repository

This skill's process memory is **not** authored in the installed package. In
the active Autogenesis source repository, it is mounted from
`autogenesis-atlas` at the Atlas default repository-local path.

**Remote:** `https://github.com/sergio-sisternes-epam/autogenesis-atlas`

On a machine with git and Atlas CLI:

```text
atlas auth login --host github.com
python3 <atlas-skill>/scripts/atlas.py mount github.com/sergio-sisternes-epam/autogenesis-atlas --ref main
python3 <atlas-skill>/scripts/atlas.py resolve github.com/sergio-sisternes-epam/autogenesis-atlas
```

Default mount and compile/query root:
`.atlas/github.com/sergio-sisternes-epam/autogenesis-atlas`.

Other subjects use the Atlas declared by their active git repository. Never
mount or write process memory inside a skill package.
Git root of the store **is** the OKF root (`SCHEMA.json`).
