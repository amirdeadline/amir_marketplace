---
name: palo-kb-read
description: >-
  Brief guide for reading and retrieving from the Palo Alto Prisma SASE knowledge
  base. Use when answering product questions from local KB evidence, navigating
  palo-alto-knowledge-base, prisma-sdwan research corpora, or pan-dev developer
  docs, or when the user invokes /palo-kb-read.
argument-hint: "[question or topic]"
---

# palo-kb-read — use the Palo Alto KB (short)

Ground answers in local evidence. Do not invent product behavior.

## Locate roots

Once per session, resolve:

| Name | What it is | Typical path |
|---|---|---|
| **Repo** | Prisma_SASE_KB workspace | folder containing `palo-alto-knowledge-base/` |
| **KB** | Authored topic library (source of truth for agents) | `<Repo>/palo-alto-knowledge-base/` |
| **prisma-sdwan** | SD-WAN research / dependency / playbook corpus at repo root | `<Repo>/prisma-sdwan/` |
| **pan-dev** | pan.dev developer-docs clone | `<Repo>/pan-dev/` |

Fallbacks: env `PRISMA_DOCS_PATH` (KB or repo), then search upward from CWD for `palo-alto-knowledge-base/`.

Optional: if `amir_prisma_sdwan` is installed, run `python "<that_skill>/scripts/kbq.py" brief` for KB root + routing.

## Three folders — when to use which

### 1. `palo-alto-knowledge-base/` (prefer for answers)

AI-optimized **topic-per-file** KB (public + `[INTERNAL]`).

**Start here (in order):**
1. `KB/INDEX.md` — grep title/summary; open the path
2. `KB/KNOWLEDGE-MAP.md` or `KB/knowledge-map.json` — product → section → topics; read `negative_routing_rules`
3. Tree README, e.g. `KB/prisma-sd-wan/README.md`, `KB/prisma-access/README.md`
4. Topic doc itself (frontmatter + `##` chunks)

**Also:**
- `KB/corpus/README.md` (**SRC-000097**) — read-only mirrors of large root corpora; prefer when scoped inside KB
- `KB/confluence-index/` + `confluence/` (or corpus copies) — internal Confluence by `pageId`
- `KB/source-registry.json` — cite `SRC-*`
- `KB/.ai/prompts/kb_use.md` if present (full retrieval spec) — else repo `.ai/prompts/kb_use.md`

**Do not confuse:** Prisma SD-WAN ≠ PAN-OS SD-WAN; SCM-managed ≠ Panorama-managed Prisma Access; legacy CloudGenix API ≠ unified SASE API.

### 2. `prisma-sdwan/` (repo root research)

Deep SD-WAN analysis artifacts (dependency graphs, API catalogs, research notes, TAC playbooks). Use when the curated KB topic is thin or you need delete-order / object-catalog / research detail.

Typical entries: `00_EXECUTIVE_SUMMARY.md`, `0*_*.md` catalogs/graphs, `playbooks/`, `research-*`, `ion-bugs/`. Prefer matching KB topics under `KB/prisma-sd-wan/` first; use this folder to deepen.

Mirrored under `KB/corpus/prisma-sd-wan/research/` when present.

### 3. `pan-dev/` (developer docs clone)

Official developer documentation / OpenAPI-oriented content. Use for API shapes, SDK examples, product API landing pages.

Prefer KB automation mirrors when present: `KB/automation/` (pan-dev indexes) and `KB/corpus/developer/pan-dev/`. Cite pan.dev URLs or local paths; do not invent endpoints.

## Retrieval pattern (keep it narrow)

1. Classify product + intent (configure / troubleshoot / API / architecture / internal runbook).
2. Open product index → 2–5 best topic docs or registry sources.
3. Search inside those paths (`rg` / graphify), not the whole repo.
4. Read slices around hits — never load multi-MB containers whole (`prisma_*.md`, `pages-index.jsonl`).
5. Label claims: official → CONFIRMED; Confluence/TSE-only → INTERNAL; your reasoning → INFERENCE; missing → UNKNOWN and ask.

## Cite

- Topic path under `palo-alto-knowledge-base/...`
- `SRC-######` from `source-registry.json` when registered
- Confluence `pageId` + title for internal pages

## Out of scope

Writing/updating KB topics → use **palo-kb-add**. Prisma SD-WAN SME deep mode → **amir_prisma_sdwan**.
