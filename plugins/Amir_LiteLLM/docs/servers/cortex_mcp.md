# cortex_mcp

## Overview

`cortex_mcp` is the **read-only** query surface for **Palo Alto Cortex XSIAM / XDR**,
exposed through the MCP gateway. Every tool is a `get_*` operation that retrieves
information from a Cortex tenant without changing any state.

It lets an agent inspect:

- **Cases** — grouped security incidents (`get_cases`).
- **Issues / alerts** — individual security events (`get_issues`).
- **Assets** — asset inventory, individual assets, and asset-assessment results
  (`get_assets`, `get_asset_by_id`, `get_assessment_profile_results`).
- **Vulnerabilities** — CVE/vulnerability findings with rich filtering
  (`get_vulnerabilities`).
- **Endpoints** — XDR-agent-managed endpoints (`get_filtered_endpoints`).
- **Detection content** — correlation rules (`get_correlation_rules`), playbooks
  (`get_playbook`), and scripts (`get_script`).
- **Audit** — tenant management audit logs (`get_audit_management_log`).
- **Tenant** — license/tenant metadata (`get_tenant_info`).

### Relationship to `cortex_bot`

`cortex_bot` is the **full** Cortex tool surface: it includes read tools plus many
**write / destructive** actions (isolate endpoints, terminate processes, quarantine
files, insert/delete correlation rules, run scripts, blocklist hashes, SCM wipes, etc.).

**`cortex_mcp` is the safe, read-only subset of that surface** — it contains only
`get_*` tools and can never modify the tenant, endpoints, or security posture. When a
task only needs to *read* Cortex data, prefer `cortex_mcp`. Note that some tool names
overlap between the two servers (e.g. `get_cases`, `get_issues`, `get_assets`); the
`cortex_mcp` variants carry identical read semantics but no companion write actions.

> This document is documentation-only. None of these tools were invoked to produce it.

## Authentication

The MCP gateway authenticates to the Cortex tenant on the agent's behalf using
tenant-scoped Cortex API credentials configured server-side. These are referenced by
**name / mechanism only** (never by value):

- **Cortex API Key** — the secret advanced/standard API key.
- **Cortex API Key ID** — the numeric identifier paired with the API key
  (sent in the request headers alongside the key).
- **Cortex tenant FQDN / API base URL** — the tenant-specific API host the gateway
  targets.

None of the `cortex_mcp` tools accept credentials as parameters; authentication is
handled entirely by the gateway configuration. No secret values are ever passed through
tool arguments or returned in responses.

## Tools

### get_tenant_info

**What it does:** Retrieves the tenant's license information, including Cortex
environment details and license type.

**Details:** Useful for verifying license status, entitlements, and general operational
visibility/compliance for the connected tenant. Lightweight — takes no filters.

**Key parameters:** None.

**Example usage:**
```json
{}
```

---

### get_cases

**What it does:** Retrieves a list of cases (incidents) from the Cortex platform,
optionally filtered.

**Details:** Cases are containers for related security events. Use for security
monitoring, historical analysis, and reporting. Leave `filters` empty to fetch all
cases. Results are paginated and sorted (default: `creation_time`, descending).

**Key parameters:**
- `filters` — array of objects — **required** — list of filter clauses to select cases;
  pass an empty array `[]` to get all cases. Each clause is a free-form object
  (field/operator/value style).
- `search_from` — integer — optional (default `0`) — pagination start marker.
- `search_to` — integer — optional (default `30`, max `100`) — pagination end marker.
- `sort` — object — optional — `{field, keyword}` to override the default sort.

**Example usage:**
```json
{ "filters": [], "search_from": 0, "search_to": 30 }
```

---

### get_issues

**What it does:** Retrieves a list of issues (alerts), a filtered subset, or a single
issue from the Cortex platform.

