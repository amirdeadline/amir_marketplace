# Palo Alto MCP Gateway — Servers & Tools Reference

> **Generated:** 2026-09-28
> **Source:** live `mcp-gateway` `get_status` pull (authoritative)
> **Gateway endpoint:** `https://api.mcp.pan.dev`
> **Scope:** every MCP server currently registered behind the gateway, every tool it exposes,
> what each does in plain language, how to call them, and how authentication works.

---

> **Naming in the Amir_LiteLLM plugin.** Servers installed one at a time with `litellm_install_<server>` are
> registered as `litellm-<server>`, so tools are called `mcp__litellm-<server>__<tool>` (for example
> `mcp__litellm-confluence__confluence_search`). Only the aggregated entry installed with
> `litellm_install_gateway` keeps the `mcp__mcp-gateway__<server>__<tool>` names used below.
> Machine-specific paths below (`C:\Users\arashidi\...`) come from the machine where this was generated.

## 1. What the MCP Gateway is

The **MCP Gateway** (`mcp-gateway`) is a single aggregating endpoint that fronts many
downstream Model Context Protocol (MCP) servers. Instead of your client connecting to
GitLab, Jira, Google Workspace, Cortex, etc. individually, it connects **once** to the
gateway, and the gateway proxies each call to the right downstream server, applying
security policy (per-tool approval, risk gating, auth) along the way.

| Property | Value |
|---|---|
| API URL | `https://api.mcp.pan.dev` |
| API enabled | `true` |
| Security enabled | `true` |
| Status | `running` |
| Total tools | **268** (267 dynamic + gateway meta tools) |
| Approved / Blocked / Pending | 268 / 0 / 0 |
| Servers with tools | **12** |
| Tool sync interval | 600 s (10 min) |
| Identity (this session) | `arashidi@paloaltonetworks.com` |
| MCP client | `claude-code` |

### Meta tools (the gateway itself)

These are not downstream tools — they inspect the gateway:

| Tool | Purpose |
|---|---|
| `mcp__mcp-gateway__get_status` | Real-time gateway health, connected servers, tool counts, per-tool risk levels, auth/identity state. Start here to diagnose anything. |
| `mcp__mcp-gateway__describe_tool` | Full metadata + parameter schema + usage stats for a single downstream tool. Call before using an unfamiliar/high-risk tool. |

---

## 2. How to call a tool (naming convention)

Every downstream tool is invoked with a **fully namespaced** name:

```
mcp__mcp-gateway__<server>__<tool>
```

- The `<server>` segment uses **underscores**, even where the server's display name uses
  hyphens: `google-workspace` → `google_workspace`, `cortex-bot` → `cortex_bot`,
  `figma-desktop` → `figma_desktop`.
- **Bare tool names are rejected.** `get_status` fails; `mcp__mcp-gateway__get_status` works.
- The gateway's internal registry lists tools in a shorter single-underscore form
  (e.g. `gitlab__create_issue`). That is the **registry** name, not the callable name — always
  use the full `mcp__mcp-gateway__...` form when actually invoking.

**Examples**

```
mcp__mcp-gateway__jira__jira_search
mcp__mcp-gateway__google_workspace__search_drive_files
mcp__mcp-gateway__gitlab__list_projects
mcp__mcp-gateway__cortex_bot__get_cases
```

---

## 3. Authentication model

### 3.1 Gateway-level auth (this session)

At the time of this document the session shows:

| Field | Value |
|---|---|
| `is_authenticated` | **false** |
| `auth_status.state` | `not_started` |
| `user_id` | `null` |
| `identity` / `display_name` | `arashidi@paloaltonetworks.com` |
| `token_expires_at` | set (short-lived) |

**What this means in practice:** the tools are *registered and approved*, but the session has
not yet completed an interactive auth handshake. The **first call to a given server may trigger
an authentication / consent flow** (browser/OAuth or token exchange) before it returns data.
This is expected — allow the handshake to complete, then retry the call.

### 3.2 Per-server credentials

