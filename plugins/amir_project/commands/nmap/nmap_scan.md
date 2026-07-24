---
description: Build+confirm an authorized scan.
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"nmap"`. If the manifest is missing or `"nmap"` is not listed, STOP — do not execute this command — and tell the user to enable the `nmap` component via `/amir:configure_project`.

# /amir:nmap_scan

`$ARGUMENTS` → scripts/nmap/nmap_cli.py scan
