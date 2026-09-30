---
name: litellm_install_gcp_bq
description: "Install the `gcp_bq` MCP server from the Palo Alto LiteLLM MCP gateway into Claude Code and/or Cursor (BigQuery datasets, tables, dry-run cost, SQL). Use when the user says \"litellm_install_gcp_bq\", \"install gcp_bq\", or \"add gcp_bq MCP\"."
---

# litellm_install_gcp_bq

Registers the `gcp_bq` MCP server as a native remote MCP server named **`litellm-gcp-bq`** in Claude Code
(user scope, `~/.claude.json`) and/or Cursor (`~/.cursor/mcp.json`). The API key is never written
to a config file: Claude reads `${LITELLM_MCP_API_KEY}` and Cursor reads `${env:LITELLM_MCP_API_KEY}`
when they connect.

**Risk:** Queries cost money: always run `check_query_scan_amount` before `execute_query`.

## Steps

1. **Locate the installer.** Use `~/.amir/litellm/litellm_mcp.py`. If it is missing, deploy it from the
   plugin checkout (in Claude Code: `${CLAUDE_PLUGIN_ROOT}/scripts/litellm_mcp.py`; otherwise find
   `Amir_LiteLLM/scripts/litellm_mcp.py` in the amir marketplace):
   ```
   python "<plugin>/scripts/litellm_mcp.py" deploy --cursor-skills
   ```
2. **Choose the host.** Default `--host both`. Use `--host claude` or `--host cursor` if the user asked for one.
   Add `--scope project --project-dir <dir>` only if the user wants it for a single project.
3. **Install:**
   ```
   python ~/.amir/litellm/litellm_mcp.py install gcp_bq --host both
   ```
4. **Key check.** The output says whether `LITELLM_MCP_API_KEY` is set. If it is NOT set, tell the user to run
   this themselves in their own terminal (hidden input). Never ask for the key in chat, never echo it:
   ```
   python ~/.amir/litellm/litellm_mcp.py set-key
   ```
5. **Verify live** (needs the Palo Alto VPN):
   ```
   python ~/.amir/litellm/litellm_mcp.py status gcp_bq --probe
   ```
   Report exactly what happened: tool count on success, or the real error (network / VPN, HTTP 401 key,
   HTTP 404 wrong server name or base URL). Do not claim success without a probe result.
6. **Tell the user to restart** Claude Code (or run `/mcp` → reconnect) and, in Cursor, reload MCP
   (Settings → MCP). Tools then appear as `mcp__litellm-gcp-bq__<tool>` in Claude.

Usage reference: `docs/servers/` in the Amir_LiteLLM plugin, and `docs/USING_TOOLS.md`.
