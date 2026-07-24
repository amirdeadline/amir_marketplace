---
name: security_scan
description: "Run secrets scanning and host-native security audit tools; triage findings into `ai/state/risks.json` via `4-security` review."
---

# security_scan

Follow the procedure in the host-agnostic amir skill file `skill-specs/security_scan.md`.

**Resolve path:** `<amir-root>/skill-specs/security_scan.md` where `<amir-root>` is this plugin directory (contains `core/`, `skill-specs/`, and `tools/`).

1. Read the skill file completely.
2. Execute per its **Behavior** section.
3. Use `node tools/*.js` from the amir `tools/` directory.
4. Follow `core/` modules referenced by the skill — never restate them inline.