**Details:** Issues/alerts are individual security events (contrast with cases, which
group them). Filter by time range, severity, status, or specific alert IDs. Valuable for
security monitoring, threat hunting, and reporting. Leave `filters` empty to fetch all
issues. Default sort is by observation time, descending.

**Key parameters:**
- `filters` — array of objects — **required** — filter clauses; empty array `[]` returns
  all issues.
- `search_from` — integer — optional (default `0`) — pagination start marker.
- `search_to` — integer — optional (default `30`) — pagination end marker.
- `sort` — object — optional — `{field, keyword}` to override the default sort.

**Example usage:**
```json
{ "filters": [{ "field": "severity", "operator": "in", "value": ["high", "critical"] }] }
```

---

### get_filtered_endpoints

**What it does:** Retrieves a filtered list of endpoints managed by the Cortex XDR
agents, by ID, status, platform, and other attributes.

**Details:** Wraps a strongly-typed request object. Each filter clause is one
`{field, operator, value}` triple where the allowed `field` values are a fixed
enumeration and `operator` is almost always `in` (except time fields, which also allow
`gte`/`lte`/`eq`). Supports pagination and sorting.

**Key parameters (all inside `request_data`):**
- `filters` — array of clauses — optional — each is `{field, operator, value}`. Supported
  fields include: `endpoint_id_list`, `endpoint_status`
  (`connected`/`disconnected`/`lost`/`uninstalled`), `dist_name`, `first_seen`,
  `last_seen` (epoch-ms integers), `ip_list`, `public_ip_list`, `group_name`,
  `platform` (`windows`/`linux`/`macos`/`android`), `alias`, `isolate`
  (`isolated`/`unisolated`), `hostname`, `username`, and `scan_status`.
- `search_from` — integer — optional (default `0`) — zero-based start offset.
- `search_to` — integer — optional (default `100`) — end offset.
- `sort` — object — optional — `{field, keyword}` where `field` ∈
  `endpoint_id`/`first_seen`/`last_seen`/`scan_status` and `keyword` ∈ `ASC`/`DESC`.

**Example usage:**
```json
{
  "request_data": {
    "filters": [
      { "field": "endpoint_status", "operator": "in", "value": ["connected"] },
      { "field": "platform", "operator": "in", "value": ["windows"] }
    ],
    "search_from": 0,
    "search_to": 100
  }
}
```

---

### get_assets

**What it does:** Retrieves all assets, or a filtered list, from the asset inventory
(max 1000 assets per request).

**Details:** Uses a nested boolean filter grouping. `filters` is a logical group with
`AND` and/or `OR` arrays; each element is a criterion
`{SEARCH_FIELD, SEARCH_TYPE, SEARCH_VALUE}`. `SEARCH_TYPE` is a comparison operator
(`EQ`, `NEQ`, `GT`, `GTE`, `LT`, `LTE`, `LIKE`, `CONTAINS`, `IN`, `NOT_IN`). Supports
on-demand fields, pagination, and sorting.

**Key parameters (all inside `request_data`):**
- `filters` — object — optional — logical grouping with `AND` / `OR` arrays of
  `{SEARCH_FIELD, SEARCH_TYPE, SEARCH_VALUE}` criteria (e.g. field
  `xdm.asset.type.class`).
- `on_demand_fields` — array of strings — optional — extra fields to include.
- `search_from` — integer — optional (default `0`).
- `search_to` — integer — optional (default `1000`).
- `sort` — array — optional — list of `{FIELD, ORDER}` (`ASC`/`DESC`).

**Example usage:**
```json
{
  "request_data": {
    "filters": {
      "AND": [
        { "SEARCH_FIELD": "xdm.asset.type.class", "SEARCH_TYPE": "EQ", "SEARCH_VALUE": "endpoint" }
      ]
    },
    "search_to": 100
  }
}
```

---

### get_asset_by_id

**What it does:** Retrieves detailed information about a single asset by its asset ID.

**Details:** Point lookup for one asset record; use `get_assets` first to discover asset
IDs.

