## Autogenesis-aware runtime (mandatory)

During execution, under the governance rules below, record short experiences
through Atlas `remember` in the active subject repository's resolved Atlas,
under `autogenesis/experiences/`. If the store is missing or cannot resolve,
fail closed; do not create a package-local store.

1. **Novel self-use** – situation or inputs not yet present in the Atlas
   → append short experience: what was novel, what you did, outcome

2. **Novel peer-skill use** – another skill used in a way not yet recorded  
   → append short experience: peer skill, how used, contract/result observed

3. **Improvement opportunity** – problem or brittleness observed  
   → append experience: symptom, suspected cause, suggested direction  
   → **Do not implement any change**

### Governance (non-negotiable)

- Tag every record with `source: runtime-aware` and `status: unverified`
- Respect the write budget (default: max 3 runtime experiences per skill run). Stop when the cap is reached.
- Cheap-dedup before writing (skip if a very similar title/body already exists in recent experiences)
- Runtime experiences are subject to pruning/archival after a declared horizon (default: 30 days or when clearly superseded)
- High-impact skills may run with this hook disabled or with promotion gated by human review
- All writes go only into the resolved subject Atlas
- Load Atlas path `mount` and `remember`; mount with no `--target`, use the
  root from `atlas resolve`, and require compile exit 0
- Prefer short template + deferred/end-of-turn write
- Never treat `status: unverified` runtime experiences as compiled knowledge without an explicit promotion step

### Mandatory closing step

Before finishing this skill run:
- If any novel self-use, novel peer-skill use, or improvement opportunity occurred, append the corresponding short experience under the governance rules above.
- If none occurred, do nothing.
- Do not implement any improvement.
- Skipping this check means the run is incomplete with respect to Autogenesis-aware discipline.
