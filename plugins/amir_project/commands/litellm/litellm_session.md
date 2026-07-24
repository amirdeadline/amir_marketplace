---
description: Launch a Claude Code session routed through the LiteLLM proxy.
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"litellm"`. If the manifest is missing or `"litellm"` is not listed, STOP — do not execute this command — and tell the user to enable the `litellm` component via `/amir:configure_project`.

# /amir:litellm_session

Optional args: `$ARGUMENTS` (e.g. `--model name -- <claude flags>`)

## Instructions

Explain that you will launch a **new** Claude Code process with session-scoped env
(not by rewriting settings.json). Then run:

```powershell
python "${CLAUDE_PLUGIN_ROOT}/scripts/litellm/litellm_claude.py" $ARGUMENTS
```

If preflight fails, do not launch. Show masked config from `--dry-run` on request.
