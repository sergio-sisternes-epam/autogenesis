# Process memory is not in this package

Do not add `references/atlas/` or any process-memory tree to this repo.

**Remote:** `https://github.com/sergio-sisternes-epam/autogenesis-atlas`

```text
atlas mount github.com/sergio-sisternes-epam/autogenesis-atlas --ref main
```

Default clone path and compile/query root: `.atlas/github.com/sergio-sisternes-epam/autogenesis-atlas`  
OKF root is the git clone root (`SCHEMA.json`), not a nested `atlas/` folder.
