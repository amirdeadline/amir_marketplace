# paloalto

PAN-OS / Panorama / GlobalProtect companion to prisma (SASE/SCM). Knowledge skills + API helper; mutations confirm-first.

## Pattern

**Knowledge+API + CLI-wrap**



## Prerequisites

Optional: pan-os-python or curl; env PANOS_HOST, PANOS_API_KEY (or user/password for keygen).

## Environment

`PANOS_HOST`, `PANOS_API_KEY`

All secrets from env only; displayed as `****last4`. Never written to files by this plugin.

## Safety

API set/edit/delete/commit confirm-first. Companion to prisma; no corpus overlap.

Default mode is **read-only**. State-changing actions confirm first and print the exact command/request.

## Always-on token cost (estimate)

~1.5k (thin skills; references on demand)

Heavy material lives under `skills/*/references/` (on demand).

## Examples

See commands under `/` + plugin namespace after install (e.g. `/paloalto:`…).

## Install

Packed into `amir_marketplace` as `paloalto`.
