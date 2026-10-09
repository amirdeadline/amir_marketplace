---
name: workspace_mcp_setup
description: "One-time deploy of Amir_Workspace_MCP to ~/.amir/workspace_mcp and optional Cursor skills. Use for workspace MCP setup, palo Confluence/Jira/Asana tokens."
---

# workspace_mcp_setup

1. Confirm tokens exist on palo: `CONFLUENCE_API_TOKEN`, `JIRA_TOKEN`, `ASANA_TOKEN` (names only — never print values).
2. Deploy from plugin checkout:
   ```
   python "<Amir_Workspace_MCP>/scripts/workspace_mcp.py" deploy --cursor-skills
   ```
3. Point user to `docs/INSTALL.md` for `install all --host all-hosts`.
4. Verify with:
   ```
   python ~/.amir/workspace_mcp/workspace_mcp.py status all --probe
   ```
