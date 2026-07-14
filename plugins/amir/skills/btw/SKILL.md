---
name: btw
description: "Temporary read-only side question; not saved to amir state."
---

# btw

## CLAUDE CODE GATE

If the host is **Claude Code**, refuse this skill. amir intentionally does **not**
register `/btw` there (no true zero-pollution ephemeral session). Tell the user
to ask in a normal chat or switch to Cursor/Codex for `/btw`.


Temporary read-only side question outside the amir project loop.

## BTW MODE — Temporary • Read-only • Not saved

- Read-only: no filesystem writes, no shell, no state tool invocations, no memory persistence.
- Single turn: answer once, then emit `Temporary session closed.`
- Do not load or mutate `ai/state/*` or run other amir skills.

## Residual limitations (honest)

Codex has no native zero-pollution ephemeral session. This skill approximates /btw via strict self-imposed read-only behavior. Host transcript retention may still apply. For true isolation, use a separate Codex session.
