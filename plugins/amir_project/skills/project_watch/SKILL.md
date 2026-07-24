---
name: project_watch
description: "Live operational snapshot: last N activity events, agents table with heartbeat/stale flags, and in-progress task linkage."
---

# project_watch

Follow the procedure in the host-agnostic amir skill file `skill-specs/project_watch.md`.

**Resolve path:** `<amir-root>/skill-specs/project_watch.md` where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).

1. Read the skill file completely.
2. Execute per its **Behavior** section.
3. Use `node tools/*.js` from the amir `tools/` directory.
4. Follow `core/` modules referenced by the skill — never restate them inline.
