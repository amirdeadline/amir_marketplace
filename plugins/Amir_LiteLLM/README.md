# Amir_LiteLLM

Palo Alto **LiteLLM MCP gateway** toolkit that works the same in **Claude Code** and **Cursor**.

- One installer skill per gateway server: `litellm_install_<server>`
- `litellm_mcp_gateway_status`, `litellm_setup`, `litellm_uninstall`
- **`amir_use_litellm_subagent`** — Cursor slash command to delegate to Claude Code via Palo **litellm** (requires [workspaces-venv](https://github.com/amirdeadline/workspaces-venv) + palo credentials)
- Usage skills (starting with `litellm_confluence`) and full tool docs in `docs/`

## How it stays portable

| Concern | Claude Code | Cursor |
|---|---|---|
| Server registration | `claude mcp add-json -s user litellm-<server>` → `~/.claude.json` | `~/.cursor/mcp.json` (merged, backed up) |
| Transport | native remote `http` | native remote `url` |
| Key reference | `x-litellm-api-key: Bearer ${LITELLM_MCP_API_KEY}` | `x-litellm-api-key: Bearer ${env:LITELLM_MCP_API_KEY}` |
| Skills | loaded from this plugin | copied to `~/.cursor/skills/` by `deploy --cursor-skills` (`litellm_*` + `amir_use_litellm_subagent`) |
| Slash commands | — | `commands/*.md` copied to `~/.cursor/commands/` by `deploy --cursor-skills` |
| Subagents | inherit user-scope MCP servers | inherit global MCP servers |

The skills call one stdlib-only script, `~/.amir/litellm/litellm_mcp.py`, so they behave the same in any
host and on Windows, macOS and Linux. The plugin itself does **not** declare `mcpServers`: servers are opt-in
per server, and tool names stay `mcp__litellm-<server>__<tool>` (not plugin-prefixed).

## Quick start

```
python "<this plugin>/scripts/litellm_mcp.py" deploy --cursor-skills
python ~/.amir/litellm/litellm_mcp.py set-key            # run yourself; hidden input
python ~/.amir/litellm/litellm_mcp.py install confluence --host both
python ~/.amir/litellm/litellm_mcp.py status confluence --probe   # needs Palo Alto VPN
```
Then restart Claude Code and reload MCP in Cursor.

See `docs/INSTALL.md` and `docs/USING_TOOLS.md`.
