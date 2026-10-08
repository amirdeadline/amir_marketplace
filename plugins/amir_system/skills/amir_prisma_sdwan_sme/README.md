# amir_prisma_sdwan_sme

Prisma SD-WAN subject-matter-expert skill built on a curated, evidence-labelled knowledge layer: 58 notes
with claims registers, 14 worked scenarios, a term index, a question router, the source catalog and the gap
register. Every claim carries VERIFIED / CORROBORATED / INFERRED / UNVERIFIED / CONFLICTED / OBSOLETE and an
evidence type (DOC / SCENARIO / LAB). It sits on top of `amir_prisma_sdwan` (raw knowledge-base retrieval)
and pairs with `amir_official_doc` for documents. Python only for automation examples.

Research project name: `prisma-sdwan-sme` (Phase 7 of the 2026-10-08 research plan). Skill name follows the
plugin's snake_case `/amir:` convention. Future sibling skills (`prisma-access-sme`, `cloud-identity-engine-sme`,
`globalprotect-sme`, `prisma-access-agent-sme`, `prisma-access-browser-sme`, umbrella `prisma-sase-sme`) are
designed to share the label scheme and citation form; none is built yet.

## Invoke

| Tool | How |
|---|---|
| Claude Code | `/amir_prisma_sdwan_sme <question>`; plugin form `/amir:amir_prisma_sdwan_sme` once the plugin cache is refreshed |
| Cursor | Type `/` in Agent chat, pick `amir_prisma_sdwan_sme`, then type the request |
| Either | Prisma SD-WAN design, policy, routing, HA, API or troubleshooting questions can trigger it by description |

`/amir_prisma_sdwan_sme` alone confirms the mode, the knowledge manifest date and whether the KB helper was found.

## Files

| Path | Purpose |
|---|---|
| `SKILL.md` | The skill: session start, triage, knowledge-first retrieval, labelling rules, stop-and-ask, answer format, sibling skills, maintenance |
| `references/labels_and_answer_format.md` | Label definitions and mapping to the sibling skill, standing rules (numbers, navigation, negative routing), missing-evidence template, answer format |
| `knowledge/` | Synced copy of the research corpus: `notes/` (10 folders), `scenarios/` (S01–S14 + index), `index/` (note index, term index, router), `03_SOURCE_CATALOG.md`, `04_KNOWLEDGE_GAPS.md`, `05_UNRESOLVED_QUESTIONS.md`, `06_SME_READINESS_ASSESSMENT.md`, `MANIFEST.json` (SHA-256 per file) |
| `scripts/sme.py` | Read-only lookup: `brief`, `route`, `find`, `note`, `scenario`, `term`, `gap`, `src [--kb]`, `verify` |
| `scripts/sync_knowledge.py` | One-way copy research workspace → `knowledge/` with manifest; `--check` reports drift only |
| `config.json` | `research_root` (editing place), `kb_root` (read-only KB), optional `kbq_path` |
| `tests/test_sme.py` | Unit tests for both scripts |

## Knowledge layer provenance

Built 2026-10-08 from the read-only knowledge base at `E:\PC3_Shared\Palo\COE\Prisma_SASE_KB` plus original
PDFs and allowed public pages, in the research workspace `E:\PC3_Shared\Palo\COE\prisma-sdwan-sme-research`
(status file `00_PROJECT_STATUS.md`, plan `02_RESEARCH_PLAN.md`). Readiness per domain (R1–R4) is in
`knowledge/06_SME_READINESS_ASSESSMENT.md`: design, fundamentals, operations R4; application traffic and API
R4-; network and security R3; SCM navigation R2+; troubleshooting and datapath internals R2 (internal
material only). No claim is lab-validated yet.

## Maintenance

```text
python scripts/sync_knowledge.py --check        # what changed in the research workspace
python scripts/sync_knowledge.py                # copy and rewrite MANIFEST.json
python scripts/sme.py verify                    # knowledge/ matches the manifest
python -m pytest -q -p no:cacheprovider tests   # after editing the scripts
```

User-level links for Claude Code and Cursor: `powershell -File <marketplace>\scripts\install-user-skills.ps1 [-Verify]`
(this skill is in the installer's default list).
