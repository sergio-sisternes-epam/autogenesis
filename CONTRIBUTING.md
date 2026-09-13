# Contributing

## Prerequisites

| Tool | Required version | Purpose |
|---|---|---|
| Git | 2.x | Source and gitlink verification |
| Python | 3.12 | Repository-owned checks |
| APM CLI | 0.30.0 (`8c2e0d9`) | Frozen install and audit |

Use any available Python 3.12 interpreter (`python3.12` if installed, or the
default `python3` when it reports 3.12). Public github.com consumers do not
need a personal access token for public catalog and package sources. This
repository's consumer CI jobs still require `APM_READ_TOKEN` as a workflow
secret and fail closed when that secret is absent; those jobs are not
anonymous.

```text
python3 - <<'PY'
import sys
print(sys.version)
PY
```

Never print, persist, or commit credentials. Do not expose normal `gh`
credentials in logs or files.

## Issues and pull requests

Use the GitHub issue templates in `.github/ISSUE_TEMPLATE/` for bugs and
feature requests. Do not file public issues for vulnerabilities; report them
through a
[private GitHub security advisory](https://github.com/sergio-sisternes-epam/autogenesis/security/advisories/new).

External substantive work needs a linked issue first. Maintainer-authored
small docs or maintenance may skip that wait. Open pull requests with
`.github/PULL_REQUEST_TEMPLATE.md`. Confirm human scope approval before agent
implementation, except for maintainer-authored small docs or maintenance. The
GitHub author owns the change, including any agent-generated diffs, and must
not open the pull request as an unattended GitHub author.

## Repository contract

The package root contains `SKILL.md` and `apm.yml`. Direct dependency refs in
`apm.yml` are marketplace objects (`name` + `marketplace:
atlas`). APM 0.30.0 rejects `package@marketplace` string
shorthand in the manifest (it is parsed as an unsupported alias). Catalog
entries resolve to released tags, and their exact resolutions are committed
in `apm.lock.yaml`. The lock is generated state: commit it, but never edit
it by hand. `apm_modules/` and harness deployment directories are disposable
and must remain untracked.

Autogenesis v0.8.0 has 22 parent-routed modules and no `discuss` operation.
Think support modules nest-load catalog `think@atlas`; they do not vendor
forked think procedure. The root `SKILL.md` owns the version surface and
module registry. Module
arguments cannot override parent-owned subject, mode, operation, work
identity, Atlas, or approval, and the removed path surface has no aliases.

The Autogenesis Atlas uses mutable `main` semantics in `.gitmodules` and
`atlas-mesh.json`; the gitlink itself must match the reviewed commit. Updating
the store pointer requires separate store evidence and review.

`discuss@atlas` is a direct external dependency. Do not add a local
`references/modules/discuss/SKILL.md` or `references/paths/discuss.md` adapter
or discussion-mode routing to Autogenesis. Changes identified through a
Discuss session must return through the normal Autogenesis design and
approval flow.

## Local checks

Run the focused offline suite first with a Python 3.12 interpreter:

```text
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/release_readiness.py
python3 scripts/dependency_contract.py
python3 scripts/store_contract.py
```

Register the catalog (required `--name`; do not use alias `me` or default
`atlas-marketplace`), then replay the exact dependency lock and audit
source. CI consumer jobs inject `APM_READ_TOKEN` for that registration and
install path:

```text
apm marketplace add sergio-sisternes-epam/atlas-marketplace --name atlas
apm lock --no-policy --target agent-skills
python3 scripts/audit_source.py --jobs 8
```

APM 0.30.0 `apm install --frozen` compares marketplace placeholder keys
(`_marketplace/atlas/<name>`) to resolved git lock keys and
cannot validate this manifest. Replay with `apm lock` and require the
committed lock to stay byte-identical.

For the complete consumer checks:

```text
python3 scripts/validate_consumer.py --target agent-skills
python3 scripts/validate_consumer.py --target claude,codex,copilot,cursor,gemini,grok-build,kiro,opencode,windsurf
```

These validators require Autogenesis itself, matching name/version metadata,
source provenance, exact direct dependency locks, stable frozen replay, and a
green APM audit. Transitive dependency skills are expected and permitted.
They also reject extra Autogenesis-owned exports and missing or altered nested
assets, repeating ownership/content validation after frozen replay. Legitimate
APM link transformations are constrained, not treated as arbitrary text drift.

Module behavior is governed by the root router, module instructions and their
linked contract. Do not introduce a generic runtime validator solely to enforce
instruction-level routing. Use actual tool/file evidence for behavioural
claims. Current suites come from
`references/scenarios/suite-index.json`; never rewrite historical suite bodies.
Local checks support implementation; final acceptance is GitHub CI, including
the pinned Linux APM artifact and both consumer profiles.

S8 (`autogenesis:S8`) is a draft pattern resource, not a new module export.
Keep applicability reasons and draft/active admission explicit in design and
review guidance. Known-use entries need actual evidence; do not count the
21 leaves of one package as independent adoptions. Pattern changes must preserve
B17 and the single invocation authority. New scenario suites extend the current
index without rewriting existing YAML bodies.
Scenario files are evaluator-neutral specifications. Execute applicable
commands through tools already available in the repository and retain actual
output; no separate evaluator is required. GitHub CI remains the final
release gate.

The invocation authority and repository checks above govern Autogenesis, not
all S8 adopters. Preserve the instruction-first boundary in design, initialise,
templates and review facets: no mandatory generated framework or validator.
Evaluate representative derived outputs as well as this repository's source.
Keep fixtures and their evidence out of generated runtime bundles; report
unavailable live evaluation explicitly rather than treating source checks as
proof of agent behavior.

Formal designs apply
`references/skill-design-principles.md` after Genesis. New-surface and
new-skill plans require the full five-row applicable / not-applicable /
trade-off record; hardening may abbreviate the assessment to material
principles. Review meaning through plans, scenarios and actual design evidence.
The Python source-contract tests enforce only the shared authority's presence
and resolvable Markdown linkage. Portable scenario smokes additionally assert
the stable OCP/LSP, approval, prospective-adoption and no-machinery guidance;
neither proves semantic design quality. Do not add semantic validators or force
modularization.

## Reviewed dependency divergence

Do not remove direct OKF: two Autogenesis modules invoke it directly.
Catalog Atlas v0.11.2 and Discuss v0.3.10 now resolve nested OKF/Atlas through
the same marketplace pins as this root. There are no reviewed graph
divergences. Any new divergence requires an explicit dependency review.

Released pins from `apm.lock.yaml`:

| Direct package | Released pin | Resolved commit |
|---|---|---|
| Atlas | `v0.11.2` | `579e8090273ce991ea0717abed0775dc03f28de2` |
| OKF | `v0.2.1` | `5246f7b193b58a32ac8a15fc76aedf37c42b042c` |
| Discuss | `v0.3.10` | `c1c0936d9a0346dce7d877646046c918de335d69` |
| Think | `v0.1.0` | `874613a67018c74ee95f857416fb315d2f80b92b` |

## Consumer version pins

The public README documents only the Atlas marketplace install. Git-tag
and target-specific consumer commands stay here.

Keep these commands on the same version as `apm.yml`:

```text
apm install sergio-sisternes-epam/autogenesis#v0.8.0 --target agent-skills
```

```text
apm install sergio-sisternes-epam/autogenesis#v0.8.0 --target claude,codex,copilot,cursor,gemini,grok-build,kiro,opencode,windsurf
```

Do not update any global consumer yet. After a release, and only with
explicit approval, prefer an immutable dependency:
  `sergio-sisternes-epam/autogenesis#v0.8.0`.

## Release handoff

1. Keep `apm.yml`, `SKILL.md`, both consumer version-pin install commands
   above, the bug-report example, the current changelog section, and
   changelog links on one version.
2. Regenerate `apm.lock.yaml` with APM 0.30.0 only when dependency declarations
   change, then verify every expected commit.
3. Run the local checks and obtain normal review before merge.
4. After merge, manually dispatch **Autogenesis CI** with the exact current
   `main` SHA. Its final stable check must report
   `release_readiness_decision=ready-to-tag`.
5. Hand the exact SHA and matching `vX.Y.Z` name to an authorized maintainer.
   Tag creation/push requires separate approval and must use an annotated tag.
6. The tag workflow verifies the remote object in `refs/release-tags/`, reruns
   reusable CI against the immutable package source, and re-verifies immediately
   before creating the GitHub Release.

Never move, delete, overwrite, or reuse a pushed release tag. Never create a
tag, push, publish a release, change repository settings, or update a global
APM consumer during local preparation.

The stable required-check names are **Release metadata**, **APM source
integrity**, **Frozen dependency graph**, **Atlas store validation**,
**Consumer install (agent-skills)**, **Consumer install (stable-runtimes)**,
and **Release readiness decision**. Protect `main` with those names, require
current branches and review, and protect `v*` tags against update/deletion.
Repository settings remain an administrator-owned action outside this change.
