# SOLID principles for skills

Autogenesis applies this skill-native design lens after Genesis. Information
hiding, cohesion, and change locality are the foundation; the SOLID names are
prompts for disciplined judgment, not proof of quality or a requirement for
object-oriented structure.

## Principles

| Principle | Skill-native interpretation | Review questions |
|---|---|---|
| Single Responsibility (S) | A skill, module, or rule has one cohesive user-facing responsibility and one primary reason to change. Split only at a real caller, change-cadence, attention, ownership, or effect boundary. | What user-facing responsibility does this surface own? Which concrete change pressure would justify a separate boundary? |
| Open/Closed (O) | The intended contract is closed to accidental semantic drift and open through declared, governed extension points. Intentional behavior changes remain allowed when reviewed, versioned, and evaluated. | Which semantics must remain stable? Is an extension point justified by observed variation rather than speculative generality? |
| Liskov Substitution (L) | Assess only when skills or modules claim the same capability or an interchangeable contract. A substitute preserves required preconditions, promised outcomes, authority and effect boundaries, and failure semantics. | Is interchangeability actually claimed? If so, can callers switch implementations without stronger preconditions, weaker outcomes, or changed authority and failure behavior? |
| Interface Segregation (I) | Expose only the inputs, context, tools, and outputs a caller needs, using progressive disclosure. A narrow interface must still carry enough context and authority information for safe execution. | Can callers avoid unrelated instructions and tools? Does the interface still communicate required context, authority, blockers, outcomes, and failure semantics? |
| Dependency Inversion (D) | Depend on stable capabilities and contracts rather than incidental harness, provider, or tool details. Add adapters or indirection only when real portability, volatility, reuse, or ownership pressure justifies them. | Is the dependency an essential capability or an incidental implementation detail? Is there concrete pressure that earns another abstraction? |

## Application

Consider every principle, but do not force structural compliance:

- `new-surface` and `new-skill` plans contain the full five-row record below.
- `hardening` plans may contain an abbreviated statement for only the material
  principles, including why the others are not material.
- `not-applicable` is a reasoned conclusion, not an omission.
- `trade-off` names the competing property and the chosen boundary.
- Missing required evidence makes the design incomplete; do not present it for
  approval until the evidence is supplied.
- Adoption is prospective. Review an existing artifact when its design is
  materially changed; do not fail untouched legacy work solely because it
  lacks a historical SOLID record.

| Principle | Status | Rationale / design consequence |
|---|---|---|
| S | applicable / not-applicable / trade-off | Artifact-specific consequence |
| O | applicable / not-applicable / trade-off | Artifact-specific consequence |
| L | applicable / not-applicable / trade-off | Artifact-specific consequence |
| I | applicable / not-applicable / trade-off | Artifact-specific consequence |
| D | applicable / not-applicable / trade-off | Artifact-specific consequence |

## Boundaries

This lens does not require modules, speculative extension points, adapters,
runtime schemas, generated artifacts, or a semantic validator. A short
single-purpose skill can remain root-only. Instruction-only modules, domain
scripts, concrete provider dependencies, and intentionally versioned behavior
changes remain valid when the design explains their consequences.

L applies only when interchangeability is claimed. O protects governed
semantics from accidental drift; it does not freeze a contract against an
approved, versioned, and evaluated change. I favors progressive disclosure,
not unsafe minimalism. D does not justify indirection without real dependency
pressure.
