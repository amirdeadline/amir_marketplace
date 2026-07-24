---
description: Set up sandboxed OpenHands for this project (docker; strict sandbox policy)
---

# /amir:openhands_setup

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.openhands.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Sandbox policy (from manifest `project_tools.openhands.sandbox`; defaults are the safe block)

Defaults when unspecified: `project_mount: read_write` (project only), `home_mount: false`, `privileged: false`, `network: disabled`, `credentials: none`. These are hard limits: NEVER mount the user's home into the agent workspace, never forward credentials, never run privileged containers, network stays off unless the manifest explicitly enables it.

## Prerequisites

1. `docker info` exits 0 (Docker Desktop running). Official docs (https://docs.openhands.dev/usage/local-setup) note that on Windows the docker run command must execute inside a WSL 2 terminal with Docker Desktop WSL integration — verify `wsl --status` and plan to run via `wsl`.
2. Resources: report before installing — the app itself needs ~4 GB RAM minimum plus disk for the runtime images (several GB); each sandbox runtime container adds CPU/RAM. State this and get confirmation.

## Install / launch (network pulls — explicit user confirmation required first)

Official docker form (verify current tags at docs.openhands.dev before running; as verified 2026-07 the app image is `docker.openhands.dev/openhands/openhands` with an agent-server runtime image configured via env):

```powershell
wsl -e bash -lc "docker run -d --rm --pull=always -e AGENT_SERVER_IMAGE_REPOSITORY=ghcr.io/openhands/agent-server -e AGENT_SERVER_IMAGE_TAG=<current-tag> -e LOG_ALL_EVENTS=true -v /var/run/docker.sock:/var/run/docker.sock -p 3000:3000 --add-host host.docker.internal:host-gateway --name openhands-app docker.openhands.dev/openhands/openhands:<current-version>"
```

Policy adjustments vs the stock command: do NOT mount `~/.openhands` from the real home if `home_mount: false` — use a project-scoped state dir (e.g. `.amir/state/openhands/app-state`) instead; mount ONLY the selected project directory into workspaces. Note honestly: the docker socket mount is required by OpenHands' architecture to spawn runtime containers and is itself a powerful capability — say so, and require the user to accept it.

NEVER auto-launch OpenHands on project open; it starts only via `/amir:openhands_sandbox` / `/amir:openhands_run` on demand. An LLM API key is required for the agent to act — the user enters it in the OpenHands UI/settings themselves; this command never handles the key value.

## Health check (mandatory)

1. `docker ps` shows the container running.
2. `Invoke-WebRequest http://localhost:3000` (or WSL curl) returns the UI.
3. Record the exact image tags used in `.amir/state/openhands/setup.md` for reproducibility.

Report per honest-execution: "installed and healthy" only after checks pass; otherwise the exact failure. Nothing outside the project is written except pulled docker images and the container state.