**Key parameters:**
- `asset_id` — string — **required** — the unique identifier of the asset.

**Example usage:**
```json
{ "asset_id": "a1b2c3d4-0000-1111-2222-333344445555" }
```

---

### get_assessment_profile_results

**What it does:** Retrieves assessment-profile results based on the last successful
evaluation, with optional filtering.

**Details:** Returns posture/assessment evaluation output for assets. Filtering is
limited to the `labels` field.

**Key parameters (inside `request_data`):**
- `filters` — array — optional — each clause is `{field, operator, value}` where `field`
  is `labels` and `operator` is `contains` or `not_contains`.

**Example usage:**
```json
{
  "request_data": {
    "filters": [{ "field": "labels", "operator": "contains", "value": "production" }]
  }
}
```

---

### get_vulnerabilities

**What it does:** Retrieves a filtered list of vulnerabilities (CVEs/findings) with key
details. Requires the Cortex Cloud Posture Management add-on.

**Details:** Uses **cursor-based pagination** — every request must set
`use_page_token: true`, and each response returns a `next_page_token` that must be fed
back into the next request. If the filters change, pagination restarts from the first
page. The tool is designed to auto-continue paging until the requested count is reached
or the token stops advancing. `filters` is a rich typed array with per-field operator and
value constraints.

**Key parameters (inside `request_data`):**
- `use_page_token` — boolean — **required** — must be `true` to enable pagination.
- `next_page_token` — string — optional — the token from the previous response's
  `next_page_token` for the next page.
- `filters` — array — optional — typed clauses `{field, operator, value}`. Supported
  fields include: `attack_vector`, `cisa_kev` (boolean), `cvss_score` (number),
  `cvss_score_source`, `cvss_severity` (`NONE`/`LOW`/`MEDIUM`/`HIGH`/`CRITICAL`),
  `cvss_severity_source`, `cvss_version`, `distribution_and_releases` (string array),
  `epss_score` (number), `first_published` / `last_modified` (epoch-ms, range, or relative
  timestamps), `package_names`, `reported_exploited_by`, `vendors`, `vulnerability_id`
  (e.g. `CVE-2024-1234`), and `affected_cpu_archs`. Operators vary by field
  (`eq`/`neq`/`gte`/`lte`/`contains`/`not_contains`/`range`/`relative_timestamp`).
- `search_from` — integer — optional (default `0`) — start offset.
- `search_to` — integer — optional (default `500`) — end offset / page size.
- `sort` — object — optional — `{field, keyword}` (`asc`/`desc`); `field` must be a
  non-array filter field.

**Example usage:**
```json
{
  "request_data": {
    "use_page_token": true,
    "filters": [
      { "field": "cvss_severity", "operator": "eq", "value": "CRITICAL" },
      { "field": "cisa_kev", "operator": "eq", "value": true }
    ],
    "search_to": 100
  }
}
```

---

### get_correlation_rules

**What it does:** Retrieves correlation rules defined on the tenant — the tenant's
detection logic.

**Details:** Use to inspect existing detection coverage: find rules by name, severity,
status (enabled/disabled), XQL query content, MITRE definitions, alert metadata, and
execution mode. Filters are combined with logical AND; the operator and value format
vary per field (the schema enumerates the allowed fields, operators, and value types).
Set `extended_view: true` to return the full rule definition (XQL query, MITRE mapping,
schedule, suppression settings, etc.).

**Key parameters (inside `request_data`):**
- `filters` — array — optional — per-field typed clauses `{field, operator, value}`.
  Fields include string types (`name`, `xql_query`, `description`, `alert_name`,
  `dataset`, `timezone`, `crontab`, etc. with `EQ`/`NEQ`/`IN`), enums (`severity`
  `SEV_010_INFO`…`SEV_040_HIGH`; `is_enabled` `enabled`/`disabled`; `alert_category`;
  `execution_mode` `scheduled`/`real_time`; `alert_domain`; `mapping_strategy`), a
  boolean (`suppression_enabled`), and string arrays (`suppression_fields`,
  `mitre_defs` with `IN`). Empty list returns all rules (subject to pagination).
