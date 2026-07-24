# litellm

Work with the org-internal **LiteLLM proxy** two ways:

1. **Session launcher** — start Claude Code with proxy routing (`bin/litellm_claude.py`)
2. **MCP tools** — call the proxy API surface from the agent (`bin/litellm_mcp.py`)

## Honest caveat

Pointing Claude Code at a LiteLLM base URL works because LiteLLM speaks the
Anthropic `/v1/messages` format, and this deployment is an org-internal,
sanctioned gateway — but it is **not** an Anthropic-supported configuration;
behavior can change with Claude Code updates. The launcher's preflight exists
precisely to fail loudly instead of mid-session.

## Environment contract (credentials live HERE only)

All config is read from `LiteLLM_*` env vars at invocation time, mapped by
stripping the prefix into a **session-scoped** child environment. Never written
to settings files, never exported globally, never persisted by this plugin.

| Env var | Maps to / behavior |
|---------|-------------------|
| `LiteLLM_ANTHROPIC_BASE_URL` | `ANTHROPIC_BASE_URL` (required) |
| `LiteLLM_ANTHROPIC_API_KEY` | `ANTHROPIC_AUTH_TOKEN` **and** `ANTHROPIC_API_KEY` (required) |
| `LiteLLM_ANTHROPIC_MODEL` | `ANTHROPIC_MODEL` |
| `LiteLLM_CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS` | pass-through unprefixed |
| `LiteLLM_NODE_USE_SYSTEM_CA` | pass-through unprefixed |
| `LiteLLM_PROXY_enabled` | `1` → apply proxy vars + SOCKS for HTTP; else ignore |
| `LiteLLM_ALL_PROXY` / `HTTPS_PROXY` / `HTTP_PROXY` | unprefixed only when enabled (`socks5h://` supported) |

**Auth mapping (VERIFIED at build time against docs.litellm.ai):** Claude Code
static-key tutorials set `ANTHROPIC_AUTH_TOKEN`; other docs use
`ANTHROPIC_API_KEY`. The launcher sets **both** to the same value.

Keys display as `sk-****last4` only. The spawned session env must **not** contain
`LiteLLM_*` originals.

## Setup

```powershell
cd E:\PC3_Shared\Plugins\litellm
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Preflight

`GET {base}/v1/models` with `Authorization: Bearer <key>`
(VERIFIED: OpenAI-compatible LiteLLM proxy).

## Commands

`/litellm:status`, `/litellm:models`, `/litellm:chat`, `/litellm:spend`, `/litellm:session`

## MCP tools

| Tool | Endpoint |
|------|----------|
| `llm_chat` | `POST /v1/chat/completions` |
| `llm_complete` | `POST /v1/completions` |
| `llm_embeddings` | `POST /v1/embeddings` |
| `llm_models` | `GET /v1/models` |
| `llm_health` | `GET /health` |
| `llm_key_info` | `GET /key/info` |
| `llm_spend` | `GET /spend/keys` |
| `llm_request` | generic passthrough (same host only) |

Admin/management routes depend entirely on the key's permissions — the plugin
cannot grant what the key lacks.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```
