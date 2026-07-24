# Amir Marketplace — Component Map (authoritative)

Architecture: two marketplace plugins. Both declare plugin.json `"name": "amir"` so every command
surfaces as `/amir:{name}` in Claude Code (verified empirically 2026-07-24: two plugins with distinct
marketplace IDs may share plugin.json name; command sets must stay disjoint — enforced by this file).
Marketplace entry IDs are `amir_system` and `amir_project`; no plugin's *identity* is bare `amir`.

- `amir_system` — installed at USER scope (Claude Code `--scope user`; Cursor via `~/.cursor/plugins/local/amir_system` junction). Available before any project exists.
- `amir_project` — NEVER auto-enabled. Installed per-project (`--scope project`) or rendered as a component subset by the renderer during `/amir:create_project` / `/amir:onboard_project`.

Naming rules: all commands `/amir:{snake_case}`. Exception (user-specified exact name): skill `create-project-doc`.
No hyphen/underscore twin variants. Deprecation aliases are temporary and print a warning.

## amir_system command inventory

| Command | Kind | Origin |
|---|---|---|
| `/amir:create_project` | skill+command | new (spec §4.1 interactive workflow) |
| `/amir:onboard_project` | skill+command | new (spec §4.2) |
| `/amir:use_subagents` | skill+command | new (spec §4.3; supersedes harness `use_subagent`) |
| `/amir:list_projects` | command | new (spec §4.4; registry at `~/.amir/registry/projects.json`) |
| `/amir:cleanup_context` | skill+command | new (spec §4.5; supersedes harness `compact`) |
| `/amir:graphify` | command | new (spec §4.6 interactive hub) |
| `/amir:graphify_setup` | command | graphify wrapper |
| `/amir:graphify_build` | command | graphify wrapper |
| `/amir:graphify_update` | command | graphify wrapper |
| `/amir:graphify_query` | command | graphify wrapper |
| `/amir:graphify_explain` | command | graphify wrapper |
| `/amir:graphify_status` | command | graphify wrapper |
| `/amir:graphify_impact` | command | graphify wrapper (uses `graphify affected`) |
| `/amir:graphify_architecture` | command | graphify wrapper |
| `/amir:graphify_clean` | command | graphify wrapper |
| `/amir:graphify_disable` | command | graphify wrapper |
| `/amir:configure_project` | command | retained from v1 spec (manifest editing) |
| `/amir:validate_project` | command | retained (validator) |
| `/amir:repair_project` | command | retained (drift repair) |
| `/amir:list_components` | command | retained (catalog browser) |
| `/amir:update_catalog` | command | retained (git pull catalog + marketplace update) |
| `/amir:remove_project_config` | command | retained |
| `/amir:project_status` | command | moved from harness (project health report) |
| `/amir:help` | command | retained |
| `/amir:asana_status` | command | new (MCP health-check, spec §6.1) |
| `/amir:asana_auth_check` | command | new (auth check, spec §6.1) |
| `/amir:plugins_list` | command | new (user request 2026-07-24: available plugins table — name, source, summary) |
| `/amir:project_list_plugins` | command | new (project's enabled plugins table) |
| `/amir:project_add_plugin` | command | new (resolve → render → lock pipeline for one addition) |
| `/amir:project_disable_plugin` | command | new (manifest disable + stale cleanup; data preserved by default) |
| `create-project-doc` | skill (`/amir:create-project-doc`) | user-provided verbatim 2026-07-24 |
| 9 × `asana_*` skills | skills | migrated from amir-asana plugin: `asana_complete_task, asana_create_task, asana_daily_triage, asana_priorities_today, asana_review_tasks, asana_standup, asana_sync_from_report, asana_update, asana_update_task` |

Plus: rules/ (7 system rules: project-isolation, tool-scope, security-secrets, honest-execution,
goal-preservation, context-control, destructive-action) as Cursor `.mdc` + Claude skill `system_rules`;
MCP servers: `asana` (migrated existing implementation), `playwright` (official `@playwright/mcp`);
tools/: registry.py, renderer.py, validator.py, catalog.py (Python 3.12).

## amir_project component groups (all disabled by default; manifest-selected)

| Group | Commands (`/amir:` + name) | Origin |
|---|---|---|
| harness | `agent_reset, btw, build_agents, build_goal, design, design_agents, design_qa, docs_sync, document_max, git_commit, git_push, git_setup, git_tree, handoff, milestone_retro, plan, project_cleanup, project_cost, project_tasks, project_watch, resume_build, rollback, security_scan, tasks_update, troubleshoot` | renamed from plugin `amir` (kept snake_case) |
| harness (deprecated aliases) | `project_create→create_project, project_import→onboard_project, use_subagent→use_subagents, compact→cleanup_context, project_doctor→validate_project, project_status→(moved to system)` | temporary alias stubs w/ deprecation notice; removal at amir_project 1.0 |
| harness (retired) | `system_cleanup, system_settings, system_skills, user_cleanup, user_settings, user_skills` | violate project-scope principle; retired (documented) |
| aws | `aws_cli, aws_whoami` | amir-aws |
| azure | `azure_cli, azure_whoami` | amir-azure |
| cortex-xdr | `xdr_ask, xdr_incidents, xdr_preflight, xdr_respond` | amir-cortex-xdr |
| docker | `docker_build, docker_down, docker_logs, docker_push, docker_status, docker_up` | amir-docker |
| elastic | `elastic_ask, elastic_preflight, elastic_search` | amir-elastic |
| litellm | `litellm_chat, litellm_models, litellm_session, litellm_spend, litellm_status` | amir-litellm |
| nmap | `nmap_parse, nmap_scan` | amir-nmap |
| paloalto | `panos_api, panos_ask, panos_preflight` | amir-paloalto |
| prisma | `prisma_api, prisma_ask, prisma_design, prisma_review, prisma_troubleshoot, prisma_update_index, prisma_whats_new` | amir-prisma |
| qradar | `qradar_aql, qradar_ask, qradar_preflight` | amir-qradar |
| sentinel | `sentinel_ask, sentinel_preflight, sentinel_query` | amir-sentinel |
| splunk | `splunk_ask, splunk_preflight, splunk_search` | amir-splunk |
| ssh | `ssh_copy, ssh_run, ssh_session` | amir-ssh |
| terraform | `terraform_apply, terraform_destroy, terraform_fmt, terraform_init, terraform_plan, terraform_validate` | amir-terraform (+ hook) |
| wireshark | `wireshark_analyze, wireshark_capture, wireshark_extract, wireshark_filter` | amir-wireshark |
| serena | `serena_setup, serena_status, serena_index, serena_find_symbol, serena_find_references, serena_analyze_symbol, serena_refactor, serena_validate, serena_disable` | NEW (spec §8.1, official Serena MCP) |
| context7 | `context7_setup, context7_status, context7_lookup, context7_library, context7_version_docs, context7_validate, context7_disable` | NEW (spec §8.2) |
| semgrep | `semgrep_setup, semgrep_status, semgrep_scan, semgrep_scan_changed, semgrep_scan_dependencies, semgrep_scan_secrets, semgrep_security_gate, semgrep_explain, semgrep_fix, semgrep_validate, semgrep_disable` | NEW (spec §8.3) |
| langfuse | `langfuse_setup, langfuse_status, langfuse_start, langfuse_stop, langfuse_trace, langfuse_evaluate, langfuse_dataset, langfuse_experiment, langfuse_cost_report, langfuse_validate, langfuse_disable` | NEW (spec §8.4) |
| openhands | `openhands_setup, openhands_status, openhands_sandbox, openhands_run, openhands_compare, openhands_evaluate, openhands_logs, openhands_reset, openhands_validate, openhands_disable` | NEW (spec §8.5) |
| worktrees | `worktree_create, worktree_list, worktree_assign, worktree_status, worktree_validate, worktree_merge, worktree_cleanup, worktree_repair` | NEW (spec §8.6) |
| swebench | `swebench_setup, swebench_status, swebench_prepare, swebench_run, swebench_evaluate, swebench_compare, swebench_report, swebench_cleanup` | NEW (spec §8.7) |
| terminalbench | `terminalbench_setup, terminalbench_status, terminalbench_prepare, terminalbench_run, terminalbench_evaluate, terminalbench_compare, terminalbench_report, terminalbench_cleanup` | NEW (spec §8.8) |

Existing plugin skills carry over into their groups with underscore names (e.g. `amir-aws-cli-safety` → `aws_cli_safety`,
`amir-prisma-*` → `prisma_*`). Skill folders keep large `references/` intact (esp. prisma corpus skills).

## Collision resolution (defects fixed by this map)

`ask`×7 → group-prefixed; `preflight`×6 → group-prefixed; `cli`/`whoami`×2 → aws_/azure_; `search`×2 → elastic_/splunk_;
`session`×2 → litellm_/ssh_; `status`×2 → docker_/litellm_; `api`×2 → panos_/prisma_; harness `plan/design/troubleshoot`
keep bare names, terraform/prisma variants prefixed. Verified disjoint: no duplicate command name within or across
amir_system ∪ amir_project.

## Other fixes bundled into migration

1. `plugins/amir/hooks/hooks.json` broken path `../../tools/secrets_scan.js` → `${CLAUDE_PLUGIN_ROOT}/tools/secrets_scan.js`.
2. `PRISMA_DOCS_PATH` hardcoded `E:\PC3_Shared\Palo\Documents\Markdowns Prisma SASE` → env var `PRISMA_DOCS_PATH` with documented default, single definition in `components/prisma/README.md`.
3. Stale `catalog/hosts.json` → regenerated from catalog.json.
4. amir-asana `.env` token → moved to `%USERPROFILE%\.amir\secrets\asana.env`; never in repo (assert via secrets scan before any push).
5. litellm/prisma READMEs `cd` into nonexistent dirs → corrected paths.
