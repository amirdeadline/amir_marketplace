---
description: az account show preflight.
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"azure"`. If the manifest is missing or `"azure"` is not listed, STOP — do not execute this command — and tell the user to enable the `azure` component via `/amir:configure_project`.

# /amir:azure_whoami

`python "${CLAUDE_PLUGIN_ROOT}/scripts/azure/preflight.py"`
