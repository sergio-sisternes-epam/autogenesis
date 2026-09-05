---
name: autogenesis/paths/atlas-migrate
description: Migrate a subject from a legacy references/atlas mount to the repository-local .atlas/<id> write-home using Atlas migrate, then optionally ingest a legacy okf-wiki into the resolved subject Atlas. Preserves claims, relationships, compile gates, and discipline.
path_id: atlas-migrate
default: false
subject_scope: subject-atlas
---

# Path: atlas-migrate

## Enter

Activation card must show `path: atlas-migrate`, an `atlas_id`, and this file
read.

```text
skill: autogenesis
skill_path: <resolved Autogenesis skill root>
mode: run
subject: <skill under migration>
path: atlas-migrate
path_module: references/paths/atlas-migrate.md
intent: relocate <subject> Atlas storage and optionally ingest legacy okf-wiki
atlas_id: <host/org/repo>
```

Optional user input: a legacy okf-wiki source override. The default content
source is `<subject>/references/wiki/` only when that directory exists.

## Purpose

Compose two distinct operations without confusing their ownership:

1. **Storage-location migration (required when legacy mount exists):** Atlas
   path `migrate` moves the subject store from the forbidden
   `<subject>/references/atlas` location to the default
   `<active-git-root>/.atlas/<atlas_id>` mount.
2. **Legacy-content intake (optional):** Atlas CLI `migrate` stages an
   okf-wiki source into the already resolved subject Atlas; Autogenesis owns
   claim conversion, relationship review, and discipline rewrite.

Atlas owns mount, resolve, storage migration, intake, promote, and compile.
This path does not reimplement those mechanics.

## Pins (normative)

1. Require the active subject git root and explicit `atlas_id`. Do not infer
   from multiple mesh rows.
2. Apply the multi-harness substrate contract to Atlas and load its `migrate`
   path before relocating a legacy mount.
3. Mount with no `--target`, then obtain `subject_atlas` only from
   `atlas resolve <atlas_id>`.
4. A migration is single-writer: no symlink, copy, dual-write, or fallback at
   `references/atlas`.
5. Legacy okf-wiki intake is optional and starts only after the new root
   resolves and contains `SCHEMA.json`.
6. Every staged content file becomes a claim-bearing page under
   `autogenesis/` before Exit; no bulk defer.
7. Thorough relationship review is mandatory after claim conversion. Exit is
   incomplete while pages have only generic migration links.
8. Compile must exit 0 with staging empty before discipline rewrite is
   complete.

## Procedure

### 1. Resolve subject and migration inputs

- Require `subject`, active subject git root, and canonical `atlas_id`.
- Inspect `atlas-mesh.json`, `.gitmodules`, and the git index.
- If a legacy `references/atlas` gitlink exists, its remote identity must
  normalize to `atlas_id`; identity mismatch stops migration.
- If neither a legacy mount nor an optional wiki source exists, report
  `n/a: nothing to migrate`. Do not mutate storage.

### 2. Relocate the Atlas mount

Apply the substrate contract to skill **atlas**, emit its `path: migrate`
card, read `references/paths/migrate.md`, and follow it exactly.

The resulting repository state must satisfy all of these:

- tracked gitlink:
  `.atlas/<host>/<org>/<repo>`;
- `.gitmodules` path equals that gitlink;
- `atlas-mesh.json` row for `atlas_id` has the same path and ref;
- `.gitignore` does not hide `.atlas/`;
- no tracked gitlink remains at `references/atlas`.

Then load Atlas path `mount` and run mount with no `--target`. Set
`subject_atlas` only from:

```text
python3 <atlas-skill>/scripts/atlas.py resolve <atlas_id>
```

Verify `<subject_atlas>/SCHEMA.json`. A dirty existing checkout, mismatched
origin, failed mount/resolve, or missing schema stops the Run.

### 3. Optional legacy okf-wiki intake

If the user supplied a source override, require it to exist. Otherwise use
`<subject>/references/wiki/` only when present.

