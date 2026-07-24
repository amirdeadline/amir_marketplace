---
name: amir-prisma:update-index
description: Re-ingest the local Prisma markdown corpus into baked skill references.
---

# /amir-prisma:update-index

## Instructions

Run from a shell (Windows paths OK):

```powershell
python "${CLAUDE_PLUGIN_ROOT}/scripts/ingest.py"
```

Or with an explicit docs root:

```powershell
python "${CLAUDE_PLUGIN_ROOT}/scripts/ingest.py" --docs "E:\PC3_Shared\Palo\Documents\Markdowns Prisma SASE"
```

Report coverage %, unclassified files, and the path to `ingest-report.json`. If the docs path is missing, surface the ingest error verbatim — do not invent an index.
