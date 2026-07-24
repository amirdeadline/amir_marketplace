---
name: build_agents
description: "Materialize agent workspace folders and seed `prompt.md` / `notes.md` for every registered agent in `agents.json`."
---

# build_agents

Follow the procedure in the host-agnostic amir skill file `skill-specs/build_agents.md`.

**Resolve path:** `<amir-root>/skill-specs/build_agents.md` where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).

1. Read the skill file completely.
2. Execute per its **Behavior** section.
3. Use `node tools/*.js` from the amir `tools/` directory.
4. Follow `core/` modules referenced by the skill — never restate them inline.
