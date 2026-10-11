---
type: plan
title: "Add a retry note to retry-helper"
created: "2026-11-02"
updated: "2026-11-02"
revision: 1
work_id: "2026-11-02-add-retry-note"
status: designed
change_class: hardening
subject: retry-helper
plan_path: autogenesis/plans/2026-11-02-add-retry-note.md
relates_to:
  - kind: implements
    target: autogenesis/work/2026-11-02-add-retry-note.md
    path: autogenesis/work/2026-11-02-add-retry-note.md
---

# Add a retry note to retry-helper

Designed; awaiting explicit approval. Not approved. No SKILL.md edit in this operation.

## Genesis Artifacts

- Intent: warn against retrying non-idempotent requests.
- Scope: one sentence in `SKILL.md` step 2.
- Acceptance: the note is present and nothing else changes.

## Challenge

- Counter (high): a note alone does not stop a caller from retrying POST. Pin: state the rule next to the retry step.
