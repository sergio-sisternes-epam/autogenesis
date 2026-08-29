# Run record / path receipt template

## Activation card (Enter)

```text
skill: <activating skill name>
skill_path: <resolved path to that skill’s root directory>
mode: run | discussion
subject: <skill>
path: <path_id>
path_module: references/paths/<path_id>.md
intent: <one line>
```

## Path receipt (Exit)

```text
skill: <activating skill name>
skill_path: <resolved path to that skill’s root directory>
subject: …
path: …
approved: yes | n/a | no
atlas_root: <subject>/references/atlas
nested_skills_loaded: …
substrate_contract: applied | missing
remember: yes | no
compile: yes | no
Enter|Change|Exit: pass | incomplete: <cluster>
```

## Body (atlas remember experience)

- What the user asked
- What was done
- **Changed files** (mandatory for any Run that created or edited product files)
  - List every relative path from the skill root (or Atlas-relative paths under `autogenesis/`)
  - Example:
    ```
    ## Changed files
    - references/modules/think-challenge.md (created)
    - references/paths/design.md (updated)
    - SKILL.md (updated)
    - autogenesis/decisions/internal-think-modules.md (created)
    ```
- Pinned decisions / open items
- Related `relates_to` edges
