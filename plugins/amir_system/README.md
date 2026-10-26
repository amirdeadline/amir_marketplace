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

Orchestration & context: `/amir:use_subagents`, `/amir:user_subagents2`, `/amir:amir_critical`,
`/amir:amir_doc_review`, `/amir:amir_humanized`, `/amir:no-slop`, `/amir:btw`, `/amir:cleanup_context`,
`/amir:amir_handoff`, `/amir:amir-project-cleanup`, `/amir:amir_agent_notification`

Graphify (manifest-gated): `/amir:graphify`, `/amir:graphify_setup`, `/amir:graphify_build`,
`/amir:graphify_update`, `/amir:graphify_query`, `/amir:graphify_explain`,
`/amir:graphify_status`, `/amir:graphify_impact`, `/amir:graphify_architecture`,
`/amir:graphify_clean`, `/amir:graphify_disable`

Asana: `/amir:asana_status`, `/amir:asana_auth_check`

Help: `/amir:help`

## Skills

`create_project`, `onboard_project`, `use_subagents`, `user_subagents2`, `amir_critical`,
`amir_doc_review`, `amir_humanized`, `amir_handoff`, `btw`, `cleanup_context`, `system_rules`, plus
user-provided exact names `create-project-doc`, `no-slop`, `amir-project-cleanup`,
and `amir_agent_notification`.
`amir_cursor_subagent` (`/amir:amir_cursor_subagent`, user scope `/amir_cursor_subagent`) runs one bounded
task on the Cursor AI agent installed on this PC: Composer 2.5 fast by default, any Cursor model via
`--model`/`--param`; Claude writes the brief, launches `skills/amir_cursor_subagent/scripts/run_cursor_subagent.ps1`
and verifies the result.
`amir_project_artifact` (`/amir:amir_project_artifact`, user scope `/amir_project_artifact`) creates one
private claude.ai tracker artifact per project (Overview, Plan, Tasks, Questions, Mind map, Logs on a shared
database; task edit, cancel and side chat) and installs `CLAUDE.md` rules plus a Stop hook so every agent keeps it current.
`/amir:btw` redirects to Cursor native `/btw` or `/side` (does not answer in-session).
`user_subagents2`, `amir_critical`, `amir_handoff`, `amir_doc_review`,
`amir_humanized`, `amir-project-cleanup`, and `amir_agent_notification` are also
installed at user scope under
`%USERPROFILE%\.cursor\skills\` and `%USERPROFILE%\.claude\skills\` (`/user_subagents2`,
`/amir_critical`, `/amir_handoff`, `/amir_doc_review`, `/amir_humanized`,
`/amir-project-cleanup`, `/amir_agent_notification`).

### Prisma SD-WAN SME and official documentation pair

`amir_prisma_sdwan` (evidence-first Prisma SD-WAN answers from the local Palo Alto KB) and
`amir_official_doc` (numbered, checked, human-written Markdown documents with an evidence register) are
user-scope skills for both tools. One real copy lives in `skills/`; directory junctions in
`%USERPROFILE%\.claude\skills\` and `%USERPROFILE%\.cursor\skills\` point at it, created and verified by
`scripts\install-user-skills.ps1` (`-Verify` reports only). Each skill folder has a README.

Platform notes: Claude Code supports stacking (`/amir_prisma_sdwan /amir_official_doc <request>`) and
fills `${CLAUDE_SKILL_DIR}`; Cursor attaches one skill per `/` pick and shows the SKILL.md path, so each
skill loads its partner itself when a task needs both. Cursor's documentation asks for hyphenated names;
underscore names are accepted by Cursor 3.22 (as with `amir_humanized`). The plugin copy
(`/amir:amir_prisma_sdwan`) appears only after the plugin cache is updated.

### Prisma SD-WAN SME knowledge layer

`amir_prisma_sdwan_sme` is the curated reasoning layer above `amir_prisma_sdwan`: a synced copy of the
Prisma SD-WAN SME research corpus (58 notes with claims registers, 14 worked scenarios, term index, question
router, source catalog, gap register) where every claim is labelled VERIFIED / CORROBORATED / INFERRED /
UNVERIFIED / CONFLICTED / OBSOLETE with an evidence type (DOC / SCENARIO / LAB). `scripts/sme.py` looks up
routes, notes, scenarios, terms, gaps and sources without loading the corpus; `scripts/sync_knowledge.py`
refreshes `knowledge/` from the research workspace and writes a SHA-256 manifest. Same junction install as
the pair above (`scripts\install-user-skills.ps1`); Python-only automation examples. See its README.

### Prisma SD-WAN training architect

`amir_prisma_sdwan_training` designs Prisma SD-WAN curricula (Basic five-day course through advanced SME path) on the `amir_prisma_sdwan_sme` knowledge layer, maps exercises to the documented Prisma SASE lab with READY / PARTIAL / MISSING / UNVERIFIED statuses, validates schedules with `scripts/check_schedule.py`, and stops for approval after the curriculum structure. Same junction install. See its README.

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
