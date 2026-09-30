---
name: litellm_mcp_gateway_status
description: "Health check of the Palo Alto LiteLLM MCP gateway and every litellm-* MCP server installed in Claude Code and Cursor — env key present, base URL, VPN/network reachability, live MCP handshake and tool count. Use for \"mcp gateway status\", \"litellm status\", \"is confluence MCP working\"."
---

# litellm_mcp_gateway_status

Read-only diagnostics. Never prints the API key.

1. Run (add server names to limit, e.g. `confluence jira`):
   ```
   python ~/.amir/litellm/litellm_mcp.py status --probe
   ```
   If the script is missing, run the `litellm_setup` skill first.
2. If this session already has the gateway tools, also call the lightest tool of an installed server
   (e.g. `confluence_search` with `{"query":"test","limit":1}`), or `get_status` on the aggregated
   `mcp-gateway` entry, and report whether the host itself can reach it.
3. Report a short table: server | claude | cursor | live (tool count or error). Then the one next action:
   - `network ... not reachable (internal address)` → connect to the Palo Alto VPN.
   - `LITELLM_MCP_API_KEY ... NOT SET` / HTTP 401 → user runs `litellm_mcp.py set-key` in their own terminal.
   - HTTP 404 → wrong base URL or server name; check with `litellm_mcp.py config` and servers.json.
   - installed but tools missing in the host → restart Claude Code / reload Cursor MCP.
State which checks were skipped and why.
