# Document structure and Markdown conventions

## 1. Headings and numbering

- Exactly one `# Title` at the top. It is not numbered.
- Numbered sections start at level 2:

  ```text
  ## 1. Introduction
  ### 1.1 Purpose
  ### 1.2 Scope
  ## 2. Circuit Health
  ### 2.1 Packet Loss
  #### 2.1.1 Collecting Loss Data
  ## Appendix A. Sources
  ### A.1 Official Sources
  ```

- Do not skip levels (`##` straight to `####`). Keep to four numbered levels (`1.1.1.1`) at most.
- Write headings without caring about numbers, then run `mddoc.py number <doc>`. It numbers every heading,
  letters the appendices (a level-2 heading starting with "Appendix"), and rewrites internal `#anchor`
  links that the new numbers changed. `mddoc.py number <doc> --check` only reports.
- Headings are short noun phrases ("Packet Loss", "Collecting Loss Data"), not sentences or questions.

## 2. Document opening

Under the title, a document-control table (no heading), then the introduction:

- `Introduction` with `Purpose`, `Scope` (what is in and out, product and release scope) and `Intended
  Audience` (role and assumed knowledge). Add `Conventions` or `Terminology` only if the document needs them.
- No table of contents. amir_md, GitHub and Obsidian build navigation from the headings.

## 3. Body

- Organize by the reader's task or by system domain, whichever the reader uses to find things. A health
  assessment is usually organized by domain; an implementation guide by the order of work.
- For assessment or check items, give each item only the fields that help: purpose, how to check, expected
  result, interpretation, action. A table works well when there are many similar items.
- A section with more than about 600 words of text before its first subheading should be split
  (`mddoc.py check` warns, W104). Very long documents (over about 15,000 words) can become several documents
  with a short index document.

## 4. Appendices

Typical, only when useful: `Sources`, `Glossary`, `Open Items` (UNKNOWN items and decisions pending),
`Change History`. Appendices are level-2 headings starting with "Appendix".

## 5. Markdown elements

| Element | Convention |
|---|---|
| Tables | GitHub-flavored pipe tables with a header row. Escape a pipe inside a cell as `\|`. |
| Code, commands, output | Fenced blocks with a language (`text`, `bash`, `json`, `yaml`). |
| Inline literals | Backticks for commands, fields, values, paths, file names. |
| GUI labels | **Bold**, exactly as shown in the product. |
| Callouts | `> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`, `> [!CAUTION]` (GitHub alert syntax). |
| Diagrams | Mermaid in a fenced block tagged `mermaid`. Keep a one-sentence description under it. |
| Images | Relative paths, for example `images/topology.png`, with meaningful alt text. |
| Internal links | `[text](#anchor)`. Anchor = heading text in lower case, punctuation removed, spaces as hyphens (`## 2.1 Packet Loss` -> `#21-packet-loss`). |

Avoid raw HTML, `{#id}` heading attributes, footnote syntax and other extensions that the viewer or GitHub
do not support.

## 6. Files

- Document: `<slug>.md`. Evidence register: `<slug>.evidence.md` in the same folder.
- Images in an `images/` folder next to the document.
- File names in lower case with hyphens.
