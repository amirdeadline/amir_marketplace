---
name: user_cleanup
description: "**DESTRUCTIVE.** Remove user-level and project-local amir installations for the specified AI application — only after timestamped backup, explicit deletion list, typed confirmation, and audit log. Refuse if any safeguard is missing."
---

# user_cleanup

Follow the procedure in the host-agnostic amir skill file `skill-specs/user_cleanup.md`.

**Resolve path:** `<amir-root>/skill-specs/user_cleanup.md` where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).

1. Read the skill file completely.
2. Execute per its **Behavior** section.
3. Use `node tools/*.js` from the amir `tools/` directory.
4. Follow `core/` modules referenced by the skill — never restate them inline.
