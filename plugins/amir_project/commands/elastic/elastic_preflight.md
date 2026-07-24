---
description: Cluster info / auth check.
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"elastic"`. If the manifest is missing or `"elastic"` is not listed, STOP — do not execute this command — and tell the user to enable the `elastic` component via `/amir:configure_project`.

# /amir:elastic_preflight

`python "${CLAUDE_PLUGIN_ROOT}/scripts/elastic/api_helper.py" preflight`
