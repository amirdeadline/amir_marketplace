---
description: az CLI wrap with confirm for mutations.
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"azure"`. If the manifest is missing or `"azure"` is not listed, STOP — do not execute this command — and tell the user to enable the `azure` component via `/amir:configure_project`.

# /amir:azure_cli

`$ARGUMENTS` → scripts/azure/cli_wrap.py
