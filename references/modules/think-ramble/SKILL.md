---
name: think-ramble
description: Capture free-form thoughts into the subject Atlas.
metadata:
  autogenesis-parent: autogenesis
  autogenesis-role: support
---

# think-ramble (internal)

Capture unstructured thinking into the **subject Atlas** via atlas remember.

## Arguments

- Required: `thoughts`.
- Optional: `theme`, `capture_title`.
- Do not override parent-owned subject, mode, operation, work identity, Atlas, or approval.

Follow `<skill_root>/references/modules/workflow-discipline/SKILL.md` and its
invocation contract. The parent reads this entrypoint and issues a support
request with its configured compact card before the procedure. Keep the active
operation and inherited context; return results and a receipt to the caller.
Shared assets resolve from skill_root, not cwd. Do not invoke in discussion mode.

## Process

1. Accept the user’s free-form text (even if messy or incomplete).
2. Hand off to the multi-harness substrate contract applied to the skill named `atlas`, loading its `remember` path:
   - Target: the subject repository's Atlas root returned by `atlas resolve <atlas_id>`, under `autogenesis/experiences/` (or appropriate type).
   - Type-correct frontmatter; `relates_to` with `autogenesis/…` paths only for Autogenesis-authored edges.
   - `atlas compile` must go green.
3. Confirm briefly what was captured; offer grill, challenge, or Medium/Gamma next steps.

## Rules

- Do not polish or invent content.
- Prefer focused pages over one giant dump.
- All persistence goes through the normal **atlas** substrate contract on the current subject Atlas.
- Never fall back to okf-wiki for new process memory.
- This module is progressive-disclosure only; it is never activated by root skill name lookup.
