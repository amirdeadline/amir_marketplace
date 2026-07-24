---
description: Health-check the Asana MCP server — reachable, tool list, interpreter, dependencies (never prints the token)
---

# /amir:asana_status

Health check for the plugin's `asana` MCP server (Python FastMCP server launched by
`mcp/asana/run-mcp.js`).

## Checks (in order; report each honestly)

1. **MCP registration**: is the `asana` server connected in this session? If its tools
   (`get_me`, `list_workspaces`, `list_my_tasks`, ... 17 total) are available, list their count
   and names briefly. If not connected, say so and continue with the environment diagnostics.
2. **Server reachability**: call the lightest tool available (`list_workspaces` or `get_me`).
   A response — even a token error — proves the server process runs. Report exactly which case
   occurred: (a) responds with data → healthy; (b) responds with token error → server healthy,
   auth NOT configured (point to `/amir:asana_auth_check` and the setup in
   `mcp/asana/README.md`); (c) no response/tools missing → server not running.
3. **Interpreter/deps** (when the server is not running, diagnose):
   - `node --version` (runner needs Node)
   - Python resolution mirrors `run-mcp.js`: `mcp\asana\.venv\Scripts\python.exe` if present,
     else system `python.exe`. Report which one would be used.
   - Dependency probe on that interpreter:
     `python -c "import mcp, httpx, dotenv; print('deps ok')"`.
     If it fails, report the missing venv/deps honestly and give the rebuild command from
     `mcp/asana/README.md`:
     `python -m venv .venv; .venv\Scripts\python.exe -m pip install -r requirements.txt`
     (run inside the plugin's `mcp\asana\` directory).
4. **Secrets file presence**: does `%USERPROFILE%\.amir\secrets\asana.env` EXIST (Test-Path
   only)? Report exists/missing. NEVER read it, NEVER print any part of its contents, NEVER
   echo the token variable's value. The variable NAME is `ASANA_ACCESS_TOKEN` — the name may be
   mentioned, the value never.

## Output

A short status table: server connected? / tools count / auth state / interpreter path /
deps ok? / secrets file present? — followed by the single most useful next action. State
explicitly which checks were not run and why (honest-execution rule).
