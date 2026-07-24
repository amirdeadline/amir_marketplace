---
name: "amir:user_settings"
description: "Produce a clean, human-readable artifact of **user-level** settings for the specified AI application (project + user home overrides), ord..."
---

# /amir:user_settings

Produce a clean, human-readable artifact of **user-level** settings for the specified AI application (project + user home overrides), ordered by importance — read-only audit.

## Instructions

Read and follow `skill-specs/user_settings.md` in this packed amir plugin (`skill-specs/<name>.md`).

- Resolve amir root: this plugin directory (marketplace-packed; contains `core/`, `skill-specs/`, `tools/`).
- Use `node tools/<script>.js` from amir `tools/` for all state, render, activity, cost, doctor, and secrets operations.
- Obey `core/message-contract.md`, `core/workspace-rules.md`, `core/budget-rules.md`, and `core/honesty-rules.md`.
- Emit routine status using the five-field message contract.

Execute the skill **Behavior** section exactly. Do not invent steps not in the skill definition.
