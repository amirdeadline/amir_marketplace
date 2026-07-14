---
name: git_tree
description: "Render the branch and commit graph for the project as human-readable text or Mermaid, including amir checkpoint tags (`amir/T*-complete`)."
---

# git_tree

Follow the procedure in the host-agnostic amir skill file `skill-specs/git_tree.md`.

**Resolve path:** `<amir-root>/skill-specs/git_tree.md` where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).

1. Read the skill file completely.
2. Execute per its **Behavior** section.
3. Use `node tools/*.js` from the amir `tools/` directory.
4. Follow `core/` modules referenced by the skill — never restate them inline.
