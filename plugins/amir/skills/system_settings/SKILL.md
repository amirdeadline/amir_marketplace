---
name: system_settings
description: "Produce a clean, human-readable artifact of **system-level** settings for the specified AI application, ordered by importance — for audit, backup review, and troubleshooting."
---

# system_settings

Follow the procedure in the host-agnostic amir skill file `skill-specs/system_settings.md`.

**Resolve path:** `<amir-root>/skill-specs/system_settings.md` where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).

1. Read the skill file completely.
2. Execute per its **Behavior** section.
3. Use `node tools/*.js` from the amir `tools/` directory.
4. Follow `core/` modules referenced by the skill — never restate them inline.
