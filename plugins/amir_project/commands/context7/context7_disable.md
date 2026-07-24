---
description: Remove the Context7 integration from this project (key preserved unless deleted)
---

# /amir:context7_disable

## Gate

Read `.amir/project.yaml`. If the manifest is missing, stop and point to `/amir:configure_project`. May run even when already disabled, for cleanup.

## Steps — project integration only

1. Unregister: `claude mcp remove context7` (project scope). If registration exists at user scope, ask before touching it.
2. Set `project_tools.context7.enabled: false` in `.amir/project.yaml` with a dated note ("disabled by context7_disable").
3. Credentials: PRESERVE `%USERPROFILE%\.amir\secrets\context7.env` by default (it may serve other projects). Only delete it on an explicit user yes, and remind them they can also revoke the key at https://context7.com/dashboard.
4. Do not uninstall Node or clear the npx cache — system scope, out of bounds here.
5. Report what was removed, what was preserved, and the new manifest state.
