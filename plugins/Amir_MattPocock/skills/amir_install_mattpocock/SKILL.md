---
name: amir_install_mattpocock
description: >-
  Installs the curated set of 13 Matt Pocock engineering skills into the current
  project (grill-with-docs, research, to-spec, to-tickets, implement-spec, tdd,
  code-review, handoff, wait-what, wizard, wayfinder, grill-me, to-questionnaire).
  Use when the user invokes /amir_install_mattpocock or asks for the default Matt
  Pocock engineering workflow skills locally.
disable-model-invocation: true
---

# Install selected Matt Pocock skills (project-local)

Install **only** the 13 skills listed in `config/selected-skills.json`. Does not remove other Matt Pocock skills already installed (for example after `/amir_install_mattpocock_all`).

## When to run

- User message is `/amir_install_mattpocock` or equivalent.

## Steps

1. Resolve project root (git root if present, else workspace root).
2. Resolve the installer script (prefer plugin checkout):
   - Claude Code: `$env:CLAUDE_PLUGIN_ROOT\scripts\install-mattpocock.ps1`
   - Cursor: `$env:CURSOR_PLUGIN_ROOT\scripts\install-mattpocock.ps1`
   - Else: `plugins/Amir_MattPocock/scripts/install-mattpocock.ps1` in the amir marketplace clone, or a vendored `amir-mattpocock-installers/scripts/` tree in the project.
3. Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<installer-root>\scripts\install-mattpocock.ps1" `
  -Mode Selected `
  -ProjectRoot "<project-root>"
```

4. If any requested skill is missing upstream, **report it** with evidence from the discovery step. Do **not** substitute a different skill without explicit user approval.
5. Preserve unrelated project skills and non-Matt-Pocock name collisions (installer skips overwrites).

## Curated list

Defined in `amir-mattpocock-installers/config/selected-skills.json` (13 skills).

## Verification

```powershell
pwsh -NoProfile -File "<path-to>/amir-mattpocock-installers/scripts/verify-installation.ps1" -Scope Selected
```
