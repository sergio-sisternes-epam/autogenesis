---
type: experience
title: "Callers retried non-idempotent POST requests"
created: "2026-11-02"
work_id: "2026-11-02-add-retry-note"
status: designed
relates_to:
  - path: autogenesis/work/2026-11-02-add-retry-note.md
    kind: implements
---

# Callers retried non-idempotent POST requests

Callers wrapped non-idempotent POST requests in retries and created duplicate orders. The design records that lesson and stops for approval.
