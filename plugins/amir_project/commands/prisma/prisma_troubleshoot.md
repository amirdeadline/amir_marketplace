---
description: Evidence-based troubleshooting via prisma-troubleshooter.
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"prisma"`. If the manifest is missing or `"prisma"` is not listed, STOP — do not execute this command — and tell the user to enable the `prisma` component via `/amir:configure_project`.

# /amir:prisma_troubleshoot

Symptom: `$ARGUMENTS`

## Instructions

Invoke **prisma-troubleshooter**. Use the `troubleshooting` skill methodology. Collect evidence before diagnosis. No vibe-based root causes.
