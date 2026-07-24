---
name: "amir:design"
description: "Produce technical architecture and design document `ai/design.md` driven by the architect agent from approved `project.md`, question inve..."
---

# /amir:design

Produce technical architecture and design document `ai/design.md` driven by the architect agent from approved `project.md`, question inventory, and `ai/project-goal.md`. The architect leads; the human approves.

## Instructions

Read and follow `skill-specs/design.md` in this packed amir plugin (`skill-specs/<name>.md`).

- Resolve amir root: this plugin directory (marketplace-packed; contains `core/`, `skill-specs/`, `tools/`).
- Use `node tools/<script>.js` from amir `tools/` for all state, render, activity, cost, doctor, and secrets operations.
- Obey `core/message-contract.md`, `core/workspace-rules.md`, `core/budget-rules.md`, and `core/honesty-rules.md`.
- Emit routine status using the five-field message contract.

Execute the skill **Behavior** section exactly. Do not invent steps not in the skill definition.
