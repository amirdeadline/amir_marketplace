---
name: "amir:system_skills"
description: "Enumerate and present a table of skills installed at the **system level** for the specified AI application host — read-only inventory for..."
---

# /amir:system_skills

Enumerate and present a table of skills installed at the **system level** for the specified AI application host — read-only inventory for audit and troubleshooting.

## Instructions

Read and follow `skill-specs/system_skills.md` in this packed amir plugin (`skill-specs/<name>.md`).

- Resolve amir root: this plugin directory (marketplace-packed; contains `core/`, `skill-specs/`, `tools/`).
- Use `node tools/<script>.js` from amir `tools/` for all state, render, activity, cost, doctor, and secrets operations.
- Obey `core/message-contract.md`, `core/workspace-rules.md`, `core/budget-rules.md`, and `core/honesty-rules.md`.
- Emit routine status using the five-field message contract.

Execute the skill **Behavior** section exactly. Do not invent steps not in the skill definition.