No source means skip directly to step 6. A source means:

```text
python3 <atlas-skill>/scripts/atlas.py migrate <source> --root <subject_atlas>
```

Staging will be non-empty and compile must fail until claim conversion
finishes.

### 4. Claim conversion

For each staged content file:

| Source kind | Target under subject Atlas |
|-------------|----------------------------|
| knowledge / durable normative pages | `autogenesis/decisions/<name>.md` (`type: decision`) |
| raw experiences / run records | `autogenesis/experiences/<name>.md` (`type: experience`) |
| formal design packets | `autogenesis/plans/<work_id>.md` (`type: plan`) |
| work hubs | `autogenesis/work/<work_id>.md` (`type: work`) |

Use Atlas `promote` followed by claim completion, or write through Atlas
`remember` when that path allows direct claim authoring. Every page needs
type-correct frontmatter and authoritative `relates_to` edges. Create missing
work hubs so `implements` edges resolve.

Remove structural/non-concept staging files only after recording one migration
experience that lists them as non-claim intake. Do not leave content only in
staging.

### 5. Thorough relationship review

Before final compile:

1. Query or inspect the newly claimed pages.
2. Ensure every decision has at least one incoming edge from an experience or
   work hub.
3. Link experiences to the decisions they realize.
4. Reject pages whose only relationship is a generic migration self-link.
5. Surface the proposed mesh for confirmation or record an explicit waiver.
6. Record `relationship_review: yes` and `quality_edges_added: N`.

### 6. Compile gate

```text
python3 <atlas-skill>/scripts/atlas.py compile --root <subject_atlas>
```

Exit code must be 0 and staging must be empty. Existing store warnings remain
blocking; do not report them as green or silently narrow the gate.

### 7. Discipline rewrite

After compile green, update only the subject package:

- primary process memory uses its repository's resolved Atlas root;
- plan home remains `autogenesis/plans/<work_id>.md`;
- cards and receipts carry `atlas_id` and the resolved `atlas_root`;
- okf-wiki is legacy read-only when retained;
- no live instruction points to `<skill>/references/atlas`;
- all Atlas query, remember, work, and compile calls receive the resolved root.

If the rewrite cannot be completed safely, record
`discipline_rewrite: deferred: <reason>`. Storage migration is not permission
to mutate peer packages.

### 8. Lineage Exit

- Write an implementation experience with `## Changed files`.
- Update the canonical work hub for this Run.
- Append `log.md` only for structural store changes.
- Emit the receipt below.

## Path receipt

```text
skill: autogenesis
skill_path: <resolved Autogenesis skill root>
subject: <subject>
path: atlas-migrate
atlas_id: <host/org/repo>
source: <legacy wiki path | none>
atlas_root: <resolved path from atlas resolve>
autogenesis_space: autogenesis/
storage_relocated: yes | n/a
promoted_count: N
staging_empty: yes
relationship_review: yes | n/a | waived: <reason>
quality_edges_added: N
compile: yes
discipline_rewrite: yes | deferred: <reason>
nested_skills_loaded: atlas [, okf]
substrate_contract: applied
Enter|Change|Exit: pass | incomplete: <cluster>
```

## Gates

| Gate | Requirement |
|------|-------------|
| Enter | subject + atlas_id + active git root + this module read |
| Change | Atlas migrate path used for legacy mount; optional intake fully claimed and relationship-reviewed |
| Exit | one resolved write-home, no legacy gitlink, staging empty, compile green, lineage experience, discipline rewrite or explicit defer |

## Non-goals

- Replacing Atlas CLI or path modules
- Creating repositories
- Silent peer mutation
- Compatibility symlink, copy, dual-write, or fallback
- Claiming success with non-empty staging or compile warnings
- Auto-deleting `references/wiki/` without explicit human approval

## Consistency

`workflow-discipline.md` remains the sole source of Enter/Change/Exit and
subject-Atlas resolution rules. The matching `SKILL.md` registry stub must
describe this storage-first migration.
