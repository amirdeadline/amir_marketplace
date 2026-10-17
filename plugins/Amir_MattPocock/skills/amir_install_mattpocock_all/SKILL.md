---
name: amir_install_mattpocock_all
description: >-
  Installs every discoverable Matt Pocock skill from mattpocock/skills into the
  current project for Cursor, Claude Code, Codex, and Hermes Agent. Use when the
  user invokes /amir_install_mattpocock_all or asks to install all Matt Pocock
  skills locally in this repository.
disable-model-invocation: true
---

# Install all Matt Pocock skills (project-local)

Install **all** upstream Matt Pocock skills into **this project only** using the shared PowerShell engine. Skill names are discovered dynamically from the official repository (via the Vercel `skills` CLI `--list`, with a git fallback).

## When to run

- User message is `/amir_install_mattpocock_all` or equivalent natural language ("install all Matt Pocock skills in this project").

## Steps

1. Resolve the project root (git root if present, otherwise the workspace root). Do not assume the shell cwd unless no better root is available.
2. Resolve the installer script (prefer plugin checkout):
   - Claude Code: `$env:CLAUDE_PLUGIN_ROOT\scripts\install-mattpocock.ps1`
   - Cursor: `$env:CURSOR_PLUGIN_ROOT\scripts\install-mattpocock.ps1`
   - Else: marketplace `plugins/Amir_MattPocock/scripts/` or project-vendored `amir-mattpocock-installers/scripts/`.
3. Run non-interactively:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<installer-root>\scripts\install-mattpocock.ps1" `
  -Mode All `
  -ProjectRoot "<project-root>"
```

4. Read the script exit code and console summary. On partial failure, show:
   - missing upstream skills
   - name conflicts (unrelated skills with the same folder name — not overwritten)
   - log path under `.amir/mattpocock-install/logs/`
5. Do **not** install globally (`~/.cursor`, `~/.claude`, etc.). Project-local only.

## Optional flags

- `-DryRun` — log planned actions without changing files.
- `-ForceCopy` — copy skill trees instead of symlinks (Windows fallback).
- `-Agents cursor,claude-code,codex,hermes-agent` — limit target agents.

## Unsupported environments

If `git`, `node`, or `npx` is missing, report clearly and stop. Do not download arbitrary remote install scripts.

## Verification

After install, run:

```powershell
pwsh -NoProfile -File "<path-to>/amir-mattpocock-installers/scripts/verify-installation.ps1" -Scope All
```
