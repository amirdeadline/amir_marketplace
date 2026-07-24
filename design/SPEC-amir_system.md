# SPEC — amir_system plugin (user scope, Claude Code + Cursor)

Plugin dir: `plugins/amir_system`. plugin.json: `{"name": "amir", "version": "1.0.0", ...}` (namespace `/amir:`).
Marketplace entry ID: `amir_system`. Keep small, stable, security-conscious. No admin/machine-level install.
Contains ONLY capabilities needed before a project exists: create/onboard/orchestrate/inspect/manage + machine-level integrations (Asana, Playwright, Graphify wrappers).

Command files: `commands/<name>.md` with frontmatter `description` (+ `argument-hint` where useful).
Skill dirs: `skills/<name>/SKILL.md` for the complex flows (create_project, onboard_project, use_subagents, cleanup_context, system_rules; create-project-doc already exists — DO NOT modify it).
Rules: `rules/*.mdc` (Cursor consumes these via plugin; Claude gets the same content via the `system_rules` skill).

## Core skill requirements

### /amir:create_project (spec §4.1)
Interactive project creation. Ask ONE focused question at a time. Collect: name, parent dir, description,
business goal, technical goal, languages, frameworks, package manager, build system, app type, repo strategy,
Cursor y/n, Claude Code y/n, project plugins, skills, MCP servers, connectors, rules, agents, testing reqs,
security reqs, network-access, secret-access, then per-tool selection: Graphify, Serena, Context7, Semgrep,
Langfuse, OpenHands, Git worktrees, SWE-bench, Terminal-Bench.
For every category: display available catalog options (read `catalog/catalog.json`), short explanation, why
useful, supported hosts, dependencies, required credentials, network requirements, security implications,
performance implications, recommendations based on project evidence (advisory only — never auto-select).
Selection controls: Select recommended / individually / all / none, Search, Show details, Go back,
Review configuration, Cancel safely.
Secure default: no optional MCP servers, no connectors, no network access, no secret access, no telemetry,
no external evaluation, no automatic global indexing.
Before writing files: show final configuration plan (project path, hosts, plugins, skills, MCPs, connectors,
rules, agents, per-tool status, network/secret permissions, credentials still required, files created/modified,
dependencies installed). Require final confirmation before destructive/credential/network-enabling actions.
After approval: create project → write `.amir/project.yaml` (schema v2) → resolve dependencies (tools/validator)
→ write `.amir/components.lock.json` → install ONLY selected components (render via tools/renderer.py or
`claude plugin install amir_project@amir-marketplace --scope project` when full plugin selected) → generate
Cursor project files → generate Claude project files → init docs (`ai/`) → git init if selected → worktrees
config if selected → run validation (tools/validator.py) → report exact results. Register project in
`~/.amir/registry/projects.json`. NEVER report a component installed unless its executable/integration was
actually tested (run its health_check from catalog.json).

### /amir:onboard_project (spec §4.2)
Discovery: repo root, git status/branches/worktrees, languages, frameworks, deps, build/test systems, CI/CD,
containers, IaC, entry points, existing rules/skills/agents/MCP/connectors, existing Graphify/Serena/Context7/
Semgrep config, observability, benchmarks, AI docs, Cursor config, Claude config, secrets (detect presence only,
NEVER read/expose values). Classify each optional component: Strongly recommended / Recommended / Optional /
Not useful / Unsupported / Already configured / Conflicting / Requires migration — evidence-based (cite files).
Recommendation heuristics: Playwright↔web app w/ browser flows; Semgrep↔external input or credentials handling;
Serena↔supported language + medium/large repo; Context7↔external libs/APIs; Graphify↔medium/large/modular/
multi-service; Langfuse↔LLM/agent workflows; OpenHands↔sandboxed autonomous coding; SWE-bench↔issue-resolution
eval; Terminal-Bench↔terminal-agent eval; worktrees↔parallel agents.
Migration behavior: back up existing AI config (into `.amir/backups/<ts>/`), preserve valid config, MERGE not
overwrite, detect collisions, detect global config leaking into project, write manifest+lock, install only
selected, render both hosts, validate startup + isolation, produce `.amir/onboarding/onboarding-report.md`
(existed-before / preserved / migrated / added / disabled / skipped / failed / manual-config-needed /
missing credentials / active in Cursor / active in Claude Code).

