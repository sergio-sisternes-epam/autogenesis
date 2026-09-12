---
name: think-challenge
description: Challenge a design with grounded adversarial counters.
metadata:
  autogenesis-parent: autogenesis
  autogenesis-role: support
---

# think-challenge (Autogenesis Run wrapper)

Act as a rigorous but constructive critic during an Autogenesis Run. Catalog
`think@atlas` owns the search-grounded challenge procedure. This module is
only the parent-routed Run surface and Autogenesis overlays.

## Arguments

- Required: `design_target`.
- Optional: `relevant_atlas_page`, `evidence_scope`.
- Do not override parent-owned subject, mode, operation, work identity, Atlas, or approval.

Follow `<skill_root>/references/modules/workflow-discipline/SKILL.md` and its
invocation contract. The parent resolves and reads this entrypoint and issues
a support request with its configured compact card before the procedure.
Keep the active operation and inherited context; return findings and a receipt
to the caller. Shared assets resolve from skill_root, not cwd. This support
is a Run validation gate, never a discussion user verb.

## Process

1. Identify the exact idea or claim to challenge (from the current conversation, the active Autogenesis plan, or a named Atlas page).
2. Apply the multi-harness substrate contract to the **external catalog skill**
   named `think-challenge` from package `think` / `think@atlas`. Use the
   harness skill loader. Map this wrapper's arguments onto that catalog
   procedure before following it: `design_target` is the claim to challenge;
   if set, `relevant_atlas_page` is the named page and `evidence_scope`
   bounds evidence. Do not rely on ambient conversation alone when those
   arguments are present. Follow that catalog body for search-grounded
   counters. This nested load is not an Autogenesis module request: do not
   resolve it through the parent registry, do not `read_file` this wrapper
   again, and do not treat the catalog skill name as a re-entry into this module.
3. **Autogenesis overlays (Run only), after the catalog body:**
   - Persist lasting conclusions only through the subject Atlas via the
     substrate contract to `atlas` (`remember`). Conversation-only catalog fallback is not legal during a Run.
   - **Adversarial-scenario derivation** on behavior-changing work: after
     search, derive additional smokes from named theories and model knowledge
     if needed so the suite is non-empty. Each smoke names its source.
   - When called from design, return the counters for autonomous pin
     evaluation. Do not invite a user discussion verb here.
4. Return findings and a receipt to the caller.

## Rules

- Never invent unnamed counter-arguments in the catalog procedure. Search is
  preferred there. During an Autogenesis Run, named theories and model
  knowledge are valid sources for adversarial scenario smokes if each smoke
  names its source.
- Stay constructive and intellectual — the goal is stronger ideas, not winning a debate.
- Prefer quality over quantity when presenting (3–5 strong counters beat 15 weak ones).
- Persist lasting conclusions only through the normal **atlas** substrate contract on the current subject Atlas.
- Never fall back to okf-wiki for new process memory.
- Cite sources inline so the user can verify.
- This module is progressive-disclosure only; it is never activated by root skill name lookup.
