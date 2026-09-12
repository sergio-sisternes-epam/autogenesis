---
name: discuss
description: Discuss a skill change through the external Discuss skill and the resolved subject Atlas. Preserve discussion context and never implement.
metadata:
  autogenesis-parent: autogenesis
  autogenesis-role: operation
---

# Operation: discuss

Autogenesis discussion mechanism, not a catalogue skill. The external catalogue
skill is **discuss**; this parent-owned operation invokes that separate skill.

## Arguments

- Required: `objective`, `discussion_root`, `current_branch`.
- Optional: `stage`, `artifact`.
- Parent context owns subject, mode, operation, work identity, Atlas and approval.
  Follow `<skill_root>/references/modules/workflow-discipline/SKILL.md` and
  its module-local invocation contract; resolve shared assets from skill_root.

## Enter

The parent issues an operation request for `discuss` with discussion mode,
reads this entrypoint and emits the configured full request card.

Required values passed to the external Discuss skill (missing means blocked):

```text
objective: <original objective>
atlas_id: <host/org/repo>
atlas_root: <resolved path from atlas resolve>
discussion_root: <atlas-relative path>
current_branch: <atlas-relative path>
```

Pass when known: `work_id`, `stage`, `artifact`.

`atlas_root` **must** be the subject repository's resolved Atlas. Do not use
the Discuss skill default store when Autogenesis is the caller. Resolve the
card's `atlas_id` through Atlas path `mount` with no `--target`, then
`atlas resolve`.

### From an active design (review problem)

A problem during design review permits an explicit parent transition to
discussion mode and operation `discuss`. It is not a supporting call inside
design: only one operation is active. Issue a new operation request.

- Autogenesis **subject** stays the skill under change.
- **`stage: design`**.
- **`artifact`** is the design packet (or the tighter node under review).
- **`work_id`** is the design’s work.
- **Reuse `discussion_root`** when a graph already exists for that work. Do not open a blank hub.
- **`current_branch`** moves to the new problem node.
- Prior idea nodes, pins, and protostars for that work are **in scope**: query them first; edge new pages with `follows` / `derived_from` / `counters`. They are not a different subject.
- Out of scope: a new skill subject, product edits, a second fabric for the same work.
- When pinned or deferred, the parent may return to Run mode and operation
  `design` with the same work_id. Still no discussion -> implement.

The same pattern applies to discussion of a think-challenge result: this
operation, artifact = the challenged plan, prior nodes in scope.

## Procedure

1. Follow workflow-discipline Subject Atlas resolution. Require the active
   subject git root, mount the selected `atlas_id` with no `--target`, set
   `subject_atlas` from `atlas resolve`, and verify `SCHEMA.json`. On failure,
   stop; do not fall back to Discuss's own Atlas.
2. Apply the multi-harness substrate contract to catalog skill **discuss**:
   - Locate the skill by name.
   - Load its full `SKILL.md` body.
   - Follow that body exactly (Enter card, query first, one orbit, batch then 1-by-1, KVA, sprout, compile).
3. Hand discuss these values so the callee does not invent context: subject, intent, objective, atlas_root (subject Atlas), work_id when work exists, stage, artifact, discussion_root, current_branch. If this Enter left an active design, `stage` is `design`, `artifact` is the plan (or tighter node), and `discussion_root` is the existing root for that work when one exists.
4. Graph writes go to `atlas_root`. Canonical work hub is subject `work/<work_id>.md`. Same `work_id` on the discuss skill Atlas is `work_role: pointer` only.
5. New or updated discussion pages carry `stage` and `artifact` (tighter node: plan, work, receipt, or challenged page).
6. Intra-Atlas `relates_to` the canonical work hub (`kind: implements`) or the tighter artifact. Other roots are named with `external_ref` plus a body citation. No dual-write of the fabric.
7. Do **not** load internal `think-grill` or `think-ramble`. Root catalog think-* skills stay for non-Autogenesis use.
8. Do **not** invoke internal `think-challenge` from this operation. It is a
   validation support for design and similar Run operations only. Discussion
   of a self-challenge result stays here and links the challenged artifact.
9. Compile green on `atlas_root` after persist.
10. Emit the canonical invocation receipt with actual external Discuss and
    Atlas evidence. Never claim Run complete or edit product files from this
    operation. External Discuss retains its own card and path schema; do not
    mechanically convert its fields to Autogenesis's request schema.

## Gates

G0 (discussion ⇒ no implement) · G1 (this module read) · G2 (subject Atlas writes). Not G4/G5.

## Non-goals

Implement, wire, design-packet materialisation, user-activated think-challenge, dual-write, typed cross-Atlas `relates_to`.
