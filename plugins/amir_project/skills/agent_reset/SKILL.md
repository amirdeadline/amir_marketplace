---
name: agent_reset
description: "Archive an agent workspace and respawn a fresh prompt/notes shell without deleting history. Mark agent reset in registry for audit."
---

# agent_reset

Follow the procedure in the host-agnostic amir skill file `skill-specs/agent_reset.md`.

**Resolve path:** `<amir-root>/skill-specs/agent_reset.md` where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).

1. Read the skill file completely.
2. Execute per its **Behavior** section.
3. Use `node tools/*.js` from the amir `tools/` directory.
4. Follow `core/` modules referenced by the skill — never restate them inline.
