# SOLID dogfood comparative exercises

Maintainer-scope design records for Autogenesis self-dogfood of the skill-native
SOLID lens. These are contributor scenario evidence, not a public skill, private
module, runtime schema, or validator.

Loaded skill under test is the workspace checkout `SKILL.md`. Catalog Autogenesis
v0.4.3 is not evidence.

## Root-only skill

Subject: a short changelog-format helper with one user-facing job.

named-design-consequence: keep-root

| Principle | Status | Rationale / design consequence |
|---|---|---|
| S | applicable | One cohesive job: rewrite Keep a Changelog fragments. No second caller or ownership boundary. |
| O | applicable | Format-rule changes stay reviewed and versioned (`governed-change`); do not invent a plugin slot. |
| L | not-applicable | No interchangeable changelog skill is claimed, so substitution is not assessed. |
| I | applicable | Callers need the single `SKILL.md` procedure, not a module tree. |
| D | trade-off | Host editor tools are incidental; do not add an editor adapter (`no-adapter` pressure is insufficient). |

Lens decision: keep the skill root-only. Splitting would be speculative structure.

## Multi-procedure skill

Subject: one package that authors release notes, publishes GitHub releases, and
files support tickets. Three callers and three change cadences.

named-design-consequence: split

| Principle | Status | Rationale / design consequence |
|---|---|---|
| S | applicable | Notes, publish, and tickets change for different reasons. Keep one public skill only if private procedures hide the split; otherwise split the public surface. |
| O | applicable | After the split, each procedure can take a governed, versioned contract change without dragging the others. |
| L | not-applicable | The procedures do not claim to substitute for one another. |
| I | applicable | A notes author must not load publish credentials or ticket tools. |
| D | trade-off | GitHub publish coupling belongs with the publish procedure only; do not share that provider across notes authoring. |

Lens decision: split along the caller and cadence boundaries (instruction-only
private modules, or separate skills if they need independent release). Do not
keep an undivided root that mixes unrelated tools.

## Provider-coupled skill

Subject: GitHub-only issue triage that shells out to `gh`.

named-design-consequence: no-adapter

| Principle | Status | Rationale / design consequence |
|---|---|---|
| S | applicable | One user-facing job: triage GitHub issues. |
| O | applicable | When the `gh` issue contract changes, version this skill (`governed-change`). |
| L | not-applicable | This skill does not claim to replace Jira or GitLab triage skills. |
| I | applicable | Callers see GitHub issue fields and `gh` outcomes, not a generic host matrix. |
| D | trade-off | The concrete `gh` dependency is in scope; there is no second Git host, so an adapter would be speculative. |

Lens decision: keep the provider coupling and add no Git-host adapter.
