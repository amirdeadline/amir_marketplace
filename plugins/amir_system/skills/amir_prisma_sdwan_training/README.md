# amir_prisma_sdwan_training

Training-architecture skill for Prisma SD-WAN: designs progressive curricula (Basic five-day course through
advanced SME path) on top of the `amir_prisma_sdwan_sme` knowledge layer, maps every exercise to the
documented Prisma SASE lab with an honest status (READY / PARTIAL / MISSING / UNVERIFIED), and stops for
approval after the curriculum structure before any lesson, slide, lab manual or test is produced.

## Invoke

| Tool | How |
|---|---|
| Claude Code | `/amir_prisma_sdwan_training <audience, level, constraints>`; plugin form `/amir:amir_prisma_sdwan_training` after the plugin cache refreshes |
| Cursor | Type `/` in Agent chat, pick `amir_prisma_sdwan_training`, then the request |

## Files

| Path | Purpose |
|---|---|
| `SKILL.md` | Preparation (activate the SME skill, read its indexes), lab discovery rules, instructional-design rules, deliverable set, quality gates, stop-and-ask |
| `references/curriculum_templates.md` | Module record, lab blueprint format and status enum, time accounting, labels, deliverable list, quality gates, review-question format |
| `references/lab_inventory_prisma_sase_basic.md` | Documentation-derived inventory of the Prisma SASE Basic lab (2026-10-08), with what each capability means for training labs |
| `scripts/check_schedule.py` | Quality gates: `basic` (days × scheduled hours, contiguous sessions, contact vs break) and `advanced` (module hour columns sum to totals, grand total) |
| `tests/test_check_schedule.py` | Unit tests |
| `config.json` | SME skill location override, read-only lab root, KB root, default output folder |

## Dependencies

`amir_prisma_sdwan_sme` (knowledge layer; `scripts/sme.py`), which in turn delegates live KB lookups to
`amir_prisma_sdwan/scripts/kbq.py`. The lab tree is read-only and may contain secrets in `.env` and
`secrets/`; the skill never reads them.

## Maintenance

```text
python -m pytest -q -p no:cacheprovider tests
python scripts/check_schedule.py basic <curriculum>/01_BASIC_5_DAY_PLAN.md
python scripts/check_schedule.py advanced <curriculum>/02_ADVANCED_TRAINING_PATH.md
```

User-level links: `powershell -File <marketplace>\scripts\install-user-skills.ps1 [-Verify]` (this skill is in the installer's default list).
