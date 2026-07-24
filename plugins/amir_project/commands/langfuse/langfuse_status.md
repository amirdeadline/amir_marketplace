---
description: Report Langfuse mode, connectivity, and tracing health for this project
---

# /amir:langfuse_status

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.langfuse.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Checks (report each separately)

1. Mode from manifest (hosted | self_hosted | disabled) and the configured host (from the secrets env file — print the HOST only, never the keys).
2. Credentials present: `Test-Path "$env:USERPROFILE\.amir\secrets\langfuse.env"` and that it defines the three names (LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY / LANGFUSE_HOST). Presence only — never echo values.
3. Self-hosted only: `docker compose ps` in the langfuse deployment dir; containers healthy; UI port answering.
4. Auth: `langfuse.auth_check()` via a short Python snippet returns true.
5. Recent activity: query the API for trace count in the last 24h (or report "no traces yet"). Distinguish "connected but idle" from "unreachable".
6. Config hygiene: sampling rate and redaction settings in use; warn if redaction of prompts is off while the project marks its source proprietary.

Suggest `/amir:langfuse_setup` or `/amir:langfuse_validate` for failures; `/amir:langfuse_start` if self-hosted containers are down.
