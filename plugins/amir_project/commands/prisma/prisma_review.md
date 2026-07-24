---
description: Review a pasted Prisma config or file via prisma-reviewer.
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"prisma"`. If the manifest is missing or `"prisma"` is not listed, STOP — do not execute this command — and tell the user to enable the `prisma` component via `/amir:configure_project`.

# /amir:prisma_review

Target: `$ARGUMENTS` (paste path or inline config description)

## Instructions

Invoke **prisma-reviewer**. If a file path is given, read it. Output the findings table (severity, evidence, fix). Confirm before suggesting destructive remediation.
