---
description: "Safe workspace hygiene: verify version control, snapshot before changes, present a human-approved cleanup plan, execute only approved ite..."
---

# /amir:project_cleanup

Safe workspace hygiene: verify version control, snapshot before changes, present a human-approved cleanup plan, execute only approved items, and log all actions. Never destroy authoritative amir state or checkpoint evidence.

## Instructions

Read and follow `skill-specs/project_cleanup.md` in this packed amir plugin (`skill-specs/<name>.md`).

- Resolve amir root: this plugin directory (marketplace-packed; contains `core/`, `skill-specs/`, `tools/`).
- Use `node tools/<script>.js` from amir `tools/` for all state, render, activity, cost, doctor, and secrets operations.
- Obey `core/message-contract.md`, `core/workspace-rules.md`, `core/budget-rules.md`, and `core/honesty-rules.md`.
- Emit routine status using the five-field message contract.

Execute the skill **Behavior** section exactly. Do not invent steps not in the skill definition.
