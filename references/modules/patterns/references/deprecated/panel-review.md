---
name: Panel Review
id: panel-review
category: Control & Safety / Workflow
status: draft
version: 0.2
---

# Panel Review

## Context
A non-trivial change set (pull request or equivalent) needs cross-cutting expert judgment—architecture, UX, security, docs, tests, positioning—before maintainers decide to ship. A single reviewer or a single agent misses specialized concerns; a hard automated gate creates defensive inflation of “required” findings.

## Problem
- One generalist review misses domain-specific risks.
- Binary approve/reject gates push panelists to over-mark items as blocking.
- Multiple agents writing separately to the same change create noise and conflicting comments.
- Personas that always run (or never run) waste cost or skip critical angles.
- Without a synthesizer, the maintainer faces a pile of unprioritized findings.
- Unlabeled findings are often read as mandatory; a rigid named severity dialect (e.g. one team’s “Blocker / NIT”) is too specific to mandate in a portable pattern.

## Solution
Run a **fan-out advisory panel** with a single synthesizer, structured findings with **graded weights**, and a strict **one-emission** rule. The panel recommends; humans decide.

### 1. Advisory regime (not gate regime)
- No binary APPROVE/REJECT computed by the panel.
- No verdict labels that gate merge.
- Output is a **ship recommendation** stance for humans, e.g.:
  - ship now
  - ship with follow-ups
  - needs discussion
  - needs rework
- Removing the binary gate reduces incentive for panelists to inflate “required” lists.

### 2. Fan-out + synthesizer
- Orchestrator dispatches **specialist personas** in parallel (each in its own thread/context).
- Each persona returns **structured** findings (schema-validated): issue, rationale, **finding weight**, suggested follow-up—not free-form walls of text only.
- A synthesizer (arbiter) reads all returns and produces one prioritized recommendation, respecting weights and surfacing dissent when personas conflict.
- Orchestrator is the **sole writer** to the change set.

### 3. Finding weights (abstract; local names allowed)
Each finding carries a **graded weight** so authors and maintainers know intent:

| Abstract weight | Meaning |
|-----------------|--------|
| **must-address before ship** | Should be fixed or explicitly waived before merge |
| **should-address** | Important; prefer fix or tracked follow-up |
| **optional polish** | Style/preference; author may ignore without blocking ship |

Adopters may rename these (see examples below). Weights inform the synthesizer’s ship_recommendation; they do **not** auto-apply gate labels unless the deployment explicitly leaves pure advisory mode.

**Example vocabularies (reference only — not mandated):**
- Blocker / Recommended / NIT
- Conventional Comments (e.g. issue / suggestion / nitpick)
- Critical / High / Info

### 4. Roster: mandatory, conditional, and skip rules
- **Always-on** specialists for the core risk surface of the project.
- **Conditional** specialists only when the change touches matching paths or signals.
- **Skip rules** (e.g. docs-only → skip pure code-coverage specialist) to avoid empty or noisy reviews.
- Keep the roster explicit and versioned with the skill.

### 5. Single-emission discipline
- Exactly **one** recommendation comment per panel run, rendered from a fixed template after all subagents return.
- No per-persona public comments; no mid-run labels; define retry/skip policy if a persona fails.
- Consume the trigger signal so re-applying it re-runs cleanly.

### 6. What the orchestrator must not do
- Must not merge, approve, or apply gate labels by default.
- Must not let personas write directly to the change set.
- Must not invent a binary verdict from a majority vote when the regime is advisory.

### 7. Human authority
- Maintainer and author weigh the recommendation and the weighted findings.
- Re-run is explicit (re-apply trigger or equivalent).
- Follow-ups are suggestions unless a separate process creates tracked work.

## Consequences

**Benefits**
- Cross-cutting coverage without a single overloaded reviewer.
- Advisory stance reduces defensive over-blocking.
- Graded weights remove “is this mandatory?” ambiguity without locking to one label dialect.
- One comment keeps the change readable; conditional roster controls cost.

**Costs / residual risks**
- Fan-out multiplies tokens and waits on the slowest persona + synthesis.
- Weak schema or weak synthesizer → mushy or authority-biased summary.
- If culture treats “must-address” as an automatic soft gate, advisory intent erodes.
- Conditional routing bugs skip the specialist you needed most.
- Local renames of weights can fragment understanding across teams unless documented in Known uses.

## Known uses
*(draft — populate from proven Runs before status: active)*

## Related patterns
- Triage Panel (bounded triage for issues; proposal regime; pluggable triggers)
- Activation Card (Enter / Exit discipline for agent Runs)
- Application Gate (dry-run → human review → apply)

## Sketch

```text
Trigger (label / dispatch)
    → gather change context (read-only)
    → fan-out personas (mandatory + conditional − skip rules)
    → structured findings + weight (must / should / optional)
    → synthesizer → ship_recommendation (+ dissent)
    → ONE template comment (orchestrator only)
    → no merge gate labels by default
Human decides ship / rework / re-run
```
