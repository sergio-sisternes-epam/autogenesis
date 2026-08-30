---
name: autogenesis/paths/discuss
description: Use this path when Autogenesis is in discussion mode. Substrate-load catalog skill discuss and follow its full body. Pass subject Atlas as atlas_root. Zero implement authority.
path_id: discuss
default: false
subject_scope: subject-atlas
---

# Path: discuss

Autogenesis discussion *mechanism*. Not a catalog skill. Catalog skill is **discuss**; this is path_id **discuss**.

## Enter

Activation card must show `mode: discussion`, `path: discuss`, and this file **read**.

Required discuss fields on the card (missing ⇒ `incomplete: missing Enter`):

```text
objective: <original objective>
atlas_root: <subject>/references/atlas   # subject=autogenesis → .atlas/github.com/sergio-sisternes-epam/autogenesis-atlas
discussion_root: <atlas-relative path>
current_branch: <atlas-relative path>
```

Pass when known: `work_id`, `stage`, `artifact`.

`atlas_root` **must** be the subject Atlas. Do not use the discuss skill default store when Autogenesis is the caller. When subject is autogenesis, that root is `.atlas/github.com/sergio-sisternes-epam/autogenesis-atlas` after `atlas mount github.com/sergio-sisternes-epam/autogenesis-atlas --ref main`.

### From an active design (review problem)

A problem found while reviewing a design is a legal discuss Enter. It is **not** a nested path inside design (one path at a time). Re-issue the card: `mode: discussion`, `path: discuss`.

- Autogenesis **subject** stays the skill under change.
- **`stage: design`**.
- **`artifact`** is the design packet (or the tighter node under review).
- **`work_id`** is the design’s work.
- **Reuse `discussion_root`** when a graph already exists for that work. Do not open a blank hub.
- **`current_branch`** moves to the new problem node.
- Prior idea nodes, pins, and protostars for that work are **in scope**: query them first; edge new pages with `follows` / `derived_from` / `counters`. They are not a different subject.
- Out of scope: a new skill subject, product edits, a second fabric for the same work.
- When the problem is pinned or deferred, re-enter `mode: run`, `path: design` on the same `work_id`. Still no discussion → implement.

The same pattern applies if the user asks to talk about a think-challenge result: this path, artifact = the challenged plan, prior nodes in scope.

## Procedure

1. Resolve `subject_atlas = <subject>/references/atlas/` (when subject is autogenesis: `.atlas/github.com/sergio-sisternes-epam/autogenesis-atlas` after mount). If SCHEMA.json is missing, stop and follow Subject Atlas resolution — do not fall back to discuss’s own Atlas. Do not create `references/atlas/` in this repo.
2. Apply the multi-harness substrate contract to catalog skill **discuss**:
   - Locate the skill by name.
   - Load its full `SKILL.md` body.
   - Follow that body exactly (Enter card, query first, one orbit, batch then 1-by-1, KVA, sprout, compile).
3. Hand discuss these values so the callee does not invent context: subject, intent, objective, atlas_root (subject Atlas), work_id when work exists, stage, artifact, discussion_root, current_branch. If this Enter left an active design, `stage` is `design`, `artifact` is the plan (or tighter node), and `discussion_root` is the existing root for that work when one exists.
4. Graph writes go to `atlas_root`. Canonical work hub is subject `work/<work_id>.md`. Same `work_id` on the discuss skill Atlas is `work_role: pointer` only.
5. New or updated discussion pages carry `stage` and `artifact` (tighter node: plan, work, receipt, or challenged page).
6. Intra-Atlas `relates_to` the canonical work hub (`kind: implements`) or the tighter artifact. Other roots are named with `external_ref` plus a body citation. No dual-write of the fabric.
7. Do **not** load internal `think-grill` or `think-ramble`. Root catalog think-* skills stay for non-Autogenesis use.
8. Do **not** load internal `think-challenge` from this path. That module is an Autogenesis validation gate on path design (and similar Run paths) only. If the user asks to talk about a self-challenge result, stay on this path and link the challenged artifact.
9. Compile green on `atlas_root` after persist.
10. Emit a path receipt. Never claim Run complete. Never edit Autogenesis product files from this path.

## Gates

G0 (discussion ⇒ no implement) · G1 (this module read) · G2 (subject Atlas writes). Not G4/G5.

## Non-goals

Implement, wire, design-packet materialisation, user-activated think-challenge, dual-write, typed cross-Atlas `relates_to`.
