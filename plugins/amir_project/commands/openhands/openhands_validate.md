---
description: Validate the OpenHands integration and prove the sandbox policy holds
---

# /amir:openhands_validate

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.openhands.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Validation matrix (run all; pass/fail per line)

1. Docker: `docker info` succeeds (via WSL where applicable); images present (`docker images` shows the recorded openhands + agent-server tags from `.amir/state/openhands/setup.md`).
2. App starts: container reaches running state and `http://localhost:3000` answers (start it for the check if the user confirms, stop after if it was down).
3. Sandbox policy proof (the core check — inspect, do not assume). For a running or freshly started runtime container:

```powershell
docker inspect <runtime-container> --format '{{json .HostConfig.Privileged}} {{json .HostConfig.NetworkMode}} {{json .Mounts}}'
```

   Assert: Privileged is false; network mode matches the manifest (`none` when policy says disabled); Mounts contain the project path and NOTHING under the user's home (no `.ssh`, `.aws`, browser profiles); no environment variables carrying credentials (`docker inspect --format '{{json .Config.Env}}'` — scan names/values for token patterns, report matches as CRITICAL without printing values).
4. Isolation smoke test (network-disabled policy only): exec a trivial network attempt inside the runtime container and confirm it FAILS (e.g. a curl to a public IP times out). A sandbox that can reach the network under a network:disabled policy is a failed validation.
5. State: `.amir/state/openhands/` structure intact (setup record, runs index).
6. Resource headroom: free RAM/disk vs the documented requirements; warn when thin.

Verdict "healthy and policy-conformant" only when 1-5 pass. Any policy check failure is CRITICAL: recommend immediate `/amir:openhands_reset` and setup correction. Report facts from the actual inspect output.
