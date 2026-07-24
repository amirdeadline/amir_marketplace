# docker

Docker/Compose: status, logs, build, up/down; prune/volume-rm/rm -f guarded with confirmation.

## Pattern

**CLI-wrap**



## Prerequisites

docker on PATH; optional docker compose

## Environment

(none — uses local CLI auth)

All secrets from env only; displayed as `****last4`. Never written to files by this plugin.

## Safety

Confirm prune, volume rm, rm -f, compose down, push.

Default mode is **read-only**. State-changing actions confirm first and print the exact command/request.

## Always-on token cost (estimate)

~0.7k

Heavy material lives under `skills/*/references/` (on demand).

## Examples

See commands under `/` + plugin namespace after install (e.g. `/docker:`…).

## Install

Packed into `amir_marketplace` as `docker`.
