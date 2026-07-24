---
description: Re-ingest the local Prisma markdown corpus into baked skill references.
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"prisma"`. If the manifest is missing or `"prisma"` is not listed, STOP — do not execute this command — and tell the user to enable the `prisma` component via `/amir:configure_project`.

# /amir:prisma_update_index

## Instructions

Run from a shell (Windows paths OK):

```powershell
python "${CLAUDE_PLUGIN_ROOT}/scripts/prisma/ingest.py"
```

Or with an explicit docs root:

```powershell
python "${CLAUDE_PLUGIN_ROOT}/scripts/prisma/ingest.py" --docs "$env:PRISMA_DOCS_PATH"
```

Report coverage %, unclassified files, and the path to `ingest-report.json`. If the docs path is missing, surface the ingest error verbatim — do not invent an index.
