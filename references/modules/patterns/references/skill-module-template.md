# Optional instruction-only module template

Use when an approved design needs a cohesive private module. Copy only the
example below into the chosen module's SKILL.md and replace the placeholders.
The name must match its directory; keep the description useful for selection.
Headings may change if the interface remains clear.

```markdown
---
name: <module-name>
description: Use this module when <specific task or condition>.
---

# <Module purpose>

## Inputs and boundaries

- Required: <input and its meaning>.
- Optional: <input and default, or omit this line>.
- Inherit the parent's relevant scope and approval; inputs do not grant
  additional authority. Ask for missing information that blocks the task.

## Procedure

1. <Approach the task using the supplied inputs.>
2. <Read a local reference only when its stated condition applies.>
3. <Use an existing tool when a real action or fact requires it.>

## Outcome

Return <useful result> with actual evidence where applicable. If blocked or
unsuccessful, state why and what remains undone; do not claim completion.
```

Add a parent routing entry with the selection condition and relative
entrypoint. The parent reads it before following the procedure and shows a
request cue when cards are enabled. A file read is not a new thread.

Remove unused template lines. Do not scaffold empty directories, protocol
schemas, validators or an Autogenesis workflow module. A task-specific script
is optional, not forbidden; document its prerequisites and actual use.
