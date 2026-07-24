---
description: Show the amir_system command reference and how the pieces fit together
argument-hint: [command-name]
---

# /amir:help

If `$ARGUMENTS` names a specific command (with or without the `/amir:` prefix), read that command
file from this plugin's `commands/` directory and summarize: what it does, arguments, prerequisites
(manifest gates, credentials), and what it will never do. Otherwise show this overview:

## amir_system â€” user-scope commands

**Project lifecycle**
- `/amir:create_project` â€” interactive new-project creation (interview â†’ plan â†’ confirm â†’ build)
- `/amir:onboard_project` â€” adopt an existing repo (discovery â†’ recommendations â†’ safe migration)
- `/amir:list_projects` â€” registry listing/search/health (`~/.amir/registry/projects.yaml`)
- `/amir:project_status` â€” health report for the current project
- `/amir:configure_project` â€” edit the project manifest (`.amir/project.yaml`) safely
- `/amir:validate_project` â€” run the validator (schema, locks, naming, isolation, drift)
- `/amir:repair_project` â€” fix drift/missing generated files (never changes selections)
- `/amir:remove_project_config` â€” remove Amir-managed files from a project (backup first)

**Catalog**
- `/amir:list_components` â€” browse `catalog/catalog.json`
- `/amir:update_catalog` â€” refresh catalog + marketplace

**Orchestration & context**
- `/amir:use_subagents` â€” bounded, verifiable subagent task decomposition
- `/amir:cleanup_context` â€” durable context handoff into `.ai/` docs

**Graphify** (all gated by `.amir/project.yaml` â†’ `project_tools.graphify.enabled`)
- `/amir:graphify` â€” interactive hub; plus `graphify_setup`, `graphify_build`, `graphify_update`,
  `graphify_query`, `graphify_explain`, `graphify_status`, `graphify_impact`,
  `graphify_architecture`, `graphify_clean`, `graphify_disable`

**Asana**
- `/amir:asana_status` â€” MCP server health (reachable, tool list, interpreter, deps)
- `/amir:asana_auth_check` â€” token validity via get_me (never prints the token)
- 9 `asana_*` skills for task management (priorities, review, standup, triage, create/update/
  complete, sync-from-report, backlog sync)

**Rules**: 7 system rules ship as `rules/*.mdc` (Cursor) and the `system_rules` skill (Claude):
project-isolation, tool-scope, security-secrets, honest-execution, goal-preservation,
context-control, destructive-action.

Note honestly when something is unavailable on this machine (missing `amirctl.py`, missing
catalog, missing graphify CLI, missing Asana token) instead of guessing.
