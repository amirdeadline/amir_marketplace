---
name: spend
description: Show key spend/usage via MCP llm_spend / llm_key_info.
---

# /litellm:spend

## Instructions

1. Call `llm_key_info` then `llm_spend` as needed.
2. If the proxy returns 401/403, surface the proxy error (keys masked) — the plugin cannot grant permissions the key lacks.
3. Never log full tokens from `/key/info` responses.
