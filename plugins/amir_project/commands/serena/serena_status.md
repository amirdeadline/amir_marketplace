---
description: Report Serena installation, registration, and index health for this project
---

# /amir:serena_status

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.serena.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Checks (run all, report each separately — never collapse into a single "OK")

```powershell
Get-Command uv -ErrorAction SilentlyContinue
Get-Command serena -ErrorAction SilentlyContinue
serena --version
claude mcp list
Test-Path .serena
```

Report, per the manifest state model (installed / available / enabled / configured / healthy):

1. Binary installed: does `serena` resolve, and what version.
2. MCP registered: does `claude mcp list` include `serena`, and is it connected.
3. Project configured: does `.serena/` exist in the project root; is `.serena/cache/` gitignored.
4. Language support: list the project's primary languages and whether Serena's LSP backend supports them.
5. Index freshness: if `.serena/cache/` exists, report its last-modified time versus the latest source change.

If any check fails, state exactly which and suggest `/amir:serena_setup` or `/amir:serena_index`. Do not report healthy on partial success.
