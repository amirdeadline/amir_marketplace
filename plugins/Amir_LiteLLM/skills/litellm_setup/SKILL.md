---
name: litellm_setup
description: "One-time setup of the Amir_LiteLLM toolkit on a machine — deploy the installer to ~/.amir/litellm, copy litellm_* skills into Cursor, set the gateway base URL, and guide the user to store their LiteLLM key as an env var. Use for \"litellm setup\", \"set up LiteLLM MCP\", or when ~/.amir/litellm/litellm_mcp.py is missing."
---

# litellm_setup

1. **Deploy** from the plugin checkout (Claude Code: `${CLAUDE_PLUGIN_ROOT}`; otherwise the
   `Amir_LiteLLM` folder in the amir marketplace):
   ```
   python "<plugin>/scripts/litellm_mcp.py" deploy --cursor-skills
   ```
   This copies the installer + `servers.json` to `~/.amir/litellm/`, the `litellm_*` skills and
   **`amir_use_litellm_subagent`** to `~/.cursor/skills/`, and slash commands (including
   `/amir_use_litellm_subagent`) to `~/.cursor/commands/`.
   For the subagent skill, install [workspaces-venv](https://github.com/amirdeadline/workspaces-venv)
   first (`install.py`) and configure palo LiteLLM credentials (`litellm --api-token`, `litellm --models`).
2. **Base URL.** Show it with `python ~/.amir/litellm/litellm_mcp.py config`. Default is
   `https://api.mcp.pan.dev`. Only change it if the user gives a different gateway URL:
   `... config --base-url <url>` (or set env `LITELLM_MCP_BASE_URL`).
3. **API key.** The user runs this themselves in their own terminal (hidden prompt). Never ask for the
   key in chat, never print it, never put it in a file in a repo:
   ```
   python ~/.amir/litellm/litellm_mcp.py set-key
   ```
   On Windows it becomes the user env var `LITELLM_MCP_API_KEY`. Claude Code and Cursor must be fully
   quit and reopened to see it.
4. Offer next steps: `litellm_install_confluence` (or another `litellm_install_*`), then
   `litellm_mcp_gateway_status`.
