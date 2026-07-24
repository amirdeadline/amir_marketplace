---
description: "Execute the full goal delivery loop: from parsed goal through architecture, QA design, task execution, per-task worker/QA cycles, drift c..."
---

# /amir:build_goal

Execute the full goal delivery loop: from parsed goal through architecture, QA design, task execution, per-task worker/QA cycles, drift checks, and milestone QA — using state tools for all transitions.

## Instructions

Read and follow `skill-specs/build_goal.md` in this packed amir plugin (`skill-specs/<name>.md`).

- Resolve amir root: this plugin directory (marketplace-packed; contains `core/`, `skill-specs/`, `tools/`).
- Use `node tools/<script>.js` from amir `tools/` for all state, render, activity, cost, doctor, and secrets operations.
- Obey `core/message-contract.md`, `core/workspace-rules.md`, `core/budget-rules.md`, and `core/honesty-rules.md`.
- Emit routine status using the five-field message contract.

Execute the skill **Behavior** section exactly. Do not invent steps not in the skill definition.
