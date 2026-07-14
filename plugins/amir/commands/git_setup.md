# /git_setup

Guide the human through initializing version control for an amir project: repository creation, `.gitignore` with secrets and workspace temp policies, initial commit, and optional GitHub remote — every decision via structured questions.

## Instructions

Read and follow `skill-specs/git_setup.md` in this packed amir plugin (`skill-specs/<name>.md`).

- Resolve amir root: this plugin directory (marketplace-packed; contains `core/`, `skill-specs/`, `tools/`).
- Use `node tools/<script>.js` from amir `tools/` for all state, render, activity, cost, doctor, and secrets operations.
- Obey `core/message-contract.md`, `core/workspace-rules.md`, `core/budget-rules.md`, and `core/honesty-rules.md`.
- Emit routine status using the five-field message contract.

Execute the skill **Behavior** section exactly. Do not invent steps not in the skill definition.
