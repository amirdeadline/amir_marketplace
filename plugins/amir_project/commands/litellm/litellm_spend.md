---
description: Show key spend/usage via MCP llm_spend / llm_key_info.
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"litellm"`. If the manifest is missing or `"litellm"` is not listed, STOP — do not execute this command — and tell the user to enable the `litellm` component via `/amir:configure_project`.

# /amir:litellm_spend

## Instructions

1. Call `llm_key_info` then `llm_spend` as needed.
2. If the proxy returns 401/403, surface the proxy error (keys masked) — the plugin cannot grant permissions the key lacks.
3. Never log full tokens from `/key/info` responses.
