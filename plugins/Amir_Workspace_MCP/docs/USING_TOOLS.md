# Using palo-* MCP tools

## Confluence (`palo-confluence`)

| Tool | Purpose |
|------|---------|
| `confluence_search` | Plain text or CQL (`use_cql=true`) |
| `confluence_get_page` | Page body by numeric id |
| `confluence_get_page_children` | Child pages |
| `confluence_get_comments` | Comments on a page |

## Jira (`palo-jira`)

| Tool | Purpose |
|------|---------|
| `jira_search` | JQL query |
| `jira_get_issue` | Issue key, e.g. `CGPOPS-123` |
| `jira_list_projects` | Visible projects |

## Asana (`palo-asana`)

Same tool surface as **amir_system** Asana MCP (`get_me`, `list_my_tasks`, `create_task`, …). Token: **`ASANA_TOKEN`** on palo.

Write tools require explicit user approval before use.

## Agent naming

| Host | Example tool name |
|------|-------------------|
| Claude Code | `mcp__palo-jira__jira_search` |
| Cursor | namespace `palo-jira`, tool `jira_search` |
