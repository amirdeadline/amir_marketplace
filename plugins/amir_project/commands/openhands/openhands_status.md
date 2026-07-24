---
description: Report OpenHands container, sandbox policy, and resource state
---

# /amir:openhands_status

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.openhands.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Checks (report each separately)

1. Docker available: `docker info` (via WSL on Windows if that is how it was set up).
2. App container: `docker ps --filter name=openhands` — running/stopped, image tag, uptime, port mapping.
3. Runtime containers: `docker ps --filter name=openhands-runtime` (agent sandboxes) — count and ages; flag orphans older than the last known run.
4. Policy conformance audit (concrete, not assumed): `docker inspect` the running containers and verify against the manifest sandbox block — no home directory in `Mounts`, `Privileged: false`, network mode matches policy, only the project path mounted into workspaces. Report any violation as CRITICAL.
5. Resources: `docker stats --no-stream` for the OpenHands containers; disk used by images (`docker images` filtered to openhands/agent-server).
6. State dir: `.amir/state/openhands/` contents (setup record, run logs index).

Suggest `/amir:openhands_setup`, `/amir:openhands_reset`, or `/amir:openhands_validate` as remedies. Never report "sandboxed correctly" without the inspect-based audit in check 4.
