---
description: Verify the Asana token works (get_me) — reports identity, never prints the token
---

# /amir:asana_auth_check

Checks that the Asana MCP server has a valid token. The token variable is `ASANA_ACCESS_TOKEN`,
loaded by the runner from `%USERPROFILE%\.amir\secrets\asana.env` (OS env takes precedence).

## Procedure

1. Call the `asana` MCP server's `get_me` tool.
2. Interpret the result:
   - **Success** → report authenticated user (name, gid, email as returned) and workspace count
     via `list_workspaces`. Auth is VALID.
   - **Token error** (the server returns a readable missing/invalid-token message) → auth is NOT
     configured or the token is invalid/revoked. Point to setup:
     1. `New-Item -ItemType Directory -Force "$env:USERPROFILE\.amir\secrets"`
     2. Put `ASANA_ACCESS_TOKEN=<token>` in `%USERPROFILE%\.amir\secrets\asana.env`
        (token from Asana → Settings → Apps → Developer Console)
     3. Restart Claude Code / reconnect MCP, then re-run this command.
   - **Server unreachable / tools missing** → this is a server problem, not an auth problem;
     run `/amir:asana_status` for diagnostics.
3. Also report (presence only): `Test-Path "$env:USERPROFILE\.amir\secrets\asana.env"` and
   whether `ASANA_ACCESS_TOKEN` is set in the OS environment
   (`[bool]$env:ASANA_ACCESS_TOKEN` — boolean only).

## Absolute constraints (security-secrets rule)

- NEVER print, echo, log, or partially display the token value — not even a prefix, suffix, or
  length. Presence booleans and the variable NAME only.
- NEVER read the secrets file's contents into the conversation.
- If the user pastes a token into chat, warn them it is now exposed in conversation history and
  recommend revoking and re-issuing it; help them place the NEW one via the steps above (typed
  by them, not by you).
- Read-only: this command performs no Asana writes.
