---
description: Show active AWS account/role/region via STS.
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"aws"`. If the manifest is missing or `"aws"` is not listed, STOP — do not execute this command — and tell the user to enable the `aws` component via `/amir:configure_project`.

# /amir:aws_whoami

Run `python "${CLAUDE_PLUGIN_ROOT}/scripts/aws/preflight.py"`.
Refuse other AWS actions if this fails.
