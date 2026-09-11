# Atlas store lives in its own repository

## Module and resource layout

`modules/<name>/SKILL.md` is a parent-routed operation or support entrypoint.
Only the root Autogenesis skill is a catalogue export. Module-local resources
resolve from that module's directory; shared resources resolve from the loaded
skill root, never the shell cwd. The root registry selects siblings.
Invocation/card/receipt rules live in `modules/workflow-discipline/SKILL.md`
and its `references/` directory. Passive pattern definitions live in
`modules/patterns/references/`; they are not modules.

Current scenarios are selected by `scenarios/suite-index.json`. Historical
bodies remain available for provenance, not current acceptance.

## Derived-skill guidance

S8 and its optional `modules/patterns/references/skill-module-template.md`
describe instruction-first private modules. They do not require adopters to
copy Autogenesis's workflow, JSON protocol, validators or runtime Atlas.
Use modules only when useful and scripts only when the task warrants them.
Shared run/work templates record authoring, not mandatory generated runtime.

## Process memory

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
