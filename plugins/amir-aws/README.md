# aws

AWS via official managed MCP (mcp-proxy-for-aws) plus aws CLI fallback. Preflight STS; mutations confirm-first.

## Pattern

**MCP (official AWS MCP Server) + CLI-wrap fallback**

Verified: https://github.com/aws/agent-toolkit-for-aws

## Prerequisites

uv/uvx + AWS credentials (same as CLI). Optional: aws CLI on PATH.

## Environment

`AWS_REGION`, `AWS_PROFILE (optional)`

All secrets from env only; displayed as `****last4`. Never written to files by this plugin.

## Safety

STS preflight. Mutations confirm. Keys never in files. Official MCP verified: aws/agent-toolkit-for-aws mcp-proxy-for-aws@1.6.3.

Default mode is **read-only**. State-changing actions confirm first and print the exact command/request.

## Always-on token cost (estimate)

~1.2k (+ MCP tools discovered at runtime)

Heavy material lives under `skills/*/references/` (on demand).

## Examples

See commands under `/` + plugin namespace after install (e.g. `/aws:`…).

## Install

Packed into `amir_marketplace` as `aws`.
