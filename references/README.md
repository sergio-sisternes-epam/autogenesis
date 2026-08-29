# Process memory is not in this package

Do not add `references/atlas/` or any process-memory tree to this repo.

**Remote:** `https://github.com/sergio-sisternes-epam/autogenesis-atlas`

```text
atlas mount github.com/sergio-sisternes-epam/autogenesis-atlas --ref main
```

Default clone path: `.atlas/github.com/sergio-sisternes-epam/autogenesis-atlas`  
OKF root is `atlas/` inside the store repo (`atlas/SCHEMA.json`), not git root.  
Compile/query root: `.atlas/github.com/sergio-sisternes-epam/autogenesis-atlas/atlas`
