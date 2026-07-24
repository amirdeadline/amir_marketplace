---
description: "Revert project codebase to a prior checkpoint safely. Prefer git revert; allow `git reset --hard` only with explicit typed human confirma..."
---

# /amir:rollback

Revert project codebase to a prior checkpoint safely. Prefer git revert; allow `git reset --hard` only with explicit typed human confirmation.

## Instructions

Read and follow `skill-specs/rollback.md` in this packed amir plugin (`skill-specs/<name>.md`).

- Resolve amir root: this plugin directory (marketplace-packed; contains `core/`, `skill-specs/`, `tools/`).
- Use `node tools/<script>.js` from amir `tools/` for all state, render, activity, cost, doctor, and secrets operations.
- Obey `core/message-contract.md`, `core/workspace-rules.md`, `core/budget-rules.md`, and `core/honesty-rules.md`.
- Emit routine status using the five-field message contract.

Execute the skill **Behavior** section exactly. Do not invent steps not in the skill definition.
