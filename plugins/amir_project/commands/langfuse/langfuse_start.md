---
description: Start the self-hosted Langfuse stack (docker compose)
---

# /amir:langfuse_start

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.langfuse.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. This command applies to `mode: self_hosted` only. For `hosted`, report that Langfuse Cloud needs no local start and stop.
2. Locate the deployment (default `%USERPROFILE%\.amir\tools\langfuse`, or the path recorded in the manifest note). If absent, point to `/amir:langfuse_setup`.
3. Verify Docker is running (`docker info` exits 0); if not, ask the user to start Docker Desktop — do not change system services yourself.
4. Start:

```powershell
Set-Location "$env:USERPROFILE\.amir\tools\langfuse"
docker compose up -d
docker compose ps
```

5. Wait for readiness: poll `http://localhost:3000/api/public/health` (or check `docker compose logs --tail 20 langfuse-web` for "Ready"); first start can take 2-3 minutes.
6. Report actual container states from `docker compose ps` — only claim "running" when the web service answers. Include the UI URL and a reminder that tracing still requires the SDK env keys.
