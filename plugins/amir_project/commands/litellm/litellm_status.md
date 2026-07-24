---
description: Validate LiteLLM_* contract, preflight proxy, show masked config + model count.
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"litellm"`. If the manifest is missing or `"litellm"` is not listed, STOP — do not execute this command — and tell the user to enable the `litellm` component via `/amir:configure_project`.

# /amir:litellm_status

## Instructions

Run:

```powershell
python "${CLAUDE_PLUGIN_ROOT}/scripts/litellm/litellm_claude.py" --dry-run --json
```

Report the masked summary. Never print full API keys. If validation fails, list missing env var **names** only.
