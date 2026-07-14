---
name: handoff
description: "Generate a structured pause handoff from template so a fresh orchestrator instance can resume without relying on chat history."
---

# handoff

Follow the procedure in the host-agnostic amir skill file `skill-specs/handoff.md`.

**Resolve path:** `<amir-root>/skill-specs/handoff.md` where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).

1. Read the skill file completely.
2. Execute per its **Behavior** section.
3. Use `node tools/*.js` from the amir `tools/` directory.
4. Follow `core/` modules referenced by the skill — never restate them inline.
