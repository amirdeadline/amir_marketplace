---
description: Build or refresh the Serena project index for faster symbol operations
---

# /amir:serena_index

## Gate

Read `.amir/project.yaml`. If missing or `project_tools.serena.enabled` is not `true`, stop and point to `/amir:configure_project`.

## Steps

1. Verify `serena` resolves (`Get-Command serena -ErrorAction SilentlyContinue`); if not, stop and point to `/amir:serena_setup`.
2. Run the official indexing command from the project root:

```powershell
serena project index
```

3. Scope rule: index ONLY this project. Never index directories outside the project root, and never enable any global/system-wide indexing. All index data must land in `.serena/` inside the project.
4. If the language server reports unsupported files or languages, list them explicitly — do not pretend they are covered.
5. On completion, report: languages indexed, duration, index location (`.serena/cache/`), and any files skipped or errored. If the command failed, report the failure verbatim; do not claim a partial index is complete.
