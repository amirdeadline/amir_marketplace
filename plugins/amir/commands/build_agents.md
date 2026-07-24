---
name: "amir:build_agents"
description: "Materialize agent workspace folders and seed `prompt.md` / `notes.md` for every registered agent in `agents.json`."
---

# /amir:build_agents

Materialize agent workspace folders and seed `prompt.md` / `notes.md` for every registered agent in `agents.json`.

## Instructions

Read and follow `skill-specs/build_agents.md` in this packed amir plugin (`skill-specs/<name>.md`).

- Resolve amir root: this plugin directory (marketplace-packed; contains `core/`, `skill-specs/`, `tools/`).
- Use `node tools/<script>.js` from amir `tools/` for all state, render, activity, cost, doctor, and secrets operations.
- Obey `core/message-contract.md`, `core/workspace-rules.md`, `core/budget-rules.md`, and `core/honesty-rules.md`.
- Emit routine status using the five-field message contract.

Execute the skill **Behavior** section exactly. Do not invent steps not in the skill definition.
