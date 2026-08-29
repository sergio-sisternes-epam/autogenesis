---
name: autogenesis/paths/atlas-migrate
description: Migrate a subject’s legacy okf-wiki (or override path) into the subject Atlas Autogenesis space using atlas CLI migrate/promote/compile as the mechanical core. Autodiscover wiki; auto-initiate Atlas if missing; full claim conversion; then rewrite subject discipline to Atlas-only. Extends atlas migrate — does not replace the CLI.
path_id: atlas-migrate
default: false
subject_scope: subject-atlas
---

# Path: atlas-migrate

## Enter

Activation card must show `path: atlas-migrate` and this file must have been read.

```text
mode: run
subject: <skill under migration>
path: atlas-migrate
path_module: references/paths/atlas-migrate.md
intent: migrate <subject> process memory into Atlas Autogenesis space
```

Optional user input: **source override** (path to legacy store). Default source = `<subject>/references/wiki/`.

## Purpose

Package the discipline learned from Autogenesis self-migration: atlas CLI performs mechanical copy/scaffold/compile; this path owns subject resolution, Autogenesis space layout, claim policy, staging emptiness, and post-migrate discipline rewrite.

**Boundary:** skill **atlas** owns `migrate` / `promote` / `compile`. This path does not reimplement copy logic.

## Pins (normative)

1. Autodiscover okf-wiki; default `<subject>/references/wiki/`; honor explicit source override.
2. No subject Atlas → **auto-initiate** minimal Atlas including full `autogenesis/` tree (SCHEMA `autogenesis_space.initiate_includes`); stop only on bootstrap failure.
3. **Every** staged content file becomes a claim-bearing page under `autogenesis/` before Exit (no bulk defer).
4. **Thorough relationship review (mandatory, non-skippable):** after claim conversion and before final compile, perform a structured analysis of relationships among the newly claimed pages. Produce quality `relates_to` edges that meet the minimum quality bar. Surface a short summary for user confirmation (or explicit waiver with recorded reason). Path receipt must record `relationship_review: yes` and `quality_edges_added: N`. Exit is incomplete while only generic self-referential migration links exist.
5. After compile green → rewrite subject discipline (Atlas-only memory + plan home `autogenesis/plans/<work_id>.md`).
6. Ship against current atlas CLI (no dependency on dry-run/batch CLI work).
7. path_id is **`atlas-migrate`**.

## Procedure

### 1. Resolve subject and source

- `subject` from Enter card (required).
- `source` = user override if provided, else `<subject>/references/wiki/`.
- If default source missing and no override → report gap; do not invent a source.
- If override missing on disk → `incomplete: source not found`.

### 2. Resolve / initiate subject Atlas

- `subject_atlas = <subject>/references/atlas/`
- If `SCHEMA.json` present → use it; ensure `autogenesis/{experiences,decisions,work,plans}/` exist (create indexes if missing).
- If missing → **auto-initiate**:
  - SCHEMA with `autogenesis_space` (copy pattern from autogenesis skill Atlas SCHEMA 1.2+ as template)
  - `autogenesis/` tree per initiate_includes
  - root `templates/` (experience, decision, work, plan)
  - empty `staging/`, `index.md`, `log.md`
- Bootstrap failure → stop; inform user; do not migrate.

### 3. Mechanical intake (atlas CLI)

Apply multi-harness substrate contract to skill **atlas**.

```bash
python3 <atlas-skill>/scripts/atlas.py migrate <source> --root <subject_atlas>
```

Staging will be non-empty; compile must fail until step 5 completes.

### 4. Claim conversion (agent — required)

For each staged **content** file (skip pure infrastructure if it is not claim-bearing: e.g. binary sidecars already handled; still clear all staging before Exit):

| Source kind | Target under subject Atlas |
|-------------|----------------------------|
| knowledge / durable normative pages | `autogenesis/decisions/<name>.md` · `type: decision` |
| raw experiences / run records | `autogenesis/experiences/<name>.md` · `type: experience` |
| formal design packets | `autogenesis/plans/<work_id>.md` · `type: plan` |
| work hubs | `autogenesis/work/<work_id>.md` · `type: work` |

