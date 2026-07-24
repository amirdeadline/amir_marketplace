# splunk

Splunk REST/search helper + SPL authoring skill. Saved-search/alert mutations confirm-first. PARTIALLY DOABLE: enterprise MCP is host-installed (Splunkbase app), not a local npm.

## Pattern

**Knowledge+API (local REST). Splunk MCP exists as on-platform app — optional remote URL, not bundled.**



## Prerequisites

SPLUNK_BASE_URL + SPLUNK_TOKEN (bearer). Optional Splunk MCP if admin enabled on platform.

## Environment

`SPLUNK_BASE_URL`, `SPLUNK_TOKEN`

All secrets from env only; displayed as `****last4`. Never written to files by this plugin.

## Safety

Search reads limited. Saved search/alert edits confirm. Token masked. PLATFORM MCP: https://splunkbase.splunk.com/app/7931 — not bundled.

Default mode is **read-only**. State-changing actions confirm first and print the exact command/request.

## Always-on token cost (estimate)

~0.9k

Heavy material lives under `skills/*/references/` (on demand).

## Examples

See commands under `/` + plugin namespace after install (e.g. `/splunk:`…).

## Install

Packed into `amir_marketplace` as `splunk`.

## PARTIALLY DOABLE

Splunk's official MCP is an **on-platform Splunkbase app** (not a local npm we can bundle).
This plugin ships Knowledge+API over REST. If your admin enables Splunk MCP Server, configure
it separately as a remote MCP HTTP endpoint.
