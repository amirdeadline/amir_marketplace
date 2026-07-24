---
name: git_setup
description: "Guide the human through initializing version control for an amir project: repository creation, `.gitignore` with secrets and workspace temp policies, initial commit, and optional GitHub remote — every decision via structured questions."
---

# git_setup

Follow the procedure in the host-agnostic amir skill file `skill-specs/git_setup.md`.

**Resolve path:** `<amir-root>/skill-specs/git_setup.md` where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).

1. Read the skill file completely.
2. Execute per its **Behavior** section.
3. Use `node tools/*.js` from the amir `tools/` directory.
4. Follow `core/` modules referenced by the skill — never restate them inline.
