# Installing gateway MCP servers

## Prerequisites

- Python 3.9+ on PATH (`python`), and the `claude` CLI for Claude Code installs.
- A LiteLLM virtual key with MCP access, stored as env var **`LITELLM_MCP_API_KEY`**.
- **Palo Alto VPN.** `api.mcp.pan.dev` resolves to an internal address; off-VPN every call fails.

## Commands (`~/.amir/litellm/litellm_mcp.py`)

| Command | What it does |
|---|---|
| `deploy [--cursor-skills]` | Copy the script + `servers.json` to `~/.amir/litellm`; copy `litellm_*` skills + `amir_use_litellm_subagent` and slash commands to Cursor |
| `config [--base-url URL]` | Show or set the gateway base URL (default `https://api.mcp.pan.dev`; env `LITELLM_MCP_BASE_URL` wins) |
| `set-key` | Interactive, hidden. Stores `LITELLM_MCP_API_KEY` as a Windows user env var (prints instructions on macOS/Linux) |
| `list` | All servers, risk level, and whether each is installed in Claude / Cursor |
| `install <server...> [--host claude\|cursor\|both] [--scope user\|project] [--project-dir D]` | Register servers |
| `uninstall <server...> [--host ...]` | Remove them (Cursor file backed up first) |
| `status [server...] [--probe]` | Env, network/VPN, install state; `--probe` opens a live MCP session and lists tools |
| `tools <server>` | List a server's tools live |
| `call <server> <tool> '<json args>'` | Call one tool from the terminal (testing without restarting a host) |

Server keys: `confluence, jira, asana, gitlab, google_workspace, cortex_bot, cortex_mcp, gcp_bq,
figma_desktop, playwright, chrome_devtools, secure_fetch`, `gateway` (all in one entry), or `all`.

## URL and auth model

> **Status 2026-09-28: not yet verified against the real gateway.** On VPN, `https://api.mcp.pan.dev`
> answers `/health` and `/api` ("MCP Gateway Management API") but returns 404 for `/<server>/mcp` and `/mcp`.
> That host is a management API used by a local `mcp-gateway` client, not a direct MCP endpoint. Set the
> real MCP URL with `config --base-url` (and `remote` names in `servers.json`) once it is known, then
> re-run `install`.

Each server is `<base>/<remote-name>/mcp` (LiteLLM's per-server MCP route); the aggregated gateway is
`<base>/mcp`. Auth header: `x-litellm-api-key: Bearer <key>`. If your gateway uses different server names,
edit `remote` in `servers.json` and re-run `install`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `not reachable (internal address...)` | Connect to the Palo Alto VPN |
| `LITELLM_MCP_API_KEY ... NOT SET` / HTTP 401 | Run `set-key`, then fully restart the app |
| HTTP 404 | Wrong base URL or remote server name (`config`, `servers.json`) |
| Installed but no tools in the host | Restart Claude Code (`/mcp` → reconnect); Cursor: Settings → MCP → refresh |
| Cursor on macOS doesn't see the key | `launchctl setenv LITELLM_MCP_API_KEY ...` then relaunch Cursor |
