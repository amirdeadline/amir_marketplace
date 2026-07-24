# elastic

Elasticsearch/Kibana REST helper + ES|QL/DSL and detections skills. Index delete requires typed confirmation. Optional MCP to Kibana Agent Builder.

## Pattern

**Knowledge+API + optional Kibana Agent Builder MCP (mcp-remote) when ELASTIC_KIBANA_URL set**



## Prerequisites

ELASTIC_BASE_URL + ELASTIC_API_KEY. Optional Kibana MCP via npx mcp-remote.

## Environment

`ELASTIC_BASE_URL`, `ELASTIC_API_KEY`, `ELASTIC_KIBANA_URL (optional for MCP)`

All secrets from env only; displayed as `****last4`. Never written to files by this plugin.

## Safety

Deletes typed confirm. MCP optional (Kibana Agent Builder). Verified: elastic.co Agent Builder MCP endpoint.

Default mode is **read-only**. State-changing actions confirm first and print the exact command/request.

## Always-on token cost (estimate)

~1.0k

Heavy material lives under `skills/*/references/` (on demand).

## Examples

See commands under `/` + plugin namespace after install (e.g. `/elastic:`â€¦).

## Install

Packed into `amir_marketplace` as `elastic`.

## PARTIALLY DOABLE

Optional Kibana Agent Builder MCP (mcp-remote) requires `ELASTIC_KIBANA_URL` and
`ELASTIC_AUTH_HEADER` (`ApiKey …`). If unset, ignore/disable that MCP entry and use
`scripts/api_helper.py` (REST) instead — do not treat MCP failure as a credential leak.
