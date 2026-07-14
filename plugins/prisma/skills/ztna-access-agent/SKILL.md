---
name: ztna-access-agent
description: >-
  Prisma Access Agent / ZTNA constructs and private app access patterns. Use when the user asks about ZTNA / Access Agent in Prisma SASE / SCM.
  Prefer live corpus at PRISMA_DOCS_PATH; fall back to baked references/.
---

# ZTNA / Access Agent

## Knowledge layers

1. **Live layer (preferred):** read targeted sections from `PRISMA_DOCS_PATH`
   (default `E:\PC3_Shared\Palo\Documents\Markdowns Prisma SASE`) using
   `references/index.json` for topic → file → line/anchor. Never load entire
   multi‑MB files into context — search/retrieve only matching sections.
2. **Baked layer:** `references/summary.md` + `references/index.json` shipped
   inside this plugin (always available after `/prisma:update-index`).

If `PRISMA_DOCS_PATH` is unset or the path is missing, say clearly:
`Live corpus unavailable — answering from baked references (ingested: see summary header).`

## Honesty (mandatory)

- Label every material claim: `VERIFIED (source file/URL)` | `INFERRED` | `ASSUMED`.
- Cloud products change monthly — verify version-specific UI paths and limits against
  current public docs (docs.paloaltonetworks.com, pan.dev, live.paloaltonetworks.com,
  release notes) before asserting them.
- Prefer amir UNKNOWN / NOT DOABLE formats over guessing.
- Confirm before any destructive or mutating API/config change.

## Behavior

1. Parse the user question; list candidate topics from `references/index.json`.
2. Open live source sections when available; cite `path#line` or Source PDF name.
3. Cross-check freshness for version-specific claims via public docs.
4. Answer with procedures (UI path and/or API), scope implications (folder/snippet/
   push), and risks/trade-offs.
5. If evidence is thin, say what is unknown and what to collect next.

## References

- Baked: `references/summary.md`, `references/index.json`
- Public: docs.paloaltonetworks.com, pan.dev (SCM/SASE), live.paloaltonetworks.com
