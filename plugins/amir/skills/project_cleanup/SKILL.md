---
name: project_cleanup
description: "Safe workspace hygiene: verify version control, snapshot before changes, present a human-approved cleanup plan, execute only approved items, and log all actions. Never destroy authoritative amir state or checkpoint evidence."
---

# project_cleanup

Follow the procedure in the host-agnostic amir skill file `skill-specs/project_cleanup.md`.

**Resolve path:** `<amir-root>/skill-specs/project_cleanup.md` where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).

1. Read the skill file completely.
2. Execute per its **Behavior** section.
3. Use `node tools/*.js` from the amir `tools/` directory.
4. Follow `core/` modules referenced by the skill — never restate them inline.
