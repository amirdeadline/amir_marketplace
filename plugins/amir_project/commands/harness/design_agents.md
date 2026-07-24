---
description: "Populate `.ai/state/agents.json` with the project agent registry using canonical naming, and render the human-readable `.ai/views/agents.md..."
---

# /amir:design_agents

Populate `.ai/state/agents.json` with the project agent registry using canonical naming, and render the human-readable `.ai/views/agents.md` view.

## Instructions

Read and follow `skill-specs/design_agents.md` in this packed amir plugin (`skill-specs/<name>.md`).

- Resolve amir root: this plugin directory (marketplace-packed; contains `core/`, `skill-specs/`, `tools/`).
- Use `node tools/<script>.js` from amir `tools/` for all state, render, activity, cost, doctor, and secrets operations.
- Obey `core/message-contract.md`, `core/workspace-rules.md`, `core/budget-rules.md`, and `core/honesty-rules.md`.
- Emit routine status using the five-field message contract.

Execute the skill **Behavior** section exactly. Do not invent steps not in the skill definition.
