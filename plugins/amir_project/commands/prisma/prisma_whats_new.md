---
description: Summarize recent Prisma SASE / SCM / SD-WAN release notes from public sources.
---

> **Component gate (amir_project):** before doing anything else, read `.amir/project.yaml` at the project root and verify that `plugins.amir_project.components` includes `"prisma"`. If the manifest is missing or `"prisma"` is not listed, STOP — do not execute this command — and tell the user to enable the `prisma` component via `/amir:configure_project`.

# /amir:prisma_whats_new

Focus (optional): `$ARGUMENTS`

## Instructions

1. Search current public release notes / What's New pages on
   docs.paloaltonetworks.com and live.paloaltonetworks.com (and pan.dev when API-related).
2. Summarize with **dates** and product area tags (Prisma Access, SD-WAN, SCM, ADEM, Agent).
3. Label each item `VERIFIED (URL + date)` or mark ASSUMED/stale if undated.
4. Optionally map topics back to local corpus files via indexes — never claim the corpus is newer than public notes without checking.
