# MCP Gateway Local Configuration

The **local `mcp-gateway`** on your work machine brokers all requests to the 12 downstream servers. It reads a config file at `~/.mcp-gateway/user-config.json` that lists each server's credentials and which tools to enable/disable.

## File location

```
C:\Users\<username>\.mcp-gateway\user-config.json
```

## How it works

1. You configure credentials in `user-config.json` (once, per server).
2. The gateway reads this file on startup and loads it into memory.
3. When Claude Code or Cursor calls a tool like `confluence_search`, the gateway:
   - Receives the request over stdio (from Claude) or HTTP (from a remote client).
   - Looks up the server config (e.g., `mcp_confluence`).
   - Injects the configured env vars (CONFLUENCE_URL, CONFLUENCE_API_TOKEN, ...) into the downstream server's environment.
   - Calls the downstream server and returns the result.
4. Your actual API keys never leave `~/.mcp-gateway/` — they stay in memory on that machine.

## Setup steps

### 1. Create the directory (if it doesn't exist)

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.mcp-gateway"
```

### 2. Copy the template config file

Download or copy `mcp-gateway-user-config.json` from this plugin (the `docs/` folder) to your work machine:

```powershell
Copy-Item "mcp-gateway-user-config.json" "$env:USERPROFILE\.mcp-gateway\user-config.json"
```

### 3. Fill in credentials

Edit `~/.mcp-gateway/user-config.json` and add your actual API keys, tokens, and URLs:

| Server | What to add | Where to get it |
|---|---|---|
| **confluence** | `CONFLUENCE_URL`, `CONFLUENCE_USERNAME`, `CONFLUENCE_API_TOKEN` | Atlassian account settings → API tokens |
| **jira** | `JIRA_BASE_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN` | Atlassian account settings → API tokens |
| **asana** | `ASANA_PAT` | Asana Settings → Apps → Developer Console |
| **gitlab** | `GITLAB_HOST`, `GITLAB_TOKEN` | GitLab user settings → Personal Access Tokens |
| **google_workspace** | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI` | Google Cloud Console → OAuth 2.0 credentials |
| **cortex_bot** | `CORTEX_API_KEY`, `CORTEX_API_KEY_ID`, `CORTEX_TENANT_FQDN` | Cortex XSIAM → Advanced API → Key ID + Key |
| **cortex_mcp** | `CORTEX_API_KEY`, `CORTEX_API_KEY_ID`, `CORTEX_TENANT_FQDN` | Cortex XDR → API → Advanced → Key ID + Key |
| **gcp_bq** | `GOOGLE_APPLICATION_CREDENTIALS`, `GCLOUD_PROJECT_ID` | GCP Service Account key (.json file path) |
| **figma_desktop** | *(none)* | Requires Figma desktop app running |
| **playwright** | `PLAYWRIGHT_HOST`, `PLAYWRIGHT_PORT` | Local development (default localhost:3000) |
| **chrome_devtools** | `CHROME_BIN`, `CHROME_LOG_FILE` | Path to Chrome/Chromium binary |
| **secure_fetch** | *(none)* | No credentials needed |

### 4. Disable high-risk tools (optional but recommended)

The template already disables destructive Cortex tools in `cortex_bot`. If you want to further restrict access, add tool names to `disabled_tools`:

```json
"mcp_gitlab": {
  "env": { ... },
  "disabled_tools": ["push_files", "create_merge_request", "cancel_pipeline"]
}
```

### 5. Restart the gateway

On the work machine:

```powershell
# Stop any running mcp-gateway process
Stop-Process -Name "mcp-gateway" -Force -ErrorAction SilentlyContinue

# Restart Claude Code or Cursor, which auto-starts the gateway
```

## Verifying the config

Run this on the work machine (or via `litellm_mcp_gateway_status` in Claude):

```bash
python ~/.amir/litellm/litellm_mcp.py status --probe
```

If any server shows a tool count (e.g., `"tool_count": 4`), the config for that server is working.

## Secrets best practice

- Never commit `user-config.json` to git.
- Add `~/.mcp-gateway/` to `.gitignore`.
- The config file stays on your work machine; it never syncs to this repo or anywhere else.

## If a server isn't connecting

1. Check that the config file has the right credentials:
   ```powershell
   cat "$env:USERPROFILE\.mcp-gateway\user-config.json"
   ```
2. Verify the API key / token is still valid (some services rotate keys).
3. Check the gateway logs (if logging is enabled in the config).
4. Run `status --probe` to see the real error from the server.
