# amir_system — Asana MCP server

Local MCP stdio server exposing 17 Asana tools (`get_me`, `list_workspaces`,
`list_my_tasks`, `list_priority_tasks_today`, `get_task`, `create_task`,
`update_task`, `complete_task`, `add_comment`, `list_projects`,
`list_project_tasks`, `search_tasks`, `list_project_sections`,
`list_section_tasks`, `add_task_to_section`, `create_subtask`, `list_tags`).

Implementation migrated from `plugins/amir-asana` (Python, FastMCP). The plugin's
`.claude-plugin/plugin.json` registers it as MCP server `asana` via:

```json
"asana": {
  "command": "node",
  "args": ["${CLAUDE_PLUGIN_ROOT}/mcp/asana/run-mcp.js"]
}
```

## How it starts

`run-mcp.js` (Node, no npm dependencies):

1. Loads `%USERPROFILE%\.amir\secrets\asana.env` into the child environment.
   OS-level environment variables always take precedence; the file only fills gaps.
   Values are never printed or logged.
2. Selects a Python interpreter: `mcp\asana\.venv\Scripts\python.exe` if present,
   otherwise system `python.exe` / `python3` / `python`.
3. Spawns `src/asana_connector/server.py` (stdio transport).

## Token setup (exact env var: `ASANA_ACCESS_TOKEN`)

The connector reads the token from the `ASANA_ACCESS_TOKEN` environment variable
(verified in `src/asana_connector/config.py`; resolution order there is
env var → local `.env` → local `CLAUDE.md`, but under amir_system the supported
path is the secrets file below).

1. Create the secrets file (once):

   ```powershell
   New-Item -ItemType Directory -Force "$env:USERPROFILE\.amir\secrets" | Out-Null
   notepad "$env:USERPROFILE\.amir\secrets\asana.env"
   ```

2. Put a single line in it (Asana → Settings → Apps → Developer Console → create token):

   ```
   ASANA_ACCESS_TOKEN=<your personal access token>
   ```

3. Restart Claude Code (or `/mcp` reconnect). Verify with `/amir:asana_auth_check`.

Never commit this file, never paste the token into chat, manifests, or logs.
A leaked token grants full access to your Asana account — revoke it in the
Developer Console immediately if exposed.

## Python dependencies

Runtime deps: `mcp>=1.2.0`, `httpx>=0.27.0`, `python-dotenv>=1.0.0`
(`requirements.txt` in this directory).

Verified on this machine (2026-07-24): system Python 3.12.10 already has
`mcp`, `httpx`, and `dotenv` importable, so the server runs **without any venv**.
If a machine's system Python lacks them, rebuild a local venv:

```powershell
cd <plugin-root>\mcp\asana
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`run-mcp.js` picks up `.venv` automatically. `/amir:asana_status` reports which
interpreter path is in use and whether dependencies import.

## Security posture

- Default read-only usage; write/destructive Asana operations require explicit
  user confirmation (system rule: destructive-action).
- The server talks only to `https://app.asana.com/api/1.0`
  (overridable via `ASANA_BASE_URL` for tests).
- No secret value is ever echoed by the runner, the health commands, or the skills.