For each page:

1. Prefer `atlas promote <staging-file> --to <target> --type <type> --root <subject_atlas>` then **complete claims** (promote is scaffold-only unless CLI gains `--carry-body`).
2. Or write the claim-bearing page directly (allowed by atlas remember path).
3. Required: type-correct frontmatter, required sections per SCHEMA, `relates_to` with **`autogenesis/…` paths only** for Autogenesis-authored edges.
4. Create missing `autogenesis/work/<work_id>.md` hubs so `implements` edges resolve.
5. Do not leave content only in staging.

**Structural / non-concept staging files** (legacy SCHEMA.md, log journals, quality JSON, `.gitkeep`): remove from staging after recording a single migration experience that lists them as non-claim intake; they must not block compile.

### 5. Thorough relationship review (mandatory, non-skippable)

After claim conversion and before the final compile:

1. Perform a structured analysis of the newly claimed pages (decisions, experiences, plans, work hubs). Use Atlas query (or direct inspection) to identify missing or weak relationships.
2. Propose quality `relates_to` edges that meet the **minimum quality bar**:
   - Every decision page has ≥1 incoming edge from an experience or work hub (`implements`, `derived_from`, or `related`).
   - Experiences that clearly realise a decision name that decision in `relates_to`.
   - No claim-bearing page may leave Exit with *only* a self-referential link back to the migration experience.
3. Surface a short human-readable summary of the proposed mesh to the user for confirmation (or explicit waiver with recorded reason).
4. Write the confirmed edges into the claim-bearing pages.
5. Record `relationship_review: yes` and `quality_edges_added: N` on the path receipt.  
   Exit is **incomplete** while only generic self-referential migration links exist or while the quality bar is unmet (unless an explicit, recorded waiver is present).

### 6. Compile gate

```bash
python3 <atlas-skill>/scripts/atlas.py compile --root <subject_atlas>
```

- Exit ≠ 0 or staging non-empty → `incomplete: Exit (compile/staging)` — fix before discipline rewrite.
- Success requires staging **empty**.

### 7. Discipline rewrite (subject package)

After green compile, update the **subject** skill (not peers):

- Primary process memory → subject Atlas via atlas paths
- Plan home → `autogenesis/plans/<work_id>.md` (`type: plan`)
- Remove or relegate okf-wiki as sole memory authority (legacy read-only archive OK)
- Align path modules that hard-code wiki remember/ingest with Atlas remember/compile

If rewrite cannot be completed safely → set `discipline_rewrite: deferred: <reason>` on receipt; content migration may still be complete only if compile was green and claims done.

### 8. Lineage Exit

- Write `autogenesis/experiences/YYYY-MM-DD-atlas-migrate-<subject>.md` with **## Changed files**
- Update work hub for this Run’s `work_id` if any
- Append subject Atlas `log.md` for structural migration
- Path receipt (below)

## Path receipt

```text
subject: …
path: atlas-migrate
source: …
atlas_root: <subject>/references/atlas
autogenesis_space: autogenesis/
promoted_count: N
staging_empty: yes
relationship_review: yes | waived: <reason>
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
| Enter | subject + path module read |
| Change | migrate + full claim conversion under `autogenesis/` + **thorough relationship review** (quality bar met or explicit waiver) |
| Exit | staging empty, compile green, lineage experience, discipline rewrite or explicit defer, relationship_review recorded |

## Multi-harness substrate contract

When invoking **atlas** (required) or **okf** (format-only): load the target skill body via the harness loader and follow it exactly. Never invent migrate/promote behaviour from memory.

## Non-goals

- Replacing atlas CLI
- Waiting on CLI batch/dry-run features
- Silent peer skill mutation
- Claiming success with non-empty staging
- **Auto-deleting** `references/wiki/` on Exit (wiki remains read-only archive until an explicit human-gated delete; see Atlas decision `wiki-folder-deletion-policy`)

## Consistency

workflow-discipline remains source of Enter/Change/Exit rules. Plan home and Autogenesis space rules in SKILL.md / workflow-discipline apply.