The gateway holds or brokers credentials per downstream server. You generally do **not** paste
secrets into tool calls; the gateway injects them. Exceptions and specifics are listed in each
server section below (e.g. Asana accepts a per-call PAT). Downstream scoping filters
(`JIRA_PROJECTS_FILTER`, `CONFLUENCE_SPACES_FILTER`) are enforced server-side.

**Secret handling rule:** refer to secrets by name only. Never paste secret values into tool
calls, docs, or logs.

### 3.3 Risk gating

Each tool carries a `risk_level`: `null`/`low` (read-ish), `medium` (content reads / bulk ops),
or **`high`** (destructive / state-changing). High-risk tools (especially in `cortex-bot`)
require explicit confirmation flags (e.g. `confirm_destructive_action: true`) and, per project
rules, **explicit owner approval** before use.

---

## 4. Server inventory (summary)

| # | Server (display) | Callable segment | Tools | Highest risk | Auth |
|---|---|---|---|---|---|
| 1 | `gitlab` | `gitlab` | ~62 | low/null | GitLab token (gateway) |
| 2 | `google-workspace` | `google_workspace` | ~30 | medium (content reads) | Google OAuth |
| 3 | `jira` | `jira` | 5 | null | Jira token/OAuth |
| 4 | `confluence` | `confluence` | 4 | null | Confluence token/OAuth |
| 5 | `asana` | `asana` | 7 | null | Asana PAT |
| 6 | `cortex-bot` | `cortex_bot` | ~110 | **high (destructive IR)** | Cortex XSIAM/XSOAR creds |
| 7 | `cortex-mcp` | `cortex_mcp` | 12 | medium | Cortex XDR creds |
| 8 | `gcp_bq` | `gcp_bq` | 5 | null | GCP credentials |
| 9 | `figma-desktop` | `figma_desktop` | 8 | low | Local Figma desktop app |
| 10 | `playwright` | `playwright` | 14 | null | Local browser + config |
| 11 | `chrome_devtools` | `chrome_devtools` | 11 | null | Local Chrome + config |
| 12 | `secure_fetch` | `secure_fetch` | 1 | (n/a) | Gateway |

> **Not registered on this gateway:** Salesforce/SFDC, InFusion. Requests requiring those must
> use another channel.

---

## 5. Server details

### 5.1 `gitlab` — source control, MRs, CI/CD

**What it does:** full read/write access to GitLab projects, branches, commits, files, issues,
labels, merge requests, and CI/CD pipelines. This is how an agent inspects repos, opens MRs,
and reads pipeline logs.

**Auth:** GitLab token brokered by the gateway. The official product git is `SDWAN_LAB` /
GitLab `prisma-sdwan-lab` — **do not add files or commit there unless fully tested and the owner
asked**; no AI scratch in that repo.

**Tools by area**

- **Projects:** `list_projects`, `list_group_projects`, `get_project`
- **Branches:** `create_branch`
- **Commits:** `list_commits`, `get_commit`, `get_commit_diff`
- **Files:** `get_file_contents`, `get_repository_tree`, `create_or_update_file`, `push_files`
- **Issues:** `list_issues`, `my_issues`, `get_issue`, `create_issue`, `update_issue`,
  `list_issue_discussions`, `create_issue_note`, `update_issue_note`, `list_issue_links`,
  `get_issue_link`, `create_issue_link`
- **Labels:** `list_labels`, `get_label`, `create_label`, `update_label`
- **Merge requests:** `list_merge_requests`, `get_merge_request`, `create_merge_request`,
  `update_merge_request`, `get_merge_request_diffs`, `list_merge_request_diffs`,
  `get_merge_request_version`, `list_merge_request_versions`,
  `get_merge_request_approval_state`, `mr_discussions`, `get_merge_request_note`,
  `get_merge_request_notes`, `create_merge_request_note`, `update_merge_request_note`,
  `create_merge_request_thread`, `create_merge_request_discussion_note`,
  `update_merge_request_discussion_note`, `delete_merge_request_discussion_note`,
  `resolve_merge_request_thread`, `list_draft_notes`, `get_draft_note`, `create_draft_note`,
  `update_draft_note`, `create_note`
