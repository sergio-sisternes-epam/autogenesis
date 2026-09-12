---
name: think-ramble
description: Capture free-form thoughts into the subject Atlas.
metadata:
  autogenesis-parent: autogenesis
  autogenesis-role: support
---

# think-ramble (Autogenesis Run wrapper)

Capture unstructured thinking during an Autogenesis Run. Catalog `think@atlas`
owns the ramble/capture procedure. This module is only the parent-routed Run
surface and Autogenesis overlays.

## Arguments

- Required: `thoughts`.
- Optional: `theme`, `capture_title`.
- Do not override parent-owned subject, mode, operation, work identity, Atlas, or approval.

Follow `<skill_root>/references/modules/workflow-discipline/SKILL.md` and its
invocation contract. The parent reads this entrypoint and issues a support
request with its configured compact card before the procedure. Keep the active
operation and inherited context; return results and a receipt to the caller.
Shared assets resolve from skill_root, not cwd. Do not invoke while catalog Discuss is active.

## Process

1. Accept the user’s free-form text (even if messy or incomplete).
2. Apply the multi-harness substrate contract to the **external catalog skill**
   named `think-ramble` from package `think` / `think@atlas`. Use the harness
   skill loader. Map this wrapper's arguments onto that catalog procedure
   before following it: `thoughts` is the free-form text to capture; if set,
   `theme` and `capture_title` label the page. Do not rely on ambient
   conversation alone when `thoughts` is present. Follow that catalog body
   for capture. This nested load is not an Autogenesis module request: do
   not resolve it through the parent registry, do not `read_file` this
   wrapper again, and do not treat the catalog skill name as a re-entry into this module.
3. **Autogenesis overlays (Run only), after the catalog body:**
   - Persistence target is the subject repository Atlas root returned by
     `atlas resolve <atlas_id>`, under `autogenesis/experiences/` (or the
     appropriate type). Conversation-only catalog fallback is not legal during a Run.
   - Type-correct frontmatter; `relates_to` with `autogenesis/…` paths only
     for Autogenesis-authored edges.
   - `atlas compile` must go green.
4. Confirm briefly what was captured; offer grill, challenge, or Medium/Gamma next steps.
5. Return results and a receipt to the caller.

## Rules

- Do not polish or invent content.
- Prefer focused pages over one giant dump.
- All persistence goes through the normal **atlas** substrate contract on the current subject Atlas.
- Never fall back to okf-wiki for new process memory.
- This module is progressive-disclosure only; it is never activated by root skill name lookup.