### /amir:use_subagents (spec §4.3)
Read project goal + manifest + rules → decompose into ordered, independently verifiable tasks → one bounded
context package per subagent → separate git worktrees when parallel code modification (only if worktrees
enabled in manifest) → never give every agent the whole repo → per-task: acceptance criteria, allowed paths,
prohibited paths, required tests, required evidence → agents must not change the project end goal → merge only
validated work → record decisions/results in ai/ docs. Graphify/Serena usable only when manifest-enabled.

### /amir:list_projects (spec §4.4)
Registry `~/.amir/registry/projects.json` — non-secret metadata only: id, name, root, type, cursor_enabled,
claude_enabled, last_validation, last_opened, manifest_path, enabled_component_ids. Supports list, search,
status, detect missing dirs, detect moved projects, re-register, remove stale entries, open selected, run
validation. NEVER scan the whole computer; use registered roots only. Do not duplicate manifests in registry.

### /amir:cleanup_context (spec §4.5)
Durable context handoff, NOT fake context clearing. Extract: durable facts, completed work, pending work,
decisions, risks, unresolved questions, modified files, validation evidence, rollback info. Update ai/status.md,
ai/tasks.md, ai/decisions.md, ai/risks.md, ai/context_handoff.md. Handoff must state: project goal, current
task/state, completed, pending, files changed, files to read first, commands already run, tests passed/failed,
known risks, do-not-change list, next exact action. Recommend fresh session when degradation likely. Never
claim context was cleared unless a new session actually started.

### /amir:graphify (spec §4.6) + graphify_{name} wrappers
Hub: detect current project → check manifest `project_tools.graphify.enabled` → check `graphify` CLI installed
(pip package graphifyy; CLI at Python312 Scripts on this machine) → check graph health/freshness
(`graphify-out/graph.json` mtime vs source; `graphify update` supported) → present operations → invoke scoped
wrapper. Never scan outside project root without approval; never register project in a global graph
(`graphify global add`) without explicit approval.
Wrappers call the system CLI (verified subcommands, v0.8.33): `install --project --platform claude|cursor`,
`update [--force]`, `query`, `path`, `explain`, `affected`, `cluster-only`, `tree`, `uninstall`, `hook
install|uninstall|status`. graphify_setup: verify install, run project-scoped platform installs, write
include/exclude config honoring manifest excludes, ensure graphify-out/ gitignored unless project commits it,
manage the auto-registered PreToolUse hooks per manifest update_policy (manual → remove hooks). graphify_build:
full build via /graphify skill flow (project-local `.claude/skills/graphify`), respect .gitignore + manifest.
graphify_update: incremental; record timestamp + source commit; never claim current on failure. graphify_query/
graphify_explain: answer from graph, cite source_location, fall back to repo inspection when graph missing/stale.
graphify_impact: `graphify affected` + graph traversal; distinguish graph evidence from inference. 
graphify_architecture: generate/update ai/architecture.md (module map, dependency map, entry points, data flows,
external systems); never replace manual decisions without review. graphify_status: enabled?, CLI version, last
build, source commit, staleness, ignored dirs, output size; never silently rebuild. graphify_clean: remove only
this project's graphify-out/ after showing exactly what's removed; preserve config unless asked. graphify_disable:
run `graphify uninstall` per platform in project, update manifest+lock, preserve/archive output, never touch CLI
or other projects.