- **Pipelines / jobs:** `list_pipelines`, `get_pipeline`, `retry_pipeline`, `cancel_pipeline`,
  `list_pipeline_jobs`, `get_pipeline_job`, `get_pipeline_job_output`, `play_pipeline_job`,
  `retry_pipeline_job`, `cancel_pipeline_job`, `list_pipeline_trigger_jobs`

**Usage notes:** most tools take `project_id` (numeric ID or URL-encoded `group/project` path).
Write tools (`create_*`, `update_*`, `push_files`, `*_pipeline`) change state — treat as
approval-gated even though risk is registered `null`.

---

### 5.2 `google-workspace` — Drive, Docs, Sheets, Slides, Gmail

**What it does:** read and search Google Workspace content for the authenticated user —
Drive files/folders, Google Docs (incl. Markdown export), Sheets, Slides, and Gmail.

**Auth:** Google OAuth. First use likely triggers the consent handshake described in §3.1.
Content-read tools are `risk_level: medium` (they return document/message bodies); searches,
listings, permission checks, comments, and thumbnails are `low`.

**Tools by area**

- **Drive:** `search_drive_files`, `list_drive_items`, `get_drive_file_content` *(medium)*,
  `get_drive_file_download_url` *(medium)*, `get_drive_file_permissions`,
  `get_drive_shareable_link`, `check_drive_file_public_access`
- **Docs:** `get_doc_content` *(medium)*, `get_doc_as_markdown` *(medium)*,
  `inspect_doc_structure`, `list_docs_in_folder`, `search_docs`, `list_document_comments`,
  `debug_table_structure`
- **Sheets:** `list_spreadsheets`, `get_spreadsheet_info`, `read_sheet_values` *(medium)*,
  `list_sheet_tables`, `list_spreadsheet_comments`
- **Slides:** `get_presentation`, `get_page`, `get_page_thumbnail`, `list_presentation_comments`
- **Gmail:** `search_gmail_messages`, `get_gmail_message_content` *(medium)*,
  `get_gmail_messages_content_batch` *(medium)*, `get_gmail_thread_content` *(medium)*,
  `get_gmail_threads_content_batch` *(medium)*, `list_gmail_labels`,
  `get_gmail_attachment_content` *(medium)*

**Usage notes:** to open a specific Doc/Sheet, get its ID from a `search_*`/`list_*` call first,
then pass it to the content tool. Drive search supports Google query operators; note owner-based
queries don't work inside Shared Drives (search by `modifiedTime` + `order_by` instead).

---

### 5.3 `jira` — issue tracking (read)

**What it does:** search and read Jira issues, fields, projects, and attachments.

**Auth:** Jira token/OAuth via gateway. Results are scoped by `JIRA_PROJECTS_FILTER` when set.

**Tools**

| Tool | Purpose |
|---|---|
| `jira_search` | Run a JQL query; returns matching issues with pagination. |
| `jira_get_issue` | Full details of one issue (fields, comments, transitions, changelog). |
| `jira_search_fields` | Fuzzy-find field IDs (incl. custom fields) by keyword. |
| `jira_get_all_projects` | List projects the user can access. |
| `jira_download_attachments` | Download an issue's attachments to a directory. |

**Usage notes:** start from `jira_search` with JQL (e.g.
`project = PROJ AND status = "In Progress"`), then `jira_get_issue` for depth. Use
`jira_search_fields` when you need a custom field's ID for JQL.

---

### 5.4 `confluence` — wiki / docs (read)

**What it does:** search and read Confluence pages, their child pages, and comments.

**Auth:** Confluence token/OAuth via gateway. Scoped by `CONFLUENCE_SPACES_FILTER` when set.

**Tools**

| Tool | Purpose |
|---|---|
| `confluence_search` | Search by simple text or CQL; returns matching pages. |
| `confluence_get_page` | Get a page by ID, or by title + space key; Markdown or raw HTML. |
| `confluence_get_page_children` | List (optionally with content) the children of a page. |
| `confluence_get_comments` | Get comments on a page. |

