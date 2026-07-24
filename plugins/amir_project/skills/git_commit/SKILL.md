---
name: git_commit
description: "Create a git commit with message metadata derived from activity and implementation notes, after a mandatory secrets scan gate. Hard-fail on any findings with file locations before staging or committing."
---

# git_commit

Follow the procedure in the host-agnostic amir skill file `skill-specs/git_commit.md`.

**Resolve path:** `<amir-root>/skill-specs/git_commit.md` where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).

1. Read the skill file completely.
2. Execute per its **Behavior** section.
3. Use `node tools/*.js` from the amir `tools/` directory.
4. Follow `core/` modules referenced by the skill — never restate them inline.
