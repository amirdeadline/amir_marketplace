---
description: az account show + workspace check.
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"sentinel"`. If the manifest is missing or `"sentinel"` is not listed, STOP — do not execute this command — and tell the user to enable the `sentinel` component via `/amir:configure_project`.

# /amir:sentinel_preflight

`python "${CLAUDE_PLUGIN_ROOT}/scripts/sentinel/preflight.py"`
