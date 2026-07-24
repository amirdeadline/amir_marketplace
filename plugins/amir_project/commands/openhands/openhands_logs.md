---
description: Collect and summarize OpenHands app and run logs
argument-hint: [run label | "app"] [--tail N]
---

# /amir:openhands_logs

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.openhands.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Scope from `$ARGUMENTS`: a run label (agent/runtime events for that session), or `app` (the OpenHands application container), default: latest run.
2. App logs:

```powershell
docker logs openhands-app --tail 200
```

3. Run logs: the event stream for the session (from the state dir the app was configured with, `.amir/state/openhands/app-state`, or via `docker logs` on the runtime container while it lives). Copy the relevant slice into `.amir/state/openhands/runs/<label>/logs/` so it survives container removal — runtime containers are ephemeral; logs not captured now are gone after cleanup.
4. Summarize rather than dump: actions taken (commands run, files edited), errors and their context, retries, any policy-relevant events (network attempts while network is disabled — flag these as CRITICAL policy signals), token/cost lines if present.
5. Secrets hygiene: scan the extracted log slice for credential-looking strings before storing/showing; redact matches and note the redaction. Never paste raw logs containing secrets into chat.
6. Report where the preserved logs live and the summary. If logs are unavailable (container gone, nothing captured), say exactly that.
