---
description: Start a policy-conformant OpenHands sandbox for this project
argument-hint: [task label]
---

# /amir:openhands_sandbox

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.openhands.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Read the sandbox policy block (`project_tools.openhands.sandbox`). Refuse to start if the manifest asks for anything the hard limits forbid (home_mount true, privileged true, credential forwarding) — those need a deliberate manifest change AND an explicit in-chat user confirmation, and privileged stays refused outright.
2. Ensure the app is up (see `/amir:openhands_setup` health check); start it if the user confirms.
3. Configure the workspace for this session: mount ONLY this project's root, mode per `project_mount` (`read_write` default, `read_only` for observe-only experiments). No other host paths. Network per policy (`disabled` default — the agent works offline against the mounted code; enabling network requires the manifest to say so).
4. Credentials: none are forwarded into the sandbox. No env vars carrying tokens, no `.aws`/`.ssh`/browser-profile mounts, ever. The LLM key lives in the OpenHands app settings (user-entered), not in the runtime sandbox.
5. Label the session with `$ARGUMENTS` (or a timestamp) so `/amir:openhands_logs` and `/amir:openhands_evaluate` can find it; record the label, image tags, and policy snapshot in `.amir/state/openhands/runs/<label>/config.md`.
6. Verify before handing over: `docker inspect` the runtime container and confirm mounts/privilege/network match policy. Report the actual inspected values, then give the user the UI URL. If inspection shows a violation, stop the container and report it — do not hand over a non-conformant sandbox.
