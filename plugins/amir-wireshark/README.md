# wireshark

tshark analysis of existing pcaps (default). Live capture opt-in with interface, filter, limits, confirm.

## Pattern

**CLI-wrap (tshark)**



## Prerequisites

tshark on PATH (Wireshark install).

## Environment

(none — uses local CLI auth)

All secrets from env only; displayed as `****last4`. Never written to files by this plugin.

## Safety

Default=file analysis. Live capture opt-in with iface+outfile+limit+confirm.

Default mode is **read-only**. State-changing actions confirm first and print the exact command/request.

## Always-on token cost (estimate)

~0.8k

Heavy material lives under `skills/*/references/` (on demand).

## Examples

See commands under `/` + plugin namespace after install (e.g. `/wireshark:`…).

## Install

Packed into `amir_marketplace` as `wireshark`.
