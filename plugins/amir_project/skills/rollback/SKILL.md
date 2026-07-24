---
name: rollback
description: "Revert project codebase to a prior checkpoint safely. Prefer git revert; allow `git reset --hard` only with explicit typed human confirmation."
---

# rollback

Follow the procedure in the host-agnostic amir skill file `skill-specs/rollback.md`.

**Resolve path:** `<amir-root>/skill-specs/rollback.md` where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).

1. Read the skill file completely.
2. Execute per its **Behavior** section.
3. Use `node tools/*.js` from the amir `tools/` directory.
4. Follow `core/` modules referenced by the skill — never restate them inline.
