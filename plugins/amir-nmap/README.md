# nmap

Authorized nmap scanning: interview→command print→auth gate→confirm. Parse XML/gnmap to tables. Aggressive modes opt-in.

## Pattern

**CLI-wrap (authorized-use only)**



## Prerequisites

nmap on PATH

## Environment

(none — uses local CLI auth)

All secrets from env only; displayed as `****last4`. Never written to files by this plugin.

## Safety

Authz typed gate AUTHORIZED <target>. Bulk /0 refused. Aggressive opt-in.

Default mode is **read-only**. State-changing actions confirm first and print the exact command/request.

## Always-on token cost (estimate)

~0.8k

Heavy material lives under `skills/*/references/` (on demand).

## Examples

See commands under `/` + plugin namespace after install (e.g. `/nmap:`…).

## Install

Packed into `amir_marketplace` as `nmap`.
