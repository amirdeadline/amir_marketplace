# confluence

## Overview

The **confluence** MCP server provides read access to an Atlassian Confluence wiki
(Cloud or Server/Data Center). It lets an agent discover and read knowledge-base
content without leaving the toolchain:

- **Search** for pages using either simple text or full CQL (Confluence Query Language).
- **Read a page's content** by page ID, or by title + space key, returned as Markdown
  (default) or raw HTML.
- **List child pages** of a given parent page (optionally with their content).
- **Read the comment threads** attached to a page.

Typical use cases:

- Pulling design docs, runbooks, or how-to guides into an automation or research task.
- Locating a page by keyword, then reading its body and discussion.
- Walking a documentation tree (parent → children) to build context.
- Reviewing feedback/comments left on a specification page.

All tools are read-only; there are no create/update/delete operations exposed here.

Every tool is namespaced as `mcp__mcp-gateway__confluence__<tool>`.

## Authentication

Authentication and the target site are configured on the MCP gateway/server side, not
passed per call. None of the tools below take credentials as parameters — you supply
only page IDs, titles, space keys, or queries.

Confluence access is established by the server via (mechanism / credential **names**
only — never embed secret values):

- **Base URL** of the Confluence site (e.g. the `*.atlassian.net/wiki` Cloud URL, or the
  on-prem Server/Data Center URL).
- **Confluence Cloud:** an account **username / email** paired with an **API token**
  (Atlassian API token). Commonly configured through environment variables such as
  `CONFLUENCE_URL`, `CONFLUENCE_USERNAME`, and `CONFLUENCE_API_TOKEN` (names are
  deployment-specific).
- **Confluence Server / Data Center:** a **Personal Access Token (PAT)**, commonly
  configured via an environment variable such as `CONFLUENCE_PERSONAL_TOKEN`
  (name is deployment-specific).
- An optional **spaces filter** may be configured server-side (e.g.
  `CONFLUENCE_SPACES_FILTER`) to scope searches to a default set of spaces; the
  `confluence_search` tool can override it per call.

Store all of the above via your secret manager / environment. Reference credentials by
name only; never print token or password values.

## Tools

### confluence_search

**What it does:** Searches Confluence content and returns a list of simplified page
objects matching the query.

**Details:**
- Accepts either a **simple text** query or a full **CQL** (Confluence Query Language)
  string. Simple text uses `siteSearch` by default (mimics the web UI search), with an
  automatic fallback to `text` search when `siteSearch` is unsupported.
- The result count is bounded by `limit` (1–50).
- `spaces_filter` narrows results to specific space keys and overrides any server-side
  `CONFLUENCE_SPACES_FILTER` default; pass an empty string to disable filtering.
- CQL supports rich predicates. Examples from the schema:
  - Basic: `type=page AND space=DEV`
  - Personal space (must quote keys starting with `~`): `space="~username"`
  - By title: `title~"Meeting Notes"`
  - Site search: `siteSearch ~ "important concept"`
  - Text search: `text ~ "important concept"`
  - Recent: `created >= "2023-01-01"`
  - By label: `label=documentation`
  - Recently modified: `lastModified > startOfMonth("-1M")`
  - Contributor: `contributor = currentUser() AND lastModified > startOfWeek()`
  - Watcher: `watcher = "user@domain.com" AND type = page`
  - Exact phrase + label: `text ~ "\"Urgent Review Required\"" AND label = "pending-approval"`
  - Title wildcards across spaces: `title ~ "Minutes*" AND (space = "HR" OR space = "Marketing")`
- Note: special identifiers (personal space keys, reserved words, numeric IDs, values
  with special characters) must be properly quoted in CQL.

**Key parameters:**

| Name | Type | Required? | Meaning |
| --- | --- | --- | --- |
| `query` | string | Yes | Simple text OR a CQL query string (see examples above). |
| `limit` | integer (1–50) | No (default 10) | Maximum number of results to return. |
| `spaces_filter` | string \| null | No (default null) | Comma-separated space keys to filter by; overrides the server env default. Empty string disables filtering. |

**Example usage:**

