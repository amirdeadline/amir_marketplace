---
name: session
description: Launch a Claude Code session routed through the LiteLLM proxy.
---

# /litellm:session

Optional args: `$ARGUMENTS` (e.g. `--model name -- <claude flags>`)

## Instructions

Explain that you will launch a **new** Claude Code process with session-scoped env
(not by rewriting settings.json). Then run:

```powershell
python "${CLAUDE_PLUGIN_ROOT}/bin/litellm_claude.py" $ARGUMENTS
```

If preflight fails, do not launch. Show masked config from `--dry-run` on request.
