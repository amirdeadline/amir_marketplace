# amir_system

User-scope plugin of the Amir system (marketplace entry `amir_system`, plugin name `amir`,
namespace `/amir:`). Contains everything needed BEFORE a project exists: project
creation/onboarding, orchestration, context handoff, the project registry, the component
catalog interface, Graphify wrappers, and machine-level integrations (Asana MCP, Playwright
MCP). Per-project components live in the sibling `amir_project` plugin and are never
auto-enabled.

## Install

Claude Code (user scope):

```
claude plugin install amir_system@amir-marketplace --scope user
```

Cursor (junction into the local plugins dir — machine-local path note):

```
cmd /c mklink /J "%USERPROFILE%\.cursor\plugins\local\amir_system" "E:\PC3_Shared\Plugins\amir_marketplace\plugins\amir_system"
```

## Commands

Project lifecycle: `/amir:create_project`, `/amir:onboard_project`, `/amir:list_projects`,
`/amir:project_status`, `/amir:configure_project`, `/amir:validate_project`,
`/amir:repair_project`, `/amir:remove_project_config`

Catalog: `/amir:list_components`, `/amir:update_catalog`

Orchestration & context: `/amir:use_subagents`, `/amir:cleanup_context`

Graphify (manifest-gated): `/amir:graphify`, `/amir:graphify_setup`, `/amir:graphify_build`,
`/amir:graphify_update`, `/amir:graphify_query`, `/amir:graphify_explain`,
`/amir:graphify_status`, `/amir:graphify_impact`, `/amir:graphify_architecture`,
`/amir:graphify_clean`, `/amir:graphify_disable`

Asana: `/amir:asana_status`, `/amir:asana_auth_check`

Help: `/amir:help`

## Skills

`create_project`, `onboard_project`, `use_subagents`, `cleanup_context`, `system_rules`,
plus the user-provided `create-project-doc` (exact name preserved).

## MCP servers

- **asana** — local Python FastMCP server (17 tools), launched via
  `mcp/asana/run-mcp.js`. Token: `ASANA_ACCESS_TOKEN` in
  `%USERPROFILE%\.amir\secrets\asana.env`. See `mcp/asana/README.md`.
- **playwright** — official `@playwright/mcp@latest` via npx with `--isolated`
  (ephemeral browser profile; session storage discarded on close). Availability is not
  authorization: project use is gated by the project manifest
  (`system_capabilities.playwright.allowed`).

## Rules

Seven system rules, always in force, shipped twice: `rules/*.mdc` for Cursor and the
`system_rules` skill for Claude — project-isolation, tool-scope, security-secrets,
honest-execution, goal-preservation, context-control, destructive-action.

## Security model (summary)

- **Manifest gating**: optional tools (Graphify, Playwright, project Asana use, …) require
  `.amir/project.yaml` enablement; globally installed ≠ enabled in a project.
- **Secrets**: values live only in `%USERPROFILE%\.amir\secrets\` or OS env; referenced by name;
  never displayed, committed, or logged. No secrets in this repo.
- **Secure defaults**: new projects get no optional MCP servers, no connectors, no network or
  secret access, no telemetry, no global indexing — every grant is an explicit opt-in.
- **Destructive actions**: plan shown + explicit confirmation required (deletes, config
  replacement, git history rewrites, pushes, external-system writes including Asana).
- **Honest execution**: components are reported installed/healthy only when their health checks
  actually ran and passed; completed/failed/skipped/blocked are always separated.
- **Isolation**: project work never writes outside the project root (except `~/.amir/`), and
  `remove_project_config` never touches user-owned files or global tools.

## Engine dependency

Management commands prefer the deterministic engine
`python "%USERPROFILE%\.amir\bin\amirctl.py" <subcommand>` (provisioned separately by the
amir_system tools). When it is absent, commands say so and either degrade to supervised
read-only/manual mode or stop — they never fake engine results.
