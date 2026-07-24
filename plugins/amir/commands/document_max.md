---
name: "amir:document_max"
description: "Run a multi-phase documentation sprint with `doc-lead`, `doc-worker`, and `doc-verifier` roles: inspect sources, obtain human approval on..."
---

# /amir:document_max

Run a multi-phase documentation sprint with `doc-lead`, `doc-worker`, and `doc-verifier` roles: inspect sources, obtain human approval on outline and budget, write sections incrementally with strict traceability, checkpoint every 15 sections, and complete only after three final verification passes.

## Instructions

Read and follow `skill-specs/document_max.md` in this packed amir plugin (`skill-specs/<name>.md`).

- Resolve amir root: this plugin directory (marketplace-packed; contains `core/`, `skill-specs/`, `tools/`).
- Use `node tools/<script>.js` from amir `tools/` for all state, render, activity, cost, doctor, and secrets operations.
- Obey `core/message-contract.md`, `core/workspace-rules.md`, `core/budget-rules.md`, and `core/honesty-rules.md`.
- Emit routine status using the five-field message contract.

Execute the skill **Behavior** section exactly. Do not invent steps not in the skill definition.
