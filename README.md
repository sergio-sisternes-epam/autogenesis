# Autogenesis

Autogenesis is a skill-design discipline for designing, evolving, reviewing, and implementing agent skill packages from durable experience.

## Why / what this is not

Autogenesis extends the Genesis design process with Atlas-backed experience and parent-routed operations. Design produces a challenged, persisted plan and stops for explicit approval; implementation applies only an approved plan. Discussion does not implement. Autogenesis is not for ordinary application refactoring and does not auto-implement from reflection.

## Modules

| Module | What you get |
| --- | --- |
| `design` | Design a skill change through Genesis and stop for approval. |
| `initialise` | Confirm a skill's purpose and initialise it; stop for approval. |
| `implement` | Apply an explicitly approved persisted plan. |
| `research` | Expand the subject Atlas with sourced knowledge. |
| `review-package` | Review package composition and applicable conformance. |
| `reflect-challenge` | Challenge observed behavior without implementation authority. |
| `learn-skill` | Record peer skill usage without mutating the peer. |
| `reevaluate` | Assess material knowledge impact; advisory only. |
| `aware-runtime` | Maintain governed runtime awareness. |
| `wire` | Record approved wiring with version provenance. |
| `atlas-migrate` | Migrate legacy Atlas storage and preserve knowledge. |
| `help` | Explain Autogenesis modules without executing them. |
| `getting-started` | Explain purpose, prerequisites, and a first journey. |

These are the public operations; support and validation procedures are internal modules.

## Install

```bash
apm marketplace add sergio-sisternes-epam/atlas-marketplace --name atlas
apm install autogenesis@atlas
```

## Use

- `/autogenesis Design a change to <skill> that <objective>.`
- `/autogenesis Review the composition and conformance of <package>.`
- `/autogenesis Help me get started with Autogenesis.`

Design stops for explicit approval before implementation. For a live durable discussion, activate the catalog `discuss` package directly.

## Prerequisites

Autogenesis uses Atlas as its durable subject store for design plans and process memory. Its APM manifest declares dependencies on `atlas`, `okf`, `discuss`, and `think`.

## Related

- [Atlas marketplace](https://github.com/sergio-sisternes-epam/atlas-marketplace) — package catalog.
- [`atlas`](https://github.com/sergio-sisternes-epam/atlas) — durable knowledge substrate.
- [`okf`](https://github.com/sergio-sisternes-epam/okf) — Open Knowledge Format.
- [`discuss`](https://github.com/sergio-sisternes-epam/discuss) — durable discussion; activate it directly.
- [`think`](https://github.com/sergio-sisternes-epam/think) — capture, question, and challenge thinking.
- [`SKILL.md`](SKILL.md) — operation routing and approval boundaries.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for local checks and release handoff. Report vulnerabilities through a [private GitHub security advisory](https://github.com/sergio-sisternes-epam/autogenesis/security/advisories/new).

## License

Autogenesis is licensed under the [Apache License 2.0](LICENSE), as declared in `apm.yml`. The Genesis repository code it builds on is Apache-2.0; the Genesis book is a separate work licensed under CC BY-NC 4.0, which does not apply to the code or to Autogenesis. See [`NOTICE`](NOTICE) for attribution.
