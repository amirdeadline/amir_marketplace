---
name: litellm_uninstall
description: "Remove one or more litellm-* MCP servers from Claude Code and/or Cursor (config backups are kept). Use for \"remove confluence MCP\", \"uninstall litellm server\", \"litellm uninstall\"."
---

# litellm_uninstall

1. Confirm with the user which server(s) and which host(s) (`claude`, `cursor`, `both`).
2. Run:
   ```
   python ~/.amir/litellm/litellm_mcp.py uninstall <server...> --host both
   ```
   Cursor edits leave a timestamped `mcp.json.bak-*` next to the file. Claude uses `claude mcp remove -s user`.
3. It does not touch `LITELLM_MCP_API_KEY`. Only remove that env var if the user explicitly asks.
4. Tell the user to restart Claude Code / reload Cursor MCP.