```json
// Simple text search
{ "query": "prisma sase lab runbook", "limit": 10 }

// CQL search scoped to a space, filtered by label
{ "query": "type=page AND space=DEV AND label=documentation", "limit": 25 }

// Restrict simple search to specific spaces
{ "query": "onboarding guide", "spaces_filter": "HR,IT" }
```

---

### confluence_get_page

**What it does:** Retrieves the content and/or metadata of a specific Confluence page,
identified either by page ID or by exact title + space key.

**Details:**
- Provide **either** `page_id` **or** both `title` and `space_key`. If `page_id` is
  given, `title` and `space_key` are ignored.
- The numeric `page_id` can be parsed from the page URL — e.g. in
  `https://example.atlassian.net/wiki/spaces/TEAM/pages/123456789/Page+Title`, the ID is
  `123456789`.
- `convert_to_markdown` controls the body format: Markdown (default) or raw HTML. Raw
  HTML can expose macros (e.g. dates) not visible in Markdown, but **significantly
  increases token usage** — prefer Markdown unless HTML detail is needed.
- `include_metadata` toggles inclusion of creation date, last update, version, and labels.

**Key parameters:**

| Name | Type | Required? | Meaning |
| --- | --- | --- | --- |
| `page_id` | string \| null | No (default null) | Numeric Confluence page ID. Provide this OR both `title`+`space_key`; if set, the other two are ignored. |
| `title` | string \| null | No (default null) | Exact page title. Must be used together with `space_key`. |
| `space_key` | string \| null | No (default null) | Space key (e.g. `DEV`, `TEAM`) the page lives in. Required when using `title`. |
| `include_metadata` | boolean | No (default true) | Include page metadata (created/updated, version, labels). |
| `convert_to_markdown` | boolean | No (default true) | Convert body to Markdown (true) or return raw HTML (false — higher token cost). |

**Example usage:**

```json
// By page ID, Markdown body + metadata (defaults)
{ "page_id": "123456789" }

// By title + space key
{ "title": "Prisma SASE Basic — LLD", "space_key": "DEV" }

// Raw HTML body, no metadata
{ "page_id": "123456789", "convert_to_markdown": false, "include_metadata": false }
```

---

### confluence_get_page_children

**What it does:** Retrieves the child pages of a specified parent page.

**Details:**
- Requires the parent page's ID (`parent_id`).
- Supports pagination via `start` (0-based offset) and `limit` (1–50 per call).
- `expand` controls which fields are expanded in the response (e.g. `version`,
  `body.storage`); defaults to `version`.
- `include_content` optionally returns each child's page content; when true,
  `convert_to_markdown` decides Markdown vs raw HTML for that content.

**Key parameters:**

| Name | Type | Required? | Meaning |
| --- | --- | --- | --- |
| `parent_id` | string | Yes | ID of the parent page whose children to retrieve. |
| `expand` | string | No (default `version`) | Comma/dotted fields to expand (e.g. `version`, `body.storage`). |
| `limit` | integer (1–50) | No (default 25) | Maximum number of child pages to return. |
| `include_content` | boolean | No (default false) | Include each child page's body content. |
| `convert_to_markdown` | boolean | No (default true) | When `include_content` is true, convert content to Markdown (true) or keep raw HTML (false). |
| `start` | integer (≥0) | No (default 0) | 0-based starting index for pagination. |

**Example usage:**

```json
// First page of children, metadata only
{ "parent_id": "123456789", "limit": 25 }

// Children with Markdown content, second page of results
{ "parent_id": "123456789", "include_content": true, "start": 25, "limit": 25 }
```

---

### confluence_get_comments

**What it does:** Retrieves the comments attached to a specific Confluence page.

**Details:**
- Returns a list of comment objects for the given page.
- Identify the page with its numeric ID (same ID form used by `confluence_get_page` and
  parseable from the page URL).

**Key parameters:**

| Name | Type | Required? | Meaning |
| --- | --- | --- | --- |
| `page_id` | string | Yes | Numeric Confluence page ID whose comments to fetch. |

**Example usage:**

```json
{ "page_id": "123456789" }
```
