# palo-kb-read

Short routing skill for reading the Palo Alto Prisma SASE knowledge base and related corpora
(`palo-alto-knowledge-base/`, `prisma-sdwan/`, `pan-dev/`).

## Invoke

| Tool | How |
|---|---|
| Claude Code / Cursor | `/palo-kb-read <question>` or attach the skill when answering from the KB |

One real copy lives under `plugins/amir_system/skills/palo-kb-read`. User junctions:

```powershell
powershell -File <marketplace>/scripts/install-user-skills.ps1 -Skills palo-kb-read
```
