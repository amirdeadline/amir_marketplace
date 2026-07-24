---
description: Opt-in live capture (confirm).
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"wireshark"`. If the manifest is missing or `"wireshark"` is not listed, STOP — do not execute this command — and tell the user to enable the `wireshark` component via `/amir:configure_project`.

# /amir:wireshark_capture

`python "${CLAUDE_PLUGIN_ROOT}/scripts/wireshark/tshark_cli.py" capture -- $ARGUMENTS`
