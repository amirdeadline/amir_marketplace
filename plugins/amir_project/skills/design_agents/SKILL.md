---
name: design_agents
description: "Populate `.ai/state/agents.json` with the project agent registry using canonical naming, and render the human-readable `.ai/views/agents.md` view."
---

# design_agents

Follow the procedure in the host-agnostic amir skill file `skill-specs/design_agents.md`.

**Resolve path:** `<amir-root>/skill-specs/design_agents.md` where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).

1. Read the skill file completely.
2. Execute per its **Behavior** section.
3. Use `node tools/*.js` from the amir `tools/` directory.
4. Follow `core/` modules referenced by the skill — never restate them inline.
