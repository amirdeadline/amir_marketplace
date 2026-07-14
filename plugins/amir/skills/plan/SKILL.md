---
name: plan
description: "Produce a phased implementation plan, run context-engineering quality review, obtain human approval, and populate `ai/state/tasks.json`."
---

# plan

Follow the procedure in the host-agnostic amir skill file `skill-specs/plan.md`.

**Resolve path:** `<amir-root>/skill-specs/plan.md` where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).

1. Read the skill file completely.
2. Execute per its **Behavior** section.
3. Use `node tools/*.js` from the amir `tools/` directory.
4. Follow `core/` modules referenced by the skill — never restate them inline.
