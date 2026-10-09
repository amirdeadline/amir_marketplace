# Amir_Workspace_MCP

Local **stdio MCP servers** for **Confluence**, **Jira**, and **Asana** using **your personal API tokens**
(typically stored in the **palo** workspace `.env`). Works with **Claude Code**, **Cursor**, and **Codex**.

This complements **Amir_LiteLLM** (corporate LiteLLM MCP gateway + `LITELLM_MCP_API_KEY`). Use this plugin when you want direct PAT/token access with names like `palo-confluence`, not `litellm-confluence`.

| Server | MCP name | Token env (palo) | Default base URL |
|--------|----------|------------------|------------------|
| Confluence | `palo-confluence` | `CONFLUENCE_API_TOKEN` | `https://confluence-dc.paloaltonetworks.com` |
| Jira | `palo-jira` | `JIRA_TOKEN` | `https://jira-dc.paloaltonetworks.com` |
| Asana | `palo-asana` | `ASANA_TOKEN` | Asana cloud API |

Full install guide: [`docs/INSTALL.md`](docs/INSTALL.md).

Quick start (after tokens are in palo `.env`):

```powershell
palo
python "E:\PC3_Shared\Plugins\amir_marketplace\plugins\Amir_Workspace_MCP\scripts\workspace_mcp.py" deploy --cursor-skills
python "$env:USERPROFILE\.amir\workspace_mcp\workspace_mcp.py" install all --host all-hosts
python "$env:USERPROFILE\.amir\workspace_mcp\workspace_mcp.py" status all --probe
```
