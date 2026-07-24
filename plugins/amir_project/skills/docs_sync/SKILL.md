---
name: docs_sync
description: "Detect drift between documentation and actual behavior; produce a fix list and apply doc updates only with human approval."
---

# docs_sync

Follow the procedure in the host-agnostic amir skill file `skill-specs/docs_sync.md`.

**Resolve path:** `<amir-root>/skill-specs/docs_sync.md` where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).

1. Read the skill file completely.
2. Execute per its **Behavior** section.
3. Use `node tools/*.js` from the amir `tools/` directory.
4. Follow `core/` modules referenced by the skill — never restate them inline.
