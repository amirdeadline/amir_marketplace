---
description: Report Context7 registration, key presence, and lookup health
---

# /amir:context7_status

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.context7.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Checks (report each separately)

1. Mode from manifest: `project_tools.context7.mode` (mcp | cli).
2. Runtime: `node --version` and `npx --version` succeed.
3. Registration: `claude mcp list` includes `context7` and shows connected (mcp mode).
4. API key: report only PRESENCE (`Test-Path "$env:USERPROFILE\.amir\secrets\context7.env"` or whether `CONTEXT7_API_KEY` is set) — never print the value. Note that no key means lower rate limits, not failure.
5. Live check: one real `resolve-library-id` call for a dependency from this project's lockfile; report whether a non-empty result came back.
6. Network permission: confirm `.amir/project.yaml` `permissions.network` allows context7; flag if the manifest denies network but the tool is enabled.

State conclusions per check; suggest `/amir:context7_setup` or `/amir:context7_validate` for failures. No claim of health without the live check passing now.
