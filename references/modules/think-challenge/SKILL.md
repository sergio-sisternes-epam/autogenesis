---
name: think-challenge
description: Challenge a design with grounded adversarial counters.
metadata:
  autogenesis-parent: autogenesis
  autogenesis-role: support
---

# think-challenge (internal)

Act as a rigorous but constructive critic. Search for the strongest real-world counter-arguments, failure cases and opposing viewpoints, then present them clearly so the user (or the design path) can harden thinking.

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
2. Read any relevant content via the multi-harness substrate contract applied to the skill named `atlas` (load its `query` path or open the named page under the subject Atlas). Do not invent a parallel query path.
3. Formulate 2–4 sharp search queries aimed at known criticisms, documented failures, alternative approaches, and contrary data/case studies.
4. Perform the searches and extract the strongest, most credible counters (prefer primary sources, reputable analysis, concrete examples).
5. Present the counters in a clear, structured way (counter, evidence/source, severity).
6. **Adversarial-scenario derivation** (Autogenesis Run, behavior-changing
   work): after search, derive additional smokes from named theories and model
   knowledge if needed so the suite is non-empty. Each smoke names its source.
7. Optionally persist a short “challenged” note via the substrate contract to `atlas` (`remember`) with `relates_to` to the original idea.
8. Invite the user to respond, refine, or request a deeper dive. When called from the design path, return the counters for autonomous pin evaluation.

## Rules

- Never invent unnamed counter-arguments. Search is preferred. During an
  Autogenesis Run, named theories and model knowledge are valid sources for
  adversarial scenario smokes if each smoke names its source.
- Stay constructive and intellectual — the goal is stronger ideas, not winning a debate.
- Prefer quality over quantity when presenting (3–5 strong counters beat 15 weak ones).
- Persist lasting conclusions only through the normal **atlas** substrate contract on the current subject Atlas.
- Never fall back to okf-wiki for new process memory.
- Cite sources inline so the user can verify.
- This module is progressive-disclosure only; it is never activated by root skill name lookup.
