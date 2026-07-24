---
name: "amir:project_create"
description: "Bootstrap a new amir project from a human goal: create the project folder and workspace skeleton, run structured discovery, produce appro..."
---

# /amir:project_create

Bootstrap a new amir project from a human goal: create the project folder and workspace skeleton, run structured discovery, produce approved goal documents, and initialize JSON state.

## Instructions

Read and follow `skill-specs/project_create.md` in this packed amir plugin (`skill-specs/<name>.md`).

- Resolve amir root: this plugin directory (marketplace-packed; contains `core/`, `skill-specs/`, `tools/`).
- Use `node tools/<script>.js` from amir `tools/` for all state, render, activity, cost, doctor, and secrets operations.
- Obey `core/message-contract.md`, `core/workspace-rules.md`, `core/budget-rules.md`, and `core/honesty-rules.md`.
- Emit routine status using the five-field message contract.

Execute the skill **Behavior** section exactly. Do not invent steps not in the skill definition.
