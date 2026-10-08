---
name: amir_official_doc
description: >-
  Use when the user invokes /amir_official_doc or /amir:amir_official_doc, or asks for professional
  technical documentation written in Markdown: customer or internal guides, implementation, operations or
  Day-2 guides, runbooks, health or maturity assessments, design documents, troubleshooting guides, or
  technical reports, including editing or reviewing such a document. Use together with /amir_prisma_sdwan
  when the document covers Palo Alto Networks Prisma SD-WAN.
argument-hint: "[document request]"
---

# Official technical documentation

Write like an experienced technical writer who is also an engineer. This skill controls structure, writing
quality, formatting and presentation. It does **not** establish technical truth.

## 1. Skill folder and tool

`<skill_dir>` is the folder containing this file. Claude Code: `${CLAUDE_SKILL_DIR}`. Cursor: the folder of
the SKILL.md path shown with the attached skill. Fallbacks: `~/.claude/skills/amir_official_doc`,
`~/.cursor/skills/amir_official_doc`.

The document tool is `python "<skill_dir>/scripts/mddoc.py"` (`number`, `check`, `outline`; `--help` for details).

## 2. Where technical facts come from

- **Prisma SD-WAN content:** `/amir_prisma_sdwan` supplies every technical claim. If it is not loaded, load it
  now (Claude Code: the Skill tool; Cursor: read `../amir_prisma_sdwan/SKILL.md` next to this skill folder)
  and follow its retrieval, evidence and stop-and-ask rules.
- **Other subjects:** use sources the user supplied, files in the project, or another evidence skill. If
  there is no source for a technical statement, ask. Never fill a section from memory.
- Writing never changes a claim's evidence label. Rewording must not turn INFERENCE into fact.

## 3. Workflow

1. **Scope.** Establish document type, audience (customer or internal), purpose, depth, product and release
   scope, and output path (default `docs/<slug>.md` in the current project unless the user names one). Ask
   only for what is missing and material, in one message.
2. **Evidence.** Determine the domains the document must cover from the evidence, not from a fixed
   checklist. Record every substantive claim in `<slug>.evidence.md` (format: `references/evidence_register.md`).
   List gaps. Ask the user about material gaps before drafting the sections they affect.
3. **Outline.** Build it from the evidence and the reader's needs. For a long document (more than about
   eight major sections), show the outline and the open gaps once and wait for confirmation. A section exists
   only if it has supported content or the reader needs it.
4. **Draft.** Read `references/writing_style.md` and `references/structure.md` before writing. Start from
   `templates/document_skeleton.md`. Do not type section numbers by hand; the tool assigns them. Spell out
   acronyms and product terms the way the evidence spells them, never from memory.
5. **Number.** `mddoc.py number <doc>`. Run it again after every structural edit.
6. **Check.** `mddoc.py check <doc>`; add `--registry <KB root>/palo-alto-knowledge-base/source-registry.json`
   when the evidence uses SRC IDs. The sibling `<slug>.evidence.md` is picked up automatically. Fix every
   ERROR. Fix each WARN or keep it for a reason you can state.
7. **Quality gate (mandatory).** Read the finished document top to bottom against
   `references/quality_gate.md` and fix what fails. A document is not complete until this is done; a
   passing `mddoc.py check` does not replace it.
8. **View.** Open the document for the user (section 6).
9. **Report.** Give the document and evidence paths, the check result, open (UNKNOWN) items, a warning if
   the document relies on internal sources, and the quality gate as five lines (Technical, Content,
   Writing, Structure, Evidence), each "pass" or what remains and why.

## 4. Writing essentials

Full rules and examples: `references/writing_style.md`. The short version:
- Plain, direct professional English. No filler, hype, generic introductions, repeated summaries or
  artificial transitions. No em dashes as sentence separators.
- Explain context before detail: what it is, why it matters, what is checked or configured, how it affects
  the system, how to check it, how to read the result. Include only the parts that help; never force a template.
- Progressive depth: concept, purpose, operational relevance, technical behavior, check, interpretation,
  then troubleshooting or recommendation.
- Prose for explanation, numbered steps for procedures, tables for comparisons and check matrices. Bullets
  only for real lists. Notes only for things a reader must not miss.
- One term per concept throughout. Define each acronym at first use.

## 5. Structure essentials

Full rules: `references/structure.md`.
- Markdown is the source of truth. Standard Markdown only (GitHub-flavored tables, fenced code with a
  language, `> [!NOTE]` style callouts, Mermaid fenced blocks for diagrams). No proprietary syntax, no
  `{#id}` attributes, no hand-made table of contents (the viewer builds navigation from headings).
- One `# Title`. Numbered sections start at `##` (`## 1.`, `### 1.1`, `#### 1.1.1`). Appendices are
  `## Appendix A.` with `### A.1`.
- Evidence stays out of the reading flow: a Sources appendix in the document, full traceability in the
  sidecar register. For customer documents, do not expose internal paths; describe internal references
  generically or leave them out of the appendix (the register keeps them).
- UNKNOWN items stay visible to the reader, as "To be confirmed" text in the section or in an Open items appendix.

## 6. Viewing the document

The user's viewer is the `amir_md` extension (installed in Cursor and VS Code). It gives a navigation pane
with a collapsible heading tree, folding sections, current-section highlight, readable tables and code, and
export to Word, PDF and HTML.

- Open the file in the editor: `cursor -r "<doc path>"` (or `code -r "<doc path>"`). Then tell the user to
  click the book icon **Open with amir_md** in the editor title bar, or right-click the file and choose
  **Open with amir_md**.
- Do not change the user's editor settings to force this.
- amir_md 0.1.0 shows Mermaid diagrams and `> [!NOTE]` callouts as code and quotes. GitHub and Obsidian
  render them. Keep them portable; do not replace them with images or HTML unless the user asks.

## 7. Editing an existing document

Keep its structure unless the user asks for a restructure. Run `mddoc.py number` and `mddoc.py check` after
every structural change. If the document was not written with this skill, run `mddoc.py check` first and
show the user the findings before rewriting anything.

## Red flags

| Thought | Reality |
|---|---|
| "I'll add a section on X to look complete" | No evidence, no section. Ask, or leave it out. |
| "I'll renumber the headings myself" | Run `mddoc.py number`. Hand numbering drifts. |
| "A citation after every sentence is safest" | Use the evidence register; keep prose readable. |
| "This value is typical, I'll use it" | Typical is not sourced. Stop and ask. |
| "Every topic needs all six context points" | Only the ones that help the reader. |
| "The check passed, so the document is done" | The tool checks structure. Walk the quality gate too. |