- `extended_view` — boolean — optional — include full rule definition when `true`.
- `search_from` — integer — optional (default `0`) — start offset.
- `search_to` — integer — optional (default `100`) — end offset.

**Example usage:**
```json
{
  "request_data": {
    "filters": [{ "field": "is_enabled", "operator": "EQ", "value": "enabled" }],
    "extended_view": true
  }
}
```

---

### get_audit_management_log

**What it does:** Retrieves tenant management audit logs (actions performed on the
tenant), with filtering, sorting, and pagination.

**Details:** Audit entries record who did what and when. Filter clauses come in two
shapes: a **string-list** filter for `email`/`type`/`sub_type`/`result` (operator `in`,
value is a string array), and a **numeric timestamp** filter for `timestamp` (operators
`gte`/`lte`/`eq`, value is epoch **milliseconds** as a JSON integer — never a float or
string).

**Key parameters (inside `request_data`):**
- `filters` — array — optional — clauses combined with AND; empty list = no scoping.
  Shape 1: `{field: email|type|sub_type|result, operator: in, value: [strings]}`.
  Shape 2: `{field: timestamp, operator: gte|lte|eq, value: <epoch-ms integer>}`.
- `search_from` — integer — optional (default `0`) — zero-based first result.
- `search_to` — integer — optional (default `100`, server max `100`) — last result
  (exclusive).
- `sort` — object — optional — `{field, keyword}`; `field` ∈
  `timestamp`/`email`/`type`/`sub_type`/`result`, `keyword` ∈ `asc`/`desc`
  (default: `timestamp` desc).

**Example usage:**
```json
{
  "request_data": {
    "filters": [
      { "field": "result", "operator": "in", "value": ["FAILURE"] },
      { "field": "timestamp", "operator": "gte", "value": 1730419200000 }
    ]
  }
}
```

---

### get_playbook

**What it does:** Retrieves a playbook from Cortex by display name or UUID, parsing its
returned archive into structured content.

**Details:** Cortex returns the playbook as a ZIP archive of YAML/JSON files. The tool
downloads it in memory, parses each entry, and returns the structured contents so the
playbook YAML can be read and analyzed directly. `identifier_type` defaults to `auto`,
which sends `id` when the identifier looks like a UUID and `name` otherwise.

**Key parameters:**
- `identifier` — string — **required** — playbook display name (e.g.
  `Investigation - Suspicious Login`) or UUID.
- `identifier_type` — enum `auto`/`id`/`name` — optional (default `auto`) — force lookup
  by UUID or by display name when auto-detection misroutes.
- `include_metadata` — boolean — optional (default `false`) — include the
  `metadata.json` content-pack wrapper (packID, packName, tags, etc.).

**Example usage:**
```json
{ "identifier": "Investigation - Suspicious Login", "identifier_type": "auto" }
```

---

### get_script

**What it does:** Retrieves an automation script from Cortex by display name or UUID,
parsing its returned archive into structured content.

**Details:** Like `get_playbook`, Cortex returns the script as a ZIP archive (the script
source plus optional pack metadata). The tool downloads it in memory, parses each
YAML/JSON entry, and returns the structured contents so the script can be read and
analyzed. `identifier_type` `auto` picks `id` for UUID-shaped identifiers, else `name`.

**Key parameters:**
- `identifier` — string — **required** — script display name (e.g.
  `CommonServerPython`) or UUID.
- `identifier_type` — enum `auto`/`id`/`name` — optional (default `auto`) — force lookup
  mode when auto-detection misroutes.
- `include_metadata` — boolean — optional (default `false`) — include the
  `metadata.json` content-pack wrapper.

**Example usage:**
```json
{ "identifier": "CommonServerPython" }
```
