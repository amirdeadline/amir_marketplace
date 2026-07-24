# ssh-terminal

SSH/SCP via system OpenSSH. Confirm host+command before run; block destructive remote commands unless host-named typed confirm; no password inline; no multi-host loops without per-host confirm.

## Pattern

**CLI-wrap (OpenSSH)**



## Prerequisites

ssh/scp on PATH (Windows OpenSSH client).

## Environment

(none — uses local CLI auth)

All secrets from env only; displayed as `****last4`. Never written to files by this plugin.

## Safety

Authorized systems only. Per-host confirm. Destructive needs typed hostname. No multi-host auto loops.

Default mode is **read-only**. State-changing actions confirm first and print the exact command/request.

## Always-on token cost (estimate)

~0.7k

Heavy material lives under `skills/*/references/` (on demand).

## Examples

See commands under `/` + plugin namespace after install (e.g. `/ssh-terminal:`…).

## Install

Packed into `amir_marketplace` as `ssh-terminal`.
