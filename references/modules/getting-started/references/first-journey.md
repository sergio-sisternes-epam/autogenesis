# Autogenesis first journey

Packaged baseline for Autogenesis **v0.8.0**. Usable with no Atlas mounted.

## Purpose

Autogenesis is a root APM skill for evolving, designing, reviewing, or
initialising agent skills from durable experience. Genesis remains the design
process; Autogenesis fuses and extends it. Procedures are parent-routed
**modules** under one catalog identity. Derived skills receive the runtime
they need, not an Autogenesis framework by default.

## Prerequisites

- Install from the Atlas marketplace only:

```bash
apm marketplace add sergio-sisternes-epam/atlas-marketplace --name atlas
apm install autogenesis@atlas
```

- Catalog **discuss** for durable discussion (not an Autogenesis module).
- Atlas is required before **design**, **initialise**, or **implement**,
  because those operations persist plans and lineage in the subject Atlas.
  Help and getting-started do not require a mounted Atlas.
- A subject git repository before any Autogenesis write-home.

## Shortest useful first journey

1. **Explore** — If you are still shaping the problem, activate the catalog
   **discuss** package. Discussion has no implement authority and must not
   write product files.
2. **Design or initialise** — When a skill change is needed, ask Autogenesis
   to **design** (default Run). To confirm purpose and start a new skill,
   ask **initialise** instead. Both persist a plan in the subject Atlas and
   stop for **explicit approval**. Do not skip to implement.
3. **Implement** — Only after that persisted plan is explicitly approved,
   ask Autogenesis to **implement**. Never implement from discussion.
   Discussion-driven change is `discussion -> design -> explicit approval
   -> implement`. New-skill confirmation is `initialise -> explicit
   approval -> implement`.
4. **Next help** — For a map of what Autogenesis can do, ask **help** with no
   target. For one procedure, ask **help** with that module name (`design`,
   `implement`, `initialise`, `review-package`, and the other operations).

Do not treat a visible request card as approval or as proof that design or
implement ran.

## Boundaries

- Unqualified "help" about unrelated tasks is not Autogenesis getting-started.
- Getting-started explains; it does not initialise, design, or implement.
- Support helpers (`validate-*`, think wrappers, `patterns`) are not the
  first-use surface.
