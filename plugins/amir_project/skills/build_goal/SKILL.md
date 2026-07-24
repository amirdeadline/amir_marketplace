---
name: build_goal
description: "Execute the full goal delivery loop: from parsed goal through architecture, QA design, task execution, per-task worker/QA cycles, drift checks, and milestone QA — using state tools for all transitions."
---

# build_goal

Follow the procedure in the host-agnostic amir skill file `skill-specs/build_goal.md`.

**Resolve path:** `<amir-root>/skill-specs/build_goal.md` where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).

1. Read the skill file completely.
2. Execute per its **Behavior** section.
3. Use `node tools/*.js` from the amir `tools/` directory.
4. Follow `core/` modules referenced by the skill — never restate them inline.
