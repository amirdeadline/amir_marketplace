---
description: Run an aws CLI command with confirm-first for mutations.
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"aws"`. If the manifest is missing or `"aws"` is not listed, STOP — do not execute this command — and tell the user to enable the `aws` component via `/amir:configure_project`.

# /amir:aws_cli

Args: `$ARGUMENTS`
Use scripts/aws/cli_wrap.py. Print exact command. Confirm create/delete/modify/put/update/attach.
