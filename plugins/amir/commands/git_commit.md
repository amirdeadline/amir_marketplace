---
name: "amir:git_commit"
description: "Create a git commit with message metadata derived from activity and implementation notes, after a mandatory secrets scan gate. Hard-fail ..."
---

# /amir:git_commit

Create a git commit with message metadata derived from activity and implementation notes, after a mandatory secrets scan gate. Hard-fail on any findings with file locations before staging or committing.

## Instructions

Read and follow `skill-specs/git_commit.md` in this packed amir plugin (`skill-specs/<name>.md`).

- Resolve amir root: this plugin directory (marketplace-packed; contains `core/`, `skill-specs/`, `tools/`).
- Use `node tools/<script>.js` from amir `tools/` for all state, render, activity, cost, doctor, and secrets operations.
- Obey `core/message-contract.md`, `core/workspace-rules.md`, `core/budget-rules.md`, and `core/honesty-rules.md`.
- Emit routine status using the five-field message contract.

Execute the skill **Behavior** section exactly. Do not invent steps not in the skill definition.
