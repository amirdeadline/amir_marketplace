---
name: amir-prisma:api
description: SCM/SASE API guidance via scm-api skill. Never executes mutating calls without confirmation.
---

# /amir-prisma:api

Task: `$ARGUMENTS`

## Instructions

1. Use the **scm-api** skill (live corpus + pan.dev).
2. Generate curl and/or Python examples for OAuth2/TSG auth and the requested endpoints.
3. **Never execute mutating API calls** (POST/PUT/PATCH/DELETE that change config) without explicit user confirmation.
4. Warn about scoped tokens and production tenants.
