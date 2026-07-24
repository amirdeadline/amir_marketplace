---
description: Stop the self-hosted Langfuse stack (data volumes preserved)
---

# /amir:langfuse_stop

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.langfuse.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Self-hosted mode only; for hosted, nothing to stop.
2. From the deployment dir:

```powershell
Set-Location "$env:USERPROFILE\.amir\tools\langfuse"
docker compose down
```

   NEVER add `-v` by default — `docker compose down -v` deletes the trace database volumes. Only run with `-v` on an explicit user request to destroy data, and confirm once more before doing it (destructive-action rule).
3. Confirm with `docker compose ps` that services are stopped.
4. Report: services stopped, data volumes preserved (list them via `docker volume ls` filtered to the langfuse compose project), and that in-flight SDK events buffered by applications may be lost while the server is down.