### Management commands (retained from v1): configure_project, validate_project, repair_project,
list_components, project_status, update_catalog, remove_project_config, help — thin commands that drive
tools/*.py and catalog.json. repair_project fixes drift/missing generated files only, never changes selections.
remove_project_config: backup → show deletion plan → remove only Amir-managed files → preserve unrelated
Cursor/Claude config and project docs → never uninstall Graphify globally.

### Asana (spec §6.1): MCP migrated from existing implementation (see mcp/ notes in repo). Health commands
asana_status (server reachable, tool list) and asana_auth_check (token valid via get_me equivalent; never print
token). Default read-only posture: destructive/write ops require confirmation (rule 7.7). Token via env
ASANA_ACCESS_TOKEN (existing implementation's variable — VERIFY in source; spec suggests
ASANA_PERSONAL_ACCESS_TOKEN, use existing name if different), loaded from `%USERPROFILE%\.amir\secrets\asana.env`;
never in repo/manifest/logs.

### Playwright (spec §6.2): official `@playwright/mcp` via `npx @playwright/mcp@latest` (verify exact form from
official docs before finalizing). Isolated browser profiles (`--isolated`), never personal profiles/credentials.
Artifacts inside project, gitignored unless selected. Availability ≠ authorization: manifest
`system_capabilities.playwright.allowed` gates use (rule 7.2).

## System rules (rules/*.mdc + skills/system_rules) — spec §7 verbatim intent
1 project-isolation, 2 tool-scope (check .amir/project.yaml before Graphify/Playwright/Asana/etc; globally
available ≠ enabled; Asana allowed for system-level PM when explicitly requested), 3 security-secrets (never
display/commit secrets; env vars/secret stores; confirm writes to external systems; confirm network enable; no
unreviewed remote scripts; verify package identity), 4 honest-execution (never claim untrue runs/tests; separate
completed/failed/skipped/blocked; state unsupported directly; preserve evidence), 5 goal-preservation, 6
context-control (bounded subagents; persist durable facts; trigger /amir:cleanup_context before degradation),
7 destructive-action (explicit approval before: delete files, remove plugins, replace configs, force-reset git,
rewrite history, push, publish, change external systems, modify Asana, expose MCP over network, clear
unrecreatable data).

## tools/ (Python 3.12, stdlib + pyyaml + jsonschema)
- catalog.py: load/validate catalog.json; component lookup; dependency resolution (requires,
  optional_dependencies, conflicts_with, supported_hosts, supported_operating_systems, required_executables,
  required_credentials, network_access, secret_access, min/max host version); reject missing deps, unsupported
  host, missing credentials, rejected permissions, incompatible versions, conflicts.
- renderer.py: manifest → rendered outputs. Claude: `.amir/generated/claude/plugins/amir_project/` (plugin.json
  name "amir", selected command/skill/agent/hook/mcp subset) + project-settings registration via `claude plugin
  marketplace add <generated marketplace> --scope project` + install; full-selection fast path = install
  amir_project@amir-marketplace --scope project. Cursor: `.cursor/commands/amir_<name>.md` (flat; colon illegal
  on Windows), `.cursor/rules/amir_*.mdc`, `.cursor/mcp.json` (merge-preserve unrelated entries). Generated-file
  header comment in every rendered file. Preserve user files; drift detection via lock checksums; dry-run mode;
  regeneration idempotent.
- validator.py: manifest schema validation (schemas/project-manifest.schema.json), lock checksums, naming
  compliance (/amir: + underscore), duplicate command detection, host compatibility, MCP definitions, secret
  references (never values), graphify health, project isolation (no writes outside root), drift report.
- registry.py: ~/.amir/registry/projects.json CRUD per §4.4.
- migrate.py: detect old `amir`/`amir-ai`/`amir-asana` installs; map to amir_system/amir_project; backup;
  compatibility notes.

## State/manifest distinctions (spec §9): installed_at_system_scope ≠ available_to_project ≠ enabled_in_project
≠ authorized_write ≠ configured ≠ healthy. Manifest schema v2 in schemas/project-manifest.schema.json (see
SPEC-amir_project-tools.md for the full schema example).
