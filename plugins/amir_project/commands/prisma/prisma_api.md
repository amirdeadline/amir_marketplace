---
description: SCM/SASE API guidance via prisma_scm_api skill. Never executes mutating calls without confirmation.
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"prisma"`. If the manifest is missing or `"prisma"` is not listed, STOP — do not execute this command — and tell the user to enable the `prisma` component via `/amir:configure_project`.

# /amir:prisma_api

Task: `$ARGUMENTS`

## Instructions

1. Use the **prisma_scm_api** skill (live corpus + pan.dev).
2. Generate curl and/or Python examples for OAuth2/TSG auth and the requested endpoints.
3. **Never execute mutating API calls** (POST/PUT/PATCH/DELETE that change config) without explicit user confirmation.
4. Warn about scoped tokens and production tenants.
