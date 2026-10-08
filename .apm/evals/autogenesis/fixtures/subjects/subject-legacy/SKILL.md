---
name: retry-helper
description: Use this skill to add bounded retries with backoff around flaky network calls in small Python services.
version: 0.1.0
---

# retry-helper

Fixture skill for the Autogenesis dogfood suite. It is a test subject, not a
real skill.

## Procedure

1. Find the network call that fails intermittently.
2. Wrap it in at most three attempts with exponential backoff.
3. Log each retry with the attempt number.
