---
name: review
description: Review a pasted Prisma config or file via prisma-reviewer.
---

# /prisma:review

Target: `$ARGUMENTS` (paste path or inline config description)

## Instructions

Invoke **prisma-reviewer**. If a file path is given, read it. Output the findings table (severity, evidence, fix). Confirm before suggesting destructive remediation.
