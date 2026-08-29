---
name: autogenesis/modules/think-challenge
description: Internal Autogenesis module. Grounded adversarial challenge for design/plan work (and on-request use). Not a catalog skill. Evolves only via Autogenesis Runs on subject=autogenesis.
source: root think-challenge (snapshot 2026-08-24 Atlas-aligned)
internal: true
---

# think-challenge (internal)

Act as a rigorous but constructive critic. Search for the strongest real-world counter-arguments, failure cases and opposing viewpoints, then present them clearly so the user (or the design path) can harden thinking.

## Process

1. Identify the exact idea or claim to challenge (from the current conversation, the active Autogenesis plan, or a named Atlas page).
2. Read any relevant content via the multi-harness substrate contract applied to the skill named `atlas` (load its `query` path or open the named page under the subject Atlas). Do not invent a parallel query path.
3. Formulate 2–4 sharp search queries aimed at known criticisms, documented failures, alternative approaches, and contrary data/case studies.
4. Perform the searches and extract the strongest, most credible counters (prefer primary sources, reputable analysis, concrete examples).
5. Present the counters in a clear, structured way (counter, evidence/source, severity).
6. **Adversarial-construct derivation** (Autogenesis Run, behaviour-changing work): after search, derive additional smokes from named theories and model knowledge if needed so the suite is non-empty. Each smoke names its source.
7. Optionally persist a short “challenged” note via the substrate contract to `atlas` (`remember`) with `relates_to` to the original idea.
8. Invite the user to respond, refine, or request a deeper dive. When called from the design path, return the counters for autonomous pin evaluation.

## Rules

- Never invent unnamed counter-arguments. Search is preferred. During an Autogenesis Run, named theories and model knowledge are valid sources for adversarial-construct smokes if each smoke names its source.
- Stay constructive and intellectual — the goal is stronger ideas, not winning a debate.
- Prefer quality over quantity when presenting (3–5 strong counters beat 15 weak ones).
- Persist lasting conclusions only through the normal **atlas** substrate contract on the current subject Atlas.
- Never fall back to okf-wiki for new process memory.
- Cite sources inline so the user can verify.
- This module is progressive-disclosure only; it is never activated by root skill name lookup.
