---
name: btw
description: >-
  Aside question via Cursor native Side Chat. Redirects to Cursor /btw or /side;
  does not answer in the parent thread. Use for /amir:btw.
disable-model-invocation: true
argument-hint: [question]
---

# btw

Aside question without interrupting the current agent. **Do not answer the user's question in this thread.**

## Cursor

Cursor 3.11+ provides native Side Chat. Instruct the user to run:

- `/btw <question>` or `/side <question>`
- Or Plus → Side Chat / selection → Ask in Side Chat

Findings return to the main agent only if the Side Chat is `@`-mentioned. Amir cannot open Side Chat programmatically — this skill only redirects.

If a question was supplied, echo it once for copy-paste into `/btw …`, then stop.

## Claude Code

Refuse. Amir intentionally does not register a working `/btw` aside for Claude Code. Use a normal chat or switch to Cursor for native `/btw` / `/side`.

## Codex / other

Refuse in-session answering. Use a separate session for isolation, or Cursor native Side Chat when available.
