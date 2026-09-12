---
type: activation-plan
subject: <skill>
intent: <outcome>
date: YYYY-MM-DD
---

# Invocation plan

This template plans an Autogenesis authoring Run. Its operations and protocol
are not a runtime scaffold to copy into a derived skill. For a private module,
use the optional S8 module template instead.

| step | operation | approval_point | notes |
|------|---------|----------------|-------|
| 1 | research | no | optional |
| 2 | design | **yes — stop** | genesis packet |
| 3 | implement | requires G4 | only after approve |

One operation is active at a time. Resolve each module from the loaded parent
registry and read its entrypoint before invocation. Follow the sole authority
at `<skill_root>/references/modules/workflow-discipline/SKILL.md`.
An activation card signals a request, not approval or execution. Supporting
calls inherit protected context and return without replacing the operation.
