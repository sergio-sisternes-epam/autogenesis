---
type: plan
title: "Jittered exponential backoff with a retry budget"
created: "2026-10-08"
updated: "2026-10-08"
revision: 1
work_id: "2026-10-08-retry-backoff-guidance"
status: designed
change_class: hardening
subject: retry-helper
plan_path: autogenesis/plans/2026-10-08-retry-backoff-guidance.md
---

# Jittered exponential backoff with a retry budget

Designed; awaiting explicit approval.

## Genesis Artifacts

- Intent: recommend full-jitter exponential backoff and a per-call retry budget.
- Scope: step 2 of `SKILL.md` only. Non-goal: a retry library.
- Acceptance: step 2 names jitter, the exponential base and a budget of three attempts.

## Challenge

- Counter (high): a budget alone still retries non-idempotent calls. Pin: retry only idempotent requests.
- Counter (medium): jitter hides latency regressions. Pin: log each retry with its delay.
