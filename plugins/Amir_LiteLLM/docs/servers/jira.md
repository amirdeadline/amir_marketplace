# jira

## Overview

The **jira** MCP server provides read-only access to an Atlassian Jira instance
(Cloud or Server/Data Center). It lets you search issues with JQL (Jira Query
Language), retrieve full details of a single issue (including comments, status
transitions, changelog, and Epic/relationship links), list the projects you can
access, discover Jira field definitions (including custom fields) by keyword, and
download attachments from an issue to a local directory.

These tools are for **finding and reading** Jira data. There are no create/update
tools exposed here; all tools query existing content or download files.

## Authentication

Authentication is handled by the MCP gateway, not by tool parameters. Jira uses:

- **Base URL** — the Jira site/instance URL (Cloud, e.g. `https://<site>.atlassian.net`,
  or a self-hosted Server/Data Center URL).
- **Credentials** — for Jira Cloud, a **username/email + API token**; for
  Jira Server/Data Center, a **Personal Access Token (PAT)**.

These are supplied to the gateway through environment/configuration by name; the
tools themselves take no credential arguments. Never pass or print secret values.

- **`JIRA_PROJECTS_FILTER`** — optional environment variable holding a
  comma-separated list of project keys. When configured, project listing and
  search are scoped to those projects unless overridden by a tool parameter
  (`projects_filter` on `jira_search`).

## Tools

### jira_search

**What it does:** Runs a JQL query and returns matching issues, with pagination
and configurable fields.

**Details:** Accepts any valid JQL string. Supports pagination via `limit` and
`start_at`, selection of returned `fields`, expansion of extra data via `expand`,
and an optional per-call `projects_filter` that overrides the
`JIRA_PROJECTS_FILTER` environment variable. Returns a JSON string with the
result set plus pagination info.

**Key parameters:**
- `jql` — string — **required** — the JQL query string.
- `fields` — string — optional (default: `description,updated,summary,priority,assignee,reporter,created,labels,status,issuetype`) — comma-separated fields to return; use `*all` for all fields (including custom), or a single field name.
- `limit` — integer — optional (default 10, range 1–50) — maximum number of results.
- `start_at` — integer — optional (default 0) — zero-based starting index for pagination.
- `projects_filter` — string — optional — comma-separated project keys to restrict results; overrides `JIRA_PROJECTS_FILTER`.
- `expand` — string — optional — fields to expand, e.g. `renderedFields`, `transitions`, `changelog`.

**JQL examples:**
- Find Epics: `issuetype = Epic AND project = PROJ`
- Issues in an Epic: `parent = PROJ-123`
- By status: `status = 'In Progress' AND project = PROJ`
- Assigned to me: `assignee = currentUser()`
- Recently updated: `updated >= -7d AND project = PROJ`
- By label: `labels = frontend AND project = PROJ`
- By priority: `priority = High AND project = PROJ`

**Example usage:**
```json
{
  "jql": "project = PROJ AND status = 'In Progress' ORDER BY updated DESC",
  "fields": "summary,status,assignee,priority",
  "limit": 25,
  "start_at": 0
}
```

### jira_get_issue

**What it does:** Retrieves the full details of a single Jira issue by key,
including comments and relationship/Epic-link information.

**Details:** Returns a JSON representation of the issue. Supports limiting the
number of comments, selecting fields, expanding extra data (rendered content,
available transitions, changelog history), returning issue properties, and
optionally updating the requesting user's view history.

**Key parameters:**
- `issue_key` — string — **required** — the issue key, e.g. `PROJ-123`.
- `fields` — string — optional (default: `description,updated,summary,priority,assignee,reporter,created,labels,status,issuetype`) — comma-separated fields; `*all` for all fields including custom, or a single field name (e.g. `duedate`).
- `expand` — string — optional — fields to expand: `renderedFields`, `transitions`, `changelog`.
- `comment_limit` — integer — optional (default 10, range 0–100) — max comments to include; `0` for none.
- `properties` — string — optional — comma-separated list of issue properties to return.
- `update_history` — boolean — optional (default true) — whether to record this issue in the user's view history.

**Example usage:**
```json
{
  "issue_key": "PROJ-123",
  "fields": "*all",
  "expand": "changelog,transitions",
  "comment_limit": 20
}
```

### jira_get_all_projects

**What it does:** Lists all Jira projects accessible to the authenticated user.

**Details:** Returns a JSON list of project objects. Project keys are returned in
uppercase. If `JIRA_PROJECTS_FILTER` is configured, only projects matching those
keys are returned. Optionally includes archived projects.

**Key parameters:**
- `include_archived` — boolean — optional (default false) — whether to include archived projects.

**Example usage:**
```json
{
  "include_archived": false
}
```

### jira_search_fields

**What it does:** Searches Jira field definitions by keyword using fuzzy
matching — useful for discovering custom field IDs (e.g. `customfield_10010`).

**Details:** Returns a JSON list of matching field definitions. An empty keyword
lists the first `limit` available fields in default order. The field list can be
force-refreshed.

**Key parameters:**
- `keyword` — string — optional (default empty) — keyword for fuzzy search; empty lists the first `limit` fields.
- `limit` — integer — optional (default 10, minimum 1) — maximum number of results.
- `refresh` — boolean — optional (default false) — force refresh of the cached field list.

**Example usage:**
```json
{
  "keyword": "story points",
  "limit": 10
}
```

### jira_download_attachments

**What it does:** Downloads all attachments from a Jira issue and saves them to a
local directory.

**Details:** Fetches the attachments on the given issue and writes them to the
specified target directory. Returns a JSON string describing the result of the
download operation.

**Key parameters:**
- `issue_key` — string — **required** — the issue key whose attachments to download, e.g. `PROJ-123`.
- `target_dir` — string — **required** — local directory where attachments should be saved.

**Example usage:**
```json
{
  "issue_key": "PROJ-123",
  "target_dir": "/tmp/proj-123-attachments"
}
```
