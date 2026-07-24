---
name: amir-litellm:status
description: Validate LiteLLM_* contract, preflight proxy, show masked config + model count.
---

# /amir-litellm:status

## Instructions

Run:

```powershell
python "${CLAUDE_PLUGIN_ROOT}/bin/litellm_claude.py" --dry-run --json
```

Report the masked summary. Never print full API keys. If validation fails, list missing env var **names** only.
