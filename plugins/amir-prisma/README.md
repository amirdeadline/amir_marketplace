# prisma

Claude Code / Cursor / Codex plugin for **Prisma SASE / Strata Cloud Manager (SCM)**
expertise: skills, agents, and commands grounded in a local markdown corpus plus
live public documentation.

## Licensing (mandatory)

The corpus contains **Palo Alto Networks documentation**. This plugin is for the
user's **internal / personal use only**.

- Do **not** publish this plugin, or any marketplace containing its baked
  `references/`, publicly.
- The ingestion script (`scripts/ingest.py`) **never uploads** corpus content
  anywhere. It only reads local files and writes distilled indexes inside the
  plugin directory.

## Knowledge design

| Layer | Location | Role |
|-------|----------|------|
| **Baked** | `skills/*/references/` | Distilled summaries + topic index (always available after ingest) |
| **Live** | `PRISMA_DOCS_PATH` | Full source markdown — retrieve sections, never stuff whole files |

Default live path:

```text
E:\PC3_Shared\Palo\Documents\Markdowns Prisma SASE
```

Override:

```powershell
$env:PRISMA_DOCS_PATH = "D:\path\to\Markdowns Prisma SASE"
```

If unset/missing, skills **degrade to baked** and must say so.

## Setup

```powershell
cd E:\PC3_Shared\Plugins\prisma
python scripts\gen_skills.py
python scripts\ingest.py
```

Re-ingest when the folder changes: `/prisma:update-index`

## Commands

| Command | Purpose |
|---------|---------|
| `/prisma:ask` | Route question via index |
| `/prisma:design` | prisma-architect |
| `/prisma:review` | prisma-reviewer |
| `/prisma:troubleshoot` | prisma-troubleshooter |
| `/prisma:api` | scm-api guidance (confirm before mutating calls) |
| `/prisma:update-index` | Re-run ingest |
| `/prisma:whats-new` | Public release notes with dates |

## Agents (subagent-capable)

`prisma-architect`, `prisma-engineer`, `prisma-troubleshooter`, `prisma-reviewer`

## Skills

`scm-platform`, `prisma-access`, `security-policy`, `sdwan`, `adem`,
`ztna-access-agent`, `scm-api`, `troubleshooting`

## Marketplace

Packed into `../amir_marketplace` as plugin `prisma`. **Keep the marketplace
private** while it contains baked references derived from PANW docs.

## Honesty

Claims: `VERIFIED (source file/URL) | INFERRED | ASSUMED`. Prefer UNKNOWN over guessing.