**Usage notes:** simple-text search mimics the web UI; use CQL for precision
(e.g. `type=page AND space=DEV AND title~"Runbook"`). Page IDs come from the numeric portion
of a page URL or from search results.

---

### 5.5 `asana` — work management

**What it does:** browse Asana workspaces/teams/projects and read, search, create, and update
tasks.

**Auth:** Asana Personal Access Token — via `ASANA_PAT` env on the gateway, or passed per-call
as the optional `asana_token` argument.

**Tools**

| Tool | Purpose | Writes? |
|---|---|---|
| `get_workspaces` | List/find workspaces. | no |
| `get_teams` | List/find teams (org workspaces only). | no |
| `get_projects` | List/find projects. | no |
| `get_project_tasks` | List tasks in a project. | no |
| `search_tasks` | Search tasks in a workspace, or fetch one by GID. | no |
| `create_task` | Create a task. | **yes** |
| `update_task` | Update/complete/reassign a task. | **yes** |

**Usage notes:** most calls need a `workspace_gid` (get it from `get_workspaces`). `create_task`
and `update_task` change state — approval-gated in practice.

---

### 5.6 `cortex-bot` — Cortex XSIAM / XSOAR (full ops, incl. destructive IR)

**What it does:** the largest server (~110 tools). Full Cortex XSIAM/XSOAR surface: case & alert
management, endpoint response actions, threat hunting (XQL), detection content, assets &
vulnerabilities, scripts, integrations/automation, playbooks, widgets, content generators, the
demisto-sdk, and how-to guides.

**Auth:** Cortex XSIAM/XSOAR tenant credentials via gateway. **Many tools are `high` risk /
destructive** and must not run without explicit owner approval; most require an explicit
confirm flag (e.g. `confirm_destructive_action: true`).

**Tools by area** (⚠ = high-risk/destructive)

- **Cases / issues / incidents:** `get_cases`, `get_issues`, `create_issue` ⚠,
  `get_incident_extra_data`, `update_incident` ⚠, `update_issue` ⚠, `update_case_ai_summary` ⚠,
  `update_case_timeline` ⚠, `add_war_room_entry` ⚠, `get_war_room_entries`
- **Endpoints / response:** `get_endpoints`, `get_filtered_endpoints`, `get_endpoint_profiles`,
  `isolate_endpoint` ⚠, `unisolate_endpoint` ⚠, `scan_endpoint` ⚠, `abort_scan` ⚠,
  `terminate_process` ⚠, `terminate_causality` ⚠, `quarantine_files` ⚠, `restore_file` ⚠,
  `retrieve_files` ⚠, `get_quarantine_status`, `get_file_retrieval_details`,
  `blocklist_files` ⚠, `allowlist_files` ⚠, `get_distributions`, `get_audit_agent_reports`
- **Threat hunting:** `run_xql_query`, `get_datasets`, `discover_dataset_schema`,
  `enrich_ip_address` ⚠, `enrich_domain` ⚠, `enrich_url` ⚠, `enrich_file_hash` ⚠ *(these WRITE War Room
  entries and may create a scratch issue, see servers/cortex_bot.md)*,
  `get_alert_multi_events`, `get_contributing_events`, `list_risky_users`, `list_risky_hosts`
- **Detection content:** `get_correlation_rule`, `get_correlation_rules`,
  `search_correlation_rules`, `insert_correlation_rule` ⚠, `delete_correlation_rule` ⚠,
  `get_biocs`, `insert_bioc` ⚠, `get_indicators`, `insert_indicators_csv` ⚠,
  `insert_indicators_json` ⚠
- **Assets / vulnerabilities:** `get_assets`, `get_asset_by_id`, `get_vulnerabilities`,
  `trigger_vulnerability_scan` ⚠, `get_assessment_profile_results`, `get_triage_presets`,
  `get_tenant_info`, `get_audit_management_log`, `get_audit_management_logs`
- **Scripts:** `get_scripts`, `get_script`, `get_script_metadata`, `run_script` ⚠,
  `run_snippet_code_script` ⚠, `get_script_execution_status`, `get_script_execution_results`,
  `get_action_status`
