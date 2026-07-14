---
name: user_settings
description: "Produce a clean, human-readable artifact of **user-level** settings for the specified AI application (project + user home overrides), ordered by importance — read-only audit."
---

# user_settings

Follow the procedure in the host-agnostic amir skill file `skill-specs/user_settings.md`.

**Resolve path:** `<amir-root>/skill-specs/user_settings.md` where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).

1. Read the skill file completely.
2. Execute per its **Behavior** section.
3. Use `node tools/*.js` from the amir `tools/` directory.
4. Follow `core/` modules referenced by the skill — never restate them inline.
