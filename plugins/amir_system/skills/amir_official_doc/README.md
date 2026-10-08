# amir_official_doc

Writes professional technical documents in Markdown: numbered headings kept correct by a script, human
technical-writing style, context before detail, a separate evidence register, and a final quality gate.
It does not decide technical truth; for Prisma SD-WAN content it uses `amir_prisma_sdwan`.

## Invoke

| Tool | How |
|---|---|
| Claude Code | `/amir_official_doc <request>`; with Prisma SD-WAN content: `/amir_prisma_sdwan /amir_official_doc <request>` |
| Cursor | Type `/` in Agent chat, pick `amir_official_doc` (and `amir_prisma_sdwan` if the topic is Prisma SD-WAN), then the request |

## Files

| Path | Purpose |
|---|---|
| `SKILL.md` | Workflow (scope, evidence, outline, draft, number, check, quality gate, view, report) and essentials |
| `references/writing_style.md` | Voice, AI-pattern removal, context and progressive depth, procedures, terminology |
| `references/structure.md` | Numbering scheme, document opening, appendices, Markdown element conventions |
| `references/evidence_register.md` | `<slug>.evidence.md` format and the rules `mddoc.py` enforces |
| `references/quality_gate.md` | Final review checklist (automated and manual items) |
| `templates/document_skeleton.md` | Title, document-control table, introduction, sources appendix |
| `scripts/mddoc.py` | `number` (renumber headings, fix anchors), `check` (structure, links, tables, style, evidence), `outline` |
| `tests/` | Unit tests for `mddoc.py` and a load check for both paired skills |

## Viewer

Documents open in the `amir_md` extension (Cursor and VS Code): book icon **Open with amir_md** in the
editor title bar, or right-click the `.md` file. The Markdown file stays the source of truth.

## Maintenance

```text
python scripts/mddoc.py check <doc.md> --registry <KB root>/palo-alto-knowledge-base/source-registry.json
python -m pytest -q -p no:cacheprovider tests
```
