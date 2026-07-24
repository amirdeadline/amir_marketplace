---
description: One-off chat completion through the LiteLLM proxy MCP tool.
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"litellm"`. If the manifest is missing or `"litellm"` is not listed, STOP — do not execute this command — and tell the user to enable the `litellm` component via `/amir:configure_project`.

# /amir:litellm_chat

Prompt: `$ARGUMENTS`

## Instructions

1. Call `llm_chat` with messages `[{"role":"user","content":"<prompt>"}]`.
2. Model optional (uses `LiteLLM_ANTHROPIC_MODEL` / default).
3. Return the assistant text; mask any secrets in the response.
