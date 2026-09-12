---
name: think-grill
description: Clarify assumptions with focused Socratic questions.
metadata:
  autogenesis-parent: autogenesis
  autogenesis-role: support
---

# think-grill (Autogenesis Run wrapper)

Act as a sharp but constructive interlocutor during an Autogenesis Run.
Catalog `think@atlas` owns the Socratic grill procedure. This module is only
the parent-routed Run surface and Autogenesis overlays.

## Arguments

- Required: `topic`.
- Optional: `assumption_list`, `clarity_goal`.
- Do not override parent-owned subject, mode, operation, work identity, Atlas, or approval.

Follow `<skill_root>/references/modules/workflow-discipline/SKILL.md` and its
invocation contract. The parent reads this entrypoint and issues a support
request with its configured compact card before the procedure. Keep the active
operation and inherited context; return results and a receipt to the caller.
Shared assets resolve from skill_root, not cwd. Do not invoke while catalog Discuss is active.

## Process

1. Identify the target:
   - Current conversation topic, **or**
   - A specific Atlas page the user names / points to, **or**
   - The active Autogenesis plan / design under review.
2. Apply the multi-harness substrate contract to the **external catalog skill**
   named `think-grill` from package `think` / `think@atlas`. Use the harness
   skill loader. Map this wrapper's arguments onto that catalog procedure
   before following it: `topic` is the idea to grill; if set,
   `assumption_list` and `clarity_goal` constrain the questions. Do not
   rely on ambient conversation alone when those arguments are present.
   Follow that catalog body for Socratic questions. This nested load is not
   an Autogenesis module request: do not resolve it through the parent
   registry, do not `read_file` this wrapper again, and do not treat the
   catalog skill name as a re-entry into this module.
3. **Autogenesis overlays (Run only), after the catalog body:**
   - Read and persist only through the subject Atlas via the substrate
     contract to `atlas` (`query` / `remember`). Conversation-only catalog fallback is not legal during a Run.
4. Return results and a receipt to the caller.

## Rules

- Stay concise and Socratic — do not lecture or answer your own questions.
- Never invent content the user has not supplied.
- Read and write only through the normal **atlas** substrate contract on the current subject Atlas.
- Never fall back to okf-wiki for new process memory.
- Keep the tone practical and respectful.
- This module is progressive-disclosure only; it is never activated by root skill name lookup.
