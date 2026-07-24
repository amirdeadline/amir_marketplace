---
description: Validate XDR API auth.
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"cortex-xdr"`. If the manifest is missing or `"cortex-xdr"` is not listed, STOP — do not execute this command — and tell the user to enable the `cortex-xdr` component via `/amir:configure_project`.

# /amir:xdr_preflight

`python "${CLAUDE_PLUGIN_ROOT}/scripts/xdr/api_helper.py" preflight`
