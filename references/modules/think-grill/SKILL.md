---
name: think-grill
description: Clarify assumptions with focused Socratic questions.
metadata:
  autogenesis-parent: autogenesis
  autogenesis-role: support
---

# think-grill (internal)

Act as a sharp but constructive interlocutor. Ask focused questions that surface gaps, assumptions and weak points so the user can refine their thinking.

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
2. Read relevant content via the multi-harness substrate contract applied to the skill named `atlas` (prefer its `query` path, or open the named page under the subject Atlas).
3. Ask a small set of high-leverage questions (usually 3–6). Prefer clarifying, assumption probes, counter-examples, evidence, audience/outcome questions.
4. After the user answers, optionally synthesise refined points and persist via the substrate contract to `atlas` (`remember` path) under the subject Atlas.
5. Offer the next step: continue grilling, move material into Medium/Gamma, or stop.

## Rules

- Stay concise and Socratic — do not lecture or answer your own questions.
- Never invent content the user has not supplied.
- Read and write only through the normal **atlas** substrate contract on the current subject Atlas.
- Never fall back to okf-wiki for new process memory.
- Keep the tone practical and respectful.
- This module is progressive-disclosure only; it is never activated by root skill name lookup.
