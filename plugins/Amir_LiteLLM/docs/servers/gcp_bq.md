# gcp_bq

## Overview

The **gcp_bq** MCP server provides read-and-query access to **Google BigQuery**. It lets
you explore the warehouse structure and run SQL against it:

- **Discover** datasets in the configured project(s) (`get_datasets`).
- **List** the tables inside a dataset (`get_tables`).
- **Search** dataset / table / column metadata by keyword (`search_metadata`).
- **Estimate** how much data a query will scan, without running it — a dry-run cost check
  (`check_query_scan_amount`).
- **Run** SQL with built-in safety checks and automatic `LIMIT` management
  (`execute_query`).

**Recommended flow:** discover structure with `get_datasets` / `get_tables` /
`search_metadata`, then **dry-run first** with `check_query_scan_amount` to confirm the
scan volume (BigQuery bills on bytes scanned), and only then call `execute_query`.

All tools are exposed as `mcp__mcp-gateway__gcp_bq__<tool>`.

## Authentication

The server authenticates to BigQuery using **GCP service-account / Application Default
Credentials (ADC)** scoped to one or more **project IDs**. Authentication is handled by
the server's environment; you do not pass credentials in tool calls.

Mechanisms and credential **names** only (never print secret values):

- **GOOGLE_APPLICATION_CREDENTIALS** — path to a GCP service-account key / ADC credential
  used by the BigQuery client.
- **Application Default Credentials (ADC)** — the standard GCP credential-resolution chain
  (env key file, gcloud user creds, or attached service account).
- **Project ID** — every tool accepts an optional `project_id`; when omitted, the server
  falls back to the **first configured project**.

Secrets are supplied out of band via the environment; only names appear here.

## Tools

### mcp__mcp-gateway__gcp_bq__get_datasets

**What it does:** Returns the list of all BigQuery datasets available to the configured
project.

**Details:** A structure-discovery call. Use it as the first step to learn which datasets
exist before drilling into tables or writing queries. Takes no parameters; operates on the
server's configured project context.

**Key parameters:** None.

**Example usage:**
```json
{}
```

### mcp__mcp-gateway__gcp_bq__get_tables

**What it does:** Returns the list of all tables in a given dataset.

**Details:** Second discovery step after `get_datasets`. Names the dataset to enumerate its
tables. Optionally targets a specific project; otherwise the first configured project is
used.

**Key parameters:**
- `dataset_id` — string — **required** — the dataset whose tables to list.
- `project_id` — string or null — optional — project to query; defaults to the first
  configured project when omitted/null.

**Example usage:**
```json
{
  "dataset_id": "analytics_prod"
}
```

### mcp__mcp-gateway__gcp_bq__search_metadata

**What it does:** Searches metadata across datasets, tables, and columns for a keyword.

**Details:** Useful when you know roughly what you are looking for (e.g. a column name like
`user_id` or a table topic) but not where it lives. Matches the supplied key against
dataset, table, and column metadata and returns the matching entries.

**Key parameters:**
- `key` — string — **required** — the search term to match against dataset/table/column
  metadata.

**Example usage:**
```json
{
  "key": "revenue"
}
```

### mcp__mcp-gateway__gcp_bq__check_query_scan_amount

**What it does:** Performs a **dry-run** of a SQL query to report how many bytes it would
scan, **without executing it**.

**Details:** BigQuery bills on bytes scanned, so this is the cost/safety pre-check. It uses
BigQuery's dry-run mode: no data is read and no results are returned — only the estimated
scan amount. **Run this before `execute_query`** on any unfamiliar or potentially large
query to avoid scanning more data than intended.

**Key parameters:**
- `sql` — string — **required** — the SQL query to estimate.
- `project_id` — string or null — optional — project to run the dry-run against; defaults
  to the first configured project when omitted/null.

**Example usage:**
```json
{
  "sql": "SELECT event_name, COUNT(*) FROM analytics_prod.events GROUP BY event_name"
}
```

### mcp__mcp-gateway__gcp_bq__execute_query

**What it does:** Executes a BigQuery SQL query and returns the results.

**Details:** Runs SQL with **automatic safety checks and `LIMIT` clause management** — the
server applies/adjusts a `LIMIT` and validates the query before execution to guard against
runaway or oversized result sets. Best practice: confirm scan cost with
`check_query_scan_amount` first, then execute. Optionally targets a specific project;
otherwise the first configured project is used.

**Key parameters:**
- `sql` — string — **required** — the SQL query to execute.
- `project_id` — string or null — optional — project to run against; defaults to the first
  configured project when omitted/null.

**Example usage:**
```json
{
  "sql": "SELECT event_name, COUNT(*) AS n FROM analytics_prod.events GROUP BY event_name ORDER BY n DESC"
}
```
