---
name: user_skills
description: "Enumerate and present a table of skills installed at the **user level** for the specified AI application — project-scoped or user-home overrides, read-only inventory."
---

# user_skills

Follow the procedure in the host-agnostic amir skill file `skill-specs/user_skills.md`.

**Resolve path:** `<amir-root>/skill-specs/user_skills.md` where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).

1. Read the skill file completely.
2. Execute per its **Behavior** section.
3. Use `node tools/*.js` from the amir `tools/` directory.
4. Follow `core/` modules referenced by the skill — never restate them inline.
