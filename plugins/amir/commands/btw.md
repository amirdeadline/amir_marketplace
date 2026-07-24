---
name: "amir:btw"
description: "Temporary read-only side question. Not saved to project state or long-term memory."
---

# /amir:btw

Temporary read-only side question. Not saved to project state or long-term memory.

## BTW MODE — Temporary • Read-only • Not saved

**Constraints (strict):**

- **Read-only:** no file edits, no terminal/shell commands, no tool calls that write (including git, npm, state tools, memory MCP writes).
- **Single turn:** answer the user's question in one response, then close.
- **No amir state:** do not read or write `ai/state/*`, do not append activity, do not invoke skills or subagents.
- **No project side effects:** treat this as ephemeral chat scoped to the question only.

## UX

Open with a one-line banner:

```
BTW MODE — Temporary • Read-only • Not saved
```

Answer concisely. Close with:

```
Temporary session closed.
```

## Residual limitations (honest)

Cursor Ask / read-only modes may still retain this turn in host chat history depending on IDE settings. amir cannot guarantee zero host-side persistence or perfect tool isolation — the agent must still refuse writes even if tools appear available. For zero-pollution ephemeral sessions, start a fresh chat instead.
