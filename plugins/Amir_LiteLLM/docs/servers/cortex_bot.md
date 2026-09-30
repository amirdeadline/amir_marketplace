# cortex_bot

## Overview

`cortex_bot` is the MCP server for **Palo Alto Networks Cortex** security operations —
covering **XSIAM** (Extended Security Intelligence and Automation Management), **XSOAR**
(SOAR / playbook automation) and **XDR** (endpoint detection and response). It is by far
the largest server in the gateway (~100+ tools).

Functional coverage:

- **Case & incident management** — list/read cases and incidents, update status/assignment,
  generate AI summaries and visual timelines.
- **Issues / alerts** — list, create, update, and pull raw contributing events.
- **Endpoints & response** — inventory endpoints, isolate/unisolate, scan, terminate
  processes/causality chains, run scripts and snippets.
- **File response** — quarantine/restore, retrieve files, blocklist/allowlist hashes.
- **Threat hunting** — XQL queries, dataset/schema discovery, indicator enrichment.
- **IOC / BIOC & indicators** — read/insert threat indicators and behavioral rules.
- **Correlation rules** — create/read/search/delete detection logic.
- **Scripts & playbooks** — list, fetch, run, insert, delete.
- **Content development** — SDK operations plus `create_*` generators for layouts,
  fields, dashboards, reports, parsing/modeling rules, AgentIX actions/agents.
- **Assets & vulnerabilities** — asset inventory, vulnerability lists, assessment results.
- **Audit & platform** — audit/management logs, distributions, profiles, tenant info.
- **War Room** — read/add investigation entries.
- **Developer guides** — read-only reference documents for building XSOAR content.

> **This is a read + WRITE server.** It contains many **destructive / high-risk** actions
> (endpoint isolation, process termination, file quarantine, hash blocklisting, rule and
> playbook deletion, playbook/script execution, incident/case mutation). Treat every write
> tool as requiring explicit operator approval.

## Authentication

Cortex authenticates with an **API key** plus a **key ID** and a **tenant FQDN / API base
URL** (the Cortex XSIAM/XDR advanced API model). These credentials are supplied to the MCP
server via its environment/configuration — **credential names only**, never document or
print values:

- Cortex API key (secret) — mechanism: `Authorization` header advanced auth.
- Cortex API key ID — the numeric key identifier paired with the key.
- Cortex tenant FQDN / API base URL — the per-tenant `api-<tenant>` endpoint.