- **Integrations / automation:** `list_integrations`, `get_integration_commands`,
  `run_xsoar_automation` ⚠, `test_all_tools`
- **Playbooks:** `get_playbook`, `get_playbook_building_blocks`, `run_playbook` ⚠,
  `insert_playbook` ⚠, `delete_playbook` ⚠, `create_playbook` ⚠
- **Widgets:** `get_widgets`, `insert_widgets` ⚠, `delete_widgets` ⚠
- **Content generators:** `create_case_field` ⚠, `create_case_layout` ⚠,
  `create_case_layout_rule` ⚠, `create_modeling_rule` ⚠, `create_parsing_rule` ⚠,
  `create_assets_modeling_rule` ⚠, `create_xsiam_dashboard` ⚠, `create_xsiam_report` ⚠,
  `create_agentix_action` ⚠, `create_agentix_agent` ⚠
- **demisto-sdk:** `sdk_validate`, `sdk_lint`, `sdk_unify`, `sdk_split`, `sdk_upload` ⚠,
  `sdk_download`, `sdk_run`, `sdk_run_playbook`, `sdk_generate_docs`
- **Guides (read-only reference):** `get_xsiam_content_guide`, `get_xsoar_best_practices`,
  `get_xsoar_pattern_guide`, `get_xsoar_event_collector_guide`, `get_xsoar_feed_guide`,
  `get_xsoar_mirroring_guide`, `get_xsoar_long_running_guide`,
  `get_xsoar_scheduled_commands_guide`, `get_xsoar_playbook_operations_guide`,
  `get_xsoar_layout_guide`, `get_slack_interactive_workflows_guide`

**Usage notes:** for read/hunt work start with `get_cases`/`get_issues`/`run_xql_query` and the
`enrich_*` tools. Before any XQL, use `get_datasets` → `discover_dataset_schema` to learn field
names, and always bound queries with `| limit N`. **Never** run isolate/terminate/quarantine/
blocklist or any `insert_`/`create_`/`delete_`/`run_` write without owner sign-off.

---

### 5.7 `cortex-mcp` — Cortex XDR (read-focused)

**What it does:** a lean, read-oriented Cortex XDR surface — the safe subset for inspection and
reporting. Overlaps `cortex-bot` names but scoped to reads.

**Auth:** Cortex XDR tenant credentials via gateway.

**Tools:** `get_assets`, `get_asset_by_id`, `get_cases`, `get_issues`, `get_correlation_rules`,
`get_filtered_endpoints`, `get_playbook` *(medium)*, `get_script` *(medium)*, `get_tenant_info`,
`get_vulnerabilities`, `get_audit_management_log` *(medium)*, `get_assessment_profile_results`.

**Usage notes:** prefer this server over `cortex-bot` when you only need to read Cortex state —
it has no destructive tools.

---

### 5.8 `gcp_bq` — Google BigQuery

**What it does:** explore BigQuery datasets/tables/metadata and run SQL, with a cost-preview
step.

**Auth:** GCP credentials via gateway.

**Tools**

| Tool | Purpose |
|---|---|
| `get_datasets` | List all datasets. |
| `get_tables` | List tables in a dataset. |
| `search_metadata` | Search datasets/tables/columns by keyword. |
| `check_query_scan_amount` | Dry-run a query to see bytes scanned before you pay for it. |
| `execute_query` | Run SQL (auto safety checks + LIMIT management). |

**Usage notes:** always `check_query_scan_amount` before `execute_query` on unfamiliar tables to
avoid large scans. `project_id` is optional (defaults to the first configured project).

---

### 5.9 `figma-desktop` — Figma design context

**What it does:** pulls design context (code, screenshots, metadata, variables, FigJam) from the
**locally running Figma desktop app** for the selected node.

**Auth:** none over the network — requires the **Figma desktop app running locally** with a file
open; tools act on the current selection or a given `nodeId`.

**Tools:** `get_design_context`, `get_screenshot`, `get_metadata`, `get_variable_defs`,
`get_figjam`, `get_strategy_for_mapping`, `send_get_strategy_response`,
`create_design_system_rules`.

