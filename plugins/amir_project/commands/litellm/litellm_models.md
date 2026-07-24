---
description: List models from the LiteLLM proxy via MCP llm_models.
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"litellm"`. If the manifest is missing or `"litellm"` is not listed, STOP — do not execute this command — and tell the user to enable the `litellm` component via `/amir:configure_project`.

# /amir:litellm_models

## Instructions

Call MCP tool `llm_models`. Summarize ids (and metadata if present). On auth failure, show the proxy error with keys masked.
