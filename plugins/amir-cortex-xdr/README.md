# cortex-xdr

Cortex XDR API: read incidents/alerts/endpoints; response actions require typed confirmation.

## Pattern

**Knowledge+API (Cortex XDR)**



## Prerequisites

XDR_FQDN + XDR_API_KEY_ID + XDR_API_KEY (Advanced API)

## Environment

`XDR_FQDN`, `XDR_API_KEY_ID`, `XDR_API_KEY`

All secrets from env only; displayed as `****last4`. Never written to files by this plugin.

## Safety

Response actions require typed confirmation action+endpoint_id. Keys masked.

Default mode is **read-only**. State-changing actions confirm first and print the exact command/request.

## Always-on token cost (estimate)

~1.0k

Heavy material lives under `skills/*/references/` (on demand).

## Examples

See commands under `/` + plugin namespace after install (e.g. `/cortex-xdr:`…).

## Install

Packed into `amir_marketplace` as `cortex-xdr`.
