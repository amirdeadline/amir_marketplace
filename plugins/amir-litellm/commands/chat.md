---
name: amir-litellm:chat
description: One-off chat completion through the LiteLLM proxy MCP tool.
---

# /amir-litellm:chat

Prompt: `$ARGUMENTS`

## Instructions

1. Call `llm_chat` with messages `[{"role":"user","content":"<prompt>"}]`.
2. Model optional (uses `LiteLLM_ANTHROPIC_MODEL` / default).
3. Return the assistant text; mask any secrets in the response.
