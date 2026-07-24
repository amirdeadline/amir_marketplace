---
name: "amir:security_scan"
description: "Run secrets scanning and host-native security audit tools; triage findings into `ai/state/risks.json` via `4-security` review."
---

# /amir:security_scan

Run secrets scanning and host-native security audit tools; triage findings into `ai/state/risks.json` via `4-security` review.

## Instructions

Read and follow `skill-specs/security_scan.md` in this packed amir plugin (`skill-specs/<name>.md`).

- Resolve amir root: this plugin directory (marketplace-packed; contains `core/`, `skill-specs/`, `tools/`).
- Use `node tools/<script>.js` from amir `tools/` for all state, render, activity, cost, doctor, and secrets operations.
- Obey `core/message-contract.md`, `core/workspace-rules.md`, `core/budget-rules.md`, and `core/honesty-rules.md`.
- Emit routine status using the five-field message contract.

Execute the skill **Behavior** section exactly. Do not invent steps not in the skill definition.
