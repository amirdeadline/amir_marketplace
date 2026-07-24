# terraform

Terraform plan/validate/fmt/init safe; apply/destroy confirm-first with typed destroy confirm. Blocks bare -auto-approve via hook.

## Pattern

**CLI-wrap + knowledge + PreToolUse hook**



## Prerequisites

terraform on PATH

## Environment

(none — uses local CLI auth)

All secrets from env only; displayed as `****last4`. Never written to files by this plugin.

## Safety

Hook blocks bare auto-approve/destroy. Typed DESTROY for destroy.

Default mode is **read-only**. State-changing actions confirm first and print the exact command/request.

## Always-on token cost (estimate)

~0.8k + hook

Heavy material lives under `skills/*/references/` (on demand).

## Examples

See commands under `/` + plugin namespace after install (e.g. `/terraform:`…).

## Install

Packed into `amir_marketplace` as `terraform`.
