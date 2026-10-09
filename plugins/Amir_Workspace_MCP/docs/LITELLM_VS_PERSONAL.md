# LiteLLM gateway MCP vs personal-token MCP

| | **Amir_LiteLLM** (`litellm-*`) | **Amir_Workspace_MCP** (`palo-*`) |
|---|--------------------------------|-----------------------------------|
| Auth | `LITELLM_MCP_API_KEY` | `CONFLUENCE_API_TOKEN`, `JIRA_TOKEN`, `ASANA_TOKEN` in palo |
| Transport | Remote HTTP MCP on corporate gateway | Local stdio (`node` + Python) |
| VPN | Usually required for `api.mcp.pan.dev` | VPN for Palo Atlassian DC sites |
| Best for | Standardized gateway tooling, shared server implementations | Your personal PATs already in palo venv |

Both can be installed at once — **names must differ** (`litellm-confluence` vs `palo-confluence`).

**Claude models via LiteLLM** (`litellm` launcher + `ANTHROPIC_BASE_URL`) are unrelated to MCP auth; MCP servers connect independently.
