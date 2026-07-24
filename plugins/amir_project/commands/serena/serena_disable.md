---
description: Remove the Serena integration from this project (data preserved by default)
---

# /amir:serena_disable

## Gate

Read `.amir/project.yaml`. If the manifest is missing, stop and point to `/amir:configure_project`. (This command may run even if `project_tools.serena.enabled` is already `false`, to clean up leftovers.)

## Steps — project integration only; never uninstall system-wide tools here

1. Unregister the MCP server from this project's host config:

```powershell
claude mcp remove serena
```

   (If it was registered at user scope by an earlier setup, tell the user and ask before touching user scope.)
2. Set `project_tools.serena.enabled: false` in `.amir/project.yaml` and add a short note (date + "disabled by serena_disable") so `/amir:validate_project` can explain the state.
3. Data: PRESERVE `.serena/` by default. Ask the user explicitly whether to delete it; only on a clear yes:

```powershell
Remove-Item -Recurse -Force .serena -Confirm:$false
```

4. Do NOT uninstall the `serena-agent` uv tool or uv itself — those are system-scope and may serve other projects. Mention the command (`uv tool uninstall serena-agent`) for the user to run themselves if they want a full removal.
5. Report exactly what was removed, what was preserved, and the new manifest state.
