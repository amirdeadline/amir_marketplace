---
description: List the current project's enabled plugins/components as a table
---

# /amir:project_list_plugins

Read-only. Requires an Amir project.

## Procedure

1. Locate the project: nearest ancestor with `.amir/project.yaml`. If none → STOP: "Not an Amir
   project. Use /amir:list_projects to see registered projects, /amir:onboard_project to onboard this
   directory, or /amir:plugins_list to browse what could be enabled."
2. Read the manifest. Collect, without guessing:
   - `plugins.amir_project.components` (component groups)
   - every `project_tools.*` entry with `enabled: true` (graphify, serena, context7, semgrep,
     langfuse, openhands, git_worktrees, swe_bench, terminal_bench)
   - `system_capabilities.*` with `allowed: true` (asana, playwright)
   - `hosts` (cursor / claude_code enabled flags)
3. Cross-check reality (state ≠ manifest): does `.amir/components.lock.json` exist and cover each
   component? Do rendered outputs exist (`.cursor/commands/amir_<group>_*.md`, or the project-scope
   plugin entry in `.claude/settings.json` / `.amir/generated/claude/`)? Prefer the deterministic
   engine for this: `python "$env:USERPROFILE\.amir\bin\amirctl.py" drift` (report MANUAL best-effort
   if amirctl is missing).

## Output — one table, exactly these columns

| Plugin / Component | Kind | Status | Hosts | Notes |
|---|---|---|---|---|

- Kind: `component group` / `project tool` / `system capability`.
- Status: `enabled + rendered` / `enabled, NOT rendered (run /amir:repair_project)` /
  `enabled, lock stale` — from the drift evidence, never asserted without it.
- Hosts: which of cursor / claude_code this project renders for.
- Notes: credential names still unset (presence check only — never values), health-check hints.

If the manifest enables nothing, say exactly that (empty selection is a valid state) and point to
`/amir:project_add_plugin`.
