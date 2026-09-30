---
description: Write a self-contained session handoff document so a fresh session in any host can resume cold without the chat history
argument-hint: [optional reason or output path]
disable-model-invocation: true
---

# /amir:amir_handoff

Follow the skill at `skills/amir_handoff/SKILL.md` in this plugin (also installed at user
scope as `/amir_handoff` for Cursor and Claude Code).

Apply that skill now. Treat `$ARGUMENTS` as an output path if it looks like one, otherwise as
the reason for pausing. Gather evidence from the working tree before writing — do not describe
state from memory — and report the absolute path of the file you wrote.

For an Amir project where the full `.ai/` doc set should be updated together, use
`/amir:cleanup_context` instead; this command writes one portable file.
