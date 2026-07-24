---
description: Reset OpenHands state - stop containers, clear session state, keep run records
argument-hint: [--hard]
---

# /amir:openhands_reset

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.openhands.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Inventory first, then confirm: list what will be affected (`docker ps -a` filtered to openhands app + runtime containers; `.amir/state/openhands/app-state` size). Show the list and get explicit confirmation — reset is destructive to sessions.
2. Check for unsaved work: if any runtime container has a mounted project tree with uncommitted changes, STOP and surface them (`git status` in the mount) before touching the container. Never destroy uncommitted agent work without the user seeing it.
3. Soft reset (default):

```powershell
docker stop openhands-app
docker ps -aq --filter name=openhands-runtime | ForEach-Object { docker rm -f $_ }
```

   Clear session/conversation state in `.amir/state/openhands/app-state` (delete contents, keep the dir). PRESERVE `.amir/state/openhands/runs/` — run records and evaluations are project history.
4. Hard reset (`--hard`, second confirmation required): additionally remove the app container and pulled images (`docker rmi` the openhands and agent-server images). State the disk space reclaimed and that the next setup re-downloads everything.
5. Report exactly what was stopped, removed, and preserved, with the post-state of `docker ps -a`.
