---
description: Run a Claude Code subagent through Palo LiteLLM (palo venv). Fails loudly with sound if LiteLLM is down.
---

Read and follow the skill **`amir_use_litellm_subagent`** (`~/.cursor/skills/amir_use_litellm_subagent/SKILL.md`) in full.

The user's task for the LiteLLM subagent is everything in this message after the command name (or the full message if they only sent the slash command — ask what to delegate).

**Model (optional):** Default is palo Opus **4.8** with **1M** context. If the user asks for **opus 5** / **opus-5**, pass `-Model opus-5` to `run-litellm-subagent.ps1`. For **4.8** explicitly use `-Model opus-4.8`. Any full proxy id from `litellm --models` also works. This does not change palo `.env`.

Do not use Cursor Task subagent for this request unless LiteLLM probe fails and the user explicitly chooses a fallback.
