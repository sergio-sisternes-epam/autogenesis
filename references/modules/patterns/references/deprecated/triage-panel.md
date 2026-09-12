---
name: Triage Panel
id: triage-panel
category: Control & Safety / Workflow
status: draft
version: 0.4
---

# Triage Panel

## Context
A repository or product receives **human- or AI-authored** issues (or equivalent work items). Maintainers need consistent labeling, theming, prioritization, and routing regardless of author kind. Different teams prefer different trigger models: bulk sweep, event-driven on arrival, or a hybrid. The pattern supports both trigger models and lets the adopter choose.

## Problem
- Authors may be humans or AI agents; both produce real work items that need triage, but trust, spam shape, and volume profiles differ.
- A single generalist agent misses cross-cutting concerns (UX, security, architecture, growth).
- Fully automatic label application without clear human authority erodes trust and fights maintainer edits.
- Treating “no human reply” as formal approval is unsafe when maintainers are offline or overloaded.
- Full multi-persona fan-out on every item wastes cost on simple cases; never fanning out misses specialized judgment.
- Bulk-only can delay urgent new items; event-driven-only can create unbounded cost and latency spikes—especially if AI authors open issues at high rate.
- Synthesis can manufacture consensus and hide dissent.
- If applied labels drive other automation, an “advisory” panel becomes a de facto gate.

## Solution
Run a **bounded multi-persona triage panel** over human- and AI-authored items, with **pluggable trigger models**, explicit human authority, optional thin path, and visible dissent.

### 1. Trigger model (adopter chooses)

Support **both**; pick one primary model (or combine) to fit volume, SLA, and cost tolerance:

| Model | How it fires | Fits when |
|-------|----------------|-----------|
| **Bulk** | Scheduled sweep of *untriaged* items, oldest-first, hard cap per run | Predictable cost; fairness/backlog drain; medium–high volume (including AI-authored bursts) |
| **Event-driven** | On item opened / reopened (and optionally edited), with optional rate limits and filters | Low latency; lower volume; “triage as it arrives” preference |

**Optional fast path (orthogonal):** human applies a needs-triage signal → immediate re-triage; consume the signal after the run.

Document the chosen model in the deployment (and in Known uses).

**Cost & latency forces:**
- Bulk → bounded cost, higher median latency for new items; natural fit when AI authors create bursts.
- Event-driven → low latency; **must** pair with rate limits / per-author quotas if AI authors can open at scale.
- Hybrid (e.g. event-driven for high-signal types + bulk for the rest) when needed.

### 2. Author-aware filtering (human and AI)
- Triage **both** human- and AI-authored items; do not drop an item solely because the author is an agent.
- Still filter: locked items, empty/template-only bodies, spam-shaped content, and (if desired) known malicious bots — using explicit rules, not “all non-human authors.”
- Optional: different thin vs full thresholds or quotas by author class (e.g. stricter per-author cap for high-volume AI accounts) without denying triage.

### 3. Thin triage vs full panel
- **Thin path** (default for simple / low-signal items): smaller roster or single structured classifier → one proposal comment.
- **Full panel**: fan-out when the item is non-trivial or routing rules say so.
- Conditional personas stay conditional.

### 4. Fan-out + synthesizer (full panel)
- Each persona returns a **structured** verdict (schema-validated).
- Synthesizer produces one consolidated proposal **and** must surface **dissent** when returns conflict.
- In bulk runs, reset context between items.

### 5. Single emission + proposal framing (silence is not formal approval)
- Exactly **one** public comment per item: proposed labels, milestone suggestion, next action, dissent summary if any.
- Footer: this is an **agentic proposal**, not a final decision.
- **Silence means uncontested so far**, not formal ratification. Human edits are authoritative and must not be reverted on later runs.
- High-impact label classes should prefer an explicit human signal rather than silence.

### 6. Safety rails on writes
- Writes only to an allow-listed set of actions/labels; never fight human-applied labels.
- Prefer determining the write allow-list before trusting untrusted item bodies (whether human- or AI-written).
- Bulk: hard cap per run; prefer server-side untriaged + oldest-first.
- Event-driven: rate limits and per-author quotas recommended when AI authors are present.

### 7. When labels drive automation
- If label application triggers boards, SLAs, or security routing, the panel is **no longer purely advisory**.
- Scope the allow-list accordingly, or use comment-only for those classes.

### 8. Re-triage without fighting humans
- Humans re-trigger via needs-triage (fast path) or by clearing the triaged marker (reenroll in bulk).
- Fast path removes only the needs-triage trigger after success.

## Consequences

**Benefits**
- Works for mixed human/AI issue streams without treating AI authors as non-issues.
- Adopter chooses bulk, event-driven, or hybrid to match preferences and cost/latency needs.
- Cross-cutting quality when the full panel is justified; thin path for the rest.
- Maintainer authority preserved; dissent visible; urgency has a fast path under either model.

**Costs / residual risks**
- AI-authored volume can stress event-driven deployments without strong rate limits.
- Author-class rules can be wrong (over-filtering legitimate AI tools or under-filtering spam bots).
- Thin vs full routing can mis-classify.
- “Uncontested so far” still leaves bad labels if humans never review.
- Downstream automation on labels can reintroduce gate-like behaviour.

## Known uses
*(draft — populate from proven Runs before status: active)*

Record: primary trigger model, whether AI-authored items are in scope, thin/full rules, caps/quotas, and outcome.

## Related patterns
- Panel Review (fan-out advisory review for changesets)
- Activation Card (structured Enter / Exit discipline for agent Runs)
- Application Gate (dry-run → human review → apply)

## Sketch

```text
Authors: human OR AI

Trigger model (choose) ──┬─ Bulk: schedule, oldest untriaged, cap N
                         ├─ Event-driven: on open/reopen (+ limits if AI volume)
                         └─ Fast path: human needs-triage

Per item:
  filter (not “drop all AI”) → thin OR full panel
         → ONE comment (proposal; silence ≠ formal approval)
         → allow-listed labels; human edits win
```
