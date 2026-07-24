---
description: Install Semgrep for this project (CLI, MCP, and/or Guardian per manifest)
---

# /amir:semgrep_setup

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.semgrep.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Integration modes (from `project_tools.semgrep.integration`: guardian | mcp | both)

Verified July 2026 against official sources:

- **CLI** (needed for local scans in every mode): official install is via pipx or uv (preferred per https://docs.semgrep.dev/getting-started/quickstart). Native Windows support is BETA and requires Python 3.10+ with UTF-8 encoding; Docker is the fallback. Free, no account needed for `semgrep scan`.
- **Semgrep Guardian** (https://github.com/semgrep/guardian) is Semgrep's Claude Code plugin: MCP server + hooks that scan on every file write. It REQUIRES a Semgrep account login, and in Claude Code it uses Semgrep's hosted remote MCP server by default (findings go through Semgrep's platform). Mark this clearly to the user as account-gated before installing.
- **Semgrep MCP** without Guardian: local MCP wrapping the CLI, no account required for OSS rules.

## Steps

1. Check what exists: `Get-Command semgrep -ErrorAction SilentlyContinue`, `semgrep --version`, `Get-Command pipx, uv, python, docker -ErrorAction SilentlyContinue`.
2. This machine has no pipx and no uv by default. Present the options and ask for EXPLICIT confirmation before any install (network access):
   - `pip install semgrep` into the project's virtualenv (works, but pipx/uv is the documented preference; note the Windows-beta caveat and set `$env:PYTHONUTF8 = '1'`).
   - Install uv first (`powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`) then `uv tool install semgrep`.
   - Docker: `docker run --rm -v "${PWD}:/src" semgrep/semgrep semgrep scan /src` (no local Python needed).
3. If mode includes `guardian`: warn that it needs a Semgrep account and sends findings to the Semgrep platform; on user confirmation, follow the official plugin flow (`/plugin marketplace add semgrep/guardian`, `/plugin install semgrep@semgrep-marketplace`, then `semgrep login` when prompted). Never store the token in the repo; `semgrep login` manages it in the user profile.
4. Create the findings directory `.amir/state/semgrep/` and ensure it is gitignored unless the manifest says otherwise.
5. Policy: read `project_tools.semgrep.policy` (scan_changed_files, scan_before_commit, block_on, scan_secrets, scan_dependencies). Do NOT enforce `block_on` gating until the project has approved the policy — record approval status in the manifest note.

## Health check (mandatory)

1. `semgrep --version` exits 0 (or the docker equivalent runs).
2. A real scan of one small project file completes: `semgrep scan --config p/default <file> --json` returns valid JSON.
3. Guardian mode only: the Semgrep MCP appears connected in `claude mcp list` / plugin status.

Report honestly per check. Local scans do not upload code; state that `semgrep login`/`semgrep ci`/Guardian send FINDINGS (not code) to the platform, and cloud/`--pro` features require explicit opt-in.
