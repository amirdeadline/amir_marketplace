# /user_cleanup

**DESTRUCTIVE.** Remove user-level and project-local amir installations for the specified AI application — only after timestamped backup, explicit deletion list, typed confirmation, and audit log. Refuse if any safeguard is missing.

## Instructions

Read and follow `skill-specs/user_cleanup.md` in this packed amir plugin (`skill-specs/<name>.md`).

- Resolve amir root: this plugin directory (marketplace-packed; contains `core/`, `skill-specs/`, `tools/`).
- Use `node tools/<script>.js` from amir `tools/` for all state, render, activity, cost, doctor, and secrets operations.
- Obey `core/message-contract.md`, `core/workspace-rules.md`, `core/budget-rules.md`, and `core/honesty-rules.md`.
- Emit routine status using the five-field message contract.

Execute the skill **Behavior** section exactly. Do not invent steps not in the skill definition.
