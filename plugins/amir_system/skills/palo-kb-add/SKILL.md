---
name: palo-kb-add
description: >-
  Ingest Markdown (file, files, or folder) into palo-alto-knowledge-base: analyze,
  classify confidentiality, dedupe/MERGE, write topic docs, update INDEX/map/ledger.
  Use for bulk topic-queue writer waves or when the user says add this to the KB,
  /palo-kb-add, or provides documents to land in the Palo Alto knowledge base.
argument-hint: "[path or TOPIC_ID]"
---

# palo-kb-add — ingest into the Palo Alto KB

You are the **KB Writer**. Input: `.md` file(s), a folder, an analysis brief, or a lean TOPIC card.
Output: topic docs under `palo-alto-knowledge-base/` plus index updates (unless the prompt says Writer-only).

## 0. Locate KB

`KB` = nearest `palo-alto-knowledge-base/` (CWD upward, workspace, or `PRISMA_DOCS_PATH`).
Write **only** inside `KB/`. Scratch → `.ai/kb-build/` outside KB. Never rewrite `KB/source-material/**` except adding new verbatim copies.

Read first: `KB/README.md`, `KB/INDEX.md`, `KB/knowledge-map.json`, `KB/kb-meta/ledger.json`, `KB/terminology.json`.

## 1. Analyze

Per input: product(s), section, document_type, versions/era, management model (SCM vs Panorama — never blend), audience, **confidentiality**:
- `public` — TechDocs, pan.dev, OpenAPI, public GitHub
- `internal` — Confluence, TSE/PS, lab/tenant, anything Confidential
- unsure → `internal`

Split into **topics** (one coherent agent question each). Briefs in `.ai/kb-build/briefs/<UNIT>.md` with `### Tn` are preferred when present.

## 2. Dedupe (hard rule)

Search `INDEX.md`, `knowledge-map.json`, and `rg` under `KB/<tree>/` (exclude `source-material/`, raw confluence dumps).
- Same subject exists → **MERGE** (integrate facts, bump `last_updated`, widen to `mixed` + `[INTERNAL]` markers as needed)
- Else **NEW** at `KB/<tree>/<section>/<kebab-topic>.md`

Authority: official (1–4) > internal (9) > inference (10); if internal corrects public, state both with dates.

## 3. Topic contract

Trees include: `prisma-access`, `prisma-sd-wan`, `strata-cloud-manager`, `strata-logging-service`, `globalprotect`, `cloud-identity-engine`, `panorama`, `pan-os-ngfw`, `prisma-sase-sdk`, `automation`, `reference-architecture`, `product-activation`, `customer-support-portal`, `professional-services`, `shared`, `prisma-airs`, `vm-series`.

Sections: `architecture` · `concepts` · `licensing-and-requirements` · `activation-and-onboarding` · `configuration` · `security` · `monitoring` · `operations` · `upgrades` · `integrations` · `troubleshooting` · `reference` · `migration` · `automation` · `api` · `hardware` · `faq` · `tooling`.

Required frontmatter keys: `title`, `product`, `tree`, `section`, `document_type`, `confidentiality`, `management_models`, `versions`, `sources`, `source_paths`, `tags`, `related`, `summary`, `last_updated`, `status`.

Body: `# Title` = exact title string → TL;DR → Context → type-specific core → Gotchas → Internal notes (if internal/mixed) → Related → Sources → Version history.

Rules: UTF-8 **no BOM**; size **>2000** bytes; H1 **exactly** equals `title`; maximal detail, verbatim commands/tables; no secrets; negative routing respected.

## 4. Indexes (full ingest runs)

Update in the same run: `INDEX.md`, `KNOWLEDGE-MAP.md`, `knowledge-map.json`, `KB/<tree>/README.md`, `kb-meta/ledger.json`, `kb-meta/confidentiality.json`, `terminology.json` / `GLOSSARY.md` if terms added. Prefer `python .ai/kb-build/tools/sync_tree_indexes.py <tree>` when available.

Register new raw sources in `source-registry.json` (additive only).

## 5. Writer-pool / topic-queue mode (cost-efficient bulk)

When draining `.ai/kb-build/topic-queue.json` with a fixed Composer pool:

1. Lead only: verify fragments → `_close_assigned_wave.py` (or equivalent) → commit **wave docs + indexes only** in the KB git → resume **same** 5 writers.
2. Lean resume prompt only (no skill dump):

```
NEXT TOPIC ONLY. Skill: <path>/palo-kb-add/SKILL.md. Overrides: no indexes/validate/queue. Write only KB path + fragment.

TOPIC_ID: ...
ACTION: NEW|MERGE
PATH: palo-alto-knowledge-base/<tree>/...
TITLE: <exact H1>
BRIEF: <repo>/.ai/kb-build/briefs/<UNIT>.md ### Tn
SCOPE: <one line>
FRAGMENT: <repo>/.ai/kb-build/fragments/<TOPIC_ID>.json

product ...; confidentiality internal; H1=title; UTF-8 no BOM; size>2000; ECC_GATEGUARD=off.
If path collides, MERGE. Return path/bytes/fragment.
```

3. Writer writes **doc + fragment JSON only** — no INDEX/queue edits.
4. Ignore delayed completions for topics already closed.
5. New trees (e.g. `prisma-airs`, `vm-series`) must exist in `sync_tree_indexes.TREE_LABELS` + README before close.

## 6. Validate + report

Assert frontmatter, confidentiality enum, related paths exist, index/ledger rows present, no scripts/logs left in KB.
Report: NEW/MERGE paths, confidentiality, index updates, skipped/failed separately.

## Hard rules

- One topic per file; merge never duplicate
- Confidentiality always tagged; `[INTERNAL]` on internal facts in mixed docs
- Only Markdown/JSON in KB
- Sources immutable; registry additive
- Indexes updated same run as docs (unless Writer-only override)
