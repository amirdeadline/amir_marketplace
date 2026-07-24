---
description: Install and register the Serena MCP server (LSP-based symbol tools) for this project
---

# /amir:serena_setup

## Gate

Read `.amir/project.yaml` in the project root. If the manifest is missing, or `project_tools.serena.enabled` is not `true`, stop immediately and tell the user to run `/amir:configure_project` first. Do not install anything.

## Prerequisite check

Serena's only officially supported install path is `uv` (official source: https://github.com/oraios/serena — `uv tool install -p 3.13 serena-agent`). Check what exists:

```powershell
Get-Command uv -ErrorAction SilentlyContinue
Get-Command serena -ErrorAction SilentlyContinue
```

- If `serena` already resolves: skip to Health check.
- If `uv` is missing (this machine has no uv and no pipx by default): report that Serena requires uv, show the official Windows install command, and ASK THE USER FOR EXPLICIT CONFIRMATION before running it (network access + install outside the project):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

  Source: https://docs.astral.sh/uv/getting-started/installation/. After install, a new shell may be needed for PATH; verify with `uv --version`. Do not fall back to `pip install serena-agent` — it is not the documented install path; if the user insists, mark the install as unofficial in your report.

## Install Serena (after user confirmation)

```powershell
uv tool install -p 3.13 serena-agent
serena --version
```

## Register the MCP server (after user confirmation)

For Claude Code, per-project registration (run from the project root):

```powershell
claude mcp add serena -- serena start-mcp-server --context claude-code --project "$PWD"
```

For other hosts, the launch command is `serena start-mcp-server --context <client> --project <abs-path>`.

## Project configuration

- Serena stores per-project data in `.serena/` inside the project root — this is the only approved data location. Ensure `.serena/cache/` is gitignored (ask before editing `.gitignore`).
- Verify the project's languages are supported by Serena's language-server backend (Python, TypeScript/JavaScript, Java, Rust, Go, C/C++, and ~40 others). If the project's primary language is unsupported, say so plainly and recommend leaving Serena disabled — do not claim partial support works.

## Health check (mandatory before claiming success)

1. `serena --version` exits 0.
2. `claude mcp list` shows `serena` as connected (or run `serena start-mcp-server --context claude-code --project "$PWD"` briefly and confirm it binds without error, then stop it).
3. Optionally run `serena project index` to pre-index and confirm the language server starts for this project.

Honest-execution rule: report "installed and healthy" only if the checks above passed. If any check failed, report exactly which one and why, and leave the manifest unchanged. Nothing outside the project may be modified except the uv tool install itself and Serena's documented caches.
