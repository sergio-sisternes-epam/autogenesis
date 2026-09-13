# Bundled help topics

Packaged baseline for Autogenesis **v0.7.0**. These names are **not**
parent-registry modules. Resolve `target` here only after it fails to match
a registry module name. Aliases map to the canonical topic name.

| Topic | Aliases | Answers from this baseline |
| --- | --- | --- |
| discussion | discuss, catalog-discuss | Durable discussion is catalog `discuss@atlas`, not an Autogenesis module. Autogenesis has no `discuss` operation. Discussion does not implement. |
| approval | approve, stop | Design and initialise stop for explicit human approval. Implement applies only an approved persisted plan. A requested card is not approval. |
| install | marketplace | Public consumers install `autogenesis@atlas` from the Atlas marketplace. Do not document git-tag install here. |
| first-use | onboarding, overview | Purpose, prerequisites, and the shortest useful first journey. Point to the `getting-started` operation; do not run it from help. |

Do not invent extra topics. If `target` matches none of these names or
aliases and is not a registry module, it is unknown.

Discussion vs design vs implement, and the approval stop, are also covered
by getting-started's first-journey baseline.
