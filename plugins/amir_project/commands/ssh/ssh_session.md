---
description: Open interactive ssh (human-driven).
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"ssh"`. If the manifest is missing or `"ssh"` is not listed, STOP — do not execute this command — and tell the user to enable the `ssh` component via `/amir:configure_project`.

# /amir:ssh_session

`python "${CLAUDE_PLUGIN_ROOT}/scripts/ssh/ssh_cli.py" session -- $ARGUMENTS`
Claude must not drive interactive session blind.
