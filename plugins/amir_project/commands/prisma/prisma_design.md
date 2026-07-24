---
description: Launch prisma-architect for a SASE design brief.
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"prisma"`. If the manifest is missing or `"prisma"` is not listed, STOP — do not execute this command — and tell the user to enable the `prisma` component via `/amir:configure_project`.

# /amir:prisma_design

Design brief: `$ARGUMENTS`

## Instructions

Invoke the **prisma-architect** agent (Task/subagent when available; otherwise emulate in-session labeled `[prisma-architect]`). Pass the brief. Follow agent discovery (A–E questions) and design-doc output format.
