# sentinel

Microsoft Sentinel: KQL hunting skill + analytics/incidents helpers. Queries read-free; rule/incident mutations confirm-first. Reuses az auth.

## Pattern

**Knowledge+API via Azure (az / Log Analytics REST)**



## Prerequisites

az login; workspace IDs via env SENTINEL_WORKSPACE_ID, SENTINEL_RESOURCE (optional ARM id)

## Environment

`SENTINEL_WORKSPACE_ID`, `SENTINEL_RESOURCE (optional)`

All secrets from env only; displayed as `****last4`. Never written to files by this plugin.

## Safety

KQL reads free. Rule/incident writes confirm. Uses az credentials (no keys in files).

Default mode is **read-only**. State-changing actions confirm first and print the exact command/request.

## Always-on token cost (estimate)

~1.0k

Heavy material lives under `skills/*/references/` (on demand).

## Examples

See commands under `/` + plugin namespace after install (e.g. `/sentinel:`…).

## Install

Packed into `amir_marketplace` as `sentinel`.
