---
name: autogenesis/modules/think-ramble
description: Internal Autogenesis module. Capture free-form thoughts and half-formed ideas into the subject Atlas. Not a catalog skill. Evolves only via Autogenesis Runs on subject=autogenesis.
source: root think-ramble (snapshot 2026-08-24 Atlas-aligned)
internal: true
---

# think-ramble (internal)

Capture unstructured thinking into the **subject Atlas** via atlas remember.

## Process

1. Accept the user’s free-form text (even if messy or incomplete).
2. Hand off to the multi-harness substrate contract applied to the skill named `atlas`, loading its `remember` path:
   - Target: subject Atlas root (`<subject>/references/atlas/`; when subject is autogenesis: `.atlas/github.com/sergio-sisternes-epam/autogenesis-atlas` after mount) under `autogenesis/experiences/` (or appropriate type).
   - Type-correct frontmatter; `relates_to` with `autogenesis/…` paths only for Autogenesis-authored edges.
   - `atlas compile` must go green.
3. Confirm briefly what was captured; offer grill, challenge, or Medium/Gamma next steps.

## Rules

- Do not polish or invent content.
- Prefer focused pages over one giant dump.
- All persistence goes through the normal **atlas** substrate contract on the current subject Atlas.
- Never fall back to okf-wiki for new process memory.
- This module is progressive-disclosure only; it is never activated by root skill name lookup.
