---
name: litellm-usage
description: >-
  When to route work through the org LiteLLM proxy vs answer with the native
  model. Use for cheap bulk/classification, second opinions, spend checks, and
  session launch via litellm-claude.
---

# LiteLLM usage

## Routing guidance

| Work type | Prefer |
|-----------|--------|
| Cheap bulk classification, extraction, summarization of large dumps | Proxy model via MCP (`llm_chat`) or `/litellm:chat` |
| Second opinion / cross-check | Proxy model |
| Nuanced reasoning, tool-heavy coding in this IDE | Native Claude Code session (or `/litellm:session` if proxy is the sanctioned gateway) |
| Spend / model inventory | MCP `llm_models`, `llm_spend`, `llm_key_info` |

## Credentials

Read only `LiteLLM_*` env vars at invocation time. Never write keys to files.
Display keys as `sk-****last4` only.

## Session launch

```powershell
python "${CLAUDE_PLUGIN_ROOT}/bin/litellm_claude.py"
# or
${CLAUDE_PLUGIN_ROOT}/bin/litellm-claude.cmd --model <override> -- <claude args>
```

Preflight calls `GET {base}/v1/models`. Refuses on missing vars or failed preflight.

## Honesty

Pointing Claude Code at LiteLLM works because the proxy speaks Anthropic
`/v1/messages`, and this deployment is an org-internal sanctioned gateway —
but it is **not** an Anthropic-supported configuration; behavior can change
with Claude Code updates. The launcher's preflight exists to fail loudly.
