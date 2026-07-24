---
description: terraform destroy — typed confirmation required.
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"terraform"`. If the manifest is missing or `"terraform"` is not listed, STOP — do not execute this command — and tell the user to enable the `terraform` component via `/amir:configure_project`.

# /amir:terraform_destroy

`python "${CLAUDE_PLUGIN_ROOT}/scripts/terraform/tf.py" destroy -- $ARGUMENTS`
