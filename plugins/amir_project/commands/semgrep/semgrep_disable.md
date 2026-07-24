---
description: Remove the Semgrep integration from this project (findings preserved by default)
---

# /amir:semgrep_disable

## Gate

Read `.amir/project.yaml`. If the manifest is missing, stop and point to `/amir:configure_project`. May run when already disabled, for cleanup.

## Steps — project integration only

1. If Guardian/MCP is registered for this project: `claude mcp remove semgrep` (and note that the Guardian plugin itself, if installed via the plugin marketplace at user scope, is user-scope — ask before uninstalling it there).
2. Remove any project-local hooks this integration added (check `.claude/settings.json` / hooks files in the project for semgrep entries; show the user the diff before editing).
3. Set `project_tools.semgrep.enabled: false` in `.amir/project.yaml` with a dated note ("disabled by semgrep_disable").
4. Data: PRESERVE `.amir/state/semgrep/` (findings, gate log, remediations) by default — it is audit history. Delete only on an explicit user yes:

```powershell
Remove-Item -Recurse -Force .amir\state\semgrep -Confirm:$false
```

5. Do NOT uninstall the semgrep CLI (pip/uv/docker) — system scope; give the user the command for their install method instead. Do not touch their Semgrep platform account or login token; mention `semgrep logout` for them to run if desired.
6. Report what was removed, preserved, and the new manifest state.
