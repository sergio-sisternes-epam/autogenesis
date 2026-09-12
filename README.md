# autogenesis

Grows a skillset from durable experience. Core design process is Genesis;
memory via Atlas.

## Why / what this is not

Autogenesis is a root APM skill (`SKILL.md` + `apm.yml` at the repository
root). Use it to evolve, design, review, or initialise agent skills from
durable experience. Genesis remains the design process; Autogenesis fuses
and extends it. Derived skills receive the runtime capabilities their
purpose needs, not an Autogenesis framework by default. Design stops for
explicit approval. Discussion does not implement.

Do not use it for ordinary application refactoring, automatic wiring, or
direct module discovery. It does not supersede Genesis, auto-implement from
reflection, or author process memory into the installed skill package.

## Install

```bash
apm marketplace add sergio-sisternes-epam/atlas-marketplace --name atlas
apm install autogenesis@atlas
```

Optional immutable git-tag install:

```bash
apm install sergio-sisternes-epam/autogenesis#v0.6.0
```

Autogenesis is validated with APM CLI 0.30.0 (`8c2e0d9`).

## Use

```text
Use autogenesis to design: <objective>
```

Procedures and invocation rules live in `SKILL.md`.

## Modules

| Module | Summary |
|---|---|
| design | Design a skill change through Genesis; stop for approval |
| initialise | Confirm purpose and initialise a skill; stop for approval |
| implement | Apply only an explicitly approved persisted plan |
| research | Expand the subject Atlas with sourced knowledge |
| review-package | Review a package's composition and applicable conformance |
| reflect-challenge | Challenge observed behaviour without implementing |
| learn-skill | Record peer skill usage without mutating the peer |
| atlas-migrate | Migrate legacy Atlas storage and preserve knowledge |

Support, validation, and think helpers stay in `references/modules/`.

## Related

- [atlas](https://github.com/sergio-sisternes-epam/atlas) — durable knowledge substrate
- [okf](https://github.com/sergio-sisternes-epam/okf) — Open Knowledge Format
- [discuss](https://github.com/sergio-sisternes-epam/discuss) — durable discussion; activate the catalog Discuss package directly
- [think](https://github.com/sergio-sisternes-epam/think) — ramble, grill, and challenge
- Companion store: [autogenesis-atlas](https://github.com/sergio-sisternes-epam/autogenesis-atlas)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for local checks and release handoff.
Report vulnerabilities through a
[private GitHub security advisory](https://github.com/sergio-sisternes-epam/autogenesis/security/advisories/new).

## License

Autogenesis is Copyright 2026 Sergio Sisternes and is licensed under the
[Apache License 2.0](LICENSE), as declared in `apm.yml`.

Autogenesis integrates with and builds upon concepts from
[Genesis](https://github.com/danielmeppiel/genesis), Copyright 2025 Daniel
Meppiel. The Genesis repository code is licensed under Apache-2.0. Its
long-form book is a separate work licensed under CC BY-NC 4.0; that book
license does not apply to the Genesis repository code or to Autogenesis.
See [NOTICE](NOTICE) for the preserved attribution.
