---
description: Generate or run a PAN-OS API call (reads free; writes confirm).
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"paloalto"`. If the manifest is missing or `"paloalto"` is not listed, STOP — do not execute this command — and tell the user to enable the `paloalto` component via `/amir:configure_project`.

# /amir:panos_api

Args: `$ARGUMENTS`
Use `scripts/paloalto/api_helper.py`. Print exact request. Confirm set/edit/delete/commit.
