---
description: Run a Claude Code subagent through Palo LiteLLM (palo venv). Fails loudly with sound if LiteLLM is down.
---

Read and follow the skill **`amir_use_litellm_subagent`** (`~/.cursor/skills/amir_use_litellm_subagent/SKILL.md`) in full.

The user's task for the LiteLLM subagent is everything in this message after the command name (or the full message if they only sent the slash command — ask what to delegate).

Do not use Cursor Task subagent for this request unless LiteLLM probe fails and the user explicitly chooses a fallback.
