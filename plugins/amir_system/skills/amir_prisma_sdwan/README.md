# amir_prisma_sdwan

Prisma SD-WAN subject-matter expert that answers only from the local Palo Alto knowledge base (KB),
labels every important claim (CONFIRMED, INTERNAL, INFERENCE, UNKNOWN), and stops to ask when evidence is
missing. Pairs with `amir_official_doc` for documents.

## Invoke

| Tool | How |
|---|---|
| Claude Code | `/amir_prisma_sdwan <question>`; `/amir_prisma_sdwan /amir_official_doc <request>` for both skills |
| Cursor | Type `/` in Agent chat, pick `amir_prisma_sdwan`, then type the request |
| Either | Plain Prisma SD-WAN questions can also trigger it automatically (description match) |

`/amir_prisma_sdwan` alone, with no task, confirms the mode and the KB folder and waits.

## Files

| Path | Purpose |
|---|---|
| `SKILL.md` | The skill: KB location, task triage, narrow retrieval, evidence labels, stop-and-ask rule, answer format |
| `references/evidence_policy.md` | Label definitions, authority and citation rules, freshness, conflicts, missing-evidence template |
| `references/sdwan_topic_map.md` | Concept to related concepts to KB entry files (navigation only, never evidence) |
| `scripts/kbq.py` | Read-only KB lookup: `root`, `brief`, `src`, `find`, `pages`, `term`, `grep`, `check-map` |
| `config.json` | Fallback KB location |
| `tests/test_kbq.py` | Unit tests for `kbq.py` |

## KB location

`kbq.py` checks, in order: `--root`, the `PRISMA_DOCS_PATH` variable, the current folder and its parents,
then `kb_root` in `config.json`. The KB's own retrieval guide `.ai/prompts/kb_use.md` stays the authority
for where to look; the skill reads it rather than copying it.

## Maintenance

```text
python scripts/kbq.py check-map references/sdwan_topic_map.md   # after KB reorganizations
python -m pytest -q -p no:cacheprovider tests                    # after editing kbq.py
```

Install or verify the user-level links for Claude Code and Cursor:
`powershell -File <marketplace>\scripts\install-user-skills.ps1 [-Verify]`.
