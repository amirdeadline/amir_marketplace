---
name: resume_build
description: "Safely resume an interrupted build: diagnose health, repair or flag issues, consume handoff context, regenerate orchestrator prompt, and continue the next orchestrator action."
---

# resume_build

Follow the procedure in the host-agnostic amir skill file `skill-specs/resume_build.md`.

**Resolve path:** `<amir-root>/skill-specs/resume_build.md` where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).

1. Read the skill file completely.
2. Execute per its **Behavior** section.
3. Use `node tools/*.js` from the amir `tools/` directory.
4. Follow `core/` modules referenced by the skill — never restate them inline.
