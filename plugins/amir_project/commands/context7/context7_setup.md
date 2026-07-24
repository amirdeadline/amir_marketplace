---
description: Register the Context7 MCP server for version-accurate library docs
---

# /amir:context7_setup

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.context7.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Mode

Read `project_tools.context7.mode` (`mcp` | `cli`). Default is `mcp`. Official source: https://github.com/upstash/context7.

## Prerequisites

```powershell
node --version
npx --version
```

Node.js is required for the local MCP server (`npx @upstash/context7-mcp`). If Node is missing, stop and report it — do not install Node without the user arranging it.

## API key (optional, account-dependent)

Context7 works without an API key at lower rate limits. A free key from https://context7.com/dashboard raises limits. If the user wants a key:

- Store it OUTSIDE the repo, e.g. `%USERPROFILE%\.amir\secrets\context7.env` as `CONTEXT7_API_KEY=...`. Never write the key into `.amir/project.yaml`, plugin files, or any tracked file. Reference it by env var only.

## Register (requires network; ask for explicit confirmation first)

Local MCP server for Claude Code:

```powershell
claude mcp add context7 -- npx -y "@upstash/context7-mcp"
```

If a key is configured, pass it via env (`claude mcp add context7 --env CONTEXT7_API_KEY=$env:CONTEXT7_API_KEY -- npx -y "@upstash/context7-mcp"`), reading the value from the secrets file at registration time — never hardcode it.

Alternative documented transport: remote endpoint `https://mcp.context7.com/mcp` with the key sent as the `CONTEXT7_API_KEY` header. Use only if the user prefers no local Node process; note it sends every query to Upstash directly.

CLI mode: the documented CLI is `npx ctx7` (`ctx7 library <name> <query>`, `ctx7 docs <libraryId> <query>`); `npx ctx7 setup` runs an OAuth flow that creates a key — do NOT run it without explicit user confirmation, since it authenticates and writes credentials.

## Health check (mandatory)

1. `claude mcp list` shows `context7` connected, or the remote endpoint answers.
2. Perform one real lookup: resolve a library id for a dependency this project actually uses and fetch a one-topic doc snippet. The result must be non-empty.

Report honestly: "configured and healthy" only after the live lookup succeeds. Otherwise report the failing step. Nothing outside the project is modified except the npx cache and the optional secrets file the user approved.
