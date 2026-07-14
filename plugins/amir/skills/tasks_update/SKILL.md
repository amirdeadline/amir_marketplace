---
name: tasks_update
description: "Reconcile reported task or scope changes through state tools and regenerate task views."
---

# tasks_update

Follow the procedure in the host-agnostic amir skill file `skill-specs/tasks_update.md`.

**Resolve path:** `<amir-root>/skill-specs/tasks_update.md` where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).

1. Read the skill file completely.
2. Execute per its **Behavior** section.
3. Use `node tools/*.js` from the amir `tools/` directory.
4. Follow `core/` modules referenced by the skill — never restate them inline.
