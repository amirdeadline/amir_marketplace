---
description: Configure Langfuse tracing for this project (hosted or self-hosted; opt-in only)
---

# /amir:langfuse_setup

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.langfuse.enabled` is not `true`, stop and point to `/amir:configure_project`. Also read `project_tools.langfuse.mode` (hosted | self_hosted | disabled); if `disabled`, stop — the project chose no telemetry.

## Consent rule (absolute)

Never auto-enable telemetry. Before configuring anything, state plainly what will be recorded (model, latency, tokens, cost, retries, tool calls, trace hierarchy) and what will NOT be captured by default (full proprietary prompts/completions — redaction on). Get explicit user confirmation.

## Mode: hosted (Langfuse Cloud — account required; free tier exists, higher volumes paid)

1. The user creates a project at their chosen region and gets keys: EU `https://cloud.langfuse.com`, US `https://us.cloud.langfuse.com` (official: https://langfuse.com/docs).
2. Store keys OUTSIDE the repo: `%USERPROFILE%\.amir\secrets\langfuse.env` containing `LANGFUSE_PUBLIC_KEY=pk-lf-...`, `LANGFUSE_SECRET_KEY=sk-lf-...`, `LANGFUSE_HOST=<region url>`. Never write key values into the manifest or any tracked file — env references only. (SDK v3 also accepts `LANGFUSE_BASE_URL`; set both names to be safe.)

## Mode: self_hosted (free, local, docker compose)

Official local deployment (https://langfuse.com/self-hosting/local); requires Docker. Ask for confirmation before cloning/pulling (network + disk):

```powershell
git clone https://github.com/langfuse/langfuse.git "$env:USERPROFILE\.amir\tools\langfuse"
Set-Location "$env:USERPROFILE\.amir\tools\langfuse"
docker compose up -d
```

UI at `http://localhost:3000` after startup ("Ready" in logs, 2-3 minutes). Change the `# CHANGEME` credentials in docker-compose.yml before first start. Resource note: comfortable at ~4 cores / 8-16 GB for real use; the compose stack is for local/dev, not HA production. Then create a local org/project in the UI and store the generated keys as in hosted mode, with `LANGFUSE_HOST=http://localhost:3000`.

## SDK wiring

Install into the project's environment on confirmation: `pip install langfuse` (Python) or the JS SDK if the project is Node. Configure sampling and redaction per the `langfuse_tracing` skill before first trace.

## Health check (mandatory)

1. Self-hosted: `docker compose ps` shows services up; `Invoke-WebRequest http://localhost:3000/api/public/health` (or opening the UI) succeeds.
2. Both modes: run a Python one-liner that loads the env file and calls `langfuse.auth_check()`; it must return true.
3. Send ONE test trace (clearly named `amir-setup-healthcheck`) and confirm it appears via the API. Only after that may you report "configured and healthy".

Report per the honest-execution rule; on any failure, name the failing step and leave the manifest note reflecting reality.
