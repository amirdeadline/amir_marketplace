---
name: document_max
description: "Run a multi-phase documentation sprint with `doc-lead`, `doc-worker`, and `doc-verifier` roles: inspect sources, obtain human approval on outline and budget, write sections incrementally with strict traceability, checkpoint every 15 sections, and complete only after three final verification passes."
---

# document_max

Follow the procedure in the host-agnostic amir skill file `skill-specs/document_max.md`.

**Resolve path:** `<amir-root>/skill-specs/document_max.md` where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).

1. Read the skill file completely.
2. Execute per its **Behavior** section.
3. Use `node tools/*.js` from the amir `tools/` directory.
4. Follow `core/` modules referenced by the skill — never restate them inline.
