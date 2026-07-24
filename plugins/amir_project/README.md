# amir_project

Marketplace entry ID `amir_project`; plugin.json name `amir` (all commands surface
as `/amir:<name>`). NEVER auto-enabled — installed per project (`--scope project`)
or rendered as a component subset during `/amir:create_project` /
`/amir:onboard_project` (both live in the amir_system plugin).

## Structure

- `commands/<group>/<name>.md` — group dirs are organizational only; the command
  name is the filename.
- `skills/<name>/SKILL.md` — underscore skill names; large `references/` corpora
  kept intact.
- `scripts/<group>/` — per-group helper scripts (paths referenced as
  `${CLAUDE_PLUGIN_ROOT}/scripts/<group>/...`).
- `agents/`, `core/`, `templates/`, `tools/`, `schemas/`, `rules/`, `bin/` —
  harness support content migrated from the old `amir` plugin.
- `hooks/hooks.json` — secrets PreToolUse scan (harness) + terraform
  plan/apply guard.

## Component gating

Every non-harness command starts with a component gate: it reads
`.amir/project.yaml` and requires `plugins.amir_project.components` to include
its group id (e.g. `"aws"`, `"cortex-xdr"`). If the manifest is missing or the
group is not enabled the command refuses and points to `/amir:configure_project`.
Harness commands are gated by the plugin being enabled for the project at all.

## Groups

| Group (dir) | Commands | Origin plugin |
|---|---|---|
| `harness` | `/amir:agent_reset`, `/amir:btw`, `/amir:build_agents`, `/amir:build_goal`, `/amir:design`, `/amir:design_agents`, `/amir:design_qa`, `/amir:docs_sync`, `/amir:document_max`, `/amir:git_commit`, `/amir:git_push`, `/amir:git_setup`, `/amir:git_tree`, `/amir:handoff`, `/amir:milestone_retro`, `/amir:plan`, `/amir:project_cleanup`, `/amir:project_cost`, `/amir:project_tasks`, `/amir:project_watch`, `/amir:resume_build`, `/amir:rollback`, `/amir:security_scan`, `/amir:tasks_update`, `/amir:troubleshoot` | `amir` |
| `aws` (manifest id `aws`) | `/amir:aws_cli`, `/amir:aws_whoami` | `amir-aws` |
| `azure` (manifest id `azure`) | `/amir:azure_cli`, `/amir:azure_whoami` | `amir-azure` |
| `xdr` (manifest id `cortex-xdr`) | `/amir:xdr_ask`, `/amir:xdr_incidents`, `/amir:xdr_preflight`, `/amir:xdr_respond` | `amir-cortex-xdr` |
| `docker` (manifest id `docker`) | `/amir:docker_build`, `/amir:docker_down`, `/amir:docker_logs`, `/amir:docker_push`, `/amir:docker_status`, `/amir:docker_up` | `amir-docker` |
| `elastic` (manifest id `elastic`) | `/amir:elastic_ask`, `/amir:elastic_preflight`, `/amir:elastic_search` | `amir-elastic` |
| `litellm` (manifest id `litellm`) | `/amir:litellm_chat`, `/amir:litellm_models`, `/amir:litellm_session`, `/amir:litellm_spend`, `/amir:litellm_status` | `amir-litellm` |
| `nmap` (manifest id `nmap`) | `/amir:nmap_parse`, `/amir:nmap_scan` | `amir-nmap` |
| `paloalto` (manifest id `paloalto`) | `/amir:panos_api`, `/amir:panos_ask`, `/amir:panos_preflight` | `amir-paloalto` |
| `prisma` (manifest id `prisma`) | `/amir:prisma_api`, `/amir:prisma_ask`, `/amir:prisma_design`, `/amir:prisma_review`, `/amir:prisma_troubleshoot`, `/amir:prisma_update_index`, `/amir:prisma_whats_new` | `amir-prisma` |
| `qradar` (manifest id `qradar`) | `/amir:qradar_aql`, `/amir:qradar_ask`, `/amir:qradar_preflight` | `amir-qradar` |
| `sentinel` (manifest id `sentinel`) | `/amir:sentinel_ask`, `/amir:sentinel_preflight`, `/amir:sentinel_query` | `amir-sentinel` |
| `splunk` (manifest id `splunk`) | `/amir:splunk_ask`, `/amir:splunk_preflight`, `/amir:splunk_search` | `amir-splunk` |
| `ssh` (manifest id `ssh`) | `/amir:ssh_copy`, `/amir:ssh_run`, `/amir:ssh_session` | `amir-ssh` |
| `terraform` (manifest id `terraform`) | `/amir:terraform_apply`, `/amir:terraform_destroy`, `/amir:terraform_fmt`, `/amir:terraform_init`, `/amir:terraform_plan`, `/amir:terraform_validate` | `amir-terraform` |
| `wireshark` (manifest id `wireshark`) | `/amir:wireshark_analyze`, `/amir:wireshark_capture`, `/amir:wireshark_extract`, `/amir:wireshark_filter` | `amir-wireshark` |

New tool groups (serena, context7, semgrep, langfuse, openhands, worktrees,
swebench, terminalbench) are built separately — see
`design/SPEC-amir_project-tools.md`.

## Deprecated aliases (removed at amir_project 1.0)

| Alias | Replacement |
|---|---|
| `/amir:project_create` | `/amir:create_project` (provided by the amir_system plugin) |
| `/amir:project_import` | `/amir:onboard_project` (provided by the amir_system plugin) |
| `/amir:use_subagent` | `/amir:use_subagents` (provided by the amir_system plugin) |
| `/amir:compact` | `/amir:cleanup_context` (provided by the amir_system plugin) |
| `/amir:project_doctor` | `/amir:validate_project` (provided by the amir_system plugin) |
| `/amir:project_status` | `/amir:project_status` (which now lives in the amir_system plugin) |

## Retired commands

Retired because they violate the project-scope principle (they operated on
user/system scope). No aliases are provided:

- `/amir:system_cleanup`
- `/amir:system_settings`
- `/amir:system_skills`
- `/amir:user_cleanup`
- `/amir:user_settings`
- `/amir:user_skills`

## Prisma docs corpus

Prisma skills and `scripts/prisma/ingest.py` read the live corpus location from
the environment variable `PRISMA_DOCS_PATH`. The historical default —
machine-specific, documented once here only — was:

```
E:\PC3_Shared\Palo\Documents\Markdowns Prisma SASE
```

Set `PRISMA_DOCS_PATH` before running `/amir:prisma_update_index` if the corpus
lives elsewhere (or on any other machine). If the variable is unset and the
default path does not exist, prisma skills fall back to the baked
`skills/prisma_*/references/` layer.

## MCP servers

Declared in `.claude-plugin/plugin.json` and loaded only when the plugin (or a
rendered subset containing the group) is enabled: `aws-mcp` (aws), `azure-mcp`
(azure), `litellm` (litellm, `scripts/litellm/litellm_mcp.py`),
`elastic-agent-builder` (elastic). Credentials always via `${env:...}`
references — never inlined.
