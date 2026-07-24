---
name: amir-use-subagent
description: >-
  Orchestrate via plan, atomic tasks, dedicated subagents or isolated contexts,
  validation, and verification. Slash: /amir:use_subagent {prompt}. Aliases:
  /use_subagent, trailing trigger. Do not code before planning.
---

# use_subagent

Follow the procedure in the host-agnostic amir skill file `skill-specs/use_subagent.md`.

**Resolve path:** `<amir-root>/skill-specs/use_subagent.md` where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).

1. Read the skill file completely.
2. Execute per its **Behavior** section; use `templates/use_subagent/` and schemas.
3. Host notes: `templates/use_subagent/adapters/codex.md` — default Mode C unless native delegation exists.
4. Never claim native parallel subagents when simulating isolation.
5. Clarifications: `core/question-format.md` (A–E).
