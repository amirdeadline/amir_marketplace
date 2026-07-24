---
description: Remove the OpenHands integration from this project (run records preserved)
---

# /amir:openhands_disable

## Gate

Read `.amir/project.yaml`. If the manifest is missing, stop and point to `/amir:configure_project`. May run when already disabled, for cleanup.

## Steps — project integration only

1. Check for unfinished work: any live runtime container with uncommitted changes in the mounted tree must be surfaced (`git status`) and resolved with the user before teardown.
2. Stop and remove this project's containers:

```powershell
docker stop openhands-app
docker rm openhands-app
docker ps -aq --filter name=openhands-runtime | ForEach-Object { docker rm -f $_ }
```

3. Set `project_tools.openhands.enabled: false` in `.amir/project.yaml` with a dated note ("disabled by openhands_disable").
4. Data: PRESERVE `.amir/state/openhands/runs/` (history, evaluations) by default. Session state (`app-state`) may be cleared with the containers. Full deletion of run records only on explicit user yes.
5. Images: ask whether to reclaim disk (`docker rmi` the openhands and agent-server images — report sizes first). Default: keep, they are cache. Docker itself and WSL are system scope — never touched here.
6. No credentials were stored by this integration (policy forbids forwarding); if the user entered an LLM key in the OpenHands UI, note that it lived in the app state and is gone with it — recommend rotating the key if the project is decommissioned.
7. Report what was removed, preserved, and the new manifest state.