Per-tool passthrough tokens: cortex_bot tools do **not** expose per-call credential
parameters (unlike some other gateway servers such as Asana's `asana_token`). All Cortex
auth is server-side configuration. Enrichment/automation tools operate through the tenant's
configured XSOAR integrations, which carry their own credentials configured inside Cortex.

Gateway session auth: all calls are brokered by the MCP gateway, which applies its own
session authentication and approval/permission layer on top of the Cortex credentials.

## Risk / Safety

Require **explicit operator approval before invoking any write or destructive tool.**

- **HIGH-destructive (endpoint/host impact, irreversible or hard to reverse):**
  `isolate_endpoint`, `unisolate_endpoint`, `scan_endpoint`, `abort_scan`,
  `terminate_process`, `terminate_causality`, `quarantine_files`, `restore_file`,
  `retrieve_files`, `blocklist_files`, `allowlist_files`, `run_script`,
  `run_snippet_code_script`, `run_playbook`, `sdk_run`, `sdk_run_playbook`,
  `trigger_vulnerability_scan`.
- **Destructive to content/config (delete or overwrite):** `delete_correlation_rule`,
  `delete_playbook`, `delete_widgets`, `insert_correlation_rule`, `insert_bioc`,
  `insert_playbook`, `insert_widgets`, `insert_indicators_csv`, `insert_indicators_json`,
  `sdk_upload`, all `create_*` generators (create content/files, optionally upload),
  `update_incident`, `update_issue`, `update_case_ai_summary`, `update_case_timeline`,
  `add_war_room_entry`, `create_issue`, `run_xsoar_automation` (can run arbitrary/write
  commands), `enrich_*` (write results into a War Room / can create a scratch issue),
  `test_all_tools` (exercises many tools).
- **Read-only (safe to query):** `get_*` tools, `list_*` tools, `search_correlation_rules`,
  `discover_dataset_schema`, `run_xql_query` (query only), `sdk_download`, `sdk_lint`,
  `sdk_split`, `sdk_unify`, `sdk_validate`, `sdk_generate_docs`, and all `get_xsoar_*_guide`
  / `get_*_guide` reference tools.

> Several "enrichment" and "automation" tools are nominally investigative but **write** to
> the tenant (creating scratch issues or War Room entries, or running commands). They are
> flagged as write below.

## Tools

### Cases & Incidents

#### get_cases
- **What it does:** Retrieves a list of cases/incidents, optionally filtered.
- **Risk:** read-only.
- **Key parameters:** `filters` (array; empty = all), `search_from`, `search_to` (max 100), `sort`.
- **Notes:** Primary tool for listing incidents; use `get_incident_extra_data` for full detail.

#### get_incident_extra_data
- **What it does:** Returns comprehensive detail for one incident — all alerts, affected users/hosts, artifacts, network activity, timeline, MITRE techniques.
- **Risk:** read-only.
- **Key parameters:** `incident_id` (required), `alerts_limit` (default 1000).
- **Notes:** Deep-dive per case; can return large responses.

#### update_incident
- **What it does:** Updates a CASE's status, assignment, severity, resolution comment, AI summary, or timeline.
- **Risk:** write.
- **Key parameters:** `incident_id` (required), `status`, `assigned_user_mail`, `manual_severity`, `resolve_comment`, `aisummary` (markdown), `timeline` (HTML), `unassign_user`.
- **Notes:** Only two custom fields valid: `aisummary`, `timeline`. Status values are lowercase (`new`, `under_investigation`, `resolved_*`). For alerts use `update_issue`.

#### update_case_ai_summary
- **What it does:** Investigates a case and writes a comprehensive AI-generated summary into the case's `aisummary` field.
- **Risk:** write.
- **Key parameters:** `case_id` (required).
- **Notes:** Use only on explicit request ("update the case summary"); not for routine updates.

#### update_case_timeline
- **What it does:** Generates a visual HTML timeline of a case's alerts and stores it in the `visualstoryline` field.
- **Risk:** write.
- **Key parameters:** `case_id` (required).
- **Notes:** Severity color-coded, chronological, MITRE mapped.

### Issues / Alerts

#### get_issues
- **What it does:** Retrieves a list of issues/alerts, optionally filtered.
- **Risk:** read-only.
- **Key parameters:** `filters` (array; empty = all), `search_from`, `search_to`, `sort`.
- **Notes:** Alerts are individual events; cases are containers of alerts.

#### create_issue
- **What it does:** Creates a new issue/alert, usable as a "scratch pad" workspace for War Room automation/enrichment.
- **Risk:** write.
- **Key parameters:** `name`, `description`, `severity` (default MEDIUM), `domain`, `category`, `tags`.
- **Notes:** Returns an `external_id`/alert_id used by enrichment/automation tools. MEDIUM+ severity creates a Case with War Room.

#### update_issue
- **What it does:** Updates an individual alert/issue severity, status, and resolution.
- **Risk:** write.
- **Key parameters:** `issue_id` (integer, required), `severity` (INFO..CRITICAL), `status` (`New`/`In Progress`/`Resolved` — Title Case), `status_resolution_reason`, `status_resolution_comment`.
- **Notes:** Status casing differs from `update_incident`. Use for triage / false-positive marking.

#### get_alert_multi_events
- **What it does:** Retrieves the raw events that triggered a specific alert for forensic investigation.
- **Risk:** read-only.
- **Key parameters:** `request_data` = `{"alert_id": "<id>", "filter_alert_fields": false}`.
- **Notes:** Works for ALL alert types; preferred over `get_contributing_events`.

#### get_contributing_events
- **What it does:** Returns the individual events contributing to an XSIAM-native CORRELATION alert.
- **Risk:** read-only.
- **Key parameters:** `alert_id` (required).
- **Notes:** ONLY works for XSIAM-native correlation alerts; fails (500) on external correlations. Prefer `get_alert_multi_events`.

### Endpoints & Response

#### get_endpoints
- **What it does:** Retrieves detailed endpoint info (ID, hostname, OS, IPs, agent/isolation status).
- **Risk:** read-only.
- **Key parameters:** `request_data` (filters: endpoint_id, hostname, ip_address, endpoint_status, os_type, domain; operators in/contains; pagination).

#### get_filtered_endpoints
- **What it does:** Retrieves a filtered list of XDR-agent-managed endpoints with a strongly-typed filter schema.
- **Risk:** read-only.
- **Key parameters:** `request_data.filters` (endpoint_id_list, endpoint_status, platform, hostname, ip_list, isolate, scan_status, etc.), `search_from`, `search_to`, `sort`.

#### isolate_endpoint
- **What it does:** Isolates an endpoint from the network (only Cortex agent can communicate).
- **Risk:** HIGH-destructive.
- **Key parameters:** `confirm_destructive_action` (must be True), `request_data` (endpoint_id or filters; optional incident_id).
- **Notes:** Reverse with `unisolate_endpoint`.

#### unisolate_endpoint
- **What it does:** Restores network access to a previously isolated endpoint.
- **Risk:** HIGH-destructive (state-changing).
- **Key parameters:** `request_data` (same format as isolate; optional incident_id).

#### scan_endpoint
- **What it does:** Initiates a malware scan on one or more endpoints.
- **Risk:** HIGH-destructive (agent action).
- **Key parameters:** `request_data` (filters or `{"filters":"all"}`; optional incident_id).

#### abort_scan
- **What it does:** Aborts a running malware scan on endpoints.
- **Risk:** HIGH-destructive (agent action).
- **Key parameters:** `request_data` (same filter format as scan_endpoint).

#### terminate_process
- **What it does:** Terminates all processes matching a name on a specific endpoint (via `process_kill_name` script).
- **Risk:** HIGH-destructive (irreversible).
- **Key parameters:** `endpoint_id`, `process_name`, `confirm_destructive_action` (True), `timeout`.
- **Notes:** Kills ALL matching instances; use `terminate_causality` for a full process tree.

#### terminate_causality
- **What it does:** Terminates an entire process tree (causality chain) on an endpoint.
- **Risk:** HIGH-destructive (irreversible).
- **Key parameters:** `confirm_destructive_action` (True), `request_data` (filters + `causality_id`).

#### get_action_status
- **What it does:** Retrieves status of a previously initiated action (scan, isolate, etc.).
- **Risk:** read-only.
- **Key parameters:** `request_data` = `{"group_action_id": <id>}`.

#### get_distributions
- **What it does:** Lists agent distribution packages (installers) available in XSIAM.
- **Risk:** read-only.
- **Key parameters:** none.

#### get_endpoint_profiles
- **What it does:** Lists endpoint security/prevention profiles (policies).
- **Risk:** read-only.
- **Key parameters:** none.

#### get_audit_agent_reports
- **What it does:** Retrieves agent audit reports (install/upgrade/status events, agent health/deployment history).
- **Risk:** read-only.
- **Key parameters:** `filters`, `search_from`, `search_to`.

#### list_risky_hosts
- **What it does:** Lists hosts flagged high-risk by XSIAM behavioral analytics.
- **Risk:** read-only.
- **Key parameters:** none.

#### list_risky_users
- **What it does:** Lists users flagged high-risk by XSIAM behavioral analytics.
- **Risk:** read-only.
- **Key parameters:** none.

### Files / Quarantine / Blocklist

#### quarantine_files
- **What it does:** Quarantines files on endpoints.
- **Risk:** HIGH-destructive (reversible via restore_file).
- **Key parameters:** `confirm_destructive_action` (True), `request_data` (endpoint filters + `file_path` + `file_hash`).

#### restore_file
- **What it does:** Restores a previously quarantined file after validating quarantine status.
- **Risk:** HIGH-destructive (re-enables the file).
- **Key parameters:** `file_hash` (SHA256), `endpoint_id` (optional; else all), `file_path` (optional).
- **Notes:** Validates SHA256 format and quarantine status before restoring.

#### get_quarantine_status
- **What it does:** Gets quarantine status of files on endpoints.
- **Risk:** read-only.
- **Key parameters:** `request_data.files` = `[{endpoint_id, file_path, file_hash}]`.

#### retrieve_files
- **What it does:** Retrieves files from endpoints for forensic analysis.
- **Risk:** HIGH-destructive (agent action / data exfil from host).
- **Key parameters:** `request_data` (endpoint filters + `files` per os_type: windows/linux/macos).

#### get_file_retrieval_details
- **What it does:** Gets details of a file retrieval action, including the download link.
- **Risk:** read-only.
- **Key parameters:** `request_data` = `{"group_action_id": <id>}`.

#### blocklist_files
- **What it does:** Adds file hashes to the Cortex blocklist to prevent execution across endpoints.
- **Risk:** HIGH-destructive.
- **Key parameters:** `hash_list` (MD5/SHA1/SHA256), `confirm_destructive_action` (True), `comment`, `incident_id`.
- **Notes:** Reverse via allowlist.

#### allowlist_files
- **What it does:** Adds file hashes to the Cortex allowlist, exempting them from security controls.
- **Risk:** HIGH-destructive (weakens security if misused).
- **Key parameters:** `hash_list`, `confirm_destructive_action` (True), `comment`, `incident_id`.

### Threat Hunting (XQL)

#### run_xql_query
- **What it does:** Executes an XQL query for hunting/analysis; polls asynchronously for results.
- **Risk:** read-only (query).
- **Key parameters:** `query` (required), `time_frame` (e.g. "24 hours"), `timeout` (default 600s).
- **Notes:** Always add `| limit N`. Recommended workflow: `get_datasets` → `discover_dataset_schema` → build query.

#### get_datasets
- **What it does:** Lists all datasets available for XQL (name, type, size, event count, last updated).
- **Risk:** read-only.
- **Key parameters:** none.

#### discover_dataset_schema
- **What it does:** Runs `dataset = <name> | limit 1` and returns clean field names/types/samples.
- **Risk:** read-only.
- **Key parameters:** `dataset` (required).
- **Notes:** Use before writing XQL to get exact field names.

### Enrichment

> All `enrich_*` tools run `!<type>` commands via a War Room and write results into an
> issue's War Room — they **write** to the tenant. Provide an `alert_id`/`case_id` or let
> them create a scratch issue.

#### enrich_ip_address
- **What it does:** Enriches an IP via configured threat-intel integrations (reputation, geo, ASN).
- **Risk:** write (War Room entry).
- **Key parameters:** `ip_address` (required), `alert_id`, `case_id`.

#### enrich_domain
- **What it does:** Enriches a domain (WHOIS, reputation, DNS, categorization).
- **Risk:** write (War Room entry).
- **Key parameters:** `domain` (required), `alert_id`, `case_id`.

#### enrich_file_hash
- **What it does:** Enriches a file hash (reputation, AV verdicts, malware family).
- **Risk:** write (War Room entry).
- **Key parameters:** `file_hash` (MD5/SHA1/SHA256, required), `alert_id`, `case_id`.
- **Notes:** Requires a file reputation integration configured.

#### enrich_url
- **What it does:** Enriches a URL (reputation, category, malware/scanner detections).
- **Risk:** write (War Room entry).
- **Key parameters:** `url` (required, include protocol), `alert_id`, `case_id`.

### IOC / BIOC & Indicators

#### get_indicators
- **What it does:** Retrieves IOC rules (IP/DOMAIN/HASH/FILENAME, severity, expiration).
- **Risk:** read-only.
- **Key parameters:** `filters`, `search_from`, `search_to`.

#### insert_indicators_json
- **What it does:** Inserts threat indicators (IOCs) in JSON format.
- **Risk:** write.
- **Key parameters:** `request_data.indicators` = `[{indicator, type, reputation, comment}]`.

#### insert_indicators_csv
- **What it does:** Inserts threat indicators via CSV upload (header row required).
- **Risk:** write.
- **Key parameters:** `csv_data` (required; columns indicator,type[,reputation,comment,expiration,severity]).

#### get_biocs
- **What it does:** Retrieves Behavioral IOC (BIOC) rules (behavioral detection patterns, MITRE mapping).
- **Risk:** read-only.
- **Key parameters:** `filters`, `search_from`, `search_to`.

#### insert_bioc
- **What it does:** Inserts or updates BIOC rules.
- **Risk:** write.
- **Key parameters:** `request_data` (array of BIOC objects: name, type, severity, status, is_xql, indicator, comment, MITRE fields). Omit `rule_id` to create; include to update.
- **Notes:** `rule_id` is tenant-specific.

### Correlation Rules

#### get_correlation_rules
- **What it does:** Retrieves correlation (detection) rules with a rich filter schema; optional extended view (XQL, MITRE, schedule).
- **Risk:** read-only.
- **Key parameters:** `request_data.filters`, `extended_view`, `search_from`, `search_to`.

#### get_correlation_rule
- **What it does:** Gets one correlation rule by ID (full detail incl. XQL, severity, schedule, suppression).
- **Risk:** read-only.
- **Key parameters:** `rule_id`.

#### search_correlation_rules
- **What it does:** Searches/lists correlation rules (names, IDs, status, severity, XQL).
- **Risk:** read-only.
- **Key parameters:** `filters`, `search_from`, `search_to`.

#### insert_correlation_rule
- **What it does:** Creates or updates an XQL-based correlation (detection) rule.
- **Risk:** write.
- **Key parameters:** `name`, `xql_query`, `severity`, `alert_name`, `alert_category` (required); plus schedule/suppression fields; `rule_id` to update.

#### delete_correlation_rule
- **What it does:** Permanently deletes a correlation rule by ID.
- **Risk:** HIGH-destructive (irreversible).
- **Key parameters:** `rule_id`, `confirm_destructive_action` (True).

### Scripts & Playbooks

#### get_scripts
- **What it does:** Lists available scripts that can be run on endpoints.
- **Risk:** read-only.
- **Key parameters:** `request_data.filters` or empty.

#### get_script
- **What it does:** Retrieves a script by display name or UUID (parses the returned ZIP).
- **Risk:** read-only.
- **Key parameters:** `identifier`, `identifier_type` (auto/id/name), `include_metadata`.

#### get_script_metadata
- **What it does:** Gets detailed metadata for a script (incl. parameters).
- **Risk:** read-only.
- **Key parameters:** `request_data` = `{"script_uid": "<uid>"}`.

#### run_script
- **What it does:** Runs a script on one or more endpoints.
- **Risk:** HIGH-destructive.
- **Key parameters:** `confirm_destructive_action` (True), `request_data` (script_uid, timeout, filters, parameters_values).

#### run_snippet_code_script
- **What it does:** Runs an arbitrary Python code snippet directly on endpoints.
- **Risk:** HIGH-destructive.
- **Key parameters:** `confirm_destructive_action` (True), `request_data` (filters + `snippet_code`).

#### get_script_execution_status
- **What it does:** Gets execution status of a previously run script.
- **Risk:** read-only.
- **Key parameters:** `request_data` = `{"action_id": "<id>"}`.

#### get_script_execution_results
- **What it does:** Gets results of a completed script execution.
- **Risk:** read-only.
- **Key parameters:** `request_data` = `{"action_id": "<id>"}`.

#### get_playbook
- **What it does:** Retrieves a playbook by name or ID as a ZIP (YAML).
- **Risk:** read-only.
- **Key parameters:** `filter` = `{field: name|id, value}`.

#### insert_playbook
- **What it does:** Adds or updates a playbook by uploading a ZIP containing its YAML.
- **Risk:** write.
- **Key parameters:** `file` (path to ZIP).
- **Notes:** Requires Instance Administrator permissions.

#### delete_playbook
- **What it does:** Deletes a playbook by name or ID.
- **Risk:** HIGH-destructive (irreversible).
- **Key parameters:** `confirm_destructive_action` (True), `filter` = `{field, value}`.

#### run_playbook
- **What it does:** Runs an XSOAR playbook on an issue (via `!setPlaybook`); can create a new issue.
- **Risk:** HIGH-destructive (executes automation).
- **Key parameters:** `playbook_name` (required), `issue_id`, `create_new_issue`, `wait_for_investigation`, `max_retries`.
- **Notes:** New issues require a human to open them in the UI before the playbook can run.

#### get_playbook_building_blocks
- **What it does:** Returns a library of modern XSOAR/XSIAM playbook building-block patterns.
- **Risk:** read-only.
- **Key parameters:** `category` (enrichment/containment/investigation/closure/transformers/all).

#### run_xsoar_automation
- **What it does:** Runs ANY XSOAR automation/integration command in a War Room and retrieves results.
- **Risk:** write (can run write/destructive commands).
- **Key parameters:** `command` (required, e.g. `!ip ip=1.1.1.1`), `alert_id`, `case_id`, `wait_for_results`, `timeout_seconds`.
- **Notes:** Universal command runner; results land in an issue's War Room.

#### get_integration_commands
- **What it does:** Retrieves command detail (names, params, outputs) for a specific integration.
- **Risk:** read-only (may fall back to War Room `!GetInstances`, which writes).
- **Key parameters:** `integration_name` (required), `alert_id` (for fallback).

#### list_integrations
- **What it does:** Lists all XSOAR integrations/automation capabilities configured in the tenant.
- **Risk:** read-only (may fall back to War Room `!GetInstances`, which writes).
- **Key parameters:** `integration_filter`, `only_enabled`, `alert_id` (for fallback).

### Content Development (SDK & create_*)

> `sdk_*` tools wrap the demisto-sdk for content development. `create_*` tools generate
> content files locally and can optionally upload to the tenant.

#### sdk_validate
- **What it does:** Validates XSOAR content structure/metadata.
- **Risk:** read-only.
- **Key parameters:** `path`.

#### sdk_lint
- **What it does:** Lints Python code in integrations/scripts (optionally auto-fix).
- **Risk:** read-only (write when `fix=True` — edits local files).
- **Key parameters:** `path`, `fix`.

#### sdk_split
- **What it does:** Splits a unified YAML file into a directory structure.
- **Risk:** read-only (writes local files).
- **Key parameters:** `path`, `output_dir`.

#### sdk_unify
- **What it does:** Combines a content directory into a unified YAML file.
- **Risk:** read-only (writes local files).
- **Key parameters:** `path`, `output_file`.

#### sdk_generate_docs
- **What it does:** Generates README documentation for content.
- **Risk:** read-only (writes local files).
- **Key parameters:** `path`, `output_dir`.

#### sdk_download
- **What it does:** Downloads content from the tenant to local files for editing.
- **Risk:** read-only (writes local files).
- **Key parameters:** `content_name`, `output_dir`.

#### sdk_upload
- **What it does:** Uploads a content pack/integration/script to the tenant.
- **Risk:** HIGH-destructive (deploys to tenant).
- **Key parameters:** `path`.

#### sdk_run
- **What it does:** Executes an integration command on the tenant via the SDK (dev testing).
- **Risk:** HIGH-destructive (runs command against tenant).
- **Key parameters:** `command`, `integration_name`.

#### sdk_run_playbook
- **What it does:** Runs a playbook on the tenant via the SDK for testing.
- **Risk:** HIGH-destructive (executes playbook).
- **Key parameters:** `playbook_name`, `wait`, `timeout`.

#### create_playbook
- **What it does:** Generates an XSOAR/XSIAM playbook YAML (+ZIP) with smart content discovery.
- **Risk:** write (creates files; upload via `insert_playbook`).
- **Key parameters:** `name`, `description`, `tasks` (JSON), `output_path`, `skip_discovery`.

#### create_parsing_rule
- **What it does:** Creates a ParsingRule (YML + XIF) for parsing raw logs.
- **Risk:** write (creates files; optional upload).
- **Key parameters:** `pack_name`, `rule_name`, `vendor`, `product`, `target_dataset`, `xql_rules`, `upload`.

#### create_modeling_rule
- **What it does:** Creates a ModelingRule (YML + XIF) mapping data to XDM.
- **Risk:** write (creates files; optional upload).
- **Key parameters:** `pack_name`, `rule_name`, `dataset`, `model`, `xql_rules`, `schema_json`, `upload`.

#### create_assets_modeling_rule
- **What it does:** Creates an AssetsModelingRule (model="Assets") for asset inventory mapping.
- **Risk:** write (creates files; optional upload).
- **Key parameters:** `pack_name`, `rule_name`, `dataset`, `xql_rules`, `upload`.

#### create_case_field
- **What it does:** Creates a CaseField (custom field on Cases) JSON.
- **Risk:** write (creates files; optional upload).
- **Key parameters:** `pack_name`, `field_id`, `field_name`, `field_type`, `select_values`, `upload`.

#### create_case_layout
- **What it does:** Creates a CaseLayout (UI structure for Cases, group="case") JSON.
- **Risk:** write (creates files; optional upload).
- **Key parameters:** `pack_name`, `layout_name`, `tabs`, `upload`.

#### create_case_layout_rule
- **What it does:** Creates a CaseLayoutRule selecting a CaseLayout by conditions.
- **Risk:** write (creates files; requires pack upload to deploy).
- **Key parameters:** `pack_name`, `rule_name`, `layout_id`, `upload`.

#### create_xsiam_dashboard
- **What it does:** Creates an XSIAMDashboard JSON, optionally with an XQL widget.
- **Risk:** write (creates files; requires pack upload).
- **Key parameters:** `pack_name`, `dashboard_name`, `xql_query`, `widget_type`, `widget_title`, `upload`.

#### create_xsiam_report
- **What it does:** Creates an XSIAMReport JSON, optionally with an XQL widget.
- **Risk:** write (creates files; requires pack upload).
- **Key parameters:** `pack_name`, `report_name`, `xql_query`, `widget_type`, `dashboard_id`, `upload`.

#### create_agentix_action
- **What it does:** Creates an AgentIXAction YAML wrapping an existing command/script/playbook for AI agents.
- **Risk:** write (creates files; optional upload).
- **Key parameters:** `pack_name`, `action_name`, `display_name`, `description`, `underlying_type`, `underlying_id`, `underlying_name`, `args`, `outputs`, `requires_user_approval`, `upload`.

#### create_agentix_agent
- **What it does:** Creates an AgentIXAgent YAML defining an AI assistant configuration.
- **Risk:** write (creates files; optional upload).
- **Key parameters:** `pack_name`, `agent_name`, `description`, `color`, `visibility`, `action_ids`, `system_instructions`, `conversation_starters`, `upload`.

#### get_xsiam_content_guide
- **What it does:** Returns a guide to XSIAM content types (Case vs Issue, file structure, upload).
- **Risk:** read-only.
- **Key parameters:** none.

### Widgets

#### get_widgets
- **What it does:** Lists XQL dashboard widgets.
- **Risk:** read-only.
- **Key parameters:** `request_data.filters` or empty.

#### insert_widgets
- **What it does:** Creates XQL dashboard widgets.
- **Risk:** write.
- **Key parameters:** `request_data.widgets` = `[{tab_id, widget_key, title, widget_type, params:{xql_query, time_frame}, ...}]`.

#### delete_widgets
- **What it does:** Deletes XQL dashboard widgets by key.
- **Risk:** HIGH-destructive (irreversible).
- **Key parameters:** `request_data` = `{"widget_keys": ["<key>"]}`.

### Assets & Vulnerabilities

#### get_assets
- **What it does:** Retrieves all assets or a filtered list (max 1000/request).
- **Risk:** read-only.
- **Key parameters:** `request_data.filters` (AND/OR groups with SEARCH_FIELD/TYPE/VALUE), `on_demand_fields`, `search_from`, `search_to`, `sort`.

#### get_asset_by_id
- **What it does:** Retrieves detailed info for one asset.
- **Risk:** read-only.
- **Key parameters:** `asset_id`.

#### get_vulnerabilities
- **What it does:** Retrieves vulnerabilities matching filters, with cursor-based pagination.
- **Risk:** read-only.
- **Key parameters:** `request_data` (filters: cvss_score, cvss_severity, cisa_kev, epss_score, vulnerability_id, vendors, etc.), `use_page_token` (must be true), `next_page_token`, `sort`.
- **Notes:** Requires Cortex Cloud Posture Management add-on.

#### trigger_vulnerability_scan
- **What it does:** Triggers a vulnerability scan on a specific asset.
- **Risk:** HIGH-destructive (agent/scanner action).
- **Key parameters:** `asset_id`, `scanner_type` (default CORTEX_XDR_AGENT).
- **Notes:** Requires Cloud Runtime Security / Posture Management license.

#### get_assessment_profile_results
- **What it does:** Retrieves assessment profile results (last successful evaluation), optionally filtered by labels.
- **Risk:** read-only.
- **Key parameters:** `request_data.filters` (field=labels, contains/not_contains).

### Audit & Platform

#### get_tenant_info
- **What it does:** Retrieves tenant license info (Cortex environment, license type).
- **Risk:** read-only.
- **Key parameters:** none.

#### get_audit_management_log
- **What it does:** Retrieves audit management logs (typed filter schema, sort, pagination).
- **Risk:** read-only.
- **Key parameters:** `request_data.filters` (email/type/sub_type/result via `in`; timestamp via gte/lte/eq in epoch ms), `search_from`, `search_to` (max 100), `sort`.

#### get_audit_management_logs
- **What it does:** Retrieves management audit logs (who did what, API key usage, config changes).
- **Risk:** read-only.
- **Key parameters:** `filters`, `search_from`, `search_to`, `sort`.
- **Notes:** Looser variant of `get_audit_management_log`.

#### get_triage_presets
- **What it does:** Lists forensic triage presets (predefined IR data-collection configs).
- **Risk:** read-only.
- **Key parameters:** none.
- **Notes:** Requires Forensics add-on license.

#### test_all_tools
- **What it does:** Comprehensive testing framework that systematically exercises the ~100+ MCP tools by category.
- **Risk:** write (can invoke many tools; `skip_destructive=True` by default).
- **Key parameters:** `categories`, `skip_destructive`, `endpoint_id`, `test_case_id`, `test_alert_id`, `verbose`.
- **Notes:** Do not run casually — it drives real tools against the tenant.

### War Room

#### get_war_room_entries
- **What it does:** Gets War Room entries for a case/alert, filterable by time/ID/category/tags.
- **Risk:** read-only.
- **Key parameters:** `id` (`CASE-{id}` or alert id), `filter` (categories, pagesize, fromTime, firstID/lastID, tags).

#### add_war_room_entry
- **What it does:** Adds an entry (note or `!command`) to a case/alert War Room.
- **Risk:** write (can run commands).
- **Key parameters:** `id` (`CASE-{id}` or alert id), `data` (text or `!command`).
- **Notes:** Requires an alert that is part of a case with an active investigation.

### Developer Guides (read-only reference)

All return static reference markdown; **read-only**, no parameters unless noted.

| Tool | Purpose |
|---|---|
| `get_xsoar_pattern_guide` | Recognize which integration pattern to use (call first) |
| `get_xsoar_best_practices` | Integration dev best practices (`topic`: threading/state/all) |
| `get_xsoar_event_collector_guide` | Building event collector integrations |
| `get_xsoar_feed_guide` | Building threat-intel feed integrations |
| `get_xsoar_long_running_guide` | Building long-running integrations |
| `get_xsoar_mirroring_guide` | Building bidirectional mirroring integrations |
| `get_xsoar_scheduled_commands_guide` | Scheduled commands / polling pattern |
| `get_xsoar_layout_guide` | Creating layouts + button syntax |
| `get_xsoar_playbook_operat_1bf2581c` | Running playbooks on alerts/incidents; correlation-rule limits |
| `get_slack_interactive_wor_58758a43` | Building interactive Slack workflows (SlackAskV2, entitlements) |

---

*This document is generated from the cortex_bot MCP tool schemas. Every tool is
documentation-only here; no tool was invoked. Treat all write/destructive tools as
requiring explicit operator approval before use.*