**Usage notes:** if no `nodeId` is passed, tools use the current selection in the desktop app.
Won't work headless / without Figma open.

---

### 5.10 `playwright` — browser automation (Playwright)

**What it does:** drive a real browser — navigate, click, type, fill forms, read console, manage
tabs — for web automation and testing.

**Auth / prerequisites:** local browser driver plus gateway config. **This server needs `host`
and `allowed-origins` set in `C:\Users\arashidi\.mcp-gateway\user-config.json` to actually run;**
without them, calls fail at execution time even though the tools are registered/approved.
**Do not edit that config file without approval.**

**Tools:** `browser_navigate`, `browser_navigate_back`, `browser_click`, `browser_type`,
`browser_fill_form`, `browser_hover`, `browser_drag`, `browser_select_option`,
`browser_press_key`, `browser_resize`, `browser_tabs`, `browser_console_messages`,
`browser_wait_for`, `browser_close`.

---

### 5.11 `chrome_devtools` — Chrome DevTools automation

**What it does:** control Chrome via the DevTools protocol — open/select pages, click, evaluate
JavaScript, read console messages, handle dialogs, resize.

**Auth / prerequisites:** local Chrome plus gateway config. **This server needs `log-file` set in
`C:\Users\arashidi\.mcp-gateway\user-config.json` to run;** without it, calls fail at execution
time. **Do not edit that config file without approval.**

**Tools:** `new_page`, `list_pages`, `select_page`, `click`, `drag`, `hover`, `evaluate_script`,
`get_console_message`, `handle_dialog`, `resize_page`, `wait_for`.

---

### 5.12 `secure_fetch` — internal-aware URL fetch

**What it does:** a single tool, `fetch`, that securely retrieves a URL through the gateway. Unlike
the client's built-in `WebFetch`/`WebSearch` (US-only, and disabled in some sessions), this path
may be able to reach **internal / corporate URLs**.

**Auth:** via gateway.

**Tool:** `fetch` — secure URL fetch.

**Usage notes:** use this when you need to pull an internal resource (e.g. a `*.paloaltonetworks.local`
page) that the standard web tools can't reach.

---

## 6. Quick "how do I…" recipes

| Goal | Call |
|---|---|
| See gateway health / what's connected | `mcp__mcp-gateway__get_status` |
| Inspect one tool's params before using it | `mcp__mcp-gateway__describe_tool` (`server_name`, `tool_name`) |
| Find a Jira issue | `mcp__mcp-gateway__jira__jira_search` (JQL) |
| Read a Confluence runbook | `confluence_search` → `confluence_get_page` |
| Open a Google Doc as Markdown | `google_workspace__search_drive_files` → `get_doc_as_markdown` |
| List GitLab projects | `gitlab__list_projects` |
| Hunt in Cortex | `cortex_bot__get_datasets` → `discover_dataset_schema` → `run_xql_query` (`| limit N`) |
| Preview a BigQuery cost | `gcp_bq__check_query_scan_amount` before `execute_query` |
| Fetch an internal URL | `secure_fetch__fetch` |

---

## 7. Guardrails (project rules that apply to these tools)

1. **No SCM/Cortex/GitLab writes without explicit owner approval.** Read/dry-run first.
2. **Cortex destructive IR tools** (isolate/terminate/quarantine/blocklist/scan and any
   `insert_`/`create_`/`delete_`/`run_`) are off-limits without sign-off and confirm flags.
3. **Secrets by name only** — never paste values into tool calls, logs, or docs.
4. **Do not edit** `C:\Users\arashidi\.mcp-gateway\user-config.json` (gates playwright &
   chrome_devtools) without approval.
5. **Salesforce/SFDC and InFusion are not on this gateway** — do not assume access.
6. First call to a server may trigger an **auth handshake** (session currently
   `is_authenticated: false`); let it complete, then retry.

---

*Regenerate this file after any gateway change: pull `mcp__mcp-gateway__get_status` and diff the
server/tool list and risk levels. Sync interval is 10 minutes, so newly added downstream tools
may take up to that long to appear.*
