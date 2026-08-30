# Changelog

All notable changes to this package are documented here. The skill body stays in `SKILL.md`.

## 0.3.13

- **Exit / process memory:** deferred items are `type: protostar` with `work_id`, origin `derived_from`, work-hub `implements`. Folder `autogenesis/residuals/` is forbidden. Plan heading `Accepted risks` replaces `Residual risks` so leftover *risk* is not leftover *work*. Work_id `2026-08-26-residuals-vs-protostar`.

## 0.3.12

- **path discuss / from active design:** a problem found in design review re-enters `mode: discussion` on the same `work_id`. `stage: design`, `artifact` = the plan, existing `discussion_root` reused, prior idea nodes in scope. No nested path, no blank hub. Work_id `2026-08-26-discuss-from-active-design`.

## 0.3.11

- **path discuss:** `mode: discussion` must use `path: discuss`. Path module substrate-loads catalog skill discuss, passes subject `atlas_root`, fail-closed Enter if discuss load or discuss fields are missing. think-grill / think-ramble not loaded in discussion mode. think-challenge stays an internal validation gate. Work_id `2026-08-26-autogenesis-discuss-activation`.

## 0.3.10

- **design path step 6b:** agent-spec path `specify` is now the **sole** legal producer of behavioural Gherkin. Direct authoring by Autogenesis forbidden. Explicit `deferred: <reason>` remains first-class. Activation card gains required `behavioural_contract: specify | deferred:<reason>` hint when behaviour is in scope. Discussion principles updated (explore via specify in discussion mode; only design materialises). Work_id `2026-08-25-specify-only-behavioural-contract`.

## 0.3.9

- **card pattern (B17 / workflow-discipline):** Enter card and path receipt now begin with `skill:` and `skill_path:` (first two fields). Canonical schema updated; peers receive the same leading fields.

## 0.3.8

- **design path step 6c:** `## Evaluation plan` required when behaviour is in scope — deterministic smokes primary, agent evaluations secondary; anti-pattern soft-only evaluation; gate **G-EVAL**.

## 0.3.7

- **design path:** step 6b — agent-spec behavioural contract (`## Behavioural contract (agent-spec)`); G-BDD gate.
- Depends on skill `agent-spec` for layout / coverage validation when the gate runs.

## 0.3.6

- **atlas-migrate:** mandatory thorough relationship review + quality `relates_to` before Exit (from 0.3.5).
- **Internal think modules** (challenge / grill / ramble): Atlas query/remember only; no okf-wiki substrate.
- **Paths** initialise / learn-skill / research: Atlas-first process memory.
- **activation-card / run-record-template:** `atlas_root` + compile on receipts.
- **validate-okf-conformance:** prefers Atlas store; optional `atlas compile`.
- **Canonical decision:** `wiki-folder-deletion-policy` — no auto-delete on migrate; human-gated archive removal.
- **Package metadata:** `apm.yml` deps on atlas + okf (not okf-wiki).
