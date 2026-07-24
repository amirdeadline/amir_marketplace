---
name: design
description: "Produce technical architecture and design document `.ai/design.md` driven by the architect agent from approved `project.md`, question inventory, and `.ai/project-goal.md`. The architect leads; the human approves."
---

# design

Follow the procedure in the host-agnostic amir skill file `skill-specs/design.md`.

**Resolve path:** `<amir-root>/skill-specs/design.md` where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).

1. Read the skill file completely.
2. Execute per its **Behavior** section.
3. Use `node tools/*.js` from the amir `tools/` directory.
4. Follow `core/` modules referenced by the skill — never restate them inline.
