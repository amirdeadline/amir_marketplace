---
description: compose down (confirm)
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"docker"`. If the manifest is missing or `"docker"` is not listed, STOP — do not execute this command — and tell the user to enable the `docker` component via `/amir:configure_project`.

# /amir:docker_down

`python "${CLAUDE_PLUGIN_ROOT}/scripts/docker/docker_cli.py" down -- $ARGUMENTS`
