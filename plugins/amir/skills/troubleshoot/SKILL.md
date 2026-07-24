---
name: amir-troubleshoot
description: >-
  Interactive human-controlled troubleshooting (amir marketplace). Read-only
  diagnostics without approval; state-changing fixes require plan and approval.
  Slash: /amir:troubleshoot {problem}.
---

# troubleshoot

Follow the procedure in the host-agnostic amir skill file `skill-specs/troubleshoot.md`.

**Resolve path:** `<amir-root>/skill-specs/troubleshoot.md` where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).

1. Read the skill file completely.
2. Execute per its **Behavior** section.
3. Classify commands with `templates/troubleshoot/command-classifier.md`.
4. Follow `core/question-format.md` and `core/honesty-rules.md` — never restate them inline.
