---
name: design_qa
description: "Define QA strategy: produce `ai/qa-objectives.md`, QA environment design, and project-level QA skill hooks so verification is testable before build."
---

# design_qa

Follow the procedure in the host-agnostic amir skill file `skill-specs/design_qa.md`.

**Resolve path:** `<amir-root>/skill-specs/design_qa.md` where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).

1. Read the skill file completely.
2. Execute per its **Behavior** section.
3. Use `node tools/*.js` from the amir `tools/` directory.
4. Follow `core/` modules referenced by the skill — never restate them inline.
