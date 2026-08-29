---
name: autogenesis/paths/reevaluate
description: After material knowledge change (or explicit request), reevaluate related skills for impact and produce structured skill-update proposals. Advisory only; never mutate skills in the same run. Recurring gaps escalate to design-plan candidate and stop for approval.
path_id: reevaluate
default: false
subject_scope: subject-atlas
---

# Path: reevaluate

## Enter

Activation card must show `path: reevaluate` and this file must have been read.

```text
mode: run
subject: <skill whose knowledge or dependency graph is in focus>
path: reevaluate
path_module: references/paths/reevaluate.md
intent: <one line>
```

## Purpose

New knowledge can challenge the skillset. Consolidation alone is insufficient.  
This path produces **impact reports** and **structured skill-update proposals** (advisory). It does **not** rewrite skill packages in the same run.

`learn-skill` remains peer-link only. Do not overload it.

**Product bar:** after material knowledge change, the **subject** skill always receives clear update proposals (or explicit `none` + rationale)—not only soft “consider later” notes.

## Triggers

1. **Default:** explicit user request.
2. **Optional auto:** only after **material** knowledge change (new knowledge pages or high-severity domain delta), with a **cool-down** so micro-edits do not thrash reevaluate.
3. **Never** trigger solely from this path’s own advisory outputs.

## Inputs

- Changed knowledge pages (or pointers) and a short materiality note.
- Scope: **subject always**; plus skills with peer-links / knowledge contracts against that domain; plus any user-named skills.
- Prior reevaluate experiences for the same domain (recurrence / dedupe by gap or proposal signature).

## Procedure

1. **Resolve scope**  
   - **Subject is always in scope** after material knowledge change.  
   - Add dependency-declared and user-named peers.  
   - If the **peer** graph is empty, record that **explicitly** — do not claim the whole harness was checked. Empty peers ≠ empty subject output.
2. Enforce a soft **cap on skills per run**; require user expand for larger graphs.
3. **For each skill in scope** (read-only):
   - Load SKILL.md / relevant contracts via the multi-harness substrate contract if needed.
   - Map changed knowledge → gaps vs skill surface (description, triggers, paths, contracts).
   - Classify impact: `none | advisory | capability-gap | correctness | safety`.
   - `none` requires **explicit rationale** (not silence).
   - Record **uncertainty** (thin vs strong evidence).
   - Emit a **mandatory proposal block** (template below). Soft “consider / maybe / someday” alone is **incomplete**.
   - Write the advisory experience into the **subject** Atlas only (never mutate peer or subject package files in this run). Dedupe by gap/proposal signature when possible.
4. Emit an aggregate **impact report**.
5. Link **open tasks** with **owner + domain** metadata when proposals need follow-up (dedupe by proposal signature).
6. **Recurrence check:** same proposal/gap signature for same skill/domain across sessions → escalate weight on the handoff plan / stop notes (do not implement).
7. **Evolution handoff pipeline** (only when **evolution-worthy** — see below). Otherwise skip to Exit.
8. **Exit** via Atlas (claim = action: remember executed + green compile; or explicit deferral).

### Evolution-worthy threshold (when to run full handoff)

Run the full pipeline when subject classification ∈ {**capability-gap**, **correctness**, **safety**} **or** non-empty Update proposals that change SKILL.md surface / add paths / change knowledge contracts non-trivially.

**Skip** full pipeline when pure `none` with rationale, or only trivial advisory nits (still write the proposal/none experience; no user-judgment ceremony).

### Evolution handoff pipeline (evolution-worthy only)

1. **Draft design plan** in the **subject Atlas** (`type: plan` at `autogenesis/plans/<work_id>.md`) from the subject’s structured proposals (intent, pins, implement slice, non-goals). If no Atlas, follow Subject Atlas resolution (inform + offer initiate / migrate). Do **not** implement.
2. **Automatic challenge ×1** (load think-challenge / reflect-challenge capability once). Prefer live challenge when tools allow; else structured steel-man checklist. Record on plan: counters absorbed, pins refined, **residual risks**, and label:
   `challenge: automated×1; confidence: limited`
   Challenge is **preparation**, not a safety certificate or design approval.
3. **Target skill memory** (subject Atlas — not only agent-brain):
   - Experience linking plan path, proposal summary, challenge status, residual risks.
   - **Todo**: owner, domain, proposal **signature(s)**, `gate: user-judgment`.
   - **Dedupe:** if signature already has an open todo, **refresh** it; do not spawn unbounded duplicates. Prefer merge/supersede.
4. Surface handoff status for the caller (agent-brain Learn) so a **user decision packet** can be emitted. Stop short of implement.

## Mandatory proposal template (per skill in scope)

```markdown
## Impact: <skill-id>
- classification: none | advisory | capability-gap | correctness | safety
- rationale: …
- uncertainty: low | medium | high
- evidence: [[knowledge/…]] …

### Update proposals
1. **SKILL.md** (description / triggers / non-goals): … concrete bullet changes, or “none — rationale”
2. **Paths / modules**: … e.g. add `references/paths/<name>.md` with contract …, or “none — rationale”
3. **Knowledge contracts**: … query-first / required pages, or “none — rationale”
4. **Open tasks**: owner + domain + next gate (design | implement after approval | PR)

### Decision gate
- This run: **proposal only**
- Implement: requires explicit design/implement approval (or human Git PR for package promotion)
```

**Incomplete if:** after material knowledge change, the **subject** block has empty `### Update proposals` and no explicit `none — rationale`.

**“Do not auto-create”** means do **not implement** path/SKILL edits in this run. Sharp proposals **are** required when change is warranted.

Vague-only language banned as sole content: “consider”, “maybe”, “someday”, without a concrete artifact name and contract.

## Outputs

- Per-skill impact + **structured update proposals** (or explicit none + rationale).
- Aggregate report (including “empty peer graph” when applicable; subject still fully reported).
- When evolution-worthy: **design plan** path + `challenge: automated×1; confidence: limited` + residual risks.
- Target-skill **experience + todo** (`gate: user-judgment`, signature-deduped).
- Handoff flags for caller user summary (learnings/recommendations deferred to Learn’s decision packet).

## Hard rules

- **Subject always** gets a full proposal block after material knowledge change.
- **Advisory only** — no same-run mutation of any skill’s SKILL.md, paths, or package wiki as “the update.”
- **No self-chain** — this run must not schedule another reevaluate from its own outputs.
- **No whole-harness fan-out** by default.
- **No automatic promotion** into skill packages (recurrence + human Git PR still required for generalisation).
- Default trigger is **explicit**; auto only with materiality + cool-down.
- Full handoff pipeline only for **evolution-worthy** impact (anti fatigue / anti spam).
- Automated challenge is **limited confidence**; user judgment is the real gate.
- Todo **dedupe by proposal signature**; do not unbounded-bloat active evolution todos.

## Non-goals

- Peer content copy or peer/subject package mutation in this run.
- Auto-wire.
- Auto-implementing proposed paths or subskills.
- Treating automated challenge as design approval.
- Forcing user-judgment ceremony on pure `none` or trivial advisories.
- Resolving ADR-001 beyond these path mitigations.

## Consistency

workflow-discipline remains the source of Enter/Change/Exit rules. This path specialises reevaluation procedure only.
