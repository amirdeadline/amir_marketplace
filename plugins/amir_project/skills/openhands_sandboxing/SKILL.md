---
name: openhands_sandboxing
description: >-
  OpenHands sandbox policy for amir projects: hard isolation limits, default
  policy block, verification-by-inspection, honest resource reporting.
---

# openhands_sandboxing

OpenHands (https://docs.openhands.dev) runs autonomous coding agents in docker containers. In amir projects it is an experimentation sandbox, gated on `project_tools.openhands.enabled` — never a default execution path.

## Default policy block (SPEC §8.5 — the safe baseline)

```yaml
project_tools:
  openhands:
    enabled: false
    sandbox:
      project_mount: read_write   # the selected project only; read_only for observe-runs
      home_mount: false
      privileged: false
      network: disabled
      credentials: none
```

## Hard limits (not configurable by asking nicely)

1. NEVER mount the user's home directory (or `.ssh`, `.aws`, browser profiles, secret stores) into agent workspaces.
2. No credential forwarding into sandboxes — no token env vars, no mounted keychains. The LLM key lives in the OpenHands app settings, entered by the user, and stays app-side.
3. No privileged containers, ever.
4. Network disabled by default; enabling it requires the manifest to say so explicitly.
5. Mount ONLY the selected project. Prefer mounting a dedicated git worktree (`/amir:worktree_create`) so agent writes land on an isolated branch.
6. Never auto-install or auto-launch OpenHands per project — it starts on demand via the commands, after confirmation.

## Trust by inspection, not by configuration

A policy is only as real as the running container. Verification (`/amir:openhands_validate`) inspects actual containers: `docker inspect` for Privileged/NetworkMode/Mounts/Env, plus a live negative test (network attempt must FAIL under network:disabled). A policy violation found in a running container is CRITICAL: stop the container, report, correct setup. Note the honest caveat: OpenHands' architecture needs the docker socket mounted into the APP container to spawn runtimes — that is real power; the user must knowingly accept it at setup.

## Resources and platform

App minimum ~4 GB RAM plus several GB of images; each runtime container adds load. On this Windows machine everything runs inside WSL 2 with Docker Desktop integration. Report requirements before installing, and actuals (`docker stats`) when asked.

## Results discipline and fallback

Agent claims are not results: acceptance criteria are verified by running the project's tests yourself (`/amir:openhands_evaluate`). Run records live in `.amir/state/openhands/runs/` and are preserved through resets. If OpenHands is unavailable (no docker, no resources), the fallback is ordinary supervised editing in a worktree — smaller steps, same tests; do not simulate "what the agent would have done".
