---
description: Run one remote command (confirm).
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"ssh"`. If the manifest is missing or `"ssh"` is not listed, STOP — do not execute this command — and tell the user to enable the `ssh` component via `/amir:configure_project`.

# /amir:ssh_run

`$ARGUMENTS` as `<host> <command…>` → scripts/ssh/ssh_cli.py run
