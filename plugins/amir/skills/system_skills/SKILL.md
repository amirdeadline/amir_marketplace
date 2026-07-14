---
name: system_skills
description: "Enumerate and present a table of skills installed at the **system level** for the specified AI application host — read-only inventory for audit and troubleshooting."
---

# system_skills

Follow the procedure in the host-agnostic amir skill file `skill-specs/system_skills.md`.

**Resolve path:** `<amir-root>/skill-specs/system_skills.md` where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).

1. Read the skill file completely.
2. Execute per its **Behavior** section.
3. Use `node tools/*.js` from the amir `tools/` directory.
4. Follow `core/` modules referenced by the skill — never restate them inline.
