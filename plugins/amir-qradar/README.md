# qradar

QRadar REST: AQL searches + offense reads; offense/rule/reference-set writes confirm-first. SEC token masked.

## Pattern

**Knowledge+API (QRadar REST)**



## Prerequisites

QRADAR_BASE_URL + QRADAR_SEC_TOKEN

## Environment

`QRADAR_BASE_URL`, `QRADAR_SEC_TOKEN`

All secrets from env only; displayed as `****last4`. Never written to files by this plugin.

## Safety

Writes confirm. SEC token masked. Default API Version header 20.0 (override QRADAR_API_VERSION).

Default mode is **read-only**. State-changing actions confirm first and print the exact command/request.

## Always-on token cost (estimate)

~0.9k

Heavy material lives under `skills/*/references/` (on demand).

## Examples

See commands under `/` + plugin namespace after install (e.g. `/qradar:`…).

## Install

Packed into `amir_marketplace` as `qradar`.
