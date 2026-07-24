# azure

Azure via official Azure MCP Server (@azure/mcp) and az CLI. Preflight account show; mutations confirm-first.

## Pattern

**MCP (Azure MCP Server) + CLI-wrap (az)**



## Prerequisites

Node/npx + az login. Official: microsoft/mcp Azure.Mcp.Server.

## Environment

`AZURE_SUBSCRIPTION_ID (optional)`

All secrets from env only; displayed as `****last4`. Never written to files by this plugin.

## Safety

az account show preflight. Mutations confirm. Verified MCP: npx @azure/mcp server start (microsoft/mcp).

Default mode is **read-only**. State-changing actions confirm first and print the exact command/request.

## Always-on token cost (estimate)

~1.3k

Heavy material lives under `skills/*/references/` (on demand).

## Examples

See commands under `/` + plugin namespace after install (e.g. `/azure:`…).

## Install

Packed into `amir_marketplace` as `azure`.
