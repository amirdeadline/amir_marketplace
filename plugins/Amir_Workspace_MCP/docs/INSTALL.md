# Install Amir_Workspace_MCP (Confluence, Jira, Asana)

## What you get

Three **local stdio MCP servers** registered in your agent hosts:

| Key | Registered name | Auth |
|-----|-----------------|------|
| `confluence` | `palo-confluence` | `CONFLUENCE_API_TOKEN` (+ optional `CONFLUENCE_BASE_URL`) |
| `jira` | `palo-jira` | `JIRA_TOKEN` (+ optional `JIRA_BASE_URL`) |
| `asana` | `palo-asana` | `ASANA_TOKEN` (aliases: `ASANA_ACCESS_TOKEN`, `ASANA_PAT`) |

Tokens stay in the **palo workspace** (`WORKSPACES_ROOT/virtual_envs/palo/.env`) or in the OS environment. They are **never** written into `mcp.json` / `.claude.json`.

Each `run-mcp.js` launcher merges palo `.env` into the MCP process (without printing values).

## Prerequisites

- **Node.js** on PATH (`node`) — launches Python MCP backends.
- **Python 3.12+** with `mcp` and `httpx` (palo venv usually has these after `palo` activate).
- Personal API tokens in palo (recommended):

```powershell
palo
venv --var palo --add CONFLUENCE_API_TOKEN <token>
venv --var palo --add JIRA_TOKEN <token>
venv --var palo --add ASANA_TOKEN <token>
```

Optional overrides:

```powershell
venv --var palo --add CONFLUENCE_BASE_URL https://confluence-dc.paloaltonetworks.com
venv --var palo --add JIRA_BASE_URL https://jira-dc.paloaltonetworks.com
```

Re-run `palo` in open terminals after changing variables.

## 1. Add the marketplace plugin (once per machine)

### Claude Code

```text
claude plugin marketplace add E:/PC3_Shared/Plugins/amir_marketplace
claude plugin install Amir_Workspace_MCP@amir-marketplace --scope user
```

### Cursor

```powershell
New-Item -ItemType Junction -Force `
  -Path "$env:USERPROFILE\.cursor\plugins\local\Amir_Workspace_MCP" `
  -Target "E:\PC3_Shared\Plugins\amir_marketplace\plugins\Amir_Workspace_MCP"
```

Then **Developer: Reload Window**.

## 2. Deploy the installer to `~/.amir/workspace_mcp`

From any directory:

```powershell
python "E:\PC3_Shared\Plugins\amir_marketplace\plugins\Amir_Workspace_MCP\scripts\workspace_mcp.py" deploy --cursor-skills
```

This copies runners, Python servers, `servers.json`, and (optionally) Cursor skills.

## 3. Register MCP servers in each agent host

```powershell
python "$env:USERPROFILE\.amir\workspace_mcp\workspace_mcp.py" install all --host all-hosts
```

Host options:

| `--host` | Targets |
|----------|---------|
| `all-hosts` | Claude Code (user), Cursor (`~/.cursor/mcp.json`), Codex (`~/.codex/mcp.json`) |
| `both` | Claude + Cursor only |
| `claude` / `cursor` / `codex` | Single host |

Per-server:

```powershell
python "$env:USERPROFILE\.amir\workspace_mcp\workspace_mcp.py" install confluence jira --host cursor
```

## 4. Verify

```powershell
python "$env:USERPROFILE\.amir\workspace_mcp\workspace_mcp.py" status all --probe
python "$env:USERPROFILE\.amir\workspace_mcp\workspace_mcp.py" list
```

Expected: required env vars show `set`, runners exist, install flags `yes` for chosen hosts.

Then:

- **Claude Code:** quit fully and reopen, or `/mcp` → reconnect. Tools look like `mcp__palo-confluence__confluence_search`.
- **Cursor:** Settings → MCP → refresh.
- **Codex:** restart after `~/.codex/mcp.json` is updated.

## 5. LiteLLM + Claude Code workflow

When you start Claude via `litellm`, models go through the Scale Team proxy; **MCP servers are separate**. After `palo` + `litellm`:

1. Tokens are loaded from palo `env.cmd` into the shell (optional — runners also read palo `.env`).
2. MCP entries point at `node …/run-mcp.js`, which injects palo `.env` again for the child Python process.

You can run **both** gateway MCP (`litellm-*` from Amir_LiteLLM) and personal-token MCP (`palo-*`) if names differ.

## Uninstall

```powershell
python "$env:USERPROFILE\.amir\workspace_mcp\workspace_mcp.py" uninstall all --host all-hosts
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `MISSING` for token in `status` | Add var to palo `.env`, run `palo` again |
| MCP starts but tools error with ⚠️ token | VPN for Atlassian DC; confirm PAT not expired |
| Cursor shows server, no tools | Reload MCP; launch Cursor from a shell where `palo` was run, or rely on palo `.env` merge |
| Python import errors / server exits immediately | In **palo** venv: `pip install "mcp>=1.2.0,<2.0.0" httpx python-dotenv`. **Do not** use `mcp` 2.x with these servers (FastMCP was renamed). Delete any `mcp/*/.venv` that was created with wrong versions — launchers prefer **palo `.venv`**, then system Python. |
| Wrong Confluence/Jira site | Set `CONFLUENCE_BASE_URL` / `JIRA_BASE_URL` on palo |

## Security

- Never commit palo `.env` or paste tokens into chat.
- Asana tools can **create/update** tasks — confirm before writes (see Asana server docs).
- Confluence/Jira tools here are **read-oriented**; still treat wiki/issue content as sensitive.

See also: [`USING_TOOLS.md`](USING_TOOLS.md), [`LITELLM_VS_PERSONAL.md`](LITELLM_VS_PERSONAL.md).
